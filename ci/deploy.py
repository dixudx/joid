#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Deploy JOID
"""

import yaml
import socket
import fcntl
import struct
import getpass


def get_ip_address(ifname):
    """Get local IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

with open('labconfig.yaml', 'r') as labf:
    try:
        labcfg = yaml.load(labf)
    except yaml.YAMLError as exc:
        print(exc)


opnfvcfg = {}
opnfvlabcfg = {}


def get_from_dict(dataDict, mapList):
    return reduce(lambda d, k: d[k], mapList, dataDict)

# lets define the bootstrap section
opnfvcfg['demo-maas'] = {'juju-bootstrap': {'memory': 4096,
                                            'name': "bootstrap",
                                            'pool': "default",
                                            'vcpus': 4,
                                            'disk_size': "60G",
                                            'arch': "amd64",
                                            'interfaces': []},
                         'maas': {'memory': 4096,
                                  'pool': "default",
                                  'vcpus': 4,
                                  'disk_size': "160G",
                                  'arch': "amd64",
                                  'interfaces': [],
                                  'name': "",
                                  'network_config': [],
                                  'node_group_ifaces': [],
                                  'nodes': [],
                                  'password': 'ubuntu',
                                  'user': 'ubuntu',
                                  'release': 'trusty',
                                  'apt_sources': [],
                                  'ip_address': '',
                                  'boot_source': {
                                        'keyring_filename': "/usr/share/keyrings/ubuntu-cloudimage-keyring.gpg",
                                        'url': "http://maas.ubuntu.com/images/ephemeral-v2/releases/",
                                        'sections': {
                                            '1': {
                                                'arches': 'amd64',
                                                'labels': 'release',
                                                'os': 'ubuntu',
                                                'release': 'xenial',
                                                'subarches': '*'
                                             }
                                         }
                                     },
                                  'settings': {'maas_name': '',
                                               'upstream_dns': '',
                                               'main_archive': "http://archive.ubuntu.com/ubuntu"
                                               },
                                  'virsh': {'rsa_priv_key': '/home/ubuntu/.ssh/id_rsa',
                                            'rsa_pub_key': '/home/ubuntu/.ssh/id_rsa.pub',
                                            'uri': ''
                                            }
                                  }
                         }

opnfvlabcfg['opnfv'] = {'ext-port': '',
                        'floating-ip-range': '',
                        'dataNetwork': '',
                        'ceph-disk': '/srv/',
                        'storageNetwork': '',
                        'interface-enable': '',
                        'publicNetwork': '',
                        'os-domain-name': '',
                        'vip': {'rabbitmq': '',
                                'dashboard': '',
                                'glance': '',
                                'keystone': '',
                                'ceilometer': '',
                                'mysql': '',
                                'nova': '',
                                'neutron': '',
                                'heat': '',
                                'cinder': ''}
                        }


opnfvcfg['demo-maas']['maas']['apt_sources'].append("ppa:maas/stable")
opnfvcfg['demo-maas']['maas']['apt_sources'].append("ppa:juju/stable")

# lets modify the maas general settings:

updns = get_from_dict(labcfg, ["lab", "racks", 0, "dns"])
opnfvcfg["demo-maas"]["maas"]["settings"]["upstream_dns"] = updns

location = get_from_dict(labcfg, ["lab", "location"])
rack = get_from_dict(labcfg, ["lab", "racks", 0, "rack"])
value = location+rack

opnfvcfg["demo-maas"]["maas"]["settings"]["maas_name"] = value
opnfvcfg["demo-maas"]["maas"]["name"] = "opnfv-"+value

ethbrAdm = ""
ethbrAdmin = ""

c = 0
y = 0
# z = 0

while c < len(labcfg["opnfv"]["spaces"]):
    brtype = get_from_dict(labcfg, ["opnfv", "spaces", c, "type"])
    brname = get_from_dict(labcfg, ["opnfv", "spaces", c, "bridge"])
    brcidr = get_from_dict(labcfg, ["opnfv", "spaces", c, "cidr"])
