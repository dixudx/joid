Bare Metal Installations:
=========================

Requirements as per Pharos:
===========================

Networking:
===========

**Minimum 2 networks**

| ``1. First for Admin/Management network with gateway to access external network``
| ``2. Second for floating ip network to consume by tenants for floating ips``

**NOTE: JOID support multiple isolated networks for API, data as well as storage.
Based on your network options for Openstack.**

**Minimum 6 physical servers**

1. Jump host server:

| ``   Minimum H/W Spec needed``
| ``  CPU cores: 16``
| ``  Memory: 32 GB``
| ``  Hard Disk: 1(250 GB)``
| ``  NIC: if0(Admin, Management), if1 (external network)``

2. Node servers (minimum 5):

| ``  Minimum H/W Spec``
| ``  CPU cores: 16``
| ``  Memory: 32 GB``
| ``  Hard Disk: 2(1 TB preferred SSD) this includes the space for ceph as well``
| ``  NIC: if0 (Admin, Management), if1 (external network)``


**NOTE: Above configuration is minimum and for better performance and usage of
the Openstack please consider higher spec for each nodes.**

Make sure all servers are connected to top of rack switch and configured accordingly. No DHCP server should be up and configured. Only gateway at eth0 and eth1 network should be configure to access the network outside your lab.

------------------------
Jump node configuration:
------------------------

1. Install Ubuntu 16.04.1 LTS server version of OS on the first server.
2. Install the git and bridge-utils packages on the server and configure minimum two bridges on jump host:

brAdm and brExt cat /etc/network/interfaces

| ``   # The loopback network interface``
| ``   auto lo``
| ``   iface lo inet loopback``
| ``   iface if0 inet manual``
| ``   auto brAdm ``
| ``   iface brAdm inet static``
| ``       address 10.5.1.1``
| ``       netmask 255.255.255.0``
| ``       bridge_ports if0``
| ``   iface if1 inet manual``
| ``   auto brExt``
| ``   iface brExt inet static``
| ``       address 10.5.15.1``
| ``       netmask 255.255.255.0``
| ``       bridge_ports if1``

**NOTE: If you choose to use the separate network for management, pulic , data and
storage then you need to create bridge for each interface. In case of VLAN tags
use the appropriate network on jump-host depend upon VLAN ID on the interface.**


Configure JOID for your lab
===========================

**Get the joid code from gerritt**

*git clone https://gerrit.opnfv.org/gerrit/joid.git*

**Enable MAAS (labconfig.yaml is must and base for MAAS installation and scenario deployment)**

If you have already enabled maas for your environment and installed it then there is no need to enabled it again or install it. If you have patches from previous MAAS enablement then you can apply it here.

NOTE: If MAAS is pre installed without 03-maasdeploy.sh not supported. We strongly suggest to use 03-maaseploy.sh to deploy the MAAS and JuJu environment.

If enabling first time then follow it further.
- Create a directory in joid/labconfig/<company name>/<pod number>/ for example

