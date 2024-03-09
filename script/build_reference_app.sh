#!/bin/bash

BASEDIR=$(dirname "$0")
readonly BUILD_DIR=$BASEDIR"/../test/build_reference_app"

if ! [ -d $BUILD_DIR ]; then
    mkdir $BUILD_DIR
fi

export ZEPHYR_BASE=$BASEDIR/../test/zephyr
source $ZEPHYR_BASE/zephyr-env.sh
cd $BUILD_DIR
cmake -GNinja -DBOARD=qemu_x86_64 ../reference_app
ninja
