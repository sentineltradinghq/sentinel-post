#!/usr/bin/env bash
# Instala en el VPS el publicador de cierres de los bots (Discord + GitHub).
# Uso:  curl -fsSL https://raw.githubusercontent.com/sentineltradinghq/sentinel-post/main/resultados/instalar_resultados.sh | bash
set -e
DIR=/root/sentinel-resultados
RAW=https://raw.githubusercontent.com/sentineltradinghq/sentinel-post/main/resultados

echo "== 1/5 Paquetes del sistema (venv y fuente DejaVu)"
export DEBIAN_FRONTEND=noninteractive
apt-get install -y -qq python3-venv fonts-dejavu-core >/dev/null 2>&1 || { apt-get update -qq && apt-get install -y -qq python3-venv fonts-dejavu-core >/dev/null; }

echo "== 2/5 Descargando el script en $DIR"
mkdir -p "$DIR"
curl -fsSL "$RAW/publicar_cierres.py" -o "$DIR/publicar_cierres.py"

echo "== 3/5 Entorno de Python (ccxt, pillow, requests)"
[ -d "$DIR/.venv" ] || python3 -m venv "$DIR/.venv"
"$DIR/.venv/bin/pip" install -q --upgrade pip
"$DIR/.venv/bin/pip" install -q ccxt pillow requests

echo "== 4/5 Claves (se guardan solo en este VPS, en $DIR/config.env)"
if [ -f "$DIR/config.env" ] && grep -q DISCORD_WEBHOOK "$DIR/config.env" && grep -q GITHUB_TOKEN "$DIR/config.env"; then
  echo "   Ya existen, se conservan. (Para cambiarlas: borra $DIR/config.env y vuelve a correr el instalador)"
else
  read -r -s -p "   Pega la URL del webhook de Discord y Enter: " WH < /dev/tty; echo
  read -r -s -p "   Pega el token de GitHub (sentinel-vps) y Enter: " TK < /dev/tty; echo
  umask 077
  printf 'DISCORD_WEBHOOK=%s\nGITHUB_TOKEN=%s\n' "$WH" "$TK" > "$DIR/config.env"
  chmod 600 "$DIR/config.env"
fi
# comprobar token
if "$DIR/.venv/bin/python" - <<'EOF'
import os, requests
for l in open("/root/sentinel-resultados/config.env"):
    k, _, v = l.strip().partition("="); os.environ[k] = v
r = requests.get("https://api.github.com/repos/sentineltradinghq/sentinel-post",
                 headers={"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"]}, timeout=20)
ok = r.status_code == 200 and r.json().get("permissions", {}).get("push")
print("   Token de GitHub:", "OK (puede escribir en sentinel-post)" if ok else f"PROBLEMA ({r.status_code})")
raise SystemExit(0 if ok else 1)
EOF
then :; else echo "   Revisa el token (Contents: Read and write en sentinel-post). Borra $DIR/config.env y repite."; exit 1; fi

echo "== 5/5 Primera ejecución"
cd "$DIR"
if [ ! -f estado.json ]; then
  .venv/bin/python publicar_cierres.py --init
fi
echo "   Mandando a Discord una tarjeta de prueba con el último cierre..."
.venv/bin/python publicar_cierres.py --prueba
LINEA="*/5 * * * * cd $DIR && flock -n /tmp/sentinel-resultados.lock .venv/bin/python publicar_cierres.py >> $DIR/publicar.log 2>&1"
( crontab -l 2>/dev/null | grep -v 'publicar_cierres.py' ; echo "$LINEA" ) | crontab -
echo
echo "Listo. Revisa Discord: debe haber llegado la tarjeta de prueba."
echo "Desde ahora, cada cierre nuevo se publica solo (revisión cada 5 minutos)."
echo "Registro: tail -n 30 $DIR/publicar.log"
