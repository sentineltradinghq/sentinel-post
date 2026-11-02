#!/usr/bin/env python3
"""Sentinel · Panel de posiciones en vivo (servidor del VPS).

Lee posiciones de: Binance (USDⓈ-M), Bybit (lineal USDT/USDC), Bitunix (futuros), Pionex (futuros)
y de los bots de Freqtrade (simulados). Sirve la página (static/index.html) con contraseña,
guarda el diario de trading y manda alertas a Telegram.

Todo con llaves de SOLO LECTURA definidas en cuentas.ini (junto a este archivo).
"""
import configparser, hashlib, hmac, json, logging, math, os, secrets, sqlite3, threading, time, uuid
from datetime import datetime, timezone

import requests

BASE = os.path.dirname(os.path.abspath(__file__))
INI = os.path.join(BASE, "cuentas.ini")
DB = os.path.join(BASE, "panel.db")
FREQ = os.environ.get("FREQTRADE_DIR", "/root/freqtrade")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("panel")
UA = {"User-Agent": "sentinel-panel/1.0"}

BOTS = {  # config de Freqtrade → nombre visible
    "config15m.json": "BTC 15m Long", "config15mshort.json": "BTC 15m Short", "config5m.json": "BTC 5m Long",
    "configbybit5mshort.json": "BTC 5m Short", "config_btc15mlong_usdc_live.json": "BTC 15m Long USDC",
    "config_btc15mshort_usdc_live.json": "BTC 15m Short USDC", "config_eth15m_long_live.json": "ETH 15m Long",
    "config_eth15mshort_live.json": "ETH 15m Short", "config_sol15mlong_binance_live.json": "SOL 15m Long",
    "config_sol15mshort_bybit_live.json": "SOL 15m Short",
}
CUENTA_BOTS = "Bots (simulados)"
ESTABLES = {"USDT", "USDC", "FDUSD", "BUSD", "USD", "TUSD", "DAI"}

# ======================================================================= utilidades
def f(x, d=None):
    try:
        v = float(x)
        return v if math.isfinite(v) else d
    except (TypeError, ValueError):
        return d


def ahora_ms():
    return int(time.time() * 1000)


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).isoformat() if ms else None


def par_de(raw):
    """BTCUSDT / BTC_USDT_PERP / BTC/USDT:USDT → ('BTC/USDT', 'BTC', 'BTCUSDT')"""
    s = raw.replace(":USDT", "").replace(":USDC", "").replace("_PERP", "").replace("-", "").upper()
    if "/" in s or "_" in s:
        b, q = s.replace("_", "/").split("/")[:2]
    else:
        q = next((q for q in ("USDT", "USDC", "FDUSD", "USD") if s.endswith(q)), "USDT")
        b = s[: -len(q)]
    return f"{b}/{q}", b, b + q


def leer_config():
    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str
    cp.read(INI, encoding="utf-8")
    cuentas, tg, panel = [], {}, {}
    for sec in cp.sections():
        d = {k.strip(): v.strip() for k, v in cp[sec].items()}
        low = sec.lower()
        if low == "telegram":
            tg = d
        elif low == "panel":
            panel = d
        else:
            if "PEGA_AQUI" in (d.get("api_key", "") + d.get("api_secret", "")) or not d.get("api_key"):
                continue
            cuentas.append(dict(nombre=sec, exchange=d.get("exchange", "").lower(), key=d["api_key"], secret=d.get("api_secret", "")))
    return cuentas, tg, panel


# ======================================================================= base de datos
def db():
    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as c:
        c.executescript("""
        create table if not exists cerradas(id text primary key, cuenta text, origen text, par text, lado text,
            entrada real, salida real, cantidad real, pnl real, pnl_pct real, r real, abierta text, cerrada text, aprox int default 0);
        create table if not exists notas(id text primary key, nota text, emocion text);
        create table if not exists seguimiento(id text primary key, cuenta text, exchange text, raw text, lado text, primera_vez integer,
            riesgo_inicial real, entrada real, cantidad real, margen real, ultimo_precio real, ultimo_pnl real, abierta_ms integer,
            alertas text default '{}');
        create table if not exists equity_dia(fecha text, cuenta text, equity real, primary key(fecha, cuenta));
        create table if not exists ajustes(clave text primary key, valor text);
        create table if not exists alertas_enviadas(clave text primary key, cuando integer);
        """)


def ajuste(clave, defecto):
    with db() as c:
        r = c.execute("select valor from ajustes where clave=?", (clave,)).fetchone()
    return json.loads(r["valor"]) if r else defecto


def guardar_ajuste(clave, valor):
    with db() as c:
        c.execute("insert or replace into ajustes values(?,?)", (clave, json.dumps(valor)))


ALERTAS_DEF = dict(liq_pct=8.0, be=True, r2=True, cierre=True, funding_pct=0.05, bots=False)
FONDEO_DEF = dict(cuenta="", balance_inicial=0, perdida_diaria_pct=4, drawdown_total_pct=8, objetivo_pct=10, aviso_pct=70)


# ======================================================================= precios públicos
PRECIOS, FUNDING = {}, {}   # (exchange, raw) → mark price / funding rate


def actualizar_precios():
    try:
        for x in requests.get("https://fapi.binance.com/fapi/v1/premiumIndex", headers=UA, timeout=8).json():
            PRECIOS[("binance", x["symbol"])] = f(x.get("markPrice"))
            FUNDING[("binance", x["symbol"])] = f(x.get("lastFundingRate"))
    except Exception as e:
        log.warning("precios binance: %s", e)
    try:
        for cat in ("linear", "inverse"):
            r = requests.get(f"https://api.bybit.com/v5/market/tickers?category={cat}", headers=UA, timeout=8).json()
            for x in (r.get("result") or {}).get("list") or []:
                PRECIOS[("bybit", x["symbol"])] = f(x.get("markPrice"))
                FUNDING[("bybit", x["symbol"])] = f(x.get("fundingRate"))
    except Exception as e:
        log.warning("precios bybit: %s", e)
    try:
        for x in requests.get("https://dapi.binance.com/dapi/v1/premiumIndex", headers=UA, timeout=8).json():
            PRECIOS[("binance", x["symbol"])] = f(x.get("markPrice"))
            if x["symbol"].endswith("_PERP"):
                PRECIOS[("binance", x["symbol"][:-5])] = f(x.get("markPrice"))
            FUNDING[("binance", x["symbol"])] = f(x.get("lastFundingRate"))
    except Exception as e:
        log.warning("precios binance coin-m: %s", e)
    try:
        r = requests.get("https://fapi.bitunix.com/api/v1/futures/market/tickers", headers=UA, timeout=8).json()
        for x in r.get("data") or []:
            PRECIOS[("bitunix", x["symbol"])] = f(x.get("markPrice")) or f(x.get("lastPrice"))
    except Exception as e:
        log.warning("precios bitunix: %s", e)


