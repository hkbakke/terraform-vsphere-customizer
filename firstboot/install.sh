#!/bin/bash

script="/root/firstboot.py"
service="firstboot.service"
service_file="/etc/systemd/system/${service}"


cp firstboot.py "$script"
chown root. "$script"
chmod 750 "$script"
rm firstboot.py

cp firstboot.service "$service_file"
chown root. "$service_file"
chmod 755 "$service_file"
systemctl daemon-reload
systemctl enable $service
rm firstboot.service

rm install.sh
