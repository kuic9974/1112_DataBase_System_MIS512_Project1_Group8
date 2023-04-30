#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# 下載Oracle Instant Client
wget https://download.oracle.com/otn_software/linux/instantclient/2110000/instantclient-basic-linux.x64-21.10.0.0.0dbru.zip
# 下載解壓縮套件
# apt-get update
apt-get install unzip
# 解壓縮檔案
unzip instantclient-basic-linux.x64-21.10.0.0.0dbru.zip
# 設定環境變數
# export LD_LIBRARY_PATH=/workspace/instantclient_21_9:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/workspace/instantclient_21_10:$LD_LIBRARY_PATH