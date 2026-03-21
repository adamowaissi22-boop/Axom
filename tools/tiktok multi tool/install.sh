#!/bin/bash
pkg update && pkg upgrade
pkg install -y ffmpeg python
pip install -r requirements.txt
chmod +x twr.py
mkdir -p $HOME/.twr
echo "alias twr='python $PWD/twr.py'" >> $HOME/.bashrc
source $HOME/.bashrc
echo "Installation complete. Usage: twr -u <tiktok-url>"
