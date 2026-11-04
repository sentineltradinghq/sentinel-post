#!/usr/bin/env bash
# Descarga velas de futuros (1m incluido). Cada par desde su fecha de listado en Binance,
# así Freqtrade usa la descarga rápida (data.binance.vision) en vez de la API lenta.
# BTC primero: es lo que necesita el Scalper.
cd /root/freqtrade
FT=.venv/bin/freqtrade
TF="1m 5m 15m 1h 4h"
dl () { echo; echo "== $1 $2 desde $3 ${4:+hasta $4}"; $FT download-data --exchange "$1" --trading-mode futures --pairs "$2" --timeframes $TF --timerange "$3-$4" --userdir user_data; }
# Binance solo tiene archivos diarios (descarga rápida) desde 2020-01-01:
# el tramo de 2019 va por la API (pocos meses) y el resto por la descarga rápida.
dl binance BTC/USDT:USDT 20190910 20200101
dl binance BTC/USDT:USDT 20200101
dl binance ETH/USDT:USDT 20191128 20200101
dl binance ETH/USDT:USDT 20200101
dl binance SOL/USDT:USDT 20200915
dl binance BTC/USDC:USDC 20240105
dl bybit   BTC/USDT:USDT 20210101
dl bybit   ETH/USDT:USDT 20210101
dl bybit   SOL/USDT:USDT 20211020
echo; echo "== Listo"; du -sh user_data/data/*
