#!/usr/bin/env python3
"""
圖片組合工具 - GitHub Actions 版本
隨機從 colne_icol_images 和 images 資料夾各選擇 2 張圖片，組合成一張 2x2 格子圖
"""

import os
import random
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests

def get_random_images(folder_path, count=2):
    """從指定資料夾隨機選擇指定數量的圖片"""
    if not os.path.exists(folder_path):
        print(f"❌ 資料夾不存在: {folder_path}")
        return []
    
    # 取得所有 jpg 檔案
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
    
    if len(image_files) < count:
        print(f"⚠️  {folder_path} 只有 {len(image_files)} 張圖片，少於所需的 {count} 張")
        return image_files  # 返回所有可用的圖片
    
    # 隨機選擇
    selected = random.sample(image_files, count)
    print(f"📸 從 {folder_path} 選擇了:")
    for img in selected:
        print(f"   - {img}")
    
    return selected

def resize_image_to_fit(image, target_size):
    """將圖片調整到目標尺寸，保持比例並居中"""
    target_width, target_height = target_size
    
    # 計算縮放比例，保持比例
    width_ratio = target_width / image.width
    height_ratio = target_height / image.height
    scale_ratio = min(width_ratio, height_ratio)
    
    # 新的尺寸
    new_width = int(image.width * scale_ratio)
    new_height = int(image.height * scale_ratio)
    
    # 調整圖片大小
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 建立目標尺寸的白色背景
    result = Image.new('RGB', target_size, 'white')
    
    # 計算居中位置
    x = (target_width - new_width) // 2
    y = (target_height - new_height) // 2
    
    # 貼上圖片
    result.paste(resized_image, (x, y))
    
    return result

def create_combined_image(colne_images, ice_images, output_path):
    """建立 2x2 組合圖片"""
    # 設定每個格子的大小
    cell_width = 400
    cell_height = 400
    border_width = 2
    
    # 計算總尺寸
    total_width = cell_width * 2 + border_width * 3
    total_height = cell_height * 2 + border_width * 3
    
    # 建立白色背景
    combined = Image.new('RGB', (total_width, total_height), 'white')
    draw = ImageDraw.Draw(combined)
    
    # 準備圖片列表 (colne_icol 在上方，ice_deliverer 在下方)
    all_images = []
    all_paths = []
    
    # colne_icol 圖片路徑
    colne_folder = "../colne_icol_images"
    for img_name in colne_images:
        img_path = os.path.join(colne_folder, img_name)
        all_paths.append(img_path)
        all_images.append("colne_icol")
    
    # ice_deliverer 圖片路徑  
    ice_folder = "../images"
    for img_name in ice_images:
        img_path = os.path.join(ice_folder, img_name)
        all_paths.append(img_path)
        all_images.append("ice_deliverer")
    
    # 位置配置 (2x2 格子)
    positions = [
        (border_width, border_width),                           # 左上
        (border_width + cell_width + border_width, border_width), # 右上
        (border_width, border_width + cell_height + border_width), # 左下
        (border_width + cell_width + border_width, border_width + cell_height + border_width) # 右下
    ]
    
    # 處理每張圖片
    for i, (img_path, source) in enumerate(zip(all_paths, all_images)):
        if i >= 4:  # 最多4張圖片
            break
            
        try:
            # 載入並調整圖片
            with Image.open(img_path) as img:
                resized_img = resize_image_to_fit(img, (cell_width, cell_height))
                
                # 貼上圖片
                x, y = positions[i]
                combined.paste(resized_img, (x, y))
                
                # 添加邊框
                draw.rectangle([x-1, y-1, x+cell_width, y+cell_height], outline='lightgray', width=1)
                
                print(f"✅ 已處理: {os.path.basename(img_path)} ({source})")
                
        except Exception as e:
            print(f"❌ 處理圖片失敗: {img_path} - {e}")
    
    # 添加時間戳記
    try:
        # 使用預設字體
        font_size = 16
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 在底部添加時間戳記
        text_y = total_height - 25
        draw.text((10, text_y), f"Generated: {timestamp}", fill='gray')
        
    except Exception as e:
        print(f"⚠️  添加時間戳記失敗: {e}")
    
    # 儲存圖片
    combined.save(output_path, 'JPEG', quality=90)
    print(f"🎉 組合圖片已儲存: {output_path}")
    
    return output_path