def usd(moneda):
    """Precio en dólares de una moneda (BNB, BTC…) usando los perpetuos de Binance/Bybit."""
    m = (moneda or "").upper()
    if m in ESTABLES:
        return 1.0
    for k in (("binance", m + "USDT"), ("bybit", m + "USDT"), ("binance", m + "USDC"), ("binance", m + "USD_PERP"), ("bybit", m + "USD")):
        if PRECIOS.get(k):
            return PRECIOS[k]
    return 0.0


# ======================================================================= conectores privados
class Conector:
    def __init__(self, c):
        self.c = c


class Binance(Conector):
    def __init__(self, c):
        super().__init__(c)
        import ccxt
        self.ex = ccxt.binanceusdm({"apiKey": c["key"], "secret": c["secret"], "enableRateLimit": True,
                                     "options": {"warnOnFetchOpenOrdersWithoutSymbol": False}})
        self.exs = ccxt.binance({"apiKey": c["key"], "secret": c["secret"], "enableRateLimit": True})
        self.exc = ccxt.binancecoinm({"apiKey": c["key"], "secret": c["secret"], "enableRateLimit": True,
                                      "options": {"warnOnFetchOpenOrdersWithoutSymbol": False}})
        self.ingresos, self.t_ingresos = [], 0

    def equity(self):
        b = self.ex.fetch_balance()
        info = b.get("info") or {}
        total, detalle = 0.0, {}
        for a in info.get("assets") or []:     # USDT, USDC, BNB, BTC… de la cuenta de futuros
            mb = f(a.get("marginBalance"))
            if mb is None:
                mb = f(a.get("walletBalance"), 0) + f(a.get("unrealizedProfit"), 0)
            if not mb:
                continue
            activo = a.get("asset", "")
            total += mb * usd(activo)
            detalle[activo] = round(mb, 6)
        if not detalle:
            total = f(info.get("totalMarginBalance")) or f((b.get("total") or {}).get("USDT"), 0)
        try:   # futuros COIN-M (margen en BNB, BTC, ETH…)
            bc = self.exc.fetch_balance()
            for a in (bc.get("info") or {}).get("assets") or []:
                mb = f(a.get("marginBalance"))
                if mb is None:
                    mb = f(a.get("walletBalance"), 0) + f(a.get("unrealizedProfit"), 0)
                if mb:
                    total += mb * usd(a.get("asset"))
                    detalle[a.get("asset", "") + " (COIN-M)"] = round(mb, 6)
        except Exception as e:
            log.info("%s sin COIN-M: %s", self.c["nombre"], str(e)[:120])
        self.billeteras = {"Futuros": round(total, 2)}
        try:   # resto de billeteras (Spot, Fondos, Earn, Bots…), valoradas en USDT por Binance
            for w in self.exs.sapiGetAssetWalletBalance({"quoteAsset": "USDT"}) or []:
                nombre, v = w.get("walletName", ""), f(w.get("balance"), 0)
                if v and "Futures" not in nombre:
                    total += v
                    self.billeteras[nombre] = round(v, 2)
        except Exception as e:
            log.info("%s billeteras: %s", self.c["nombre"], str(e)[:120])
        self.detalle = detalle
        return total

    def stops(self):
        out = {}
        ordenes = []
        try:
            ordenes += [(o.get("info") or {}) | {"_trig": o.get("triggerPrice") or o.get("stopPrice")} for o in self.ex.fetch_open_orders()]
        except Exception as e:
            log.warning("%s órdenes: %s", self.c["nombre"], e)
        try:   # órdenes condicionales nuevas (servicio "algo" de Binance)
            r = self.ex.request("openAlgoOrders", "fapiPrivate", "GET", {})
            ordenes += [o | {"_trig": o.get("triggerPrice")} for o in (r if isinstance(r, list) else r.get("orders") or [])]
        except Exception:
            pass
        for o in ordenes:
            tipo = str(o.get("type") or o.get("orderType") or o.get("origType") or "").upper()
            if "STOP" in tipo and "PROFIT" not in tipo:
                trig = f(o.get("_trig")) or f(o.get("stopPrice")) or f(o.get("triggerPrice"))
                lado = "long" if str(o.get("side")).upper() == "SELL" else "short"
                if trig:
                    out[(o.get("symbol"), lado)] = trig
        try:
            for o in self.exc.fetch_open_orders():
                i = o.get("info") or {}
                tipo = str(i.get("type") or i.get("origType") or "").upper()
                trig = f(o.get("triggerPrice")) or f(o.get("stopPrice")) or f(i.get("stopPrice"))
                if "STOP" in tipo and "PROFIT" not in tipo and trig:
                    out[(i.get("symbol"), "long" if str(i.get("side")).upper() == "SELL" else "short")] = trig
        except Exception:
            pass
        return out

    def posiciones(self):
        sl = self.stops()
        out = []
        for p in self.ex.fetch_positions():
            qty = abs(f(p.get("contracts"), 0) or 0)
            if not qty:
                continue
            i = p.get("info") or {}
            raw = i.get("symbol") or p["symbol"].replace("/", "").split(":")[0]
            lado = p.get("side") or ("long" if f(i.get("positionAmt"), 0) > 0 else "short")
            im = f(p.get("initialMargin")) or f(i.get("initialMargin")) or f(i.get("positionInitialMargin"))
            nocional = abs(f(p.get("notional")) or f(i.get("notional")) or 0)
            lev = f(p.get("leverage")) or f(i.get("leverage")) or (round(nocional / im, 1) if im and nocional else 1)
            out.append(dict(raw=raw, lado=lado, cantidad=qty, entrada=f(p.get("entryPrice")) or f(i.get("entryPrice")),
                            precio=f(p.get("markPrice")) or f(i.get("markPrice")), apalancamiento=lev,
                            liquidacion=f(p.get("liquidationPrice")) or None, margen=f(p.get("initialMargin")) or f(i.get("isolatedWallet")) or None,
                            sl=sl.get((raw, lado)), pnl=f(p.get("unrealizedPnl")), abierta_ms=None))
        try:   # posiciones COIN-M: contratos en USD → cantidad en moneda = contratos × tamaño / entrada
            for p in self.exc.fetch_positions():
                n = abs(f(p.get("contracts"), 0) or 0)
                if not n:
                    continue
                i = p.get("info") or {}
                raw = i.get("symbol") or ""
                ent = f(p.get("entryPrice")) or f(i.get("entryPrice"))
                mark = f(p.get("markPrice")) or f(i.get("markPrice")) or ent
                cs = f(p.get("contractSize")) or (100 if raw.startswith("BTC") else 10)
                lado = p.get("side") or ("long" if f(i.get("positionAmt"), 0) > 0 else "short")
                imc = f(p.get("initialMargin")) or f(i.get("initialMargin"))
                levc = f(p.get("leverage")) or f(i.get("leverage")) or (round((n * cs / mark) / imc, 1) if imc else 1)
                out.append(dict(raw=raw, lado=lado, cantidad=n * cs / ent, entrada=ent, precio=mark,
                                apalancamiento=levc, liquidacion=f(p.get("liquidationPrice")) or None,
                                margen=(f(p.get("initialMargin"), 0) or 0) * mark or None, sl=sl.get((raw, lado)),
                                pnl=(f(p.get("unrealizedPnl"), 0) or 0) * mark, funding=None, comisiones=None, abierta_ms=None))
        except Exception as e:
            log.info("%s posiciones COIN-M: %s", self.c["nombre"], str(e)[:120])
        return out

    def _ingresos(self):
        if time.time() - self.t_ingresos > 60:
            try:
                self.ingresos = self.ex.fapiPrivateGetIncome({"startTime": ahora_ms() - 7 * 864e5, "limit": 1000})
                self.t_ingresos = time.time()
            except Exception as e:
                log.warning("%s ingresos: %s", self.c["nombre"], e)
        return self.ingresos

    def costos(self, raw, desde_ms):
        fu = co = 0.0
        for x in self._ingresos():
            if x.get("symbol") == raw and int(x.get("time", 0)) >= desde_ms:
                if x.get("incomeType") == "FUNDING_FEE": fu += f(x.get("income"), 0)
                if x.get("incomeType") == "COMMISSION": co += -f(x.get("income"), 0)
        return fu, co

    def cierre(self, s):
        self.t_ingresos = 0
        pnl = sum(f(x.get("income"), 0) for x in self._ingresos() if x.get("symbol") == s["raw"] and int(x.get("time", 0)) >= s["primera_vez"] - 60000
                  and x.get("incomeType") in ("REALIZED_PNL", "COMMISSION", "FUNDING_FEE"))
        if not pnl:
            return dict(pnl=s["ultimo_pnl"], salida=s["ultimo_precio"], aprox=1)
        return dict(pnl=pnl, salida=s["ultimo_precio"], aprox=0)


