# 楽天検索順位自動チェックツール 🔍

楽天市場での商品の検索順位を自動で確認し、Googleスプレッドシートに記録するツールです。

## ✨ できること

- 📊 楽天市場での商品の検索順位を自動取得
- 📝 結果をGoogleスプレッドシートに自動書き込み
- 🤖 Mac上で毎日自動実行（月〜金 9:30）
- 📈 PR（RPP広告）とオーガニック検索の両方に対応

---

## 🚀 クイックスタート

### 必要なもの

- **Mac**（macOS Big Sur以降推奨）または **Windows 10/11**
- Python 3.14以上
- Googleアカウント

### インストール手順

1. **リポジトリをクローン**
```bash
git clone [このリポジトリのURL]
cd 03_検索順位チェックのコピー
```

2. **必要なパッケージをインストール**
```bash
pip install -r requirements.txt
playwright install chromium
```

3. **Google Sheets APIの設定**
   - [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
   - Google Sheets APIを有効化
   - OAuth 2.0認証情報を作成し、`credentials.json`としてダウンロード
   - このディレクトリに`credentials.json`を配置

4. **設定を編集**

`rakuten_multi_tracker.py`を開いて、以下を変更：

```python
# スプレッドシートの名前
SPREADSHEET_TITLE = "あなたのスプレッドシート名"

# チェックしたいキーワードと商品ID
KEYWORDS_PRODUCTS = [
    ("財布 レディース", "product123"),
    ("バッグ 通勤", "product456"),
]
```

5. **初回実行**

**Mac:**
```bash
python3 rakuten_multi_tracker.py
```

**Windows (PowerShell):**
```powershell
python rakuten_multi_tracker.py
```

初回はブラウザが開き、Googleアカウントでログインが必要です。

---

## ⚙️ 自動実行の設定

### 📱 Mac の場合

#### 1. ラッパースクリプトの準備

```bash
cp run_tracker.sh ~/run_rakuten.sh
chmod +x ~/run_rakuten.sh
```

#### 2. Python3に権限を付与

**重要:** これをしないと自動実行が失敗します

1. **システム設定** > **プライバシーとセキュリティ** を開く
2. **フルディスクアクセス** を選択
3. 🔒 をクリックして管理者パスワードを入力
4. **+** ボタンで以下を追加:
   - `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`
   - `/bin/bash`

#### 3. 自動実行の登録

```bash
# plistファイルをコピー
cp com.rakuten.ranking.tracker.plist ~/Library/LaunchAgents/

# launchdに登録
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.rakuten.ranking.tracker.plist

# 動作確認（テスト実行）
launchctl kickstart -k gui/$(id -u)/com.rakuten.ranking.tracker
```

---

### 🪟 Windows の場合

#### 1. タスクスケジューラに登録

**方法A: XMLファイルをインポート（簡単）**

1. **タスクスケジューラ** を開く（`Win + R` → `taskschd.msc`）
2. 右側の「タスクのインポート」をクリック
3. `RakutenRankingTracker.xml` を選択
4. **アクション** タブで、パスを確認・修正:
   ```
   cd /d "%USERPROFILE%\Documents\楽天自動化ツール\03_検索順位チェック" && run_tracker.bat
   ```
5. 「OK」をクリック

**方法B: 手動で設定**

1. **タスクスケジューラ** を開く
2. 「基本タスクの作成」をクリック
3. 名前: `楽天順位チェック`
4. トリガー: **毎週** → 月〜金にチェック → 時刻 **9:30**
5. 操作: **プログラムの起動**
6. プログラム: `cmd.exe`
7. 引数:
   ```
   /c "cd /d "%USERPROFILE%\Documents\楽天自動化ツール\03_検索順位チェック" && run_tracker.bat"
   ```

#### 2. テスト実行

タスクスケジューラで作成したタスクを右クリック → **実行**

---

### 実行スケジュール

- **月曜日〜金曜日 9:30**に自動実行
- **Mac**: `com.rakuten.ranking.tracker.plist`の`StartCalendarInterval`を編集
- **Windows**: タスクスケジューラで直接変更

---

## 📁 ファイル構成

```
.
├── README.md                          # このファイル
├── rakuten_multi_tracker.py           # メインプログラム
├── requirements.txt                   # 必要なパッケージ
├── .gitignore                         # 機密情報除外設定
├── credentials.json                   # Google認証情報（要作成）
│
├── run_tracker.sh                     # Mac用実行スクリプト
├── com.rakuten.ranking.tracker.plist  # Mac用自動実行設定
│
├── run_tracker.bat                    # Windows用実行スクリプト
└── RakutenRankingTracker.xml          # Windows用タスク設定
```

---

## 📝 使い方

### キーワードの追加・変更

`rakuten_multi_tracker.py`の`KEYWORDS_PRODUCTS`を編集：

```python
KEYWORDS_PRODUCTS = [
    ("新しいキーワード", "product_id"),
    ("別のキーワード", "product_id_2"),
]
```

### 手動実行

**Mac:**
```bash
python3 rakuten_multi_tracker.py
```

**Windows (PowerShell):**
```powershell
python rakuten_multi_tracker.py
```

### ログの確認

**Mac:**
```bash
# 実行ログ
tail -f ~/rakuten_launchd.log

# 詳細ログ
tail -f ranking_tracker.log
```

**Windows (PowerShell):**
```powershell
# 実行ログ
Get-Content -Path $env:USERPROFILE\rakuten_launchd.log -Tail 50 -Wait

# 詳細ログ
Get-Content -Path ranking_tracker.log -Tail 50 -Wait
```

---

## 🔧 トラブルシューティング

### Mac の場合

#### ❌ 自動実行されない

**原因:** Python3に権限がない

**解決策:**
1. システム設定 > プライバシーとセキュリティ > フルディスクアクセス
2. Python3を追加（上記の手順2を参照）

#### ❌ "Operation not permitted" エラー

**原因:** 同上

**解決策:** Python3とbashに権限を付与

#### 動作確認方法

```bash
# 登録状態を確認
launchctl list | grep rakuten

# 詳細を確認
launchctl print gui/$(id -u)/com.rakuten.ranking.tracker

# 手動テスト
launchctl kickstart -k gui/$(id -u)/com.rakuten.ranking.tracker
```

---

### Windows の場合

#### ❌ 自動実行されない

**原因:** タスクが無効になっている、またはパスが間違っている

**解決策:**
1. タスクスケジューラを開く
2. タスクを右クリック → **プロパティ**
3. **アクション** タブでパスを確認
4. **全般** タブで「有効」にチェック

#### ❌ Pythonが見つからないエラー

**原因:** PythonがPATHに登録されていない

**解決策:**
```powershell
# Pythonのパスを確認
where python

# PATHに追加（システム環境変数）
```

#### 動作確認方法

1. タスクスケジューラを開く
2. タスクを右クリック → **実行**
3. ログファイルを確認: `%USERPROFILE%\rakuten_launchd.log`

---

### 共通の問題

#### ❌ スプレッドシートに書き込めない

**原因:** Google認証が切れている

**解決策:**

**Mac:**
```bash
rm token.json
python3 rakuten_multi_tracker.py  # 再認証
```

**Windows:**
```powershell
Remove-Item token.json
python rakuten_multi_tracker.py  # 再認証
```

---

## 📄 ライセンス

MIT License

---

## 🙋 サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

© 2026 楽天店舗運営自動化プロジェクト