*mkdir joid/labconfig/intel/pod7/*

- copy labconfig.yaml from pod6 to pod7
*cp joid/labconfig/intel/pod5/\* joid/labconfig/intel/pod7/*

labconfig.yaml file
===================

-------------
Prerequisite:
-------------

1. Make sure Jump host node has been configured with bridges on each interface,
so that appropriate MAAS and JUJU bootstrap VM can be created. For example if
you have three network admin, data and floating ip then I would suggest to give names
like brAdm, brData and brExt etc.
2. You have information about the node MAC address and power management details (IPMI IP, username, password) of the nodes used for deployment.

---------------------
modify labconfig.yaml
---------------------

This file has been used to configure your maas and bootstrap node in a
VM. Comments in the file are self explanatory and we expect fill up the
information according to match lab infrastructure information. Sample
labconfig.yaml can be found at
https://gerrit.opnfv.org/gerrit/gitweb?p=joid.git;a=blob;f=labconfig/intel/pod6/labconfig.yaml

*lab:
  location: intel
  racks:
  - rack: pod6
    nodes:
    - name: rack-6-m1
      architecture: x86_64
      roles: [network,control]
      nics:
      - ifname: eth1
        spaces: [public]
        mac: ["xx:xx:xx:xx:xx:xx"]
      power:
        type: ipmi
        address: xx.xx.xx.xx
        user: xxxx
        pass: xxxx
    - name: rack-6-m1
      architecture: x86_64
      roles: [network,control]
      nics:
      - ifname: eth1
        spaces: [public]
        mac: ["xx:xx:xx:xx:xx:xx"]
      power:
        type: ipmi
        address: xx.xx.xx.xx
        user: xxxx
        pass: xxxx
    - name: rack-6-m1
      architecture: x86_64
      roles: [network,control]
      nics:
      - ifname: eth1
        spaces: [public]
        mac: ["xx:xx:xx:xx:xx:xx"]
      power:
        type: ipmi
        address: xx.xx.xx.xx
        user: xxxx
        pass: xxxx
    - name: rack-6-m1
      architecture: x86_64
      roles: [network,control]
      nics:
      - ifname: eth1
        spaces: [public]
        mac: ["xx:xx:xx:xx:xx:xx"]
      power:
        type: ipmi
        address: xx.xx.xx.xx
        user: xxxx
        pass: xxxx
    - name: rack-6-m1
      architecture: x86_64
      roles: [network,control]
      nics:
      - ifname: eth1
        spaces: [public]
        mac: ["xx:xx:xx:xx:xx:xx"]
      power:
        type: ipmi
        address: xx.xx.xx.xx
        user: xxxx
        pass: xxxx
    floating-ip-range: 10.5.15.6,10.5.15.250,10.5.15.254,10.5.15.0/24
    ext-port: "eth1"
    dns: 8.8.8.8
opnfv:
    release: d
    distro: xenial
    type: nonha
    openstack: newton
    sdncontroller:
    - type: nosdn
    storage:
    - type: ceph
      disk: /dev/sdb
    feature: odl_l2
    spaces:
    - type: floating
      bridge: brEx
      cidr: 10.5.15.0/24
      gateway: 10.5.15.254
      vlan:
    - type: admin
      bridge: brAdm
      cidr: 10.5.1.0/24
      gateway:
      vlan:*

Deployment of OPNFV using JOID:
===============================

Once you have done the change in above section then run the following commands to do the automatic deployments.

------------
MAAS Install
------------

After integrating the changes as mentioned above run the MAAS install.
then run the below commands to start the MAAS deployment.

``   ./03-maasdeploy.sh custom <absolute path of config>/labconfig.yaml ``
or
``   ./03-maasdeploy.sh custom http://<web site location>/labconfig.yaml ``

For deployment of Danube release on KVM please use the following command.

``   ./03-maasdeploy.sh default ``

-------------
OPNFV Install
-------------

| ``   ./deploy.sh -o newton -s nosdn -t nonha -l custom -f none -d xenial -m openstack``
| ``   ``

./deploy.sh -o newton -s nosdn -t nonha -l custom -f none -d xenial -m openstack

NOTE: Possible options are as follows:

choose which sdn controller to use.
  [-s <nosdn|odl|opencontrail|onos>]
  nosdn: openvswitch only and no other SDN.
  odl: OpenDayLight Boron version.
  opencontrail: OpenContrail SDN.
  onos: ONOS framework as SDN.

Mode of Openstack deployed.
  [-t <nonha|ha|tip>]
  nonha: NO HA mode of Openstack
  ha: HA mode of openstack.

Wihch version of Openstack deployed.
  [-o <Newton|Mitaka>]
  Newton: Newton version of openstack.
  Mitaka: Mitaka version of openstack.

Where to deploy
  [-l <custom | default>] etc...
  custom: For bare metal deployment where labconfig.yaml provided externally and not part of JOID.
  default: For virtual deployment where installation will be done on KVM created using 03-maasdeploy.sh

what feature to deploy. Comma seperated list
  [-f <lxd|dvr|sfc|dpdk|ipv6|none>]
  none: no special feature will be enabled.
  ipv6: ipv6 will be enabled for tenant in openstack.
  lxd:  With this feature hypervisor will be LXD rather than KVM.
  dvr:  Will enable distributed virtual routing.
  dpdk: Will enable DPDK feature.
  sfc:  Will enable sfc feature only supported with onos deployment.

which Ubuntu distro to use.
  [ -d <trusty|xenial> ]

Which model to deploy
JOID introduces the various model to deploy apart from openstack for docker based container workloads.
[-m <openstack|kubernetes>]
  openstack: Openstack which will be used for KVM/LXD container based workloads.
  kubernetes: Kubernes model will be used for docker based workloads.

OPNFV Scenarios in JOID
Following OPNFV scenarios can be deployed using JOID. Seperate yaml bundle will be created to deploy the individual scenario.

Scenario	         Owner	        Known Issues
os-nosdn-nofeature-ha	 Joid
os-nosdn-nofeature-noha	 Joid
os-odl_l2-nofeature-ha	 Joid           Floating ips are not working on this deployment.
os-nosdn-lxd-ha          Joid           Yardstick team is working to support.
os-nosdn-lxd-noha        Joid           Yardstick team is working to support.
os-onos-nofeature-ha	 ONOSFW
os-onos-sfc-ha	         ONOSFW
k8-nosdn-nofeature-nonha Joid	        No support from Functest and Yardstick
k8-nosdn-lb-nonha	 Joid	        No support from Functest and Yardstick

------------
Troubleshoot
------------

By default debug is enabled in script and error messages will be printed on ssh terminal where you are running the scripts.

To Access of any control or compute nodes.
juju ssh <service name>/<instance id>
for example to login into openstack-dashboard container.

juju ssh openstack-dashboard/0
juju ssh nova-compute/0
juju ssh neutron-gateway/0

All charm jog files are availble under /var/log/juju

By default juju will add the current user keys for authentication into the deployed server and only ssh access will be available.

