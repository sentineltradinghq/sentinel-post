"""Quita llaves y desactiva Telegram/API en todos los configs copiados de producción.
En el VPS de pruebas nunca deben quedar llaves de exchange ni tokens."""
import glob, json, os
n = 0
for f in sorted(glob.glob("/root/freqtrade/user_data/*.json")):
    try:
        c = json.load(open(f))
    except Exception:
        continue
    if "exchange" not in c:
        continue
    c["dry_run"] = True
    for k in ("key", "secret", "password", "uid"):
        if k in c["exchange"]:
            c["exchange"][k] = ""
    if "telegram" in c:
        c["telegram"]["enabled"] = False
        c["telegram"]["token"] = ""
        c["telegram"]["chat_id"] = ""
    if "api_server" in c:
        c["api_server"]["enabled"] = False
    if "webhook" in c:
        c["webhook"]["enabled"] = False
    if str(c.get("db_url", "")).startswith("sqlite:///"):
        c.pop("db_url")
    json.dump(c, open(f, "w"), indent=4)
    n += 1
print(f"{n} configs saneados (sin llaves, sin Telegram, sin webhooks, dry-run)")
