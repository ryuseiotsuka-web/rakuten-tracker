@echo off
REM 楽天検索順位チェックツール - Windows用実行スクリプト

REM このスクリプトのディレクトリに移動
cd /d "%~dp0"

REM ログファイルのパス
set LOG_FILE=%USERPROFILE%\rakuten_launchd.log

REM 実行開始をログに記録
echo ================================================ >> "%LOG_FILE%"
echo Started at: %date% %time% >> "%LOG_FILE%"
echo Working directory: %CD% >> "%LOG_FILE%"

REM Pythonスクリプトを実行
python rakuten_multi_tracker.py >> "%LOG_FILE%" 2>&1

REM 実行完了をログに記録
echo Completed at: %date% %time% >> "%LOG_FILE%"
echo Exit code: %errorlevel% >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"

exit /b %errorlevel%
