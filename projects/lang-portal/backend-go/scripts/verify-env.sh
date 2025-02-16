#!/bin/bash

echo "Checking development environment..."

# Check GCC
echo -n "GCC: "
if command -v gcc >/dev/null 2>&1; then
    gcc --version | head -n1
else
    echo "Not found!"
    exit 1
fi

# Check Go
echo -n "Go: "
if command -v go >/dev/null 2>&1; then
    go version
else
    echo "Not found!"
    exit 1
fi

# Check CGO
echo -n "CGO: "
if [ "$CGO_ENABLED" = "1" ]; then
    echo "Enabled"
else
    echo "Disabled!"
    exit 1
fi

echo "Environment check complete!" 