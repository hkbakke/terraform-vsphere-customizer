#!/usr/bin/env python3

import re
import subprocess
import os


class NetworkInterface:
    def __init__(self, name):
        self.name = name
        self.ipv4_address = get_vmtools_key('guestinfo.network.%s.ipv4_address' % self.name)
        self.ipv4_gateway = get_vmtools_key('guestinfo.network.%s.ipv4_gateway' % self.name)
        self.ipv6_address = get_vmtools_key('guestinfo.network.%s.ipv6_address' % self.name)


class NetworkInterfacesFile:
    def __init__(self, filename='/etc/network/interfaces'):
        self.filename = filename
        self.content = []
        self._default = [
            '#',
            '# Configured by firstboot.py',
            '# More info: https://github.com/hkbakke/terraform-vsphere-customizer',
            '#',
            '',
            'source /etc/network/interfaces.d/*',
            '',
            'auto lo',
            'iface lo inet loopback',
            ]

    def add_interface(self, interface):
        self.content.append('\nallow-hotplug %s' % interface.name)

        if interface.ipv4_address:
            self.content.append('iface %s inet static' % interface.name)
            self.content.append('\taddress %s' % interface.ipv4_address)
            if interface.ipv4_gateway:
                self.content.append('\tgateway %s' % interface.ipv4_gateway)
        else:
            self.content.append('iface %s inet dhcp' % interface.name)

        if interface.ipv6_address:
            self.content.append('iface %s inet6 static' % interface.name)
            self.content.append('\taddress %s' % interface.ipv6_address)
        else:
            self.content.append('iface %s inet6 auto' % interface.name)

    def save(self):
        if not self.content:
            return
        with open(self.filename, 'w') as f:
            f.write('\n'.join(self._default + self.content) + '\n')


class HostsFile:
    def __init__(self, filename='/etc/hosts'):
        self.filename = filename
        self.content = []
        self._header = [
            '#',
            '# Configured by firstboot.py',
            '# More info: https://github.com/hkbakke/terraform-vsphere-customizer',
            '#',
            '',
        ]
        self._default_ipv4 = [
            '127.0.0.1\tlocalhost'
            ]
        self._default_ipv6 = [
            '',
            '# The following lines are desirable for IPv6 capable hosts',
            '::1\tlocalhost ip6-localhost ip6-loopback',
            'ff02::1\tip6-allnodes',
            'ff02::2\tip6-allrouters'
            ]

    def change_hostname(self, hostname):
        """
        The hostname is expected to be a FQDN
        """
        self.content = self._header
        self.content.extend(self._default_ipv4)
        self.content.append('127.0.1.1\t%s\t%s' % (hostname, hostname.split('.')[0]))
        self.content.extend(self._default_ipv6)

    def save(self):
        if not self.content:
            return
        with open(self.filename, 'w') as f:
            f.write('\n'.join(self.content) + '\n')


class ResolvConf:
    def __init__(self, filename='/etc/resolv.conf'):
        self.filename = filename
        self.content = []

    def dns_domain(self, domain):
        self.content.append('domain %s' % domain)

    def add_dns_server(self, dns_server):
        self.content.append('nameserver %s' % dns_server)

    def save(self):
        if not self.content:
            return
        with open(self.filename, 'w') as f:
            f.write('\n'.join(self.content) + '\n')


def set_hostname(name):
    subprocess.run(['hostnamectl', 'set-hostname', name])


def get_vmtools_key(infokey, default=None):
    print("Looking up vmtoolsd info key '%s'" % infokey)
    cmd = ['vmtoolsd', '--cmd', 'info-get %s' % infokey]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    if p.returncode == 0:
        return p.stdout.strip()
    return default


def get_network_interfaces():
    for ifname in os.listdir('/sys/class/net'):
        if ifname == 'lo':
            continue
        yield NetworkInterface(ifname)


def main():
    if get_vmtools_key('guestinfo.customize') == 'false':
        return

    hostname = get_vmtools_key('guestinfo.hostname')
    if hostname:
        set_hostname(hostname)
        hostsfile = HostsFile()
        hostsfile.change_hostname(hostname)
        hostsfile.save()

    debian_config = NetworkInterfacesFile()
    for interface in get_network_interfaces():
        debian_config.add_interface(interface)
        debian_config.save()

    resolv_conf = ResolvConf()
    dns_domain = get_vmtools_key('guestinfo.dns_domain')
    if dns_domain:
        resolv_conf.dns_domain(dns_domain)
    dns_servers = get_vmtools_key('guestinfo.dns_servers')
    if dns_servers:
        for dns_server in [i.strip() for i in dns_servers.split(',')]:
            resolv_conf.add_dns_server(dns_server)
    resolv_conf.save()


if __name__ == '__main__':
    main()
