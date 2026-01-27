#!/bin/bash

# 楽天順位チェック実行スクリプト
# launchdから確実に実行されるようにするためのラッパー

# 作業ディレクトリに移動
cd "/Users/kananagai/Documents/楽天自動化ツール/03_検索順位チェック"

# 環境変数を設定
export PATH="/Library/Frameworks/Python.framework/Versions/3.14/bin:$PATH"
export HOME="/Users/kananagai"

# 実行開始をログに記録
echo "================================================" >> launchd_wrapper.log
echo "Started at: $(date '+%Y-%m-%d %H:%M:%S')" >> launchd_wrapper.log

# Pythonスクリプトを実行
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 rakuten_multi_tracker.py >> launchd_wrapper.log 2>&1

# 実行完了をログに記録
echo "Completed at: $(date '+%Y-%m-%d %H:%M:%S')" >> launchd_wrapper.log
echo "Exit code: $?" >> launchd_wrapper.log
echo "================================================" >> launchd_wrapper.log
