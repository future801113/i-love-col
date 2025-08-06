#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中央氣象署 API 除錯腳本
"""

import requests
import json

CWA_API_KEY = "CWA-350559E8-7237-49BA-9260-794B9A578D74"
CWA_BASE_URL = "https://opendata.cwa.gov.tw/api"

def debug_weather_api():
    try:
        weather_url = f"{CWA_BASE_URL}/v1/rest/datastore/O-A0003-001"
        params = {
            "Authorization": CWA_API_KEY,
            "format": "JSON"
        }
        
        print("正在測試 API...")
        response = requests.get(weather_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        print("API 回應結構:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000] + "...")
        
        # 檢查 records 結構
        records = data.get("records", {})
        print(f"\nrecords 類型: {type(records)}")
        print(f"records 鍵值: {records.keys() if isinstance(records, dict) else 'N/A'}")
        
        # 尋找測站資料
        if isinstance(records, dict):
            stations = records.get("Station", [])
            print(f"\n測站數量: {len(stations)}")
            if stations:
                first_station = stations[0]
                print(f"第一個測站: {first_station.get('StationName')}")
                print(f"測站 ID: {first_station.get('StationId')}")
                
                weather_elements = first_station.get("WeatherElement", [])
                print(f"天氣元素數量: {len(weather_elements)}")
                for elem in weather_elements[:5]:  # 只顯示前5個
                    print(f"  - {elem.get('ElementName')}: {elem.get('ElementValue')}")
        
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    debug_weather_api()
