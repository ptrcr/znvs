#!/bin/sh
cut -d' ' -f2-18 "$1" | xxd -r -p > "$2"
