#!/usr/bin/env bash
# Instala en el VPS el panel de posiciones de Sentinel (página con HTTPS + contraseña).
# Uso:  curl -fsSL https://raw.githubusercontent.com/sentineltradinghq/sentinel-post/main/panel/instalar_panel.sh | bash
set -e
DIR=/root/sentinel-panel
REF=${REF:-main}
RAW=https://raw.githubusercontent.com/sentineltradinghq/sentinel-post/$REF/panel
CADDY_VER=2.8.4

echo "== 1/6 Paquetes del sistema"
export DEBIAN_FRONTEND=noninteractive
apt-get install -y -qq python3-venv nano curl >/dev/null 2>&1 || { apt-get update -qq && apt-get install -y -qq python3-venv nano curl >/dev/null; }

echo "== 2/6 Descargando el panel en $DIR"
mkdir -p "$DIR/static"
curl -fsSL "$RAW/servidor.py" -o "$DIR/servidor.py"
curl -fsSL "$RAW/static/index.html" -o "$DIR/static/index.html"
[ -d "$DIR/.venv" ] || python3 -m venv "$DIR/.venv"
"$DIR/.venv/bin/pip" install -q --upgrade pip
"$DIR/.venv/bin/pip" install -q ccxt requests

echo "== 3/6 Archivo de cuentas"
if [ ! -f "$DIR/cuentas.ini" ]; then
  CLAVE=$(tr -dc 'a-zA-Z0-9' </dev/urandom | head -c 12)
  umask 077
  cat > "$DIR/cuentas.ini" <<EOF
# =====================================================================
#  SENTINEL · CUENTAS DEL PANEL (llaves de SOLO LECTURA)
#  Reemplaza cada PEGA_AQUI por tu llave. El nombre entre [corchetes]
#  es el que verás en la página; puedes cambiarlo.
#  Una cuenta que siga con PEGA_AQUI simplemente no se muestra.
#  Guardar: Ctrl+O y Enter · Salir: Ctrl+X
# =====================================================================

[panel]
# Contraseña para entrar a la página (puedes cambiarla)
clave = $CLAVE

[telegram]
# token: el del bot de Telegram (puede ser el mismo de Master Control, de @BotFather)
# chat_id: tu número de usuario de Telegram (escríbele a @userinfobot y te lo da)
token   = PEGA_AQUI
chat_id = PEGA_AQUI

[Binance Principal]
exchange   = binance
api_key    = PEGA_AQUI
api_secret = PEGA_AQUI

[Binance 2]
exchange   = binance
api_key    = PEGA_AQUI
api_secret = PEGA_AQUI

[Binance 3]
exchange   = binance
api_key    = PEGA_AQUI
api_secret = PEGA_AQUI

[Bybit]
exchange   = bybit
api_key    = PEGA_AQUI
api_secret = PEGA_AQUI

[Bitunix 1]
exchange   = bitunix
api_key    = PEGA_AQUI
api_secret = PEGA_AQUI

[Bitunix 2]
exchange   = bitunix
api_key    = PEGA_AQUI
api_secret = PEGA_AQUI

[Bitunix 3]
exchange   = bitunix
api_key    = PEGA_AQUI
api_secret = PEGA_AQUI

[Pionex]
exchange   = pionex
api_key    = PEGA_AQUI
api_secret = PEGA_AQUI
EOF
  chmod 600 "$DIR/cuentas.ini"
  echo "   Ahora se abre el archivo para que pegues tus llaves."
  echo "   (Pega con clic derecho o Shift+Insert. Guardar: Ctrl+O y Enter. Salir: Ctrl+X)"
  read -r -p "   Presiona Enter para abrirlo..." _ < /dev/tty
  nano "$DIR/cuentas.ini" < /dev/tty > /dev/tty
else
  echo "   Ya existe; se conserva. (Para editarlo después: escribe  panel-cuentas)"
