#!/usr/bin/env python3

import re
import subprocess
import os


def update_hosts_file(name, hosts_file='/etc/hosts'):
    with open(hosts_file, 'r') as f:
        content = f.read()

    regex = r'127\.0\.1\.1.*'
    repl = '127.0.1.1\t%s\t%s' % (name, name.split('.')[0])
    content = re.sub(regex, repl, content, count=1)

    with open(hosts_file, 'w') as f:
        f.write(content)


def set_hostname(name):
    subprocess.run(['hostnamectl', 'set-hostname', name])


def get_vmtools_info(infokey):
    cmd = ['vmtoolsd', '--cmd', 'info-get %s' % infokey]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    if p.returncode == 0:
        return p.stdout.strip()
    return None


def get_network_interfaces():
    return os.listdir('/sys/class/net')


def update_interfaces_file(ifname, config, interfaces_file='/etc/network/interfaces'):
    with open(interfaces_file, 'r') as f:
        content = f.read()

    if config['ipv4']['address']:
        params = ['address %s' % config['ipv4']['address']]
        if config['ipv4']['gateway']:
            params.append('gateway %s' % config['ipv4']['gateway'])
        regex = r'iface\s%s\sinet\s.*' % ifname
        repl = 'iface %s inet static\n\t%s' % (ifname, '\n\t'.join(params))
        content = re.sub(regex, repl, content, count=1)

    if config['ipv6']['address']:
        params = ['address %s' % config['ipv6']['address']]
        regex = r'iface\s%s\sinet6\s.*' % ifname
        repl = 'iface %s inet6 static\n\t%s' % (ifname, '\n\t'.join(params))
        content = re.sub(regex, repl, content, count=1)

    with open(interfaces_file, 'w') as f:
        f.write(content)


if __name__ == '__main__':
    name = get_vmtools_info('guestinfo.hostname')
    if name:
        set_hostname(name)
        update_hosts_file(name)

    for i in get_network_interfaces():
        if i == 'lo':
            continue

        config = {
                'ipv4': {
                    'address': get_vmtools_info('guestinfo.network.%s.ipv4_address' % i),
                    'gateway': get_vmtools_info('guestinfo.network.%s.ipv4_gateway' % i)
                },
                'ipv6': {
                    'address': get_vmtools_info('guestinfo.network.%s.ipv6_address' % i)
                }
            }
        update_interfaces_file(i, config)