class Bybit(Conector):
    def __init__(self, c):
        super().__init__(c)
        import ccxt
        self.ex = ccxt.bybit({"apiKey": c["key"], "secret": c["secret"], "enableRateLimit": True, "options": {"defaultType": "swap"}})

    def equity(self):
        total, detalle = 0.0, {}
        for tipo in ("UNIFIED", "CONTRACT"):
            try:
                r = self.ex.privateGetV5AccountWalletBalance({"accountType": tipo})
            except Exception:
                continue
            for cuenta in (r.get("result") or {}).get("list") or []:
                for c in cuenta.get("coin") or []:
                    eq = f(c.get("equity"), 0)
                    if eq:
                        v = f(c.get("usdValue")) or eq * usd(c.get("coin"))
                        total += v
                        detalle[f"{c.get('coin')}" + ("" if tipo == "UNIFIED" else " (contratos)")] = round(eq, 6)
        self.billeteras = {"Trading": round(total, 2)}
        try:
            r = self.ex.privateGetV5AssetTransferQueryAccountCoinsBalance({"accountType": "FUND"})
            fondos = sum(f(c.get("walletBalance"), 0) * usd(c.get("coin")) for c in (r.get("result") or {}).get("balance") or [])
            if fondos:
                total += fondos
                self.billeteras["Fondos"] = round(fondos, 2)
        except Exception as e:
            log.info("%s fondos: %s", self.c["nombre"], str(e)[:120])
        self.detalle = detalle
        return total

    def posiciones(self):
        out = []
        for coin in ("USDT", "USDC"):
            r = self.ex.privateGetV5PositionList({"category": "linear", "settleCoin": coin, "limit": 200})
            for i in (r.get("result") or {}).get("list") or []:
                qty = f(i.get("size"), 0)
                if not qty:
                    continue
                lado = "long" if i.get("side") == "Buy" else "short"
                out.append(dict(raw=i["symbol"], lado=lado, cantidad=qty, entrada=f(i.get("avgPrice")), precio=f(i.get("markPrice")),
                                apalancamiento=f(i.get("leverage"), 1), liquidacion=f(i.get("liqPrice")) or None,
                                margen=f(i.get("positionIM")) or None, sl=f(i.get("stopLoss")) or None, pnl=f(i.get("unrealisedPnl")),
                                funding=None, comisiones=None, abierta_ms=int(i.get("createdTime") or 0) or None))
        try:   # contratos inversos (margen en la moneda): tamaño en USD
            r = self.ex.privateGetV5PositionList({"category": "inverse", "limit": 200})
            for i in (r.get("result") or {}).get("list") or []:
                n = f(i.get("size"), 0)
                if not n:
                    continue
                ent = f(i.get("avgPrice")); mark = f(i.get("markPrice")) or ent
                out.append(dict(raw=i["symbol"], lado="long" if i.get("side") == "Buy" else "short", cantidad=n / ent, entrada=ent, precio=mark,
                                apalancamiento=f(i.get("leverage"), 1), liquidacion=f(i.get("liqPrice")) or None,
                                margen=(f(i.get("positionIM"), 0) or 0) * mark or None, sl=f(i.get("stopLoss")) or None,
                                pnl=(f(i.get("unrealisedPnl"), 0) or 0) * mark, funding=None, comisiones=None,
                                abierta_ms=int(i.get("createdTime") or 0) or None))
        except Exception as e:
            log.info("%s inversos: %s", self.c["nombre"], str(e)[:120])
        return out

    def cierre(self, s):
        cat = "inverse" if s["raw"].endswith("USD") else "linear"
        r = self.ex.privateGetV5PositionClosedPnl({"category": cat, "symbol": s["raw"], "startTime": s["primera_vez"] - 60000, "limit": 50})
        lst = (r.get("result") or {}).get("list") or []
        if not lst:
            return dict(pnl=s["ultimo_pnl"], salida=s["ultimo_precio"], aprox=1)
        k = (f(lst[0].get("avgExitPrice")) or s["ultimo_precio"] or 1) if cat == "inverse" else 1
        return dict(pnl=sum(f(x.get("closedPnl"), 0) for x in lst) * k, salida=f(lst[0].get("avgExitPrice")) or s["ultimo_precio"], aprox=0)


