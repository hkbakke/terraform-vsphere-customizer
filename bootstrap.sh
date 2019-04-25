#!/bin/bash

url="https://github.com/hkbakke/terraform-vsphere-customizer/archive/master.tar.gz"
download_dir="/tmp"
source_dir="${download_dir}/terraform-vsphere-customizer-master"
script="/usr/local/sbin/firstboot.py"
service="firstboot.service"
service_file="/etc/systemd/system/$service"


fetch () {
    wget -O - "$url" | tar xz -C "$download_dir"
}

install () {
    cp "${source_dir}/firstboot/firstboot.py" "$script"
    chown root. "$script"
    chmod 750 "$script"

    cp "${source_dir}/firstboot/firstboot.service" "$service_file"
    chown root. "$service_file"
    chmod 755 "$service_file"
    systemctl daemon-reload
    systemctl enable $service
}

cleanup () {
    [[ -d $source_dir ]] && rm -r "$source_dir"
    rm bootstrap.sh
}


set -e

# Make it possible to override download url
if [[ -n $1 ]]; then
    url=$1
fi

fetch
install
cleanup
