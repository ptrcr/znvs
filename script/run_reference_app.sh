#!/bin/bash

BASEDIR=$(dirname "$0")
readonly BUILD_DIR=$BASEDIR"/../test/build_reference_app"

export ZEPHYR_BASE=$BASEDIR/../test/zephyr
source $ZEPHYR_BASE/zephyr-env.sh
cd $BUILD_DIR
# Run app and dump NVS region memory to terminal
( echo -n; sleep 2; echo "flash read 0x1000 0xC00") | ninja run > dump.txt
