#!/usr/bin/env python3
"""
簡化版 Twitter 圖片爬蟲 - GitHub Actions 版本
使用公開的用戶頁面而不是搜尋頁面
"""

import os
import sys
import json
import time
import random
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

class TwitterImageScraperSimple:
    def __init__(self, config_file='config.json', username=None):
        self.config_file = config_file
        self.config = self.load_config()
        self.username = username
        self.images_dir = self.get_images_directory(username)
        self.setup_directories()
        self.driver = None
        
        # LINE Bot 設定 - 支援環境變數
        self.line_config = self.config.get('line_bot', {})
        self.channel_access_token = (
            os.environ.get('LINE_CHANNEL_ACCESS_TOKEN') or 
            self.line_config.get('channel_access_token', '')
        )
        self.target_id = (
            os.environ.get('LINE_TARGET_ID') or 
            self.line_config.get('target_id', '')
        )
        self.github_pages_base = self.line_config.get('github_pages_base', 'https://future801113.github.io/i-love-col')
    
    def get_images_directory(self, username):
        """根據使用者名稱決定圖片存放目錄 - GitHub Actions 版本"""
        if username == 'colne_icol':
            return self.config.get('colne_icol_directory', '../colne_icol_images')
        else:
            return self.config.get('images_directory', '../images')
        
    def load_config(self):
        """載入設定檔"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 找不到設定檔: {self.config_file}")
            # 在 GitHub Actions 環境中，提供默認設定
            return {
                "images_directory": "../images",
                "colne_icol_directory": "../colne_icol_images",
                "line_bot": {
                    "github_pages_base": "https://future801113.github.io/i-love-col"
                }
            }
        except json.JSONDecodeError as e:
            print(f"❌ 設定檔格式錯誤: {e}")
            return {}
    
    def setup_directories(self):
        """建立必要的目錄"""
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
            print(f"📁 建立圖片目錄: {self.images_dir}")
    
    def load_blacklist(self):
        """載入黑名單檔案"""
        try:
            blacklist_path = os.path.join(os.path.dirname(self.images_dir), 'images', 'blacklist.json')
            if os.path.exists(blacklist_path):
                with open(blacklist_path, 'r', encoding='utf-8') as f:
                    blacklist_data = json.load(f)
                    return {item['filename'] for item in blacklist_data}
            return set()
        except Exception as e:
            print(f"⚠️  載入黑名單時發生錯誤: {e}")
            return set()
    
    def is_filename_blacklisted(self, filename):
        """檢查檔名是否在黑名單中"""
        blacklist = self.load_blacklist()
        return filename in blacklist
    
    def setup_driver(self):
        """設定 Chrome 瀏覽器驅動 - 強化反爬蟲對抗"""
        chrome_options = Options()
        # GitHub Actions 必需的選項
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 反爬蟲對抗 - 隱藏自動化特徵
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-extensions')
        
        # 使用真實用戶代理（Windows + Chrome）
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        
        # 添加更多瀏覽器特徵使其看起來更像真實用戶
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # 加速頁面載入
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 設定多個隱藏 webdriver 的方式
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-TW', 'zh', 'en']
                    });
                '''
            })
            
            # 添加 headers 模仿真實瀏覽器
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            })
            
            print("✅ Chrome 瀏覽器驅動初始化成功（強化反爬蟲模式）")
            return True
        except Exception as e:
            print(f"❌ Chrome 瀏覽器驅動初始化失敗: {e}")
            return False
    
    def build_nitter_search_url(self, username, start_date=None, end_date=None, nitter_instance="nitter.poast.org"):
        """建立 Nitter 搜尋 URL（支援日期區間）"""
        import urllib.parse
        # 建立搜尋查詢
        if start_date and end_date:
            query = f"from:{username} since:{start_date} until:{end_date}"
        elif start_date:
            query = f"from:{username} since:{start_date}"
        else:
            query = f"from:{username}"
        encoded_query = urllib.parse.quote(query)
        # 加上 f-media=on & e-nativeretweets=on 參數
        return f"https://{nitter_instance}/search?q={encoded_query}&f=tweets&f-media=on&e-nativeretweets=on"
    
    def extract_image_urls(self):
        """提取圖片 URL"""
        image_urls = []
        
        try:
            print("🔍 開始提取圖片 URL...")
            
            # 判斷是否為 Nitter 頁面
            current_url = self.driver.current_url.lower()
            is_nitter = "nitter" in current_url
            
            if is_nitter:
                print("🐦 檢測到 Nitter 頁面，使用 Nitter 選擇器")
                # Nitter 專用選擇器
                selectors = [
                    ".still-image img",
                    ".attachment img",
                    ".gallery-row img",
                    "a.still-image",
                ]
            else:
                print("🔵 使用 Twitter/X 官方選擇器")
                # Twitter/X 官方選擇器
                selectors = [
                    "img[src*='pbs.twimg.com'][src*='media']",
                    "div[data-testid='tweetPhoto'] img",
                    "[data-testid='tweetPhoto'] img",
                    "article img[src*='pbs.twimg.com']",
                    "img[alt*='Image']"
                ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"   使用選擇器 '{selector}' 找到 {len(elements)} 個元素")
                    
                    for element in elements:
                        try:
                            # 對於 Nitter 的 a.still-image 連結，使用 href 屬性
                            if is_nitter and selector == "a.still-image":
                                href = element.get_attribute("href")
                                if href and "/pic/orig/" in href:
                                    if "media%2F" in href:
                                        media_id = href.split("media%2F")[1].split(".")[0]
                                        large_url = f"https://pbs.twimg.com/media/{media_id}?format=jpg&name=large"
                                        if large_url not in image_urls:
                                            image_urls.append(large_url)
                                            print(f"   ✅ 找到圖片 (from href): {large_url[:80]}...")
                            else:
                                # 一般的 img 元素
                                src = element.get_attribute("src")
                                if src:
                                    if is_nitter:
                                        if "/pic/media%2F" in src:
                                            media_id = src.split("media%2F")[1].split(".")[0].split("%")[0]
                                            large_url = f"https://pbs.twimg.com/media/{media_id}?format=jpg&name=large"
                                            if large_url not in image_urls:
                                                image_urls.append(large_url)
                                                print(f"   ✅ 找到圖片 (from src): {large_url[:80]}...")
                                    else:
                                        # Twitter/X 官方處理
                                        if ("pbs.twimg.com" in src or "pic.twitter.com" in src):
                                            if "?format=" in src or "&name=" in src:
                                                base_url = src.split("?")[0]
                                                large_url = f"{base_url}?format=jpg&name=large"
                                            else:
                                                large_url = src
                                            
                                            if large_url not in image_urls:
                                                image_urls.append(large_url)
                                                print(f"   ✅ 找到圖片: {large_url[:80]}...")
                        except Exception as e:
                            continue
                except Exception as e:
                    print(f"   選擇器執行失敗: {e}")
                    continue
            
            # 去重並限制數量
            unique_urls = list(dict.fromkeys(image_urls))
            print(f"🖼️  總共找到 {len(unique_urls)} 張唯一圖片")
            
            return unique_urls
            
        except Exception as e:
            print(f"❌ 提取圖片 URL 時發生錯誤: {e}")
            return []
    
    def download_image(self, url, filename):
        """下載圖片"""
        try:
            # 排除指定的 domain
            if url.startswith("https://future801113.github.io/i-love-col/"):
                print(f"   ⏭️  跳過排除的 domain: {url[:80]}...")
                return None
            
            # 更完整的 headers 模仿真實瀏覽器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Referer': 'https://twitter.com/',
                'Sec-Ch-Ua': '"Google Chrome";v="131"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            }
            
            print(f"   📥 開始下載: {url[:80]}...")
            print(f"   📁 目標目錄: {self.images_dir}")
            print(f"   📁 絕對路徑: {os.path.abspath(self.images_dir)}")
            
            # 隨機延遲下載
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            file_path = os.path.join(self.images_dir, filename)
            print(f"   💾 完整檔案路徑: {file_path}")
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # 驗證檔案是否真的存在
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"   ✅ 下載成功: {filename} ({file_size} bytes)")
                return file_path
            else:
                print(f"   ❌ 檔案未成功建立: {file_path}")
                return None
            
        except Exception as e:
            print(f"   ❌ 下載失敗: {e}")
            return None
    
    def generate_filename(self, username, index, url_hash=None):
        """生成檔案名稱（包含 URL hash 用於去重），並檢查黑名單"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if url_hash:
            filename = f"{username}_{timestamp}_{url_hash}_{index+1}.jpg"
        else:
            filename = f"{username}_{timestamp}_simple_{index+1}.jpg"
        
        # 檢查是否在黑名單中
        if self.is_filename_blacklisted(filename):
            print(f"   🚫 跳過黑名單檔案: {filename}")
            return None
            
        return filename
    
    def get_existing_image_hashes(self, username):
        """獲取已存在圖片的 URL hash 集合，用於去重"""
        existing_hashes = set()
        
        try:
            if username == 'colne_icol':
                json_path = os.path.join(os.path.dirname(self.images_dir), 'colne_icol_images', 'images.json')
            else:
                json_path = os.path.join(os.path.dirname(self.images_dir), 'images', 'images.json')
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                # 從檔案名稱中提取可能的 URL hash
                for item in existing_data:
                    filename = item.get('filename', '')
                    # 如果檔案名稱包含可識別的 hash，提取它
                    if '_' in filename:
                        parts = filename.split('_')
                        if len(parts) >= 3:
                            # 假設格式是 username_timestamp_hash_index.jpg
                            possible_hash = parts[2] if len(parts) > 3 else parts[-1].split('.')[0]
                            existing_hashes.add(possible_hash)
                    
                    # 也檢查是否有儲存的原始 URL hash
                    if 'url_hash' in item:
                        existing_hashes.add(item['url_hash'])
            
            print(f"📊 {username} 已有 {len(existing_hashes)} 個圖片 hash 記錄")
            return existing_hashes
            
        except Exception as e:
            print(f"⚠️  讀取已存在圖片記錄時發生錯誤: {e}")
            return set()
    
    def generate_url_hash(self, url):
        """為 URL 生成短 hash，用於去重和檔案命名"""
        import hashlib
        # 清理 URL，移除參數
        clean_url = url.split('?')[0].split('#')[0]
        # 生成短 hash
        return hashlib.md5(clean_url.encode()).hexdigest()[:8]
    
    def filter_duplicate_urls(self, image_urls, username):
        """過濾重複的圖片 URL"""
        if not image_urls:
            return []
        
        existing_hashes = self.get_existing_image_hashes(username)
        unique_urls = []
        
        print(f"🔍 檢查 {len(image_urls)} 個圖片 URL 是否重複...")
        
        for url in image_urls:
            url_hash = self.generate_url_hash(url)
            
            if url_hash not in existing_hashes:
                unique_urls.append((url, url_hash))
                print(f"   ✅ 新圖片: {url[:60]}... (hash: {url_hash})")
            else:
                print(f"   ⏭️  跳過重複: {url[:60]}... (hash: {url_hash})")
        
        print(f"📊 過濾結果: {len(unique_urls)} 張新圖片 / {len(image_urls)} 張總圖片")
        return unique_urls
    
    def update_images_json(self, downloaded_files, username, url_hashes=None):
        """更新對應的 images.json 檔案"""
        try:
            if username == 'colne_icol':
                # 為 colne_icol 建立獨立的 JSON 檔案
                json_path = os.path.join(os.path.dirname(self.images_dir), 'colne_icol_images', 'images.json')
                relative_path = 'colne_icol_images'
            else:
                # 原本的 ice_deliverer 使用現有的 JSON
                json_path = os.path.join(os.path.dirname(self.images_dir), 'images', 'images.json')
                relative_path = 'images'
            
            # 載入現有的 JSON 資料
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            # 加入新下載的圖片資訊
            for i, file_path in enumerate(downloaded_files):
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                image_info = {
                    "filename": filename,
                    "url": f"{relative_path}/{filename}",
                    "size": file_size,
                    "uploaded_at": datetime.now().isoformat()
                }
                
                # 如果有 URL hash 資訊，一併儲存
                if url_hashes and i < len(url_hashes):
                    image_info["url_hash"] = url_hashes[i]
                
                existing_data.append(image_info)
            
            # 儲存更新後的 JSON
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ {username} 的圖片清單已更新 (總計 {len(existing_data)} 張圖片)")
            return True
            
        except Exception as e:
            print(f"❌ 更新 {username} 圖片清單時發生錯誤: {e}")
            return False
    
    def scrape_user_media(self, username, num_images=5, start_date=None, end_date=None):
        """從用戶的頁面抓取圖片"""
        if start_date or end_date:
            print(f"🚀 開始從 @{username} 抓取圖片 (日期範圍: {start_date} ~ {end_date})")
        else:
            print(f"🚀 開始從 @{username} 抓取圖片")
        
        if not self.setup_driver():
            return []
        
        try:
            # 嘗試多個可能的 URL（包括 Nitter 鏡像）
            urls_to_try = []
            
            # 如果指定了日期，優先嘗試 Nitter 搜尋功能
            if start_date or end_date:
                print("📅 偵測到日期參數，將優先使用 Nitter 搜尋功能")
                nitter_instances = [
                    "nitter.poast.org",
                    "nitter.it", 
                    "nitter.1d4.us",
                    "nitter.net",
                    "nitter.privacydev.net",
                    "nitter.fediverse.observer"
                ]
                
                for instance in nitter_instances:
                    search_url = self.build_nitter_search_url(username, start_date, end_date, instance)
                    urls_to_try.append(search_url)
            
            # 加入一般的 URL
            urls_to_try.extend([
                # Nitter 鏡像站（/media 結尾，加上 f-media=on&e-nativeretweets=on 參數）
                f"https://nitter.poast.org/{username}/media?f-media=on&e-nativeretweets=on",
                f"https://nitter.it/{username}/media?f-media=on&e-nativeretweets=on",
                f"https://nitter.1d4.us/{username}/media?f-media=on&e-nativeretweets=on",
                f"https://nitter.net/{username}/media?f-media=on&e-nativeretweets=on",
                f"https://nitter.privacydev.net/{username}/media?f-media=on&e-nativeretweets=on",
                # 官方站點
                f"https://x.com/{username}",
                f"https://twitter.com/{username}",
                f"https://x.com/{username}/media",
                f"https://twitter.com/{username}/media"
            ])
            
            image_urls = []  # 初始化變數
            anti_crawl_keywords = ["cloudflare", "attention required", "captcha", "access denied", "verify you are human", "too many requests"]
            
            for url in urls_to_try:
                print(f"🔗 嘗試 URL: {url}")
                
                try:
                    # 隨機延遲（2-5秒）模擬真實用戶
                    random_delay = random.uniform(2, 5)
                    time.sleep(random_delay)
                    
                    self.driver.get(url)
                    
                    # 頁面載入後隨機等待（8-15秒）
                    random_wait = random.uniform(8, 15)
                    time.sleep(random_wait)
                    
                    # 模擬滑動頁面（真實用戶行為）
                    try:
                        self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
                        time.sleep(random.uniform(1, 3))
                    except:
                        pass
                    
                    current_url = self.driver.current_url
                    page_title = self.driver.title
                    print(f"   當前 URL: {current_url}")
                    print(f"   頁面標題: {page_title}")
                    page_source = self.driver.page_source.lower()
                    
                    # 檢查防爬蟲和錯誤訊息
                    if any(k in page_source for k in anti_crawl_keywords):
                        print(f"   ⚠️ 防爬蟲偵測到關鍵字，自動切換下一個鏡像！")
                        continue
                    
                    # 檢查 HTTP 錯誤碼 (403, 404 等) 和其他問題
                    if any(error in page_title for error in ["403", "404", "500", "502", "503"]):
                        print(f"   ⚠️ 服務器返回錯誤: {page_title}，自動切換下一個鏡像！")
                        continue
                    
                    if ("login" not in current_url.lower() and 
                        "signin" not in current_url.lower() and 
                        "suspended" not in page_title.lower() and
                        "error" not in page_title.lower()):
                        print("   ✅ 成功載入頁面")
                        page_length = len(self.driver.page_source)
                        print(f"   頁面內容長度: {page_length} 字元")
                        if page_length > 10000:
                            print("   📷 直接抓取初始載入的圖片內容")
                            image_urls = self.extract_image_urls()
                            if image_urls:
                                print(f"   在 {url} 找到 {len(image_urls)} 張圖片")
                                break
                            else:
                                print(f"   在 {url} 沒有找到圖片，嘗試下一個 URL")
                        else:
                            print(f"   頁面內容太少，可能載入失敗，嘗試下一個 URL")
                    else:
                        print(f"   頁面需要登入或有其他問題，嘗試下一個 URL")
                except Exception as e:
                    print(f"   載入 {url} 時發生錯誤: {e}")
                    continue
            
            if not image_urls:
                print("😔 所有 URL 都沒有找到圖片")
                return []
            
            # 過濾重複的圖片
            unique_url_pairs = self.filter_duplicate_urls(image_urls, username)
            
            if not unique_url_pairs:
                print("😔 所有找到的圖片都已經下載過了")
                return []
            
            # 如果新圖片數量不足，嘗試獲取更多
            if len(unique_url_pairs) < num_images:
                print(f"⚠️  新圖片數量 ({len(unique_url_pairs)}) 少於需求 ({num_images})")
                print(f"📥 將下載所有 {len(unique_url_pairs)} 張新圖片")
                selected_pairs = unique_url_pairs
            else:
                # 隨機選擇要下載的圖片
                selected_pairs = random.sample(unique_url_pairs, num_images)
            
            print(f"🎯 選擇下載 {len(selected_pairs)} 張新圖片")
            
            # 下載圖片
            downloaded_files = []
            url_hashes = []
            
            for i, (url, url_hash) in enumerate(selected_pairs):
                filename = self.generate_filename(username, i, url_hash)
                
                # 如果檔名在黑名單中，跳過這張圖片
                if filename is None:
                    print(f"   ⏭️  跳過黑名單圖片 (index {i})")
                    continue
                    
                file_path = self.download_image(url, filename)
                if file_path:
                    downloaded_files.append(file_path)
                    url_hashes.append(url_hash)
                
                # 隨機延遲
                time.sleep(random.uniform(1, 3))
            
            print(f"✅ 成功下載 {len(downloaded_files)} 張新圖片")
            
            # 更新 JSON 時傳入 URL hashes
            if downloaded_files:
                self.update_images_json(downloaded_files, username, url_hashes)
            
            return downloaded_files
            
        except Exception as e:
            print(f"❌ 抓取過程中發生錯誤: {e}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 瀏覽器已關閉")
    
    def send_images_to_line_group(self, downloaded_files, username):
        """發送剛下載的圖片到 LINE 群組"""
        if not self.channel_access_token or not self.target_id:
            print("⚠️ LINE Bot 設定不完整，跳過 LINE 發送")
            print(f"   Channel Access Token: {'設定' if self.channel_access_token else '未設定'}")
            print(f"   Target ID: {'設定' if self.target_id else '未設定'}")
            return False
        
        if not downloaded_files:
            print("⚠️ 沒有下載的圖片可發送")
            return False
        
        print(f"📱 準備發送 {len(downloaded_files)} 張 {username} 圖片到 LINE 群組...")
        
        headers = {
            'Authorization': f'Bearer {self.channel_access_token}',
            'Content-Type': 'application/json'
        }
        
        messages = []
        
        # 為每張圖片建立訊息
        for i, file_path in enumerate(downloaded_files):
            filename = os.path.basename(file_path)
            
            # 建立 GitHub Pages URL
            if username == 'colne_icol':
                image_url = f"{self.github_pages_base}/colne_icol_images/{filename}"
            elif username == 'daily_combined':
                image_url = f"{self.github_pages_base}/combined_images/{filename}"
            else:
                image_url = f"{self.github_pages_base}/images/{filename}"
            
            print(f"🔧 DEBUG: 圖片 {i+1} URL: {image_url}")
            
            # 測試 URL 是否可訪問
            try:
                test_response = requests.head(image_url, timeout=10)
                print(f"   🧪 URL 測試: HTTP {test_response.status_code}")
                if test_response.status_code != 200:
                    print(f"   ❌ 警告: 圖片 URL 無法訪問 ({test_response.status_code})")
            except Exception as e:
                print(f"   ❌ 警告: 無法測試 URL 訪問性: {e}")
            
            messages.append({
                'type': 'image',
                'originalContentUrl': image_url,
                'previewImageUrl': image_url
            })
        
        # LINE 一次最多發送 5 則訊息
        messages = messages[:5]
        
        data = {
            'to': self.target_id,
            'messages': messages
        }
        
        try:
            print("🚀 發送 LINE API 請求...")
            response = requests.post(
                'https://api.line.me/v2/bot/message/push',
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"📨 LINE API 回應: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 成功發送 {len(messages)} 張 {username} 圖片到 LINE 群組")
                return True
            else:
                print(f"❌ LINE 發送失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ LINE 發送時發生錯誤: {e}")
            return False

