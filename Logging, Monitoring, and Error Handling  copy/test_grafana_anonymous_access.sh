#!/bin/bash

# Script to test Grafana no-login configuration

echo "Testing Grafana No-Login Configuration"
echo "-------------------------------------"

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

# Restart Grafana container
echo "Restarting Grafana container to apply configuration changes..."
docker-compose restart grafana

# Wait for Grafana to start
echo "Waiting for Grafana to start (this may take a few seconds)..."
sleep 10

# Check if Grafana is running
if ! docker ps | grep -q "grafana"; then
    echo "Error: Grafana container is not running"
    echo "Try starting it manually with: docker-compose up -d grafana"
    exit 1
fi

# Get the operating system
OS=$(uname)

echo "Grafana should now be accessible without login at: http://localhost:3000"
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
echo "1. You should be able to see the Grafana home page without being prompted to log in"
echo "2. You should have full admin access to create and edit dashboards"
echo "3. There should be no login form or sign-out option visible"
echo ""
echo "If you're still seeing a login prompt, check the following:"
echo "- Confirm the environment variables were added correctly in docker-compose.yml"
echo "- Check Grafana logs with: docker-compose logs grafana"
echo "- Ensure you're using a recent version of Grafana (this configuration works with Grafana 8.x and newer)"
