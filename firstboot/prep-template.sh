#!/bin/bash

target="$1"

if [[ -z $target ]]
then
    echo "You must specify the target host"
    exit 1
fi

set -e

scp firstboot.service firstboot.py install.sh ${target}:
ssh -t ${target} sudo bash install.sh