def generate_random_date_range(days_span=20):
    """生成隨機的日期區間（20天）"""
    # 隨機選擇一個開始日期（過去一年內）
    today = datetime.now()
    max_days_back = 365  # 最多往前一年
    
    # 隨機選擇開始日期
    random_days_back = random.randint(days_span, max_days_back)
    start_date = today - timedelta(days=random_days_back)
    end_date = start_date + timedelta(days=days_span - 1)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    return start_str, end_str

def daily_scrape_and_send():
    """每日抓圖、提交推送、發送到 LINE 群組 - GitHub Actions 版本
    
    三層回退策略:
    1. 先抓最近三天的圖片
    2. 如果沒有新圖，用原本的隨機邏輯 (隨機20天區間)
    3. 如果還是沒有，使用 combined_images 裡面隨機抓一張
    """
    print("🤖 開始每日抓圖、提交推送、發送到 LINE 群組...")
    print("=" * 50)
    
    accounts = ['ice_deliverer', 'colne_icol']
    num_images_per_account = 2  # 每個帳號抓 2 張用於組合
    
    all_downloaded_files = {}  # 儲存所有下載的檔案
    
    # 內部函數：使用指定日期範圍嘗試抓圖
    def run_scrape_for_dates(start_date, end_date, strategy_name):
        """使用指定日期範圍抓圖"""
        print(f"\n🔄 {strategy_name}")
        temp_files = {}
        
        for account in accounts:
            print(f"   📷 {account}...", end=" ")
            scraper = TwitterImageScraperSimple(username=account)
            downloaded_files = scraper.scrape_user_media(account, num_images_per_account, start_date, end_date)
            
            if downloaded_files:
                print(f"✅ {len(downloaded_files)} 張")
                temp_files[account] = downloaded_files
            else:
                print("😔 無新圖")
                temp_files[account] = []
            
            # 兩個帳號之間等待
            if account != accounts[-1]:
                time.sleep(2)
        
        return temp_files
    
    # 測試 hook: 強制模擬沒有新圖的情況
    if os.environ.get('FORCE_NO_SCRAPE', '').lower() == 'true':
        print("\n🧪 [TEST MODE] FORCE_NO_SCRAPE=true - 模擬沒有下載到新圖片")
        all_downloaded_files = {account: [] for account in accounts}
        total_new_images = 0
        # 直接跳到第3個策略（備用圖片）
        print("\n🎯 策略 3/3: 仍無新圖，使用 combined_images 備用")
    else:
        # 策略 1: 先抓最近三天
        print("\n🎯 策略 1/3: 抓最近三天的圖片")
        today = datetime.now()
        three_days_ago = today - timedelta(days=3)
        start_date = three_days_ago.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        print(f"   日期範圍: {start_date} ~ {end_date}")
        
        all_downloaded_files = run_scrape_for_dates(start_date, end_date, "嘗試抓最近三天")
        total_new_images = sum(len(files) for files in all_downloaded_files.values())
        
        # 策略 2: 如果沒有新圖，用隨機邏輯
        if total_new_images == 0:
            print("\n🎯 策略 2/3: 沒有最近新圖，改用隨機20天區間")
            random_start, random_end = generate_random_date_range()
            print(f"   日期範圍: {random_start} ~ {random_end}")
            
            all_downloaded_files = run_scrape_for_dates(random_start, random_end, "嘗試抓隨機日期範圍")
            total_new_images = sum(len(files) for files in all_downloaded_files.values())
        
        # 策略 3: 如果還是沒有新圖，使用 combined_images 備用
        if total_new_images == 0:
            print("\n🎯 策略 3/3: 仍無新圖，使用 combined_images 備用")
    
    
    # 步驟 2: 建立組合圖片或選擇備用圖片
    print(f"\n🎨 步驟 2/3: 建立組合圖片或選擇備用")
    combined_image_path = None
    backup_image_path = None
    
    if total_new_images > 0:
        # 有新圖片，建立組合圖片
        try:
            from image_combiner import create_combined_from_new_images
            combined_image_path = create_combined_from_new_images(all_downloaded_files)
            
            if combined_image_path:
                print("   ✅ 組合圖片建立成功")
            else:
                print("   ❌ 組合圖片建立失敗")
                
        except ImportError:
            print("   ⚠️ 組合圖片模組不存在，跳過組合圖片建立")
        except Exception as e:
            print(f"   ❌ 建立組合圖片時發生錯誤: {e}")
    else:
        # 沒有新圖片，從 combined_images 隨機選擇備用圖片（排除最新的）
        print("   😔 沒有新圖片，從 combined_images 備用庫隨機選擇...")
        combined_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'combined_images'))
        
        if os.path.exists(combined_dir):
            try:
                image_files = [f for f in os.listdir(combined_dir) 
                              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
                
                if len(image_files) > 1:
                    # 按修改時間排序，排除最新的
                    image_files_with_time = [(f, os.path.getmtime(os.path.join(combined_dir, f))) 
                                            for f in image_files]
                    image_files_with_time.sort(key=lambda x: x[1], reverse=True)
                    
                    # 排除最新的，從剩餘的隨機選擇
                    eligible_images = image_files_with_time[1:]  # 跳過最新的
                    
                    if eligible_images:
                        backup_image = random.choice(eligible_images)[0]
                        backup_image_path = os.path.join(combined_dir, backup_image)
                        print(f"   📸 從組合圖片備用庫隨機選擇（排除最新）: {backup_image}")
                    else:
                        print(f"   ⚠️ 沒有符合條件的備用圖片（只有最新的）")
                        
                elif len(image_files) == 1:
                    # 只有一張，直接使用
                    backup_image = image_files[0]
                    backup_image_path = os.path.join(combined_dir, backup_image)
                    print(f"   📸 備用庫只有一張圖片，直接使用: {backup_image}")
                else:
                    print(f"   ⚠️ combined_images 目錄為空")
                    
            except Exception as e:
                print(f"   ⚠️ 選擇備用圖片時發生錯誤: {e}")
        else:
            print(f"   ⚠️ combined_images 目錄不存在: {combined_dir}")
    
    # 步驟 3: 發送組合圖片到 LINE 群組 (如果未被禁用)
    if os.environ.get('SKIP_LINE_SEND', '').lower() == 'true':
        print(f"\n📱 跳過 LINE 發送 (SKIP_LINE_SEND=true)")
        print(f"\n🎉 每日任務完成！")
        print(f"📊 總計下載 {total_new_images} 張圖片")
        if combined_image_path:
            print(f"🖼️ 已建立組合圖片: {combined_image_path}")
        elif backup_image_path:
            print(f"🖼️ 已選擇備用圖片: {backup_image_path}")
        return True
    
    print(f"\n📱 步驟 3/3: 發送圖片到 LINE 群組")
    
    total_sent = 0
    image_to_send = combined_image_path or backup_image_path
    
    if image_to_send:
        try:
            # 使用第一個帳號的 scraper 來發送圖片
            scraper = TwitterImageScraperSimple(username=accounts[0])
            
            # 決定發送的類型
            send_type = "daily_combined" if combined_image_path else "daily_backup"
            
            # 發送圖片
            if scraper.send_images_to_line_group([image_to_send], send_type):
                if combined_image_path:
                    print("   ✅ 組合圖片已發送到 LINE 群組")
                else:
                    print("   ✅ 備用圖片已發送到 LINE 群組")
                total_sent = 1
            else:
                print("   ❌ 圖片發送失敗")
                total_sent = 0
                
        except Exception as e:
            print(f"   ❌ 發送圖片時發生錯誤: {e}")
            total_sent = 0
    else:
        print("   😔 沒有可發送的圖片（無新圖片，也無備用圖片）")

    print(f"\n🎉 每日任務完成！")
    print(f"📊 總計下載 {total_new_images} 張圖片")
    print(f"📊 總計發送 {total_sent} 張圖片到 LINE 群組")
    if combined_image_path:
        print(f"🖼️ 額外建立了 1 張新組合圖片")
    elif backup_image_path:
        print(f"🖼️ 發送了 1 張備用組合圖片（因為今日無新圖片）")
    
    return total_sent > 0

def main():
    """主函數"""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("使用方法:")
        print("  python web_scraper_simple.py <username> [num_images] [start_date] [end_date]")
        print("  python web_scraper_simple.py daily  # 每日模式：兩個帳號各抓2張並發送到LINE")
        print("\n範例:")
        print("  python web_scraper_simple.py ice_deliverer 5")
        print("  python web_scraper_simple.py ice_deliverer 5 2024-01-01 2024-01-31")
        print("  python web_scraper_simple.py ice_deliverer 5 random  (使用隨機10天區間)")
        print("  python web_scraper_simple.py daily  (每日自動抓圖並發LINE)")
        print("\n支援的帳號：")
        print("  - ice_deliverer")
        print("  - colne_icol")
        return
    
    # 檢查是否為每日模式
    if sys.argv[1].lower() == 'daily':
        daily_scrape_and_send()
        return
    
    username = sys.argv[1]
    
    # 驗證使用者名稱
    valid_usernames = ['ice_deliverer', 'colne_icol']
    if username not in valid_usernames:
        print(f"❌ 不支援的使用者名稱: {username}")
        print(f"✅ 支援的使用者名稱: {', '.join(valid_usernames)}")
        return
    
    num_images = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # 檢查是否使用隨機日期
    if len(sys.argv) > 3 and sys.argv[3].lower() == 'random':
        start_date, end_date = generate_random_date_range()
        print(f"🎲 使用隨機日期區間: {start_date} ~ {end_date}")
    else:
        start_date = sys.argv[3] if len(sys.argv) > 3 else None
        end_date = sys.argv[4] if len(sys.argv) > 4 else None
        # 如果沒有指定日期，默認使用隨機日期
        if not start_date and not end_date:
            start_date, end_date = generate_random_date_range()
            print(f"🎲 默認使用隨機日期區間: {start_date} ~ {end_date}")
    
    scraper = TwitterImageScraperSimple(username=username)
    downloaded_files = scraper.scrape_user_media(username, num_images, start_date, end_date)
    
    if downloaded_files:
        print(f"\n🎉 抓取完成！下載了 {len(downloaded_files)} 張圖片:")
        for file_path in downloaded_files:
            print(f"   📸 {os.path.basename(file_path)}")
        
        # 更新對應的圖片清單
        print(f"\n📝 圖片清單已在下載過程中自動更新")
        
    else:
        print("\n😔 沒有下載任何圖片")

if __name__ == '__main__':
    main()
