#!/bin/bash

readonly BUILD_DIR="test/build_reference_app"
export ZEPHYR_BASE=$(pwd)/test/zephyr
source test/zephyr/zephyr-env.sh
cd $BUILD_DIR
# Run app and dump NVS region memory to terminal
( echo -n; sleep 2; echo "flash read 0x1000 0xB00") | ninja run > dump.txt
