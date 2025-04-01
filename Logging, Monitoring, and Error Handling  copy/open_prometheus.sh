#!/bin/bash

# Script to open Prometheus with browser flags to bypass security restrictions

# Load environment variables from .env file
if [ -f .env ]; then
    # Export variables one by one to avoid issues with spaces and special characters
    export BROWSER_ARGS_DISABLE_WEB_SECURITY=$(grep -v '^#' .env | grep BROWSER_ARGS_DISABLE_WEB_SECURITY | cut -d '=' -f2-)
    export BROWSER_ARGS_DISABLE_EXTENSIONS=$(grep -v '^#' .env | grep BROWSER_ARGS_DISABLE_EXTENSIONS | cut -d '=' -f2-)
    export BROWSER_ARGS_DISABLE_PLUGINS=$(grep -v '^#' .env | grep BROWSER_ARGS_DISABLE_PLUGINS | cut -d '=' -f2-)
    export BROWSER_ARGS_NO_SANDBOX=$(grep -v '^#' .env | grep BROWSER_ARGS_NO_SANDBOX | cut -d '=' -f2-)
    export BROWSER_ARGS_DISABLE_POPUP_BLOCKING=$(grep -v '^#' .env | grep BROWSER_ARGS_DISABLE_POPUP_BLOCKING | cut -d '=' -f2-)
    export BROWSER_ARGS_DISABLE_NOTIFICATIONS=$(grep -v '^#' .env | grep BROWSER_ARGS_DISABLE_NOTIFICATIONS | cut -d '=' -f2-)
else
    echo "Error: .env file not found"
    exit 1
fi

echo "Opening Prometheus with browser security bypassed..."

# Determine the operating system
OS=$(uname)

# Combine browser arguments
BROWSER_ARGS="$BROWSER_ARGS_DISABLE_WEB_SECURITY $BROWSER_ARGS_DISABLE_EXTENSIONS $BROWSER_ARGS_DISABLE_PLUGINS $BROWSER_ARGS_NO_SANDBOX $BROWSER_ARGS_DISABLE_POPUP_BLOCKING $BROWSER_ARGS_DISABLE_NOTIFICATIONS"

# Open the browser with Prometheus URL
if [[ "$OS" == "Darwin" ]]; then
    # macOS
    open -a "Google Chrome" --args $BROWSER_ARGS "http://localhost:9090"
elif [[ "$OS" == "Linux" ]]; then
    # Linux
    if command -v google-chrome &> /dev/null; then
        google-chrome $BROWSER_ARGS "http://localhost:9090"
    elif command -v chromium-browser &> /dev/null; then
        chromium-browser $BROWSER_ARGS "http://localhost:9090"
    else
        echo "Chrome or Chromium not found. Please install one of them."
        exit 1
    fi
else
    # Windows or other
    echo "Unsupported operating system. Please open the following URL manually:"
    echo "http://localhost:9090"
fi

echo "Browser launched. You should now be able to access Prometheus."