#
    if brtype == "admin":
        ethbrAdmin = get_from_dict(labcfg, ["opnfv", "spaces", c, "bridge"])
        brgway = get_from_dict(labcfg, ["opnfv", "spaces", c, "gateway"])
        tmpcidr = brcidr[:-4]
        opnfvlabcfg["opnfv"]["admNetwork"] = tmpcidr+"2"
        opnfvlabcfg["opnfv"]["admNetgway"] = brgway

        nodegroup = {"device": "eth"+str(y),
                     "ip": tmpcidr+"5",
                     "subnet_mask": "255.255.255.0",
                     "broadcast_ip": tmpcidr+"255",
                     "router_ip": brgway,
                     "static_range": {"high": tmpcidr+"80",
                                      "low": tmpcidr+"50"},
                     "dynamic_range": {"high": tmpcidr+"250",
                                       "low": tmpcidr+"81"}}

        ethbrAdm = ('auto lo\n'
                    '    iface lo inet loopback\n\n'
                    'auto eth'+str(y)+'\n'
                    '    iface eth'+str(y)+' inet static\n'
                    '    address '+tmpcidr+'5\n'
                    '    netmask 255.255.255.0\n'
                    '    gateway '+brgway+'\n'
                    '    dns-nameservers '+updns+' '+tmpcidr+'5 127.0.0.1\n')

        opnfvcfg['demo-maas']['maas']['ip_address'] = tmpcidr+"5"
        opnfvcfg['demo-maas']['maas']['interfaces'].append(
            "bridge="+brname+",model=virtio")
        opnfvcfg['demo-maas']['juju-bootstrap']['interfaces'].append(
            "bridge="+brname+",model=virtio")
        opnfvcfg["demo-maas"]["maas"]["node_group_ifaces"].append(nodegroup)
        y = y+1
    elif brtype:
        opnfvcfg["demo-maas"]["maas"]["interfaces"].append(
            "bridge="+brname+",model=virtio")
        brgway = get_from_dict(labcfg, ["opnfv", "spaces", c, "gateway"])
        if brtype != "external":
            tmpcidr = brcidr[:-4]
            if brgway:
                nodegroup = {"device": "eth"+str(y),
                             "ip": tmpcidr+"5",
                             "subnet_mask": "255.255.255.0",
                             "broadcast_ip": tmpcidr+"255",
                             "management": 1,
                             "router_ip": brgway,
                             "static_range": {"high": tmpcidr+"80",
                                              "low": tmpcidr+"50"},
                             "dynamic_range": {"high": tmpcidr+"250",
                                               "low": tmpcidr+"81"}}
            else:
                nodegroup = {"device": "eth"+str(y),
                             "ip": tmpcidr+"5",
                             "subnet_mask": "255.255.255.0",
                             "broadcast_ip": tmpcidr+"255",
                             "management": 1,
                             "static_range": {"high": tmpcidr+"80",
                                              "low": tmpcidr+"50"},
                             "dynamic_range": {"high": tmpcidr+"250",
                                               "low": tmpcidr+"81"}}
            opnfvcfg["demo-maas"]["maas"]["node_group_ifaces"].append(
                nodegroup)
            ethbrAdm = (ethbrAdm+'\n'
                        'auto eth'+str(y)+'\n'
                        '    iface eth'+str(y)+' inet static\n'
                        '    address '+tmpcidr+'5\n'
                        '    netmask 255.255.255.0\n')
            y = y+1
        if brtype == "public":
            opnfvcfg["demo-maas"]["juju-bootstrap"]["interfaces"].append(
                "bridge="+brname+",model=virtio")
            opnfvlabcfg["opnfv"]["publicNetwork"] = brcidr
        if brtype == "external":
            ipaddress = get_from_dict(labcfg, ["opnfv", "spaces",
                                               c, "ipaddress"])
            ethbrAdm = (ethbrAdm+'\n'
                        'auto eth'+str(y)+'\n'
                        '    iface eth'+str(y)+' inet static\n'
                        '    address '+ipaddress+'\n'
                        '    netmask 255.255.255.0\n')
            opnfvcfg["demo-maas"]["juju-bootstrap"]["interfaces"].append(
                "bridge="+brname+",model=virtio")
        if brtype == "data":
            opnfvlabcfg["opnfv"]["dataNetwork"] = brcidr
        if brtype == "storage":
            opnfvlabcfg["opnfv"]["storageNetwork"] = brcidr

    c = c+1

# lets modify the maas general settings:
value = get_ip_address(ethbrAdmin)
value = "qemu+ssh://"+getpass.getuser()+"@"+value+"/system"
opnfvcfg['demo-maas']['maas']['virsh']['uri'] = value
opnfvcfg['demo-maas']['maas']['network_config'] = ethbrAdm

if len(labcfg["lab"]["racks"][0]["nodes"]) < 1:
    print("looks like virtual deployment where nodes were not defined")
    opnfvcfg["demo-maas"]["maas"]["nodes"].remove()
    exit()

