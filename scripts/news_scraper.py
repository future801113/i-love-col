#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google News RSS 抓取器
提供台灣新聞資訊整合功能
"""

import feedparser
import json
import requests
from datetime import datetime, timezone, timedelta
import logging
import re
from urllib.parse import urlparse

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsScaper:
    def __init__(self):
        self.news_sources = {
            'google_business': 'https://news.google.com/rss/search?q=財經+OR+金融+OR+股市+OR+經濟&hl=zh-TW&gl=TW&ceid=TW:zh-Hant',
            'google_tech': 'https://news.google.com/rss/search?q=科技+OR+AI+OR+科學+OR+技術&hl=zh-TW&gl=TW&ceid=TW:zh-Hant',
            'google_entertainment': 'https://news.google.com/rss/search?q=娛樂+OR+電影+OR+音樂+OR+明星&hl=zh-TW&gl=TW&ceid=TW:zh-Hant'
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def clean_title(self, title):
        """清理新聞標題，移除不必要的字符"""
        # 移除 HTML 標籤
        title = re.sub(r'<[^>]+>', '', title)
        # 移除多餘空白
        title = re.sub(r'\s+', ' ', title).strip()
        return title
    
    def clean_description(self, description):
        """清理新聞描述"""
        if not description:
            return ""
        
        # 移除 HTML 標籤
        description = re.sub(r'<[^>]+>', '', description)
        # 移除多餘空白和換行
        description = re.sub(r'\s+', ' ', description).strip()
        # 限制長度
        if len(description) > 200:
            description = description[:200] + "..."
        
        return description
    
    def get_domain_name(self, url):
        """從 URL 提取域名"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # 移除 www. 前綴
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return "未知來源"
    
    def fetch_news_from_rss(self, rss_url, category='general'):
        """從 RSS 獲取新聞"""
        try:
            logger.info(f"正在抓取 {category} 新聞: {rss_url}")
            
            # 使用 requests 獲取 RSS 內容
            response = requests.get(rss_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 解析 RSS
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"RSS 解析警告 {category}: {feed.bozo_exception}")
            
            news_items = []
            
            for entry in feed.entries[:15]:  # 限制每個類別最多 15 條新聞
                try:
                    # 處理發布時間
                    published_time = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        # 轉換為台北時間
                        taipei_tz = timezone(timedelta(hours=8))
                        published_time = published_time.astimezone(taipei_tz)
                    
                    # 構建新聞項目
                    news_item = {
                        'title': self.clean_title(entry.title),
                        'link': entry.link,
                        'description': self.clean_description(getattr(entry, 'summary', '')),
                        'published': published_time.strftime('%Y-%m-%d %H:%M') if published_time else '未知時間',
                        'source': self.get_domain_name(entry.link),
                        'category': category
                    }
                    
                    # 只添加有效的新聞項目
                    if news_item['title'] and news_item['link']:
                        news_items.append(news_item)
                        
                except Exception as e:
                    logger.warning(f"處理新聞項目時出錯: {e}")
                    continue
            
            logger.info(f"成功抓取 {category} 新聞 {len(news_items)} 條")
            return news_items
            
        except requests.RequestException as e:
            logger.error(f"網路請求錯誤 {category}: {e}")
            return []
        except Exception as e:
            logger.error(f"抓取 {category} 新聞時出錯: {e}")
            return []
    
    def fetch_all_news(self):
        """抓取所有類別的新聞"""
        all_news = []
        categories = {
            'google_business': '財經',
            'google_tech': '科技',
            'google_entertainment': '娛樂'
        }
        
        for source_key, category_name in categories.items():
            if source_key in self.news_sources:
                news_items = self.fetch_news_from_rss(
                    self.news_sources[source_key], 
                    category_name
                )
                all_news.extend(news_items)
        
        # 按發布時間排序（最新的在前）
        all_news.sort(key=lambda x: x['published'], reverse=True)
        
        return all_news
    
    def save_news_to_json(self, output_path='../news.json'):
        """保存新聞到 JSON 檔案"""
        try:
            news_data = self.fetch_all_news()
            
            # 構建輸出數據
            output = {
                'last_updated': datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S'),
                'total_count': len(news_data),
                'categories': list(set([item['category'] for item in news_data])),
                'news': news_data
            }
            
            # 保存到檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            logger.info(f"新聞資料已保存到 {output_path}，共 {len(news_data)} 條")
            return True
            
        except Exception as e:
            logger.error(f"保存新聞資料時出錯: {e}")
            return False

def main():
    """主函數"""
    scraper = NewsScaper()
    
    # 測試單一 RSS 源
    print("=== 測試 Google News 財經 RSS ===")
    business_news = scraper.fetch_news_from_rss(
        scraper.news_sources['google_business'], 
        '財經'
    )
    
    print(f"抓取到 {len(business_news)} 條財經新聞")
    if business_news:
        print("最新財經新聞:")
        for i, news in enumerate(business_news[:3], 1):
            print(f"{i}. {news['title']}")
            print(f"   來源: {news['source']} | 時間: {news['published']}")
            print(f"   描述: {news['description'][:50]}...")
            print()
    
    # 保存所有新聞
    print("=== 保存完整新聞資料 ===")
    success = scraper.save_news_to_json()
    if success:
        print("✅ 新聞資料保存成功")
    else:
        print("❌ 新聞資料保存失敗")

if __name__ == "__main__":
    main()
