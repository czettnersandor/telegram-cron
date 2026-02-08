# Quick Start Guide

## 5-Minute Setup

### 1. Get Telegram Credentials (2 minutes)

**Create a bot:**
- Open Telegram, search for `@BotFather`
- Send: `/newbot`
- Follow instructions and save your **bot token**

**Get your chat ID:**
- Search for `@userinfobot` on Telegram
- Send any message, it replies with your **chat ID**

### 2. Install (1 minute)

```bash
# Clone to your preferred location
git clone https://github.com/czettnersandor/telegram-cron.git ~/telegram-cron
cd ~/telegram-cron

# Run the installer (creates virtual environment and installs dependencies)
chmod +x install.sh
./install.sh
```

**Note:** The installer creates a Python virtual environment (`venv` directory) to isolate dependencies from your system Python.

### 3. Configure (1 minute)

Copy some example scripts from `example-scripts/` to `scripts/`

```bash
# Edit config in your installation directory
nano ~/telegram-cron/config.yaml  # or wherever you cloned it
```

Update these two lines:
```yaml
telegram:
  bot_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # Your bot token
  chat_id: "123456789"                               # Your chat ID
```

Save and exit (Ctrl+X, Y, Enter)

### 4. Start (1 minute)

```bash
# Enable service to start on boot
loginctl enable-linger $USER

# Start the service
systemctl --user start telegram-cron

# Check status
systemctl --user status telegram-cron
```

You should receive a Telegram message: "🚀 Telegram Cron Service Started"

## What's Running?

The service includes 3 example jobs:

1. **Disk Space Check** - Every hour
   - Alerts if disk usage > 80%
   - Silent if everything is OK

2. **System Health Check** - Every 5 minutes
   - Alerts if CPU > 80% or Memory > 85%
   - Silent if everything is OK

3. **Backup Status** - Daily at 2 AM
   - Reports backup file status
   - (Requires configuration)

## Customize Your Jobs

Edit `config.yaml` in your installation directory:

```yaml
jobs:
  my_custom_job:
    schedule: "*/10 * * * *"  # Every 10 minutes
    script: "scripts/my_script.sh"  # Relative to config file
    timeout: 60
    enabled: true
```

Create your script:
```bash
# From your installation directory
cd ~/telegram-cron  # or wherever you cloned it
nano scripts/my_script.sh
chmod +x scripts/my_script.sh
```

Restart service:
```bash
systemctl --user restart telegram-cron
```

## Common Commands

```bash
# View logs
journalctl --user -u telegram-cron -f

# Restart service
systemctl --user restart telegram-cron

# Stop service
systemctl --user stop telegram-cron

# Service status
systemctl --user status telegram-cron
```

## Updating

To update to the latest version:

```bash
# Navigate to installation directory
cd ~/telegram-cron  # or wherever you cloned it

# Pull latest changes
git pull

# Update service and dependencies (updates venv packages)
./install.sh

# Restart service
systemctl --user restart telegram-cron
```

**Note:** The installer automatically updates Python packages in the virtual environment when you run it.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Add your own monitoring scripts
- Customize notification schedules
- Set up backup monitoring
- Keep your installation updated with `git pull`

**Need help?** Check the Troubleshooting section in README.md
