#!/bin/sh
if ! command -v runsc >/dev/null 2>&1; then
    exit 10
fi
if ! runsc --version >/dev/null 2>&1; then
    exit 11
fi
