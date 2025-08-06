#!/usr/bin/env python3
"""
列出所有測站
"""
import requests

CWA_API_KEY = "CWA-350559E8-7237-49BA-9260-794B9A578D74"

def list_all_stations():
    try:
        weather_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
        params = {
            "Authorization": CWA_API_KEY,
            "format": "JSON"
        }
        
        response = requests.get(weather_url, params=params, timeout=30)
        data = response.json()
        
        stations = data.get("records", {}).get("Station", [])
        
        print(f"總共 {len(stations)} 個測站:")
        print("-" * 80)
        
        for i, station in enumerate(stations[:20]):  # 只顯示前20個
            station_name = station.get("StationName", "")
            county = station.get("CountyName", "")
            town = station.get("TownName", "")
            station_id = station.get("StationId", "")
            
            temp = station.get("AirTemperature", "-")
            humidity = station.get("RelativeHumidity", "-")
            weather = station.get("Weather", "-")
            
            print(f"{i+1:2d}. {station_name} ({station_id})")
            print(f"    位置: {county} {town}")
            print(f"    溫度: {temp}°C, 濕度: {humidity}%, 天氣: {weather}")
            print()
            
        print("... (顯示前20個測站)")
        
        # 特別尋找可能的台北測站
        print("\n🔍 搜尋包含以下關鍵字的測站:")
        keywords = ["台北", "臺北", "北市", "信義", "中正", "大安", "松山", "萬華", "中山", "士林"]
        
        for keyword in keywords:
            matching = [s for s in stations if keyword in s.get("StationName", "") or 
                       keyword in s.get("CountyName", "") or keyword in s.get("TownName", "")]
            if matching:
                print(f"\n關鍵字 '{keyword}' 找到 {len(matching)} 個測站:")
                for station in matching:
                    temp = station.get("AirTemperature", "-")
                    humidity = station.get("RelativeHumidity", "-")
                    print(f"  - {station.get('StationName')} ({station.get('CountyName')} {station.get('TownName')}) 溫度:{temp}°C")
                    
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    list_all_stations()