class Bitunix(Conector):
    URL = "https://fapi.bitunix.com"

    def _get(self, path, params=None):
        params = {k: v for k, v in (params or {}).items() if v is not None}
        q = "".join(f"{k}{params[k]}" for k in sorted(params))
        nonce, ts = uuid.uuid4().hex, str(ahora_ms())
        digest = hashlib.sha256((nonce + ts + self.c["key"] + q).encode()).hexdigest()
        sign = hashlib.sha256((digest + self.c["secret"]).encode()).hexdigest()
        h = {"api-key": self.c["key"], "nonce": nonce, "timestamp": ts, "sign": sign, "Content-Type": "application/json", **UA}
        r = requests.get(self.URL + path, params=params, headers=h, timeout=10).json()
        if str(r.get("code")) != "0":
            raise RuntimeError(f"Bitunix {r.get('code')}: {r.get('msg')}")
        return r.get("data")

    def equity(self):
        total = 0.0
        detalle = {}
        for moneda in ("USDT", "USDC", "BTC", "ETH"):
            try:
                d = self._get("/api/v1/futures/account", {"marginCoin": moneda})
            except Exception:
                if moneda == "USDT":
                    raise
                continue
            d = d[0] if isinstance(d, list) and d else d or {}
            v = sum(f(d.get(k), 0) for k in ("available", "frozen", "margin", "crossUnrealizedPNL", "isolationUnrealizedPNL"))
            if v:
                total += v * usd(moneda)
                detalle[moneda] = round(v, 6)
        self.detalle = detalle
        return total

    def posiciones(self):
        sl = {}
        try:
            for o in self._get("/api/v1/futures/tpsl/get_pending_orders", {"limit": 100}) or []:
                if f(o.get("slPrice")):
                    sl[o.get("positionId")] = f(o.get("slPrice"))
        except Exception as e:
            log.warning("%s stops: %s", self.c["nombre"], e)
        out = []
        for p in self._get("/api/v1/futures/position/get_pending_positions") or []:
            qty = f(p.get("qty"), 0)
            if not qty:
                continue
            raw = p["symbol"]
            out.append(dict(raw=raw, lado=p.get("side", "").lower(), cantidad=qty, entrada=f(p.get("avgOpenPrice")),
                            precio=PRECIOS.get(("bitunix", raw)), apalancamiento=f(p.get("leverage"), 1),
                            liquidacion=f(p.get("liqPrice")) if f(p.get("liqPrice"), 0) > 0 else None, margen=f(p.get("margin")),
                            sl=sl.get(p.get("positionId")), pnl=f(p.get("unrealizedPNL")), funding=f(p.get("funding")),
                            comisiones=abs(f(p.get("fee"), 0)), abierta_ms=int(p.get("ctime") or 0) or None))
        return out

    def cierre(self, s):
        d = self._get("/api/v1/futures/position/get_history_positions", {"startTime": s["primera_vez"] - 3600000, "limit": 20}) or {}
        lst = [x for x in (d.get("positionList") or []) if x.get("symbol") == s["raw"]]
        if not lst:
            return dict(pnl=s["ultimo_pnl"], salida=s["ultimo_precio"], aprox=1)
        x = lst[0]
        # realizedPNL excluye comisiones y funding: neto = realizado − comisiones + funding (con su signo)
        return dict(pnl=f(x.get("realizedPNL"), 0) - abs(f(x.get("fee"), 0)) + f(x.get("funding"), 0),
                    salida=f(x.get("closePrice")) or s["ultimo_precio"], aprox=0)


