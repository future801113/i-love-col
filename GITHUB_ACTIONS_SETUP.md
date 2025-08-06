# GitHub Actions 自動天氣更新設定教學

## 📋 概述

本專案使用 GitHub Actions 來自動抓取台北市天氣資料並更新到網站上。設定完成後，天氣資料會每 30 分鐘自動更新一次。

## 🔧 設定步驟

### 1. 設定 GitHub Repository Secrets

為了安全地儲存 API Key，我們需要在 GitHub Repository 中設定 Secrets：

1. **進入 Repository 設定頁面**
   - 前往你的 GitHub Repository 主頁
   - 點選上方的 `Settings` 標籤

2. **進入 Secrets 設定**
   - 在左側邊欄中找到 `Secrets and variables`
   - 點選 `Actions`

3. **新增 Secret**
   - 點選 `New repository secret` 按鈕
   - 填入以下資訊：
     ```
     Name: CWA_API_KEY
     Secret: 你的中央氣象署 API Key
     ```
   - 點選 `Add secret` 儲存

### 2. 確認 GitHub Actions 檔案

確認以下檔案已存在於你的 Repository 中：
```
.github/workflows/fetch_weather.yml
```

### 3. 啟用 GitHub Actions

1. **檢查 Actions 權限**
   - 在 Repository 設定中找到 `Actions` → `General`
   - 確認 `Actions permissions` 設定為 `Allow all actions and reusable workflows`

2. **確認工作流程權限**
   - 在同一頁面找到 `Workflow permissions`
   - 選擇 `Read and write permissions`
   - 勾選 `Allow GitHub Actions to create and approve pull requests`

### 4. 手動觸發測試（可選）

1. **前往 Actions 頁面**
   - 在 Repository 主頁點選 `Actions` 標籤

2. **找到工作流程**
   - 在左側邊欄中找到 `更新天氣資料`

3. **手動執行**
   - 點選工作流程名稱
   - 點選 `Run workflow` 下拉選單
   - 點選 `Run workflow` 按鈕

## 📊 執行結果確認

### 成功指標
- ✅ GitHub Actions 執行狀態顯示綠色勾勾
- ✅ Repository 中出現更新的 `weather.json` 檔案
- ✅ 網站上的天氣資訊正常顯示

### 常見問題排解

#### 問題：Actions 執行失敗
**可能原因：**
- API Key 設定錯誤
- GitHub 權限不足
- API 請求限制

**解決方法：**
1. 檢查 Secret 名稱是否為 `CWA_API_KEY`
2. 確認 API Key 是否正確
3. 檢查 Actions 權限設定

#### 問題：天氣資料沒有更新
**可能原因：**
- 中央氣象署 API 暫時無法存取
- 網路連線問題

**解決方法：**
1. 查看 Actions 執行日誌
2. 手動重新執行工作流程

## ⏰ 自動執行時間表

**執行頻率：** 每 30 分鐘一次  
**執行時間：** UTC 時間每小時的 00 分和 30 分  
**台灣時間：** 每小時的 08 分和 38 分（UTC+8）

**範例時間表：**
- 00:08, 00:38, 01:08, 01:38...
- 12:08, 12:38, 13:08, 13:38...

## 🔍 監控與維護

### 檢查執行狀態
1. 定期查看 Actions 頁面確認執行狀態
2. 關注是否有執行失敗的情況
3. 檢查網站天氣資料是否正常更新

### 維護建議
- **每月檢查一次** Actions 執行狀態
- **API Key 到期前** 更新 Secret 設定
- **遇到問題時** 查看詳細執行日誌

## 📝 備註

- **API 使用限制：** 中央氣象署 API 有請求次數限制，目前設定的頻率在安全範圍內
- **資料更新延遲：** 氣象資料可能有 10-20 分鐘的延遲，這是正常現象
- **停用方法：** 如需停用自動更新，可以在 Actions 設定中停用對應的工作流程

## 🆘 需要協助？

如果在設定過程中遇到問題，可以：
1. 檢查本文件的常見問題排解
2. 查看 GitHub Actions 的執行日誌
3. 確認 API Key 是否有效

---

**設定完成後，你的網站就會自動顯示最新的台北市天氣資訊！** 🌤️
