# terraform-vsphere-customizer
Customize vSphere VM templates when deployed from terraform. Created to compensate for lack of
Debian support in the template customizer that VMware provides.

# Requirements
* systemd
* open-vm-tools
* python 3.5 or newer (automatically pulled in by open-vm-tools on Debian)

# Tested OS
* Debian Stretch

# Prepare template
Before shutting down your template VM for terraform do this

    wget -O bootstrap.sh https://raw.githubusercontent.com/hkbakke/terraform-vsphere-customizer/master/bootstrap.sh
    sudo sh bootstrap.sh
    
`bootstrap.sh` pulls down `https://github.com/hkbakke/terraform-vsphere-customizer/archive/master.tar.gz`. However, if you are offline you can manually download the latest master.tar.gz and provide the internal location as an argument:

    sudo sh bootstrap.sh <url_to_master.tar.gz>

# Supported settings
## Set hostname
Set the hostname. A FQDN is expected.

    "guestinfo.hostname" = "hostname.example.com"

## Set IPv4 and/or IPv6 address
If no `ipv4_address` is configured for an interface, DHCP is used. If no `ipv6_address` is set auto-configuration mode is used.

    "guestinfo.network.<ifname>.ipv4_address" = "10.0.0.10/24"
    "guestinfo.network.<ifname>.ipv4_gateway" = "10.0.0.1"
    "guestinfo.network.<ifname>.ipv6_address" = "fd77:ba12:fcs1:88::23/64"

## Configure DNS
Note that the dns_domain is only used for resolv.conf. It is not used for hostname purposes.

    "guestinfo.dns_domain" = "example.com"
    "guestinfo.dns_servers" = "1.1.1.1, 8.8.8.8, 8.8.4.4"

## Disable customizations
When the customizer is included in the boot image you might see that it touches the network configuration file using default settings, even with no settings configured. To disable customizations entirely:

    "guestinfo.customize" = "false"

# Usage in terraform
Example from within a terraform VM resource block, also including some counter fun. Just leave out any parameters that you do not need.

    extra_config {
      "guestinfo.hostname" = "web-${count.index + 1}.example.com"
      "guestinfo.network.ens192.ipv4_address" = "10.0.0.${count.index + 10}/24"
      "guestinfo.network.ens192.ipv4_gateway" = "10.0.0.1"
      "guestinfo.network.ens192.ipv6_address" = "fd77:ba12:fcs1:88::${count.index + 10}/64"
    }