# lets insert the node details here:
c = 0
ifnamelist = []
#
while c < len(labcfg["lab"]["racks"][0]["nodes"]):
    valuemac = []
    y = 0
    # setup value of name and tags accordigly
    noderoleslist = labcfg["lab"]["racks"][0]["nodes"][c]["roles"]
    noderoles = " ".join(noderoleslist)

    valuetype = get_from_dict(labcfg, ["lab", "racks", 0, "nodes",
                                       c, "power", "type"])
    namevalue = labcfg["lab"]["racks"][0]["nodes"][c]["name"]
    valuearc = get_from_dict(labcfg, ["lab", "racks", 0,
                                      "nodes", c, "architecture"])
    # setup value of architecture
    if valuearc == "x86_64":
        valuearc = "amd64/generic"

    if valuetype == "wakeonlan":
        macvalue = get_from_dict(labcfg, ["lab", "racks", 0, "nodes",
                                          c, "power", "mac_address"])
        power = {"type": "ether_wake", "mac_address": macvalue}
    if valuetype == "ipmi":
        valueaddr = get_from_dict(labcfg, ["lab", "racks", 0, "nodes", c,
                                           "power", "address"])
        valueuser = get_from_dict(labcfg, ["lab", "racks", 0, "nodes", c,
                                           "power", "user"])
        valuepass = get_from_dict(labcfg, ["lab", "racks", 0, "nodes", c,
                                           "power", "pass"])
        valuedriver = "LAN_2_0"
        power = {"type": valuetype, "address": valueaddr, "user": valueuser,
                 "pass": valuepass, "driver": valuedriver}

    opnfvcfg["demo-maas"]["maas"]["nodes"].append(
            {"name": namevalue,
             "architecture": valuearc,
             "interfaces": [],
             "mac_addresses": [],
             "power": power,
             'tags': noderoles})

    y = 0
    while y < len(labcfg["lab"]["racks"][0]["nodes"][c]["nics"]):
        valuespaces = labcfg["lab"]["racks"][0]["nodes"][c][
                        "nics"][y]["spaces"]
        valueifname = labcfg["lab"]["racks"][0]["nodes"][c][
                        "nics"][y]["ifname"]
        if "admin" not in valuespaces:
            ifnamelist += [valueifname]
        valueifmac = labcfg["lab"]["racks"][0]["nodes"][c]["nics"][y]["mac"][0]
        valuemac += labcfg["lab"]["racks"][0]["nodes"][c]["nics"][y]["mac"]
        opnfvcfg["demo-maas"]["maas"]["nodes"][c]["interfaces"].append(
                {"name": valueifname,
                 "mac_address": valueifmac,
                 "mode": "auto"})
        y = y+1

    if valueifmac:
        opnfvcfg["demo-maas"]["maas"]["nodes"][c]['mac_addresses'] = valuemac

    c = c+1

opnfvlabcfg["opnfv"]["floating-ip-range"] =\
    labcfg["lab"]["racks"][0]["floating-ip-range"]
opnfvlabcfg["opnfv"]["ext-port"] =\
    labcfg["lab"]["racks"][0]["ext-port"]
opnfvlabcfg["opnfv"]["ceph-disk"] =\
    labcfg["opnfv"]["storage"][0]["disk"]
opnfvlabcfg["opnfv"]["interface-enable"] =\
    ",".join(list(set(ifnamelist)))

# setup vip addresss for HA
opnfvlabcfg["opnfv"]["vip"]["rabbitmq"] =\
    opnfvlabcfg["opnfv"]["admNetwork"]+"0"
opnfvlabcfg["opnfv"]["vip"]["dashboard"] =\
    opnfvlabcfg["opnfv"]["admNetwork"]+"1"
opnfvlabcfg["opnfv"]["vip"]["glance"] = opnfvlabcfg["opnfv"]["admNetwork"]+"2"
opnfvlabcfg["opnfv"]["vip"]["keystone"] =\
    opnfvlabcfg["opnfv"]["admNetwork"]+"3"
opnfvlabcfg["opnfv"]["vip"]["ceilometer"] =\
    opnfvlabcfg["opnfv"]["admNetwork"]+"4"
opnfvlabcfg["opnfv"]["vip"]["mysql"] = opnfvlabcfg["opnfv"]["admNetwork"]+"5"
opnfvlabcfg["opnfv"]["vip"]["nova"] = opnfvlabcfg["opnfv"]["admNetwork"]+"6"
opnfvlabcfg["opnfv"]["vip"]["neutron"] = opnfvlabcfg["opnfv"]["admNetwork"]+"7"
opnfvlabcfg["opnfv"]["vip"]["heat"] = opnfvlabcfg["opnfv"]["admNetwork"]+"8"
opnfvlabcfg["opnfv"]["vip"]["cinder"] = opnfvlabcfg["opnfv"]["admNetwork"]+"9"

osdomname = labcfg["lab"]["racks"][0]["osdomainname"]

if osdomname:
    opnfvlabcfg["opnfv"]["os-domain-name"] =\
        labcfg["lab"]["racks"][0]["osdomainname"]
    opnfvlabcfg["opnfv"]["domain"] = labcfg["lab"]["racks"][0]["osdomainname"]

opnfvlabcfg["opnfv"]["ext_port"] = labcfg["lab"]["racks"][0]["ext-port"]
opnfvlabcfg["opnfv"]["units"] = len(labcfg["lab"]["racks"][0]["nodes"])
opnfvlabcfg["opnfv"]["admin_password"] = "openstack"
opnfvlabcfg["opnfv"]["storage"] = labcfg["opnfv"]["storage"]
opnfvlabcfg["opnfv"]["spaces"] = labcfg["opnfv"]["spaces"]

with open('deployment.yaml', 'wa') as opnfvf:
    yaml.dump(opnfvcfg, opnfvf, default_flow_style=False)

with open('deployconfig.yaml', 'wa') as opnfvf:
    yaml.dump(opnfvlabcfg, opnfvf, default_flow_style=False)