class Pionex(Conector):
    URL = "https://api.pionex.com"

    def _get(self, path, params=None):
        params = dict(params or {}, timestamp=ahora_ms())
        q = "&".join(f"{k}={params[k]}" for k in sorted(params))
        sig = hmac.new(self.c["secret"].encode(), f"GET{path}?{q}".encode(), hashlib.sha256).hexdigest()
        r = requests.get(f"{self.URL}{path}?{q}", headers={"PIONEX-KEY": self.c["key"], "PIONEX-SIGNATURE": sig, **UA}, timeout=10).json()
        if not r.get("result"):
            raise RuntimeError(f"Pionex {r.get('code')}: {r.get('message')}")
        return r.get("data") or {}

    def equity(self):
        d = self._get("/uapi/v1/account/detail")
        eq, detalle = 0.0, {}
        for b in (d or {}).get("balances") or []:
            v = f(b.get("assets"), 0) + f(b.get("unrealizedPnL"), 0)
            if v:
                eq += v * usd(b.get("coin"))
                detalle[b.get("coin", "")] = round(v, 6)
        for p in (d or {}).get("positions") or []:       # posiciones aisladas: su margen y su PnL flotante
            if str(p.get("isolatedMode", "CROSS")).upper() == "CROSS":
                continue
            for bb in p.get("balances") or []:
                v = f(bb.get("free"), 0) + f(bb.get("frozen"), 0)
                if v:
                    eq += v * usd(bb.get("coin"))
            eq += f(p.get("unrealizedPnL"), 0) * (usd(par_de(p.get("symbol", ""))[2].replace(par_de(p.get("symbol", ""))[1], "", 1)) or 1)
        self.detalle = detalle
        self.billeteras = {"Futuros": round(eq, 2)}
        try:   # spot: todas las monedas valoradas en dólares
            sp = sum((f(b.get("free"), 0) + f(b.get("frozen"), 0)) * usd(b.get("coin"))
                     for b in (self._get("/api/v1/account/balances") or {}).get("balances") or [])
            if sp:
                eq += sp
                self.billeteras["Spot"] = round(sp, 2)
        except Exception as e:
            log.info("%s spot: %s", self.c["nombre"], str(e)[:120])
        try:   # bots: valor actual (inversión + ganancia) de cada bot activo
            vb = sum(b["valor"] for b in self.bots() if b.get("valor"))
            if vb:
                eq += vb
                self.billeteras["Bots"] = round(vb, 2)
        except Exception as e:
            log.info("%s bots: %s", self.c["nombre"], str(e)[:120])
        return eq

    def posiciones(self):
        out = []
        for p in (self._get("/uapi/v1/account/positions") or {}).get("positions") or []:
            net = f(p.get("netSize"), 0) or (f(p.get("sizeLong"), 0) + f(p.get("sizeShort"), 0))
            if not net:
                continue
            lado = (p.get("positionSide") or ("LONG" if net > 0 else "SHORT")).lower()
            out.append(dict(raw=p["symbol"], lado=lado, cantidad=abs(net), entrada=f(p.get("avgPrice")), precio=f(p.get("markPrice")),
                            apalancamiento=f(p.get("leverage"), 1), liquidacion=f(p.get("liquidationPrice")) or None,
                            margen=f(p.get("initialMargin")) or None, sl=None, pnl=f(p.get("unrealizedPnL")),
                            abierta_ms=int(p.get("createTime") or 0) or None))
        return out

    def bots(self):
        try:
            d = self._get("/api/v1/bot/orders", {"status": "running"})
        except Exception as e:
            return [dict(nombre="(sin acceso a bots)", detalle=str(e)[:120])]
        out = []
        for b in (d or {}).get("results") or []:
            bd = b.get("buOrderData") or {}
            if not getattr(self, "_log_bot", False):     # una vez: anotar los campos que trae Pionex, para ajustar
                log.info("Pionex buOrderData ejemplo: %s", json.dumps({k: v for k, v in bd.items() if not isinstance(v, (dict, list))})[:600])
                self._log_bot = True
            def num(*ks):
                return next((f(bd.get(k)) for k in ks if f(bd.get(k)) is not None), None)
            inv = num("investment", "totalInvestment", "quoteInvestment", "initQuoteInvestment", "quoteTotalInvestment", "usdtInvestment")
            gan = num("totalProfit", "profit", "pnl", "totalPnl", "gridProfit")
            valor = num("totalValue", "currentValue", "equity", "netValue", "totalAsset")
            if valor is None and inv is not None:
                valor = inv + (gan or 0)
            out.append(dict(nombre=b.get("customizeName") or b.get("botName") or b.get("buOrderType"), par=f"{b.get('base')}/{b.get('quote')}",
                            tipo=b.get("buOrderType"), inversion=inv, ganancia=gan, valor=valor, desde=iso(b.get("createTime"))))
        return out

    def cierre(self, s):
        return dict(pnl=s["ultimo_pnl"], salida=s["ultimo_precio"], aprox=1)


CONECTORES = {"binance": Binance, "bybit": Bybit, "bitunix": Bitunix, "pionex": Pionex}

# ======================================================================= bots de Freqtrade
def bots_freqtrade():
    pos, cerr = [], []
    for archivo, nombre in BOTS.items():
        try:
            c = json.load(open(os.path.join(FREQ, "user_data", archivo)))
            ruta = (c.get("db_url") or ("sqlite:///tradesv3.dryrun.sqlite" if c.get("dry_run") else "sqlite:///tradesv3.sqlite")).replace("sqlite:///", "")
            ruta = ruta if os.path.isabs(ruta) else os.path.join(FREQ, ruta)
            if not os.path.exists(ruta):
                continue
            ex = "bybit" if "bybit" in (c.get("exchange") or {}).get("name", "").lower() else "binance"
            con = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True, timeout=5)
            con.row_factory = sqlite3.Row
            cols = {r[1] for r in con.execute("pragma table_info(trades)")}
            liq = "liquidation_price" if "liquidation_price" in cols else "NULL"
            for t in con.execute(f"select id,pair,is_short,open_rate,amount,leverage,stop_loss,{liq} as liq,open_date,close_rate,close_profit,"
                                 "close_profit_abs,close_date,is_open from trades where is_open=1 or close_date >= datetime('now','-90 day')"):
                par, base, raw = par_de(t["pair"])
                lado = "short" if t["is_short"] else "long"
                lev = f(t["leverage"], 1) or 1
                abierta = datetime.fromisoformat(str(t["open_date"]).split(".")[0]).replace(tzinfo=timezone.utc).isoformat()
                if t["is_open"] and not f(t["amount"], 0):
                    continue
                if t["is_open"]:
                    pos.append(dict(id=f"bot|{archivo}|{t['id']}", cuenta=CUENTA_BOTS, origen="bot", bot=nombre, par=par, moneda=base, lado=lado,
                                    cantidad=f(t["amount"], 0), entrada=f(t["open_rate"]), precio=PRECIOS.get((ex, raw)) or f(t["open_rate"]),
                                    apalancamiento=lev, sl=f(t["stop_loss"]), liquidacion=f(t["liq"]), funding=None, comisiones=None,
                                    margen=f(t["amount"], 0) * f(t["open_rate"], 0) / lev, abierta=abierta, _ex=ex, _raw=raw))
                elif t["close_date"]:
                    cerrada = datetime.fromisoformat(str(t["close_date"]).split(".")[0]).replace(tzinfo=timezone.utc).isoformat()
                    cerr.append(dict(id=f"bot|{archivo}|{t['id']}", cuenta=CUENTA_BOTS, origen="bot", par=par, lado=lado, entrada=f(t["open_rate"]),
                                     salida=f(t["close_rate"]), cantidad=f(t["amount"]), pnl=f(t["close_profit_abs"], 0),
                                     pnl_pct=f(t["close_profit"], 0) * 100, r=None, abierta=abierta, cerrada=cerrada, bot=nombre))
            con.close()
        except Exception as e:
            log.warning("bot %s: %s", archivo, e)
    return pos, cerr


