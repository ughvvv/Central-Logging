#!/bin/bash

# Script to open Kibana with browser flags to bypass security restrictions

# Load environment variables from .env file
if [ -f .env ]; then
    # Export variables one by one to avoid issues with spaces and special characters
    export KIBANA_URL=$(grep -v '^#' .env | grep KIBANA_URL | cut -d '=' -f2-)
    export ELASTIC_USERNAME=$(grep -v '^#' .env | grep ELASTIC_USERNAME | cut -d '=' -f2-)
    export ELASTIC_PASSWORD=$(grep -v '^#' .env | grep ELASTIC_PASSWORD | cut -d '=' -f2-)
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

echo "Opening Kibana with automatic login..."

# Determine the operating system
OS=$(uname)

# Create a temporary HTML file for auto-login
TMP_HTML=$(mktemp -t kibana_login_XXXXXX.html)

# Create an HTML file with a form that will auto-submit
cat > $TMP_HTML << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Kibana Auto Login</title>
    <script>
        window.onload = function() {
            // Wait for page to load and then submit the form
            document.getElementById('loginForm').submit();
        }
    </script>
</head>
<body>
    <h1>Logging in to Kibana...</h1>
    <form id="loginForm" method="POST" action="${KIBANA_URL}/login">
        <input type="hidden" name="username" value="${ELASTIC_USERNAME}">
        <input type="hidden" name="password" value="${ELASTIC_PASSWORD}">
        <input type="submit" value="Login">
    </form>
</body>
</html>
EOF

echo "Created temporary login file at $TMP_HTML"

# Combine browser arguments
BROWSER_ARGS="$BROWSER_ARGS_DISABLE_WEB_SECURITY $BROWSER_ARGS_DISABLE_EXTENSIONS $BROWSER_ARGS_DISABLE_PLUGINS $BROWSER_ARGS_NO_SANDBOX $BROWSER_ARGS_DISABLE_POPUP_BLOCKING $BROWSER_ARGS_DISABLE_NOTIFICATIONS"

# Open the browser with the temporary HTML file
if [[ "$OS" == "Darwin" ]]; then
    # macOS
    open -a "Google Chrome" --args $BROWSER_ARGS "file://$TMP_HTML"
elif [[ "$OS" == "Linux" ]]; then
    # Linux
    if command -v google-chrome &> /dev/null; then
        google-chrome $BROWSER_ARGS "file://$TMP_HTML"
    elif command -v chromium-browser &> /dev/null; then
        chromium-browser $BROWSER_ARGS "file://$TMP_HTML"
    else
        echo "Chrome or Chromium not found. Please install one of them."
        exit 1
    fi
else
    # Windows or other
    echo "Unsupported operating system. Please open the following URL manually:"
    echo "$KIBANA_URL"
    echo "Username: $ELASTIC_USERNAME"
    echo "Password: $ELASTIC_PASSWORD"
fi

echo "Browser launched. You should be automatically logged in to Kibana."
echo "If the auto-login doesn't work, use these credentials:"
echo "Username: $ELASTIC_USERNAME"
echo "Password: $ELASTIC_PASSWORD"

# Wait a bit before removing the temporary file
sleep 10
rm $TMP_HTML
