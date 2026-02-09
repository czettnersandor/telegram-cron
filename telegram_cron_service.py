#!/usr/bin/env python3
"""
Telegram Cron Service
A service that executes scheduled scripts and sends notifications via Telegram
"""

import os
import sys
import subprocess
import logging
import time
import yaml
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from croniter import croniter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/telegram_cron_service.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('TelegramCronService')


class TelegramNotifier:
    """Handles sending messages to Telegram"""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send a message to the configured Telegram chat"""
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Message sent successfully to chat {self.chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False


class ScriptExecutor:
    """Executes scripts and handles their output"""

    @staticmethod
    def execute(script_path: str, timeout: int = 300, args: list = None) -> tuple[int, str, str]:
        """
        Execute a script and return exit code, stdout, stderr

        Args:
            script_path: Path to the script to execute
            timeout: Maximum execution time in seconds
            args: Additional arguments to pass to the script

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            # Determine if it's a Python or shell script
            if script_path.endswith('.py'):
                cmd = [sys.executable, script_path]
            else:
                cmd = ['/bin/bash', script_path]
            
            # Add arguments if provided
            if args:
                cmd.extend(args)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.path.dirname(script_path) or '.'
            )

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            logger.error(f"Script {script_path} timed out after {timeout} seconds")
            return -1, "", f"Script execution timed out after {timeout} seconds"
        except Exception as e:
            logger.error(f"Error executing script {script_path}: {e}")
            return -1, "", str(e)


class CronJob:
    """Represents a single cron job"""

    def __init__(self, name: str, config: Dict[str, Any], base_dir: str = None):
        self.name = name
        self.schedule = config['schedule']
        script_path = config['script']

        # Resolve script path: support relative paths from config directory
        if not os.path.isabs(script_path):
            # If base_dir provided and path is relative, resolve from base_dir
            if base_dir:
                self.script = os.path.abspath(os.path.join(base_dir, script_path))
            else:
                self.script = os.path.abspath(script_path)
        else:
            # Absolute path, expand ~ if present
            self.script = os.path.expanduser(script_path)

        logger.debug(f"Job '{name}': resolved script path '{script_path}' -> '{self.script}'")

        self.timeout = config.get('timeout', 300)
        self.enabled = config.get('enabled', True)
        self.send_errors = config.get('send_errors', True)
        self.args = config.get('args', [])

        # Validate cron expression
        try:
            croniter(self.schedule)
        except Exception as e:
            raise ValueError(f"Invalid cron expression '{self.schedule}' for job '{name}': {e}")

        # Validate script exists
        if not os.path.exists(self.script):
            raise ValueError(f"Script not found: {self.script}")

        self.last_run = None
        self.next_run = None
        self.calculate_next_run()

    def calculate_next_run(self):
        """Calculate the next run time based on cron schedule"""
        now = datetime.now()
        cron = croniter(self.schedule, now)
        self.next_run = cron.get_next(datetime)

    def should_run(self) -> bool:
        """Check if the job should run now"""
        if not self.enabled:
            return False

        now = datetime.now()
        if self.next_run and now >= self.next_run:
            return True
        return False

    def execute(self, notifier: TelegramNotifier) -> None:
        """Execute the job and handle notifications"""
        logger.info(f"Executing job: {self.name}")
        self.last_run = datetime.now()

        executor = ScriptExecutor()
        exit_code, stdout, stderr = executor.execute(self.script, self.timeout, self.args)

        # Check for NOUPDATE flag
        if stdout.strip() == "NOUPDATE":
            logger.info(f"Job {self.name} returned NOUPDATE - no message sent")
        else:
            # Prepare message
            message = f"<b>{self.name}</b>\n"

            if stdout:
                message += f"\n{stdout[:3000]}\n"

            if stderr and (exit_code != 0 or self.send_errors):
                message += f"<b>Errors:</b>\n<pre>{stderr[:1000]}</pre>\n"

            if exit_code != 0:
                message += f"\n<b>Exit Code:</b> {exit_code}"

            notifier.send_message(message)

        # Calculate next run
        self.calculate_next_run()
        logger.info(f"Job {self.name} next run: {self.next_run}")


class TelegramCronService:
    """Main service class"""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config_dir = os.path.dirname(os.path.abspath(config_path))
        self.config = self.load_config()
        self.notifier = TelegramNotifier(
            self.config['telegram']['bot_token'],
            self.config['telegram']['chat_id']
        )
        self.jobs = self.load_jobs()
        self.running = False

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Validate required fields
            if 'telegram' not in config:
                raise ValueError("Missing 'telegram' section in config")
            if 'bot_token' not in config['telegram']:
                raise ValueError("Missing 'telegram.bot_token' in config")
            if 'chat_id' not in config['telegram']:
                raise ValueError("Missing 'telegram.chat_id' in config")

            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def load_jobs(self) -> Dict[str, CronJob]:
        """Load all jobs from configuration"""
        jobs = {}
        if 'jobs' not in self.config:
            logger.warning("No jobs defined in configuration")
            return jobs

        for job_name, job_config in self.config['jobs'].items():
            try:
                jobs[job_name] = CronJob(job_name, job_config, self.config_dir)
                logger.info(f"Loaded job: {job_name} - Next run: {jobs[job_name].next_run}")
            except Exception as e:
                logger.error(f"Failed to load job {job_name}: {e}")

        return jobs

    def run(self):
        """Main service loop"""
        logger.info("Telegram Cron Service starting...")
        self.notifier.send_message("🚀 <b>Telegram Cron Service Started</b>\n"
                                   f"Monitoring {len(self.jobs)} job(s)")

        self.running = True

        try:
            while self.running:
                # Check each job
                for job_name, job in self.jobs.items():
                    if job.should_run():
                        try:
                            job.execute(self.notifier)
                        except Exception as e:
                            logger.error(f"Error executing job {job_name}: {e}")
                            self.notifier.send_message(
                                f"❌ <b>Job Execution Error: {job_name}</b>\n"
                                f"<pre>{str(e)}</pre>"
                            )

                # Sleep for a bit
                time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            logger.info("Service interrupted by user")
        finally:
            self.shutdown()

    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Telegram Cron Service stopping...")
        self.running = False
        self.notifier.send_message("🛑 <b>Telegram Cron Service Stopped</b>")


def main():
    """Entry point"""
    if len(sys.argv) != 2:
        print("Usage: telegram_cron_service.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    if not os.path.exists(config_file):
        print(f"Config file not found: {config_file}")
        sys.exit(1)

    service = TelegramCronService(config_file)
    service.run()


if __name__ == '__main__':
    main()