# ======================================================================= telegram
TG = {}


def telegram(texto):
    if not TG.get("token") or "PEGA_AQUI" in TG.get("token", "") or not TG.get("chat_id"):
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TG['token']}/sendMessage",
                      json={"chat_id": TG["chat_id"], "text": texto, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=10)
    except Exception as e:
        log.warning("telegram: %s", e)


def una_vez(clave, cada_s=None):
    """True si la alerta 'clave' no se ha enviado (o si pasó cada_s desde la última)."""
    with db() as c:
        r = c.execute("select cuando from alertas_enviadas where clave=?", (clave,)).fetchone()
        if r and (cada_s is None or time.time() - r["cuando"] < cada_s):
            return False
        c.execute("insert or replace into alertas_enviadas values(?,?)", (clave, int(time.time())))
    return True


def olvidar_alerta(prefijo):
    with db() as c:
        c.execute("delete from alertas_enviadas where clave like ?", (prefijo + "%",))


def fmt(v):
    v = abs(v)
    return f"{v:,.{1 if v >= 1000 else 2 if v >= 10 else 4}f}"


# ======================================================================= ciclo principal
ESTADO = {"actualizado": None, "cuentas": [], "posiciones": [], "cerradas": [], "pionex_bots": []}
LOCK = threading.Lock()


def derivados(p):
    s = 1 if p["lado"] == "long" else -1
    liq = p.get("liquidacion") or (p["entrada"] * (1 - 1 / p["apalancamiento"] + 0.005) if s == 1 else p["entrada"] * (1 + 1 / p["apalancamiento"] - 0.005))
    ref = p.get("sl") or liq
    dist_r = abs(p["entrada"] - ref) if ref else None
    r_act = (p["precio"] - p["entrada"]) * s / dist_r if dist_r and p.get("precio") else None
    dist_liq = abs(p["precio"] - liq) / p["precio"] * 100 if liq and p.get("precio") else None
    return liq, dist_r, r_act, dist_liq


def ciclo_privado(conectores, cuentas_estado, posiciones):
    al = ajuste("alertas", ALERTAS_DEF)
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    vistos, con_error = set(), set()
    for nombre, con in conectores.items():
        ex = con.c["exchange"]
        info = dict(nombre=nombre, exchange=ex, estado="ok", error="")
        try:
            info["equity"] = con.equity()
            if getattr(con, "detalle", None):
                info["activos"] = con.detalle
            if getattr(con, "billeteras", None):
                info["billeteras"] = con.billeteras
            with db() as c:
                c.execute("insert or ignore into equity_dia values(?,?,?)", (fecha, nombre, info["equity"]))
                r = c.execute("select equity from equity_dia where fecha=? and cuenta=?", (fecha, nombre)).fetchone()
            info["equity_inicio_dia"] = r["equity"] if r else info["equity"]
            ps = con.posiciones()
        except Exception as e:
            log.warning("%s: %s", nombre, e)
            info.update(estado="error", error=str(e)[:200], equity=None)
            con_error.add(nombre)
            cuentas_estado.append(info)
            # mantener las posiciones previas de esa cuenta para no "cerrarlas" por un error de red
            vistos |= {p["id"] for p in ESTADO["posiciones"] if p["cuenta"] == nombre}
            posiciones += [p for p in ESTADO["posiciones"] if p["cuenta"] == nombre]
            continue
        cuentas_estado.append(info)
        for p in ps:
            par, base, raw = par_de(p["raw"])
            pid = f"{nombre}|{raw}|{p['lado']}"
            vistos.add(pid)
            p["precio"] = PRECIOS.get((ex, raw)) or p.get("precio") or p["entrada"]
            with db() as c:
                s = c.execute("select * from seguimiento where id=?", (pid,)).fetchone()
                liq, dist_r, r_act, dist_liq = derivados(p)
                riesgo = (dist_r or 0) * p["cantidad"]
                if not s:
                    c.execute("insert into seguimiento(id,cuenta,exchange,raw,lado,primera_vez,riesgo_inicial,entrada,cantidad,margen,ultimo_precio,ultimo_pnl,abierta_ms) "
                              "values(?,?,?,?,?,?,?,?,?,?,?,?,?)", (pid, nombre, ex, p["raw"], p["lado"], ahora_ms(), riesgo, p["entrada"], p["cantidad"],
                                                                    p.get("margen"), p["precio"], p.get("pnl"), p.get("abierta_ms")))
                    primera = ahora_ms()
                else:
                    primera = s["primera_vez"]
                    c.execute("update seguimiento set entrada=?, cantidad=?, margen=?, ultimo_precio=?, ultimo_pnl=? where id=?",
                              (p["entrada"], p["cantidad"], p.get("margen"), p["precio"], p.get("pnl"), pid))
            fu, co = p.get("funding"), p.get("comisiones")
            if isinstance(con, Binance) and not p["raw"].endswith("_PERP"):
                fu, co = con.costos(p["raw"], p.get("abierta_ms") or primera)
            posiciones.append(dict(id=pid, cuenta=nombre, origen="manual", bot=None, par=par, moneda=base, lado=p["lado"], cantidad=p["cantidad"],
                                   entrada=p["entrada"], precio=p["precio"], apalancamiento=p["apalancamiento"], sl=p.get("sl"),
                                   liquidacion=p.get("liquidacion"), margen=p.get("margen"), funding=fu, comisiones=co,
                                   abierta=iso(p.get("abierta_ms") or primera), _ex=ex, _raw=raw))
            alertas_posicion(posiciones[-1], al, nombre)
    # posiciones que desaparecieron → al diario
    with db() as c:
        perdidas = [dict(r) for r in c.execute("select * from seguimiento") if r["id"] not in vistos and r["cuenta"] in conectores and r["cuenta"] not in con_error]
    for s in perdidas:
        try:
            res = conectores[s["cuenta"]].cierre(s)
        except Exception as e:
            log.warning("cierre %s: %s", s["id"], e)
            res = dict(pnl=s["ultimo_pnl"], salida=s["ultimo_precio"], aprox=1)
        par, base, raw = par_de(s["raw"])
        pnl = f(res["pnl"], 0)
        rid = f"{s['id']}|{s['primera_vez']}"
        r_val = pnl / s["riesgo_inicial"] if s["riesgo_inicial"] else None
        with db() as c:
            c.execute("insert or replace into cerradas values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (rid, s["cuenta"], "manual", par, s["lado"], s["entrada"], res["salida"], s["cantidad"], pnl,
                       pnl / s["margen"] * 100 if s["margen"] else None, r_val, iso(s["abierta_ms"] or s["primera_vez"]),
                       iso(ahora_ms()), res.get("aprox", 0)))
            c.execute("delete from seguimiento where id=?", (s["id"],))
        olvidar_alerta(s["id"])
        if al.get("cierre"):
            telegram(f"{'🟢' if pnl >= 0 else '🔴'} <b>Cerrada</b> · {s['cuenta']}\n{par} {s['lado'].upper()} · resultado <b>{'+' if pnl >= 0 else '−'}${fmt(pnl)}</b>"
                     + (f" ({r_val:+.2f} R)" if r_val is not None else "") + ("\n<i>(aproximado)</i>" if res.get("aprox") else ""))


