import os
import time
import csv
import logging
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ranking_tracker.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 設定
SHEET_ID = "1O_pT_RChITr7OvukkKVcjMC7aBji0xv2sr092Fn_FwE"  # スプレッドシートID
SETTINGS_SHEET_NAME = "設定"  # キーワードリストを記載するシート名
RESULTS_SHEET_NAME = "ランキング履歴"  # 結果を書き込むシート名
CREDENTIALS_FILE = "credentials.json"  # 認証ファイル
USER_DATA_DIR = "./user_data_ranking"
CSV_FILE = "rakuten_ranking_auto.csv"
LAST_ROW_FILE = "last_row.txt"  # 最終書き込み行を記録

def scrape_rankings(page, keyword, target_url, retry_count=0):
    """楽天で検索して、PR順位と自然検索順位を取得"""
    target_id = target_url.strip("/").split("/")[-1]
    search_url = f"https://search.rakuten.co.jp/search/mall/{keyword}/"
    logger.info(f"🔍 Searching for '{keyword}' (Target: {target_id})...")
    print(f"🔍 Searching for '{keyword}' (Target: {target_id})...")
    
    try:
        page.goto(search_url, timeout=90000)
        page.wait_for_load_state("domcontentloaded", timeout=60000)
        time.sleep(3)
        page.wait_for_selector(".searchresultitem", timeout=30000)
    except Exception as e:
        logger.error(f"⚠️ Search page error for '{keyword}': {e}")
        print(f"⚠️ Search page error for '{keyword}': {e}")
        if retry_count < 1:
            logger.info(f"   → Retrying in 5 seconds...")
            print(f"   → Retrying in 5 seconds...")
            time.sleep(5)
            return scrape_rankings(page, keyword, target_url, retry_count + 1)
        return "ERROR", "ERROR"

    items = page.locator(".searchresultitem").all()
    pr_count = 0
    organic_count = 0
    target_pr_rank = None
    target_organic_rank = None
    
    for item in items:
        doc_type = item.get_attribute("data-track-doc-type")
        is_pr = (doc_type == "rpp")
        if is_pr: 
            pr_count += 1
        else: 
            organic_count += 1
            
        is_match = False
        
        # 1. Check data-track-variantid
        variant_id = item.get_attribute("data-track-variantid") or ""
        if target_id in variant_id:
            is_match = True
            
        # 2. Check all link hrefs
        if not is_match:
            links = item.locator("a").all()
            for link in links:
                if target_id in (link.get_attribute("href") or ""):
                    is_match = True
                    break
        
        # 3. Check all image sources
        if not is_match:
            imgs = item.locator("img").all()
            for img in imgs:
                if target_id in (img.get_attribute("src") or ""):
                    is_match = True
                    break
        
        if is_match:
            if is_pr and target_pr_rank is None:
                target_pr_rank = pr_count
                logger.info(f"   ✨ Found in PR (RPP)! Rank: {target_pr_rank}")
                print(f"   ✨ Found in PR (RPP)! Rank: {target_pr_rank}")
            elif not is_pr and target_organic_rank is None:
                target_organic_rank = organic_count
                logger.info(f"   ✨ Found in Organic! Rank: {target_organic_rank}")
                print(f"   ✨ Found in Organic! Rank: {target_organic_rank}")

    pr_result = target_pr_rank or "圏外"
    organic_result = target_organic_rank or "圏外"
    logger.info(f"   Result: PR={pr_result}, Organic={organic_result}")
    return pr_result, organic_result

def get_sheets_service():
    """Google Sheets APIサービスを取得"""
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=creds)
    return service

def load_keywords_from_sheet(service):
    """スプレッドシートからキーワードリストを読み込む"""
    try:
        # 設定シートからデータを読み込む（2行目以降、A列とB列）
        range_name = f'{SETTINGS_SHEET_NAME}!A2:B'
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            logger.warning(f"⚠️ No keywords found in '{SETTINGS_SHEET_NAME}' sheet")
            return []
        
        keywords_list = []
        for row in values:
            # 空行をスキップ
            if len(row) >= 2 and row[0].strip() and row[1].strip():
                keywords_list.append({
                    "keyword": row[0].strip(),
                    "url": row[1].strip()
                })
        
        logger.info(f"📋 Loaded {len(keywords_list)} keywords from spreadsheet")
        print(f"📋 Loaded {len(keywords_list)} keywords from spreadsheet")
        return keywords_list
        
    except Exception as e:
        logger.error(f"❌ Error loading keywords from spreadsheet: {e}")
        print(f"❌ Error loading keywords from spreadsheet: {e}")
        return []

