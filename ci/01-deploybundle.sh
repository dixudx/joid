#!/bin/bash
#placeholder for deployment script.
set -ex

case "$1" in
    'nonha' )
        cp odl/juju-deployer/ovs-odl.yaml ./bundles.yaml
        ;;
    'ha' )
        cp odl/juju-deployer/ovs-odl-ha.yaml ./bundles.yaml
        juju-deployer -d -r 13 -c bundles.yaml openstack-phase1
        ;;
    'tip' )
        cp odl/juju-deployer/ovs-odl-tip.yaml ./bundles.yaml
        ;;
    * )
        cp odl/juju-deployer/ovs-odl.yaml ./bundles.yaml
        ;;
esac

case "$3" in
    'orangepod2' )
        sed -i -- 's/10.4.1.1/192.168.2.2/g' ./bundles.yaml
        ;;
esac

echo "... Deployment Started ...."

#case openstack kilo with odl
juju-deployer -d -r 13 -c bundles.yaml trusty-"$2"

echo "... Deployment finished ...."
