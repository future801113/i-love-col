#!/usr/bin/env python3
"""
測試不同的天氣 API
"""
import requests

CWA_API_KEY = "CWA-350559E8-7237-49BA-9260-794B9A578D74"

def test_weather_apis():
    apis = [
        {
            "name": "現在天氣觀測報告",
            "url": "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
        },
        {
            "name": "自動氣象站-氣象觀測資料",
            "url": "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001"
        },
        {
            "name": "局屬氣象站-現在天氣觀測報告",
            "url": "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
        }
    ]
    
    for api in apis:
        print(f"\n🔍 測試 {api['name']}:")
        print("-" * 50)
        
        try:
            params = {
                "Authorization": CWA_API_KEY,
                "format": "JSON"
            }
            
            response = requests.get(api['url'], params=params, timeout=30)
            data = response.json()
            
            if data.get("success") == "true":
                stations = data.get("records", {}).get("Station", [])
                print(f"✅ 成功，共 {len(stations)} 個測站")
                
                # 尋找台北相關測站
                for station in stations:
                    station_name = station.get("StationName", "")
                    if "臺北" in station_name or "台北" in station_name:
                        temp = station.get("AirTemperature", station.get("TEMP", "-"))
                        humidity = station.get("RelativeHumidity", station.get("HUMD", "-"))
                        weather = station.get("Weather", "-")
                        obs_time = station.get("ObsTime", {})
                        
                        print(f"  📍 {station_name}:")
                        print(f"    溫度: {temp}°C")
                        print(f"    濕度: {humidity}%")
                        print(f"    天氣: {weather}")
                        print(f"    觀測時間: {obs_time}")
                        
                        # 顯示所有可用的欄位
                        print(f"    所有欄位: {list(station.keys())}")
                        break
                else:
                    print("  ❌ 未找到台北測站")
            else:
                print(f"  ❌ API 失敗: {data.get('message', '未知錯誤')}")
                
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")

if __name__ == "__main__":
    test_weather_apis()
