import datetime
import os

# 現在のディレクトリを確認
current_dir = os.getcwd()

# ログファイルに書き込み
log_file = "test_scheduler.log"
with open(log_file, "a", encoding="utf-8") as f:
    f.write(f"\n{'='*60}\n")
    f.write(f"Test run at: {datetime.datetime.now()}\n")
    f.write(f"Current directory: {current_dir}\n")
    f.write(f"Python executable: {os.sys.executable}\n")
    f.write(f"{'='*60}\n")

print(f"✅ Test completed. Check {log_file}")
