#!/usr/bin/env python3
"""
發送圖片到 LINE 群組
用法: python3 send_line_image.py <image_url>
"""
import requests
import os
import sys

def send_line_image(image_url):
    """發送圖片到 LINE 群組"""
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    target_id = os.environ.get('LINE_TARGET_ID')
    
    if not token or not target_id:
        print("❌ LINE Bot 設定不完整")
        return False
        
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'to': target_id,
        'messages': [
            {
                'type': 'image',
                'originalContentUrl': image_url,
                'previewImageUrl': image_url
            }
        ]
    }
    
    try:
        print(f"🚀 發送圖片到 LINE: {image_url}")
        response = requests.post('https://api.line.me/v2/bot/message/push', 
                               headers=headers, json=data)
        if response.status_code == 200:
            print("✅ 成功發送組合圖片到 LINE 群組")
            return True
        else:
            print(f"❌ LINE 發送失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ LINE 發送時發生錯誤: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ 使用方法: python3 send_line_image.py <image_url>")
        sys.exit(1)
        
    image_url = sys.argv[1]
    if send_line_image(image_url):
        print("🎉 LINE 訊息發送成功")
        sys.exit(0)
    else:
        print("😞 LINE 訊息發送失敗")
        sys.exit(1)
