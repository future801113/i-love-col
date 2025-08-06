#!/usr/bin/env python3
"""
檢查台北測站的詳細資料結構
"""
import requests
import json

CWA_API_KEY = "CWA-350559E8-7237-49BA-9260-794B9A578D74"

def check_taipei_station_detail():
    try:
        weather_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
        params = {
            "Authorization": CWA_API_KEY,
            "format": "JSON"
        }
        
        response = requests.get(weather_url, params=params, timeout=30)
        data = response.json()
        
        stations = data.get("records", {}).get("Station", [])
        
        for station in stations:
            if station.get("StationName") == "臺北":
                print("🎯 台北測站詳細資料:")
                print(json.dumps(station, indent=2, ensure_ascii=False))
                break
        else:
            print("❌ 未找到台北測站")
            
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    check_taipei_station_detail()