def write_to_sheets(service, start_row, data):
    """Google Sheetsに一括書き込み"""
    try:
        # データを準備
        values = []
        for row_data in data:
            values.append([
                row_data['date'],
                row_data['keyword'],
                row_data['url'],
                str(row_data['pr']),
                str(row_data['organic'])
            ])
        
        # 書き込み範囲を指定（結果シートに書き込む）
        range_name = f'{RESULTS_SHEET_NAME}!A{start_row}:E{start_row + len(values) - 1}'
        
        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        logger.info(f"✅ Successfully wrote {result.get('updatedCells')} cells to spreadsheet")
        print(f"✅ Successfully wrote {result.get('updatedCells')} cells to spreadsheet")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error writing to spreadsheet: {e}")
        print(f"❌ Error writing to spreadsheet: {e}")
        return False

def update_spreadsheet():
    start_time = datetime.now()
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 Starting Ranking Check at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*60}")
    print(f"\n🚀 Starting Ranking Check at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # スプレッドシートからキーワードリストを読み込む
    try:
        service = get_sheets_service()
        keywords_list = load_keywords_from_sheet(service)
        
        if not keywords_list:
            logger.error("❌ No keywords to process. Exiting.")
            print("❌ No keywords to process. Please check the settings sheet.")
            return
    except Exception as e:
        logger.error(f"❌ Failed to load keywords: {e}")
        print(f"❌ Failed to load keywords: {e}")
        return
    
    logger.info(f"Total keywords to process: {len(keywords_list)}")
    
    # 最終書き込み行を読み込んで次の行から追記
    if os.path.exists(LAST_ROW_FILE):
        with open(LAST_ROW_FILE, "r") as f:
            last_row = int(f.read().strip())
            start_row = last_row + 1
        logger.info(f"Last written row: {last_row}, starting from row {start_row}")
    else:
        start_row = 2  # 初回は2行目から（1行目はヘッダー）
        logger.info(f"First run - starting from row {start_row}")

    with sync_playwright() as p:
        # CI環境（GitHub Actions）またはDocker headlessモードかどうかでheadless設定を変更
        is_ci = os.environ.get('CI') == 'true'
        
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=is_ci, # CI環境ならTrue（画面なし）、ローカルならFalse（画面あり）
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # 1. 順位取得
        logger.info("🔍 Scraping rankings...")
        print("🔍 Scraping rankings...")
        all_results = []

        
        # 日本時間（JST = UTC+9）で日時を取得
        # GitHub ActionsはUTC環境なので、明示的に9時間加算
        jst_time = datetime.utcnow() + timedelta(hours=9)
        current_date = jst_time.strftime("%Y-%m-%d %H:%M")
        
        for idx, task in enumerate(keywords_list, 1):
            logger.info(f"Processing keyword {idx}/{len(keywords_list)}: {task['keyword']}")
            # Create new page for each keyword to prevent memory leaks
            try:
                page = context.new_page()
                pr, organic = scrape_rankings(page, task["keyword"], task["url"])
            except Exception as e:
                logger.error(f"❌ Error processing {task['keyword']}: {e}")
                print(f"❌ Error processing {task['keyword']}: {e}")
                pr, organic = "ERROR", "ERROR"
            finally:
                if 'page' in locals():
                    page.close()

            all_results.append({
                "date": current_date,
                "keyword": task["keyword"],
                "url": task["url"],
                "pr": pr,
                "organic": organic
            })
        

        context.close()
        logger.info(f"✅ Scraping completed. Total results: {len(all_results)}")
    
    # 2. Google Sheetsに書き込み
    logger.info("📊 Writing to Google Sheets...")
    print("📊 Writing to Google Sheets...")
    
    try:
        # serviceは既に取得済みなので再利用
        success = write_to_sheets(service, start_row, all_results)
        
        if success:
            # 最終書き込み行を保存（次回はこの次の行から追記）
            final_row = start_row + len(all_results) - 1
            with open(LAST_ROW_FILE, "w") as f:
                f.write(str(final_row))
            logger.info(f"📝 Data written to rows {start_row} to {final_row}")
            logger.info(f"📝 Next run will start from row {final_row + 1}")
            print(f"📝 Data written to rows {start_row} to {final_row}")
    except Exception as e:
        logger.error(f"❌ Failed to write to Google Sheets: {e}")
        print(f"❌ Failed to write to Google Sheets: {e}")
    
    # 3. CSV保存
    save_to_csv(all_results)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ All rankings updated in the Spreadsheet and CSV.")
    logger.info(f"Total execution time: {duration:.2f} seconds")
    logger.info(f"Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*60}\n")
    print(f"\n✅ All rankings updated! Execution time: {duration:.2f} seconds")

def save_to_csv(results):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "keyword", "url", "pr", "organic"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    update_spreadsheet()
