# Telegram Cron Service

A Python-based service that executes scheduled scripts (similar to cron) and sends notifications to Telegram. Only sends messages when scripts have updates to report.

## Features

- ✅ **Cron-like scheduling** - Schedule scripts using standard cron expressions
- 📱 **Telegram notifications** - Get instant notifications on script execution
- 🔕 **Smart notifications** - Scripts can return "NOUPDATE" to skip notifications
- 🐍 **Python & Shell support** - Run both Python and Bash scripts
- ⚙️ **Systemd integration** - Runs as a user systemd service
- 🔄 **Auto-restart** - Automatic recovery from crashes
- 📊 **Rich output** - Formatted messages with execution status and output

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- systemd (for running as a service)
- A Telegram bot token and chat ID

## Getting Your Telegram Credentials

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to name your bot
4. Copy the **bot token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID

1. Search for `@userinfobot` on Telegram
2. Start a chat with the bot
3. It will reply with your chat ID (e.g., `123456789`)

Alternatively, to get a group chat ID:
1. Add your bot to the group
2. Send a message in the group
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for the `"chat":{"id":` field in the JSON response

## Installation

### Quick Install

1. Clone the repository to your preferred location:

```bash
# Clone to your preferred location (example: ~/telegram-cron)
git clone <repository-url> ~/telegram-cron
cd ~/telegram-cron
```

2. Run the installation script:

```bash
chmod +x install.sh
./install.sh
```

The installer will:
- Set up a Python virtual environment in the current directory (isolated from system Python)
- Install all dependencies within the virtual environment using `python3 -m pip`
- Configure the systemd service with the current installation path
- Create a default config.yaml if it doesn't exist

**Note:** This installation uses Python virtual environments to isolate dependencies from your system Python installation. All packages are installed within the project's `venv` directory.

### Manual Installation

If you prefer to install manually:

```bash
# Clone to your preferred location
git clone <repository-url> ~/telegram-cron
cd ~/telegram-cron

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (using python3 -m pip ensures virtual environment isolation)
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Create configuration
cp config.example.yaml config.yaml

# Make scripts executable
chmod +x scripts/*.sh scripts/*.py

# Set up systemd service (adjust paths as needed)
mkdir -p ~/.config/systemd/user
# Edit telegram-cron.service.template and copy to ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable telegram-cron.service
```

## Configuration

Edit the configuration file in your installation directory (e.g., `~/telegram-cron/config.yaml`):

```yaml
telegram:
  bot_token: "YOUR_BOT_TOKEN_HERE"  # From @BotFather
  chat_id: "YOUR_CHAT_ID_HERE"      # From @userinfobot

jobs:
  my_first_job:
    schedule: "*/5 * * * *"          # Every 5 minutes
    script: "/full/path/to/telegram-cron/scripts/health_check.py"
    timeout: 60                       # Max execution time in seconds
    enabled: true                     # Enable/disable this job
    send_errors: true                 # Send stderr even on success
```

**Note:** Always use absolute paths for scripts in your configuration.

### Cron Schedule Format

The `schedule` field uses standard cron syntax:

```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, Sunday = 0 or 7)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

**Examples:**
- `* * * * *` - Every minute
- `*/5 * * * *` - Every 5 minutes
- `0 * * * *` - Every hour
- `0 0 * * *` - Every day at midnight
- `0 9 * * 1-5` - Weekdays at 9 AM
- `0 0 1 * *` - First day of every month
- `30 2 * * 0` - Every Sunday at 2:30 AM

## Creating Scripts

### The NOUPDATE Flag

Scripts can return `NOUPDATE` as their only output to indicate "no news" - the service won't send a Telegram notification.

### Bash Script Example

```bash
#!/bin/bash
# Check if service is running

if systemctl is-active --quiet nginx; then
    echo "NOUPDATE"  # Service is fine, don't notify
else
    echo "⚠️ Nginx is down!"
    echo "Please check the server"
fi
```

### Python Script Example

```python
#!/usr/bin/env python3
import psutil

# Check CPU usage
cpu = psutil.cpu_percent(interval=1)

if cpu < 80:
    print("NOUPDATE")  # CPU is fine
else:
    print(f"🔥 High CPU Alert!")
    print(f"Current usage: {cpu}%")
```

### Script Best Practices

1. **Always use absolute paths** in your config (e.g., `/home/user/telegram-cron/scripts/myscript.sh`)
2. **Make scripts executable**: `chmod +x yourscript.sh`
3. **Use proper shebangs**:
   - Bash: `#!/bin/bash`
   - Python: `#!/usr/bin/env python3`
4. **Test scripts manually** before scheduling them
5. **Keep output concise** - long output will be truncated
6. **Return "NOUPDATE"** when everything is fine to reduce noise
7. **Use git to update** - Pull latest changes with `git pull` and run `./install.sh` to update the service

### Example AI prompt to create a script

