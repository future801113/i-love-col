#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查並清理 colne_icol_images/images.json 中的 404 圖片
"""

import json
import requests
import os
from datetime import datetime
import time

def check_image_availability(base_url, filename, timeout=10):
    """檢查圖片是否可用"""
    full_url = f"{base_url}/colne_icol_images/{filename}"
    
    try:
        response = requests.head(full_url, timeout=timeout)
        return response.status_code == 200, response.status_code
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 網路錯誤: {e}")
        return False, "Network Error"

def check_local_file_exists(filename):
    """檢查本地檔案是否存在"""
    file_path = os.path.join("colne_icol_images", filename)
    return os.path.exists(file_path)

def clean_images_json():
    """清理 images.json 中的無效圖片"""
    json_path = "colne_icol_images/images.json"
    
    # 讀取現有的 JSON 資料
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            images_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 找不到檔案: {json_path}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式錯誤: {e}")
        return
    
    print(f"📊 開始檢查 {len(images_data)} 張圖片...")
    print("=" * 60)
    
    # GitHub Pages 基礎 URL
    github_pages_base = "https://future801113.github.io/i-love-col"
    
    valid_images = []
    invalid_images = []
    
    for i, image_info in enumerate(images_data, 1):
        filename = image_info.get("filename", "")
        
        print(f"[{i:3d}/{len(images_data)}] 檢查: {filename}")
        
        # 檢查本地檔案是否存在
        local_exists = check_local_file_exists(filename)
        print(f"   📁 本地檔案: {'存在' if local_exists else '不存在'}")
        
        # 檢查線上圖片是否可用
        is_available, status_code = check_image_availability(github_pages_base, filename)
        print(f"   🌐 線上狀態: {status_code} ({'可用' if is_available else '不可用'})")
        
        # 如果本地檔案存在或線上圖片可用，則保留
        if local_exists or is_available:
            valid_images.append(image_info)
            print(f"   ✅ 保留")
        else:
            invalid_images.append(image_info)
            print(f"   ❌ 移除")
        
        print()
        
        # 避免請求過於頻繁
        time.sleep(0.5)
    
    print("=" * 60)
    print(f"📊 檢查結果:")
    print(f"   ✅ 有效圖片: {len(valid_images)} 張")
    print(f"   ❌ 無效圖片: {len(invalid_images)} 張")
    
    if invalid_images:
        print(f"\n🗑️ 將移除的圖片:")
        for img in invalid_images:
            print(f"   - {img.get('filename', 'Unknown')}")
    
    # 如果有無效圖片，更新 JSON 檔案
    if invalid_images:
        # 備份原始檔案
        backup_path = f"{json_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(images_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 原始檔案已備份至: {backup_path}")
        
        # 寫入清理後的資料
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(valid_images, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已更新 {json_path}，移除了 {len(invalid_images)} 張無效圖片")
    else:
        print(f"\n🎉 所有圖片都是有效的，無需清理！")

def update_scraper_to_exclude_domain():
    """更新爬蟲腳本，排除指定的 domain"""
    scraper_path = "scripts/web_scraper_simple.py"
    
    if not os.path.exists(scraper_path):
        print(f"❌ 找不到爬蟲腳本: {scraper_path}")
        return
    
    print(f"\n🔧 檢查爬蟲腳本是否需要更新...")
    
    # 讀取現有腳本
    with open(scraper_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否已經有排除邏輯
    excluded_domain = "https://future801113.github.io/i-love-col/"
    
    if excluded_domain in content:
        print(f"✅ 爬蟲腳本已經包含排除邏輯")
        return
    
    # 在 download_image 方法中添加 domain 檢查
    old_download_method = '''def download_image(self, url, filename):
        """下載圖片"""
        try:
            headers = {'''
    
    new_download_method = f'''def download_image(self, url, filename):
        """下載圖片"""
        try:
            # 排除指定的 domain
            if url.startswith("{excluded_domain}"):
                print(f"   ⏭️  跳過排除的 domain: {{url[:80]}}...")
                return None
            
            headers = {{'''
    
    if old_download_method in content:
        updated_content = content.replace(old_download_method, new_download_method)
        
        # 備份原始檔案
        backup_path = f"{scraper_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 爬蟲腳本已備份至: {backup_path}")
        
        # 寫入更新後的內容
        with open(scraper_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ 已更新爬蟲腳本，添加了 domain 排除邏輯")
    else:
        print(f"⚠️ 無法找到預期的方法簽名，請手動添加排除邏輯")

def main():
    """主函數"""
    print("🧹 開始清理 colne_icol_images/images.json...")
    print("🎯 目標: 移除 404 圖片，排除指定 domain")
    print("=" * 60)
    
    # 步驟 1: 清理 JSON 中的無效圖片
    clean_images_json()
    
    # 步驟 2: 更新爬蟲腳本排除指定 domain
    update_scraper_to_exclude_domain()
    
    print("\n🎉 清理完成！")

if __name__ == "__main__":
    main()