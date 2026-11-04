#!/usr/bin/env bash
# Descarga velas de futuros (1m incluido) para las pruebas. Correr dentro de tmux:
#   tmux new -s datos   →   /root/freqtrade/descargar_datos.sh   →   Ctrl+B y luego D para dejarlo corriendo
cd /root/freqtrade
FT=.venv/bin/freqtrade
echo "== Binance (USDT y USDC), desde sept 2019"
$FT download-data --exchange binance --trading-mode futures \
  --pairs BTC/USDT:USDT ETH/USDT:USDT SOL/USDT:USDT BTC/USDC:USDC \
  --timeframes 1m 5m 15m 1h 4h --timerange 20190901- --userdir user_data
echo "== Bybit, desde 2021"
$FT download-data --exchange bybit --trading-mode futures \
  --pairs BTC/USDT:USDT ETH/USDT:USDT SOL/USDT:USDT \
  --timeframes 1m 5m 15m 1h 4h --timerange 20210101- --userdir user_data
echo "== Listo"; du -sh user_data/data/*
