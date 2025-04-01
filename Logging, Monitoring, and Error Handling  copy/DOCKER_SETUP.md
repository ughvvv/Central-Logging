# Docker Setup Guide

This guide will help you install Docker and Docker Compose on your macOS system, which are required for running the full logging, monitoring, and error handling infrastructure.

## Installing Docker Desktop for Mac

Docker Desktop for Mac is an easy-to-install application that includes Docker Engine, Docker CLI client, Docker Compose, and other tools needed for our infrastructure.

### System Requirements

- macOS 11 (Big Sur) or newer
- At least 4GB of RAM
- VirtualBox prior to version 4.3.30 must not be installed

### Installation Steps

1. **Download Docker Desktop for Mac**:
   - Visit [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
   - Click on "Download for Mac" button
   - Choose the appropriate version for your Mac (Intel chip or Apple chip)

2. **Install Docker Desktop**:
   - Open the downloaded `.dmg` file
   - Drag the Docker icon to the Applications folder
   - Open Docker from your Applications folder
   - You may be prompted to authorize Docker with your password
   - Wait for Docker to start (the whale icon in the status bar will stop animating when Docker is ready)

3. **Verify Installation**:
   - Open Terminal
   - Run the following commands to verify Docker and Docker Compose are installed:
     ```bash
     docker --version
     docker-compose --version
     ```
   - You should see version information for both commands

4. **Test Docker**:
   - Run a simple container to test that Docker is working:
     ```bash
     docker run hello-world
     ```
   - You should see a message indicating that Docker is working correctly

## Setting Docker Resource Limits

Our infrastructure requires several containers running simultaneously, so it's important to allocate sufficient resources to Docker:

1. **Open Docker Desktop Preferences**:
   - Click on the Docker icon in the status bar
   - Select "Preferences" (or "Settings")

2. **Adjust Resources**:
   - Go to the "Resources" tab
   - Set CPUs to at least 2
   - Set Memory to at least 4GB (4096MB)
   - Set Swap to at least 1GB (1024MB)
   - Click "Apply & Restart"

## Next Steps

Once Docker and Docker Compose are installed and configured, you can run the full validation script to test the infrastructure:

```bash
./run_validation.sh
```

Or run the complete end-to-end test:

```bash
./run_complete_test.sh
```

## Troubleshooting

- **Docker Desktop fails to start**: Try restarting your computer
- **Containers fail to start**: Check Docker Desktop logs for errors
- **Elasticsearch fails to start**: Increase the memory allocation in Docker Desktop preferences
- **Permission issues**: Make sure you have the necessary permissions to run Docker commands

## Uninstalling Docker Desktop

If you need to uninstall Docker Desktop:

1. Open Docker Desktop
2. Click on the Docker icon in the status bar
3. Select "Preferences" (or "Settings")
4. Click on "Uninstall" or "Reset"
5. Follow the prompts to uninstall Docker Desktop
