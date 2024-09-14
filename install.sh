#!/bin/sh

set -eu

if [ "$(id -u)" -ne 0 ]]
then
    exec sudo "$0" "$@"
fi

DEBIAN_FRONTEND=noninteractive
export DEBIAN_FRONTEND
apt -y install liquidctl
install -oroot -groot -m0755 main.py /usr/local/bin/led-hue-for-cpu-utilization.py
install -oroot -groot -m0644 led-hue-for-cpu-utilization.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable led-hue-for-cpu-utilization
systemctl restart led-hue-for-cpu-utilization
systemctl status led-hue-for-cpu-utilization
