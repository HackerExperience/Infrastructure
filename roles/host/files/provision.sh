#!/usr/local/bin/bash

set -x

set -eu

HOST_PATH="/usr/local/host"

JAIL_NAME=""
JAIL_IP=""
INTERFACE=""
DISK_QUOTA="50G"
MAX_RAM="8G"
CPU_PIN=""
PRIORITY="99"
SYSVIPC=""

while [[ $# -gt 1 ]]; do
    key="$1"

    case $key in
        -n|--name)
            JAIL_NAME="$2"
            shift
            ;;
        -i|--interface)
            INTERFACE="$2"
            shift
            ;;
        --private-ip)
            JAIL_IP="$2"
            shift
            ;;
        --no-pin-cpu)
            CPU_PIN=""
            shift
            ;;
        --pin-cpu)
            CPU_PIN="$2"
            shift
            ;;
        --no-max-ram)
            MAX_RAM=""
            shift
            ;;
        --max-ram)
            MAX_RAM="$2"
            shift
            ;;
        --no-disk-quota)
            DISK_QUOTA=""
            shift
            ;;
        --disk-quota)
            DISK_QUOTA="$2"
            shift
            ;;
        --priority)
            PRIORITY="$2"
            shift
            ;;
        --allow-sysvipc)
            SYSVIPC="1"
            shift
            ;;
        *)
            echo "Unknown argument $1"
            exit
            ;;
    esac
    shift # past argument or value
done

function require_arg {
    if [ -z "$1" ]; then
        echo "You did not specify $2"
        exit 1
    fi
}

require_arg "$JAIL_NAME" 'jail name (-n)'
require_arg "$JAIL_IP" 'jail ip (--private-ip)'
require_arg "$INTERFACE" 'network interface (-i)'

# check that the name is not in use
if (iocage list | awk -F ' ' '{print $5}' | grep -qFx "$JAIL_NAME"); then
    echo "Jail with name $JAIL_NAME already exists, exiting."
    exit 1
fi

# check that the jail ip is not in use
if (ifconfig | grep inet | awk -F ' ' '{print $2}' | grep -Fx "$JAIL_IP"); then
    echo "IP $JAIL_IP already in use, exiting."
    exit 1
fi

# create jail
iocage create tag="$JAIL_NAME" ip4_addr="$INTERFACE|$JAIL_IP/16" release=11.0-RELEASE pkglist="$HOST_PATH"/pkgs.txt

# set hostname
iocage set hostname="$JAIL_NAME" "$JAIL_NAME"
# allow ping
iocage set allow_raw_sockets=1 "$JAIL_NAME"
# make jail start on boot
iocage set boot=on "$JAIL_NAME"
# allow zfs dedup
iocage set dedup=on "$JAIL_NAME"
# set boot priority
iocage set priority="$PRIORITY" "$JAIL_NAME"
# set resolver
iocage set resolver='nameserver 8.8.8.8;nameserver 8.8.4.4' "$JAIL_NAME"

if [ -n "$SYSVIPC" ]; then
    iocage set allow_sysvipc=1 "$JAIL_NAME"
fi

# resource limits
iocage set rlimits=on "$JAIL_NAME"

if [ -n "$DISK_QUOTA" ]; then
    iocage set quota="$DISK_QUOTA" "$JAIL_NAME"
fi

if [ -n "$MAX_RAM" ]; then
    iocage set memoryuse="$MAX_RAM":deny "$JAIL_NAME"
fi

if [ -n "$CPU_PIN" ]; then
    iocage set cpuset="$CPU_PIN" "$JAIL_NAME"
fi

# enforce resource limits
iocage cap "$JAIL_NAME"

# start
iocage start "$JAIL_NAME"

# get jail id
JAIL_ID=$(iocage get host_hostuuid "$JAIL_NAME")

JAIL_PATH="/iocage/jails/$JAIL_ID/root"

# copy initial files
cp "$HOST_PATH"/sshd_config.default "$JAIL_PATH"/etc/ssh/sshd_config
cp "$HOST_PATH"/resolv.conf.default "$JAIL_PATH"/etc/resolv.conf

mkdir "$JAIL_PATH"/root/.ssh
cat "$HOST_PATH"/ssh_jail.pub >> "$JAIL_PATH"/root/.ssh/authorized_keys

# start sshd on jail
iocage exec "$JAIL_NAME" service sshd onestart

# verify jail's sshd is listening
exit $(nc -z "$JAIL_IP" 22 -w 5)
