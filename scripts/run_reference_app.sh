#!/bin/bash

readonly BUILD_DIR="test/build_reference_app"
export ZEPHYR_BASE=$(pwd)/test/zephyr
source test/zephyr/zephyr-env.sh
cd $BUILD_DIR
ninja run
