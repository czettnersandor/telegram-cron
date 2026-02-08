#!/bin/bash
# Installation script for Telegram Cron Service
# This script sets up the systemd service for the current installation

set -e

echo "==================================="
echo "Telegram Cron Service - Installer"
echo "==================================="
echo ""

# Use current directory as installation directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$INSTALL_DIR/scripts"
VENV_DIR="$INSTALL_DIR/venv"

echo "Installation directory: $INSTALL_DIR"
echo ""

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    echo "Please install python3 first: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Check if pip is installed
if ! python3 -m pip --version &> /dev/null; then
    echo "Error: pip is not installed"
    echo "Please install pip first: sudo apt install python3-pip"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists at $VENV_DIR"
fi

# Install/update Python dependencies
echo "Installing/updating Python dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

# Create scripts directory if it doesn't exist
mkdir -p "$SCRIPTS_DIR"

# Ensure example scripts are executable
if [ -f "$SCRIPTS_DIR/check_disk_space.sh" ]; then
    chmod +x "$SCRIPTS_DIR/check_disk_space.sh"
fi
if [ -f "$SCRIPTS_DIR/health_check.py" ]; then
    chmod +x "$SCRIPTS_DIR/health_check.py"
fi
if [ -f "$SCRIPTS_DIR/backup_status.py" ]; then
    chmod +x "$SCRIPTS_DIR/backup_status.py"
fi

# Create config if it doesn't exist
if [ ! -f "$INSTALL_DIR/config.yaml" ]; then
    if [ -f "$INSTALL_DIR/config.example.yaml" ]; then
        echo "Creating default configuration..."
        cp "$INSTALL_DIR/config.example.yaml" "$INSTALL_DIR/config.yaml"
        echo ""
        echo "⚠️  IMPORTANT: Edit $INSTALL_DIR/config.yaml with your Telegram credentials!"
        echo ""
    else
        echo "Warning: config.example.yaml not found. Please create config.yaml manually."
    fi
else
    echo "Configuration file already exists at $INSTALL_DIR/config.yaml"
fi

# Setup systemd service
echo "Setting up systemd service..."

# Create service file from template
SERVICE_FILE="$HOME/.config/systemd/user/telegram-cron.service"
mkdir -p "$HOME/.config/systemd/user"

if [ ! -f "telegram-cron.service.template" ]; then
    echo "Error: telegram-cron.service.template not found"
    exit 1
fi

cat telegram-cron.service.template | \
    sed "s|%USER%|$USER|g" | \
    sed "s|%INSTALL_DIR%|$INSTALL_DIR|g" | \
    sed "s|%VENV_PATH%|$VENV_DIR|g" > "$SERVICE_FILE"

echo "Reloading systemd and enabling service..."
systemctl --user daemon-reload
systemctl --user enable telegram-cron.service

echo ""
echo "==================================="
echo "Installation Complete!"
echo "==================================="
echo ""
echo "Installation directory: $INSTALL_DIR"
echo "Scripts directory: $SCRIPTS_DIR"
echo ""
echo "Next steps:"
echo "1. Edit configuration (if not done yet):"
echo "   nano $INSTALL_DIR/config.yaml"
echo ""
echo "2. Add your Telegram bot token and chat ID"
echo ""
echo "3. Start the service:"
echo "   systemctl --user start telegram-cron"
echo ""
echo "4. Check service status:"
echo "   systemctl --user status telegram-cron"
echo ""
echo "5. View logs:"
echo "   journalctl --user -u telegram-cron -f"
echo ""
echo "To enable the service to start on boot:"
echo "   loginctl enable-linger $USER"
echo ""
echo "To update the installation:"
echo "   git pull"
echo "   ./install.sh"
echo ""