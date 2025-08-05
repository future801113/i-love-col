# 音樂檔案說明

這個資料夾用來存放網站的背景音樂檔案。

## 支援的格式
- **MP3** (推薦) - 廣泛支援，檔案較小
- **OGG** - 開源格式，音質好
- **WAV** - 無損音質，但檔案較大

## 檔案命名
- 主要背景音樂：`background.mp3` 和 `background.ogg`
- 其他音樂：可以命名為 `music1.mp3`, `music2.mp3` 等

## 如何新增音樂

1. **下載音樂檔案**
   - 確保你有使用權（版權問題）
   - 建議使用無版權音樂或購買版權

2. **轉換格式**（如果需要）
   ```bash
   # 使用 ffmpeg 轉換格式
   ffmpeg -i input.wav output.mp3
   ffmpeg -i input.wav output.ogg
   ```

3. **將檔案放入此資料夾**
   - 主音樂檔案命名為 `background.mp3`
   - 同時提供 OGG 格式以提高相容性

4. **檔案大小建議**
   - 建議每個檔案小於 10MB
   - 如果檔案太大，可以調整品質：
     ```bash
     ffmpeg -i input.mp3 -b:a 128k output.mp3
     ```

## 音樂來源建議
- [Free Music Archive](https://freemusicarchive.org/)
- [Incompetech](https://incompetech.com/)
- [YouTube Audio Library](https://studio.youtube.com/channel/UC.../music)
- [Freesound](https://freesound.org/)

## 注意事項
- 確保音樂檔案的版權合法性
- 建議音量不要太大，避免影響用戶體驗
- 考慮提供音樂開關功能（已實作）
