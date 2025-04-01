#!/bin/bash

# Script to test Grafana OAuth configuration

echo "Testing Grafana OAuth Configuration"
echo "----------------------------------"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed or not in PATH"
    exit 1
fi

# Check if docker is running
if ! docker info &> /dev/null; then
    echo "Error: Docker is not running or not accessible"
    exit 1
fi

# Check if the OAuth configuration file exists
if [ ! -f "docker-compose.oauth.yml" ]; then
    echo "Error: docker-compose.oauth.yml file not found"
    exit 1
fi

# Check if Google OAuth credentials are set
if grep -q "YOUR_GOOGLE_CLIENT_ID" docker-compose.oauth.yml; then
    echo "Error: Google OAuth credentials not set in docker-compose.oauth.yml"
    echo "Please edit docker-compose.oauth.yml and replace YOUR_GOOGLE_CLIENT_ID and YOUR_GOOGLE_CLIENT_SECRET with your actual credentials"
    exit 1
fi

# Restart Grafana container with OAuth configuration
echo "Restarting Grafana container with OAuth configuration..."
docker-compose -f docker-compose.oauth.yml restart grafana

# Wait for Grafana to start
echo "Waiting for Grafana to start (this may take a few seconds)..."
sleep 10

# Check if Grafana is running
if ! docker ps | grep -q "grafana"; then
    echo "Error: Grafana container is not running"
    echo "Try starting it manually with: docker-compose -f docker-compose.oauth.yml up -d grafana"
    exit 1
fi

# Get the operating system
OS=$(uname)

echo "Grafana should now be accessible with OAuth auto-login at: http://localhost:3000"
echo "Opening Grafana in your default browser..."

# Open browser based on OS
if [[ "$OS" == "Darwin" ]]; then
    # macOS
    open "http://localhost:3000"
elif [[ "$OS" == "Linux" ]]; then
    # Linux
    xdg-open "http://localhost:3000" &> /dev/null || sensible-browser "http://localhost:3000" &> /dev/null || \
    echo "Could not open browser automatically. Please open http://localhost:3000 manually."
else
    # Windows or other
    echo "Please open http://localhost:3000 in your browser manually."
fi

echo ""
echo "Verification:"
echo "1. You should be automatically redirected to Google's login page"
echo "2. After logging in with your Google account, you should be redirected back to Grafana"
echo "3. You should have full admin access to create and edit dashboards"
echo "4. There should be no login form or sign-out option visible"
echo ""
echo "If you're not redirected to Google's login page, check the following:"
echo "- Confirm the OAuth credentials are set correctly in docker-compose.oauth.yml"
echo "- Check Grafana logs with: docker-compose -f docker-compose.oauth.yml logs grafana"
echo "- Verify that your Google OAuth client is configured correctly in Google Cloud Console"
echo "- Ensure that the redirect URI (http://localhost:3000/login/google) is configured in Google Cloud Console"