def create_combined_from_new_images(downloaded_files_dict):
    """使用新下載的圖片建立組合圖"""
    print("🎨 開始建立今日新圖片組合...")
    
    # 設定路徑 - GitHub Actions 版本
    output_folder = "../combined_images"
    os.makedirs(output_folder, exist_ok=True)
    
    # 從下載的檔案中取得圖片檔名
    colne_images = []
    ice_images = []
    
    # 處理 colne_icol 的圖片
    if 'colne_icol' in downloaded_files_dict:
        colne_files = downloaded_files_dict['colne_icol']
        # 取得檔案名稱（不含路徑）
        colne_images = [os.path.basename(f) for f in colne_files[:2]]  # 最多取2張
        print(f"📸 使用 colne_icol 新圖片: {len(colne_images)} 張")
        for img in colne_images:
            print(f"   - {img}")
    
    # 處理 ice_deliverer 的圖片
    if 'ice_deliverer' in downloaded_files_dict:
        ice_files = downloaded_files_dict['ice_deliverer']
        # 取得檔案名稱（不含路徑）
        ice_images = [os.path.basename(f) for f in ice_files[:2]]  # 最多取2張
        print(f"📸 使用 ice_deliverer 新圖片: {len(ice_images)} 張")
        for img in ice_images:
            print(f"   - {img}")
    
    # 如果沒有足夠的圖片，用隨機選擇補足
    if len(colne_images) < 2:
        print(f"⚠️  colne_icol 新圖片不足，從舊圖片中補足...")
        colne_folder = "../colne_icol_images"
        additional_needed = 2 - len(colne_images)
        additional_images = get_random_images(colne_folder, additional_needed)
        colne_images.extend(additional_images)
    
    if len(ice_images) < 2:
        print(f"⚠️  ice_deliverer 新圖片不足，從舊圖片中補足...")
        ice_folder = "../images"
        additional_needed = 2 - len(ice_images)
        additional_images = get_random_images(ice_folder, additional_needed)
        ice_images.extend(additional_images)
    
    if len(colne_images) == 0 and len(ice_images) == 0:
        print("❌ 沒有找到任何圖片！")
        return None
    
    # 建立輸出檔名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"daily_combined_{timestamp}.jpg"
    output_path = os.path.join(output_folder, output_filename)
    
    # 建立組合圖片
    print(f"\n🔨 建立今日組合圖片...")
    try:
        create_combined_image(colne_images, ice_images, output_path)
        print(f"✅ 今日組合圖片建立成功: {output_filename}")
        return output_path
        
    except Exception as e:
        print(f"❌ 建立組合圖片失敗: {e}")
        return None

def main():
    """主要功能 - 隨機模式"""
    print("🎨 開始建立圖片組合...")
    
    colne_folder = "../colne_icol_images"
    ice_folder = "../images"
    output_folder = "../combined_images"
    
    # 建立輸出資料夾
    os.makedirs(output_folder, exist_ok=True)
    
    # 隨機選擇圖片
    print("\n📸 選擇圖片中...")
    colne_images = get_random_images(colne_folder, 2)
    ice_images = get_random_images(ice_folder, 2)
    
    if len(colne_images) == 0 and len(ice_images) == 0:
        print("❌ 沒有找到任何圖片！")
        return False
    
    # 建立輸出檔名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"combined_{timestamp}.jpg"
    output_path = os.path.join(output_folder, output_filename)
    
    # 建立組合圖片
    print(f"\n🔨 建立組合圖片...")
    try:
        create_combined_image(colne_images, ice_images, output_path)
        
        print(f"\n🎉 圖片組合完成！")
        print(f"📁 檔案位置: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 建立組合圖片失敗: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 測試模式：建立圖片組合")
    
    success = main()
    sys.exit(0 if success else 1)
