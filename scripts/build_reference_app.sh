#!/bin/bash

readonly BUILD_DIR="test/build_reference_app"
if ! [ -d $BUILD_DIR ]; then
    mkdir $BUILD_DIR
fi

export ZEPHYR_BASE=$(pwd)/test/zephyr
source test/zephyr/zephyr-env.sh
cd $BUILD_DIR
cmake -GNinja -DBOARD=qemu_x86_64 ../reference_app
ninja