This software was designed with AI in mind. You should be able to ask your preferred AI assistant to create a script for you. Because asking the AI from a chat is cheaper (usually free) than asking it from an IDE. Here's an example prompt:

"Create a Python script that checks the CPU usage and prints a message if it exceeds 80%. If it's below 80%, return 'NOUPDATE'."

Then, you can copy this script to your `scripts` directory and add it to your config. Simple as that!

## Running the Service

### Start the Service

```bash
# Enable user lingering (allows services to run without login)
loginctl enable-linger $USER

# Start the service
systemctl --user start telegram-cron

# Enable auto-start on boot
systemctl --user enable telegram-cron
```

### Check Service Status

```bash
# View status
systemctl --user status telegram-cron

# View logs in real-time
journalctl --user -u telegram-cron -f

# View recent logs
journalctl --user -u telegram-cron -n 50
```

### Stop the Service

```bash
systemctl --user stop telegram-cron
```

### Restart the Service (after config changes)

```bash
systemctl --user restart telegram-cron
```

## Testing

### Test Your Bot Token

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

### Test a Script Manually

```bash
# Change to your installation directory
cd ~/telegram-cron  # or wherever you cloned it

# Or run directly with venv python without activating
venv/bin/python3 scripts/health_check.py
```

### Test Configuration

```bash
# Change to your installation directory
cd ~/telegram-cron  # or wherever you cloned it

# Or run directly with venv python without activating
venv/bin/python3 telegram_cron_service.py config.yaml
```

**Note:** All commands use the virtual environment's Python interpreter to ensure proper dependency isolation.

## Troubleshooting

### Service won't start

1. Check logs: `journalctl --user -u telegram-cron -n 50`
2. Verify config file exists in your installation directory
3. Test Python script manually from your installation directory:
   ```bash
   cd ~/telegram-cron  # or your installation path
   venv/bin/python3 telegram_cron_service.py config.yaml
   ```

### No Telegram messages

1. Verify bot token and chat ID are correct
2. Check if bot is blocked by you
3. Test with curl:
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" \
        -d "chat_id=<YOUR_CHAT_ID>" \
        -d "text=Test message"
   ```

### Scripts not executing

1. Check script permissions in your installation directory
2. Make executable: `chmod +x scripts/*.sh scripts/*.py`
3. Verify paths in config.yaml are absolute (not relative)
4. Check script syntax by running manually

### Service stops after logout

Enable user lingering:
```bash
loginctl enable-linger $USER
```

## Updating

To update to the latest version:

```bash
# Navigate to installation directory
cd ~/telegram-cron  # or wherever you cloned it

# Stop the service
systemctl --user stop telegram-cron

# Pull latest changes
git pull

# Run installer to update dependencies and service
./install.sh

# Start the service
systemctl --user start telegram-cron
```

## Log Files

- **Service logs**: `journalctl --user -u telegram-cron`
- **Script output**: Captured and sent via Telegram
- **Application log**: `/tmp/telegram_cron_service.log`

## Example Use Cases

1. **Server Monitoring**
   - Disk space alerts
   - CPU/Memory usage
   - Service health checks
   
2. **Backup Notifications**
   - Daily backup status
   - Backup file verification
   - Storage space monitoring

3. **Application Monitoring**
   - Database connection checks
   - API endpoint monitoring
   - Log file analysis

4. **Security Alerts**
   - Failed login attempts
   - Suspicious activity detection
   - Certificate expiration warnings

5. **Data Collection**
   - Website uptime monitoring
   - API data fetching
   - Report generation

## Uninstall

```bash
# Stop and disable service
systemctl --user stop telegram-cron
systemctl --user disable telegram-cron

# Remove service file
rm ~/.config/systemd/user/telegram-cron.service
systemctl --user daemon-reload

# Remove installation directory (adjust path to your installation)
rm -rf ~/telegram-cron
```

## Security Notes

- Keep your bot token secret - never commit it to version control
- Use environment variables for sensitive data if needed
- Restrict file permissions: `chmod 600 ~/telegram-cron/config.yaml`
- Only run trusted scripts
- Review script output before enabling notifications

## Dependencies

This project uses Python virtual environments to isolate dependencies from your system Python installation.

### Core Dependencies

- `requests` - HTTP library for Telegram API
- `PyYAML` - YAML configuration parsing
- `croniter` - Cron expression parsing
- `psutil` - System monitoring (for example scripts)

### Virtual Environment

All dependencies are installed in a local `venv` directory within your installation. This ensures:
- No conflicts with system Python packages
- Easy cleanup (just delete the `venv` directory)
- Reproducible installations
- No need for sudo/root access

The installation script uses `python3 -m pip` to ensure proper isolation and that all packages are installed in the virtual environment, not system-wide.

## License

MIT License - Feel free to modify and distribute

## Contributing

Contributions are welcome! Feel free to:
- Add new example scripts
- Improve error handling
- Add new features
- Fix bugs

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs
3. Test components individually
4. Create an issue with detailed information

---

**Happy monitoring! 🚀**