def alertas_posicion(p, al, cuenta):
    if p["origen"] == "bot" and not al.get("bots"):
        return
    liq, dist_r, r_act, dist_liq = derivados(p)
    base = f"{cuenta} · {p['par']} {p['lado'].upper()}"
    if dist_liq is not None:
        if dist_liq < al.get("liq_pct", 8):
            if una_vez(f"{p['id']}|liq"):
                telegram(f"🚨 <b>CERCA DE LIQUIDACIÓN</b>\n{base}\nPrecio {fmt(p['precio'])} · liquidación {fmt(liq)} · a <b>{dist_liq:.1f} %</b>")
        elif dist_liq > al.get("liq_pct", 8) * 1.5:
            olvidar_alerta(f"{p['id']}|liq")
    if r_act is not None and p.get("sl"):
        if al.get("be") and r_act >= 1 and una_vez(f"{p['id']}|be"):
            telegram(f"🟢 <b>Llegó a 1R</b> · {base}\nPuedes mover el stop a breakeven ({fmt(p['entrada'])}).")
        if al.get("r2") and r_act >= 2 and una_vez(f"{p['id']}|r2"):
            telegram(f"🎯 <b>Objetivo 1:2 alcanzado</b> · {base}\nPrecio {fmt(p['precio'])}.")
    fr = FUNDING.get((p.get("_ex"), p.get("_raw")))
    if fr is not None and al.get("funding_pct"):
        paga = (fr > 0 and p["lado"] == "long") or (fr < 0 and p["lado"] == "short")
        if paga and abs(fr) * 100 >= al["funding_pct"] and una_vez(f"{p['id']}|fund", 8 * 3600):
            telegram(f"💸 <b>Funding alto</b> · {base}\nEstás pagando {abs(fr) * 100:.3f} % cada 8 h.")


def alertas_fondeo(cuentas):
    fd = ajuste("fondeo", FONDEO_DEF)
    c = next((c for c in cuentas if c["nombre"] == fd.get("cuenta")), None)
    if not c or not fd.get("balance_inicial") or c.get("equity") is None:
        return
    ini, eq = fd["balance_inicial"], c["equity"]
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lim_dia, lim_dd = ini * fd["perdida_diaria_pct"] / 100, ini * fd["drawdown_total_pct"] / 100
    perd = max(0, c.get("equity_inicio_dia", ini) - eq)
    aviso = fd.get("aviso_pct", 70) / 100
    if lim_dia and perd >= lim_dia * aviso and una_vez(f"fondeo|dia|{hoy}"):
        telegram(f"⚠️ <b>FONDEO · pérdida diaria</b>\nLlevas −${fmt(perd)} de −${fmt(lim_dia)} permitidos hoy ({perd / lim_dia * 100:.0f} %).")
    dd = max(0, ini - eq)
    if lim_dd and dd >= lim_dd * aviso and una_vez(f"fondeo|dd|{int(dd / lim_dd * 10)}"):
        telegram(f"⚠️ <b>FONDEO · drawdown total</b>\nLlevas −${fmt(dd)} de −${fmt(lim_dd)} ({dd / lim_dd * 100:.0f} %).")


def bucle():
    global TG
    conectores, firma, t_priv, t_bots, t_pionex = {}, None, 0, 0, 0
    bots_pos, bots_cerr, pionex_bots = [], [], []
    while True:
        try:
            cuentas, TG, _ = leer_config()
            nueva = json.dumps(cuentas, sort_keys=True)
            if nueva != firma:
                conectores = {}
                for c in cuentas:
                    if c["exchange"] in CONECTORES:
                        try:
                            conectores[c["nombre"]] = CONECTORES[c["exchange"]](c)
                        except Exception as e:
                            log.error("no pude crear %s: %s", c["nombre"], e)
                    else:
                        log.error("exchange desconocido en %s: %s", c["nombre"], c["exchange"])
                firma = nueva
                t_priv = 0
            actualizar_precios()
            if time.time() - t_bots > 10:
                bots_pos, bots_cerr = bots_freqtrade()
                t_bots = time.time()
            if time.time() - t_priv > 8:
                cuentas_estado, posiciones = [], []
                ciclo_privado(conectores, cuentas_estado, posiciones)
                al = ajuste("alertas", ALERTAS_DEF)
                for p in bots_pos:
                    alertas_posicion(p, al, CUENTA_BOTS)
                alertas_fondeo(cuentas_estado)
                with LOCK:
                    ESTADO["cuentas"], ESTADO["_manuales"] = cuentas_estado, posiciones
                t_priv = time.time()
            if time.time() - t_pionex > 60:
                t_pionex = time.time()
                pionex_bots = []
                for n, con in conectores.items():
                    if isinstance(con, Pionex):
                        try:
                            pionex_bots += [b | {"cuenta": n} for b in con.bots()]
                        except Exception as e:
                            log.warning("bots %s: %s", n, e)
            # refrescar precios de todo en cada vuelta
            manuales = ESTADO.get("_manuales") or []
            for p in manuales + bots_pos:
                p["precio"] = PRECIOS.get((p.get("_ex"), p.get("_raw"))) or p["precio"]
            with db() as c:
                notas = {r["id"]: dict(r) for r in c.execute("select * from notas")}
                cerr = [dict(r) for r in c.execute("select * from cerradas where cerrada >= ? order by cerrada desc",
                                                   (datetime.fromtimestamp(time.time() - 400 * 86400, timezone.utc).isoformat(),))]
            for t in cerr + bots_cerr:
                n = notas.get(t["id"])
                if n:
                    t["nota"], t["emocion"] = n["nota"], n["emocion"]
            with LOCK:
                ESTADO.update(actualizado=datetime.now(timezone.utc).isoformat(),
                              posiciones=[{k: v for k, v in p.items() if not k.startswith("_")} | {"_ex": p.get("_ex"), "_raw": p.get("_raw")}
                                          for p in manuales + bots_pos],
                              cerradas=cerr + bots_cerr, pionex_bots=pionex_bots)
        except Exception as e:
            log.exception("ciclo: %s", e)
        time.sleep(2)


