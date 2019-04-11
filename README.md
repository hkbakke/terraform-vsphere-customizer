# terraform-vsphere-customizer
Customize vSphere VM templates when deployed from terraform. Created to compensate for lack of
Debian support in the template customizer that VMware provides.

# Requirements
* systemd
* open-vm-tools
* python 3.5 or newer

# Tested OS
* Debian Stretch

# Prepare template
This is done remotely via SSH. Note that on the next boot the firstboot-script will run and self-destruct, so you must run `prep-template` every time you create a VM before you shut it down and convert it to a template for terraform use.

    git clone https://github.com/hkbakke/terraform-vsphere-customizer
    cd terraform-vsphere-customizer/firstboot
    ./prep-template <user>@<host>

# Supported parameters
* `guestinfo.hostname" = "hostname.example.com"`
* `guestinfo.network.<ifname>.ipv4_address" = "10.0.0.10/24"`
* `guestinfo.network.<ifname>.ipv4_gateway" = "10.0.0.1"`
* `guestinfo.network.<ifname>.ipv6_address" = "fd77:ba12:fcs1:88::23/64"`

# Usage in terraform
Example from within your VM resource block, also including some counter fun

    extra_config {
      "guestinfo.hostname" = "web-${count.index + 1}.example.com"
      "guestinfo.network.ens192.ipv4_address" = "10.0.0.${count.index + 10}/24"
      "guestinfo.network.ens192.ipv4_gateway" = "10.0.0.1"
      "guestinfo.network.ens192.ipv6_address" = "fd77:ba12:fcs1:88::${count.index + 10}/64"
    }
