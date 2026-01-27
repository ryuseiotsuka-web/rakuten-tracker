import schedule
import time
import subprocess
import logging
from datetime import datetime

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [DAEMON] - %(message)s'
)
logger = logging.getLogger(__name__)

def run_tracker():
    logger.info("🚀 Starting scheduled tracker job...")
    try:
        # Execute the main script with xvfb-run for headless display
        result = subprocess.run(
            ["xvfb-run", "--auto-servernum", "--server-args=-screen 0 1280x960x24", "python", "rakuten_multi_tracker.py"],
            capture_output=True,
            text=True
        )
        
        # Log output from the script
        if result.stdout:
            logger.info(f"Script Output:\n{result.stdout}")
        if result.stderr:
            logger.error(f"Script Error Output:\n{result.stderr}")
            
        if result.returncode == 0:
            logger.info("✅ Job finished successfully.")
        else:
            logger.error(f"❌ Job failed with return code {result.returncode}.")
            
    except Exception as e:
        logger.error(f"❌ Failed to execute job: {e}")

# Schedule the job
# Default: Runs every day at 09:00 JST (You can change this)
SCHEDULE_TIME = "09:00"
schedule.every().day.at(SCHEDULE_TIME).do(run_tracker)

logger.info(f"✨ Daemon started. Scheduled to run daily at {SCHEDULE_TIME}.")
logger.info("Press Ctrl+C to stop.")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)