# ======================================================================= servidor web (solo librería estándar)
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
from urllib.parse import parse_qs

SECRETO_F = os.path.join(BASE, ".secreto")
if not os.path.exists(SECRETO_F):
    open(SECRETO_F, "w").write(secrets.token_hex(32)); os.chmod(SECRETO_F, 0o600)
SECRETO = open(SECRETO_F).read().strip()

LOGIN = """<!doctype html><html lang=es><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Sentinel · Entrar</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0B0F1A;color:#F0F2F7;font:16px system-ui}
form{background:#121828;border:1px solid #232c45;border-radius:14px;padding:28px;width:min(340px,90vw)}h1{color:#F5A623;font-size:18px;margin:0 0 16px}
input{width:100%;box-sizing:border-box;padding:12px;border-radius:10px;border:1px solid #232c45;background:#0B0F1A;color:#F0F2F7;font:inherit}
button{margin-top:12px;width:100%;padding:12px;border:0;border-radius:10px;background:#F5A623;color:#111;font-weight:700;font:inherit}.e{color:#E74C3C;font-size:14px}</style>
<form method=post action=login><h1>SENTINEL · POSICIONES</h1><input type=password name=clave placeholder=Contraseña autofocus>
<button>Entrar</button><p class=e>__ERR__</p></form></html>"""


def firma_clave(clave):
    return hmac.new(SECRETO.encode(), clave.encode(), hashlib.sha256).hexdigest()


class Web(BaseHTTPRequestHandler):
    server_version = "sentinel"

    def log_message(self, *a):
        pass

    def _enviar(self, codigo, cuerpo, tipo="application/json", extra=None):
        b = cuerpo if isinstance(cuerpo, bytes) else (json.dumps(cuerpo) if tipo == "application/json" else cuerpo).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", tipo + "; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Frame-Options", "DENY")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _ok(self):
        clave = leer_config()[2].get("clave", "")
        c = SimpleCookie(self.headers.get("Cookie", ""))
        return bool(clave) and "sp" in c and hmac.compare_digest(c["sp"].value, firma_clave(clave))

    def _ruta(self):
        return self.path.split("?")[0].rstrip("/").split("/")[-1] or ""

    def do_GET(self):
        r = self._ruta()
        if r == "login":
            return self._enviar(200, LOGIN.replace("__ERR__", ""), "text/html")
        if not self._ok():
            if r == "estado":
                return self._enviar(401, {"error": "login"})
            return self._enviar(303, "", "text/html", {"Location": "login"})
        if r == "estado":
            with LOCK:
                d = {k: v for k, v in ESTADO.items() if not k.startswith("_")}
                d["posiciones"] = [{k: v for k, v in p.items() if not k.startswith("_")} for p in d["posiciones"]]
            d["alertas"] = ajuste("alertas", ALERTAS_DEF)
            d["fondeo"] = ajuste("fondeo", FONDEO_DEF)
            return self._enviar(200, d)
        return self._enviar(200, open(os.path.join(BASE, "static", "index.html"), "rb").read(), "text/html")

    def do_POST(self):
        r = self._ruta()
        n = min(int(self.headers.get("Content-Length") or 0), 100000)
        cuerpo = self.rfile.read(n).decode("utf-8", "replace")
        if r == "login":
            clave = parse_qs(cuerpo).get("clave", [""])[0]
            real = leer_config()[2].get("clave", "")
            if not real or not hmac.compare_digest(clave, real):
                time.sleep(1.5)
                return self._enviar(401, LOGIN.replace("__ERR__", "Contraseña incorrecta"), "text/html")
            return self._enviar(303, "", "text/html", {"Location": "./",
                "Set-Cookie": f"sp={firma_clave(clave)}; Max-Age={90 * 86400}; Path=/; HttpOnly; Secure; SameSite=Strict"})
        if not self._ok():
            return self._enviar(401, {"error": "login"})
        try:
            d = json.loads(cuerpo or "{}")
        except ValueError:
            return self._enviar(400, {"error": "json"})
        if r == "nota":
            with db() as c:
                c.execute("insert or replace into notas values(?,?,?)", (str(d["id"]), str(d.get("nota", ""))[:1000], str(d.get("emocion", ""))[:40]))
        elif r == "alertas":
            guardar_ajuste("alertas", {k: d.get(k, v) for k, v in ALERTAS_DEF.items()})
        elif r == "fondeo":
            guardar_ajuste("fondeo", {k: d.get(k, v) for k, v in FONDEO_DEF.items()})
        elif r == "prueba_telegram":
            telegram("✅ Prueba del panel de posiciones de Sentinel: las alertas llegan aquí.")
        else:
            return self._enviar(404, {"error": "no existe"})
        return self._enviar(200, {"ok": True})


if __name__ == "__main__":
    init_db()
    threading.Thread(target=bucle, daemon=True).start()
    puerto = int(os.environ.get("PUERTO", "8095"))
    log.info("panel escuchando en 127.0.0.1:%s", puerto)
    ThreadingHTTPServer(("127.0.0.1", puerto), Web).serve_forever()
