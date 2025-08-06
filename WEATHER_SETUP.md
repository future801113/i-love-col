# 天氣功能設定說明

## 本地開發設定

1. 複製環境設定檔：
   ```bash
   cp .env.example .env
   ```

2. 編輯 `.env` 檔案，填入您的中央氣象署 API Key：
   ```
   CWA_API_KEY=您的API_KEY
   ```

3. 註冊 API Key：
   - 前往 [中央氣象署開放資料平台](https://opendata.cwa.gov.tw/)
   - 註冊帳號並取得 API Key
   - 將 API Key 填入 `.env` 檔案

## GitHub Actions 設定

為了讓 GitHub Actions 自動更新天氣資料，請設定 Repository Secrets：

1. 前往 GitHub Repository 設定頁面
2. 點選 `Settings` → `Secrets and variables` → `Actions`
3. 點選 `New repository secret`
4. 設定：
   - Name: `CWA_API_KEY`
   - Secret: 您的中央氣象署 API Key

## 測試

執行天氣抓取腳本：
```bash
cd scripts
python fetch_weather.py
```

成功後會在根目錄產生 `weather.json` 檔案。

## 安全注意事項

- `.env` 檔案已被加入 `.gitignore`，不會上傳到 GitHub
- 請勿在程式碼中直接寫入 API Key
- 使用 GitHub Secrets 來管理敏感資訊
