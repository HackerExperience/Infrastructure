#!/usr/local/bin/bash

set -x

if [ $# -ne 2 ] || [ "$1" != "-c" ] ; then
    echo interactive login not permitted
    exit 1
fi

case "$2" in
    "deploy "* )
        # regex: allow only azAZ09<space>
    # forbid ;&@#!@$(){}
        shift
        ;;
    * )
        echo that command is not allowed
        exit 1
        ;;
esac

/usr/local/bin/bash -c "/usr/local/bin/$@"
