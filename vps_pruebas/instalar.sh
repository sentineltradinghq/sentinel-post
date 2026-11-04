#!/usr/bin/env bash
# Prepara el VPS temporal de pruebas (hyperopt y backtests con detalle de 1m).
# Uso en el VPS NUEVO:
#   curl -fsSL https://raw.githubusercontent.com/sentineltradinghq/sentinel-post/main/vps_pruebas/instalar.sh | FT_VERSION=2026.x bash
set -e
FT_VERSION=${FT_VERSION:-}
CCXT_VERSION=${CCXT_VERSION:-}
RAW=https://raw.githubusercontent.com/sentineltradinghq/sentinel-post/${REF:-main}/vps_pruebas
export DEBIAN_FRONTEND=noninteractive

echo "== 1/5 Sistema (paquetes, hora UTC)"
apt-get update -qq
apt-get install -y -qq python3-venv python3-dev build-essential git tmux rsync htop curl jq >/dev/null
timedatectl set-timezone UTC || true

echo "== 2/5 Swap de 16 GB (red de seguridad para backtests grandes)"
if ! swapon --show | grep -q /swapfile; then
  fallocate -l 16G /swapfile && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
sysctl -w vm.swappiness=10 >/dev/null

echo "== 3/5 Freqtrade ${FT_VERSION:-última versión}"
mkdir -p /root/freqtrade && cd /root/freqtrade
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -U pip wheel
.venv/bin/pip install -q "freqtrade${FT_VERSION:+==$FT_VERSION}" ${CCXT_VERSION:+"ccxt==$CCXT_VERSION"}
.venv/bin/freqtrade create-userdir --userdir user_data >/dev/null
.venv/bin/freqtrade --version

echo "== 4/5 Herramientas"
curl -fsSL "$RAW/sanitizar.py" -o /root/freqtrade/sanitizar.py
curl -fsSL "$RAW/descargar_datos.sh" -o /root/freqtrade/descargar_datos.sh
chmod +x /root/freqtrade/descargar_datos.sh

echo "== 5/5 Listo"
echo "RAM: $(free -g | awk '/Mem/{print $2}') GB · Núcleos: $(nproc) · Swap: $(free -g | awk '/Swap/{print $2}') GB"
echo "Siguiente paso: copiar estrategias y configs DESDE PRODUCCIÓN (te lo da Claude)."