fi

cat > /usr/local/bin/panel-cuentas <<EOF
#!/usr/bin/env bash
nano $DIR/cuentas.ini && echo "Guardado. El panel lo toma solo en unos segundos."
EOF
chmod +x /usr/local/bin/panel-cuentas

echo "== 4/6 Servicio del panel"
cat > /etc/systemd/system/sentinel-panel.service <<EOF
[Unit]
Description=Sentinel panel de posiciones
After=network-online.target
[Service]
WorkingDirectory=$DIR
Environment=FREQTRADE_DIR=/root/freqtrade
Environment=PUERTO=8095
ExecStart=$DIR/.venv/bin/python $DIR/servidor.py
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable -q --now sentinel-panel
systemctl restart sentinel-panel

echo "== 5/6 HTTPS (Caddy + certificado gratuito)"
IP=$(curl -fsS4 --max-time 5 https://api.ipify.org || hostname -I | awk '{print $1}')
DOMINIO="${IP//./-}.sslip.io"
OCUPADO=$(ss -ltnp 2>/dev/null | awk '$4 ~ /:(80|443)$/' | grep -v caddy || true)
if [ -n "$OCUPADO" ]; then
  echo "   AVISO: los puertos 80/443 ya los usa otro programa:"; echo "$OCUPADO"
  echo "   Mándale una foto de esto a Claude. El panel queda corriendo, pero sin acceso web todavía."
else
  if [ ! -x /usr/local/bin/caddy ]; then
    curl -fsSL "https://github.com/caddyserver/caddy/releases/download/v$CADDY_VER/caddy_${CADDY_VER}_linux_amd64.tar.gz" | tar -xz -C /usr/local/bin caddy
  fi
  cat > "$DIR/Caddyfile" <<EOF
$DOMINIO {
	encode gzip
	header Strict-Transport-Security "max-age=31536000"
	reverse_proxy 127.0.0.1:8095
}
EOF
  cat > /etc/systemd/system/sentinel-caddy.service <<EOF
[Unit]
Description=Caddy (HTTPS del panel Sentinel)
After=network-online.target
[Service]
ExecStart=/usr/local/bin/caddy run --config $DIR/Caddyfile --adapter caddyfile
Restart=always
RestartSec=5
AmbientCapabilities=CAP_NET_BIND_SERVICE
[Install]
WantedBy=multi-user.target
EOF
  if command -v ufw >/dev/null && ufw status | grep -q "Status: active"; then ufw allow 80/tcp >/dev/null; ufw allow 443/tcp >/dev/null; fi
  systemctl daemon-reload
  systemctl enable -q --now sentinel-caddy
  systemctl restart sentinel-caddy
fi

echo "== 6/6 Comprobando (espera unos 20 segundos)"
sleep 20
ESTADO=$(systemctl is-active sentinel-panel)
echo "   Panel: $ESTADO"
"$DIR/.venv/bin/python" - <<'EOF'
import sqlite3, json, configparser
cp = configparser.ConfigParser(interpolation=None); cp.optionxform = str; cp.read("/root/sentinel-panel/cuentas.ini")
n = [s for s in cp.sections() if s.lower() not in ("panel", "telegram") and "PEGA_AQUI" not in cp[s].get("api_key", "PEGA_AQUI")]
print(f"   Cuentas con llave: {len(n)} → {', '.join(n) if n else 'ninguna todavía'}")
EOF
CLAVE=$(grep -E '^clave' "$DIR/cuentas.ini" | head -1 | cut -d= -f2 | tr -d ' ')
echo
echo "================================================================"
echo "  Abre en el celular o la PC:   https://$DOMINIO"
echo "  Contraseña:                   $CLAVE"
echo "================================================================"
echo "  Editar cuentas o llaves:  panel-cuentas"
echo "  Ver si hay errores:       journalctl -u sentinel-panel -n 30 --no-pager"
