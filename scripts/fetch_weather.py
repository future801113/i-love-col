#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中央氣象署天氣資料抓取器
自動抓取台北市即時天氣資訊並生成 JSON 檔案供前端使用

Author: GitHub Copilot Assistant
Date: 2025-08-06
"""

import requests
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 載入環境變數
def load_env():
    """載入 .env 檔案中的環境變數"""
    # 先嘗試父目錄的 .env（本地開發環境）
    env_path = Path(__file__).parent.parent / '.env'
    
    # 如果找不到，嘗試當前工作目錄的 .env（GitHub Actions 環境）
    if not env_path.exists():
        env_path = Path.cwd() / '.env'
    
    if not env_path.exists():
        raise FileNotFoundError(
            f"找不到 .env 檔案於 {Path(__file__).parent.parent / '.env'} 或 {Path.cwd() / '.env'}\n"
            "請複製 .env.example 為 .env 並填入您的 API Key"
        )
    
    print(f"📁 載入環境設定檔: {env_path}")
    
    env_vars = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

# 載入設定
env_vars = load_env()

# 中央氣象署 API 設定
CWA_API_KEY = env_vars.get('CWA_API_KEY')
if not CWA_API_KEY or CWA_API_KEY == 'YOUR_API_KEY_HERE':
    raise ValueError(
        "請在 .env 檔案中設定有效的 CWA_API_KEY\n"
        "註冊網址：https://opendata.cwa.gov.tw/"
    )
CWA_BASE_URL = "https://opendata.cwa.gov.tw/api"

# 台北市天氣觀測站代碼
TAIPEI_STATION_ID = "467490"  # 台北測站

# 天氣圖示對應表
WEATHER_ICONS = {
    "晴天": "☀️",
    "多雲": "⛅",
    "陰天": "☁️",
    "陰": "☁️",
    "雨": "🌧️",
    "雷雨": "⛈️",
    "雪": "❄️",
    "霧": "🌫️",
    "晴時多雲": "🌤️",
    "多雲時晴": "⛅",
    "多雲時陰": "☁️",
    "陰時多雲": "☁️"
}

def get_taipei_weather():
    """
    抓取台北市即時天氣資料
    """
    try:
        # 抓取現在天氣觀測報告
        weather_url = f"{CWA_BASE_URL}/v1/rest/datastore/O-A0003-001"
        params = {
            "Authorization": CWA_API_KEY,
            "format": "JSON"
        }
        
        print(f"正在抓取台北市天氣資料...")
        response = requests.get(weather_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print(f"🔍 API 回應狀態: {data.get('success')}")
        
        if data.get("success") != "true":
            raise Exception(f"API 回應錯誤: {data.get('message', '未知錯誤')}")
        
        records = data.get("records", {})
        stations = records.get("Station", [])
        
        if not stations:
            raise Exception("無法取得天氣觀測資料")
        
        # 尋找台北市的測站
        taipei_station = None
        print("🔍 搜尋台北地區測站...")
        for station in stations:
            station_name = station.get("StationName", "")
            county_name = station.get("CountyName", "")
            town_name = station.get("TownName", "")
            
            # 尋找台北市相關測站 - 優先順序：臺北 > 大安森林 > 文化大學 > 臺灣大學 > 淡水
            if station_name == "臺北":
                taipei_station = station
                print(f"🎯 找到台北主測站: {station_name}")
                break
            elif station_name == "大安森林" and not taipei_station:
                taipei_station = station
                print(f"🎯 找到台北測站: {station_name}")
            elif station_name == "文化大學" and not taipei_station:
                taipei_station = station
                print(f"🎯 找到台北測站: {station_name}")
            elif station_name == "臺灣大學" and not taipei_station:
                taipei_station = station
                print(f"🎯 找到台北測站: {station_name}")
            elif not taipei_station and ("陽明山" in station_name or "淡水" in station_name):
                taipei_station = station
                print(f"🎯 找到台北附近測站: {station_name}")
        
        if not taipei_station:
            # 如果找不到台北測站，使用第一個有資料的測站
            for station in stations:
                temp = station.get("AirTemperature", "-")
                if temp and temp != "-":
                    taipei_station = station
                    print(f"⚠️ 使用有資料的測站: {station.get('StationName', '未知測站')}")
                    break
            
        if not taipei_station:
            taipei_station = stations[0]
            print(f"⚠️ 使用第一個測站: {taipei_station.get('StationName', '未知測站')}")
        
        # 解析天氣資料 - 新的API格式在 WeatherElement 物件中
        weather_element = taipei_station.get("WeatherElement", {})
        geo_info = taipei_station.get("GeoInfo", {})
        
        temperature = 0
        humidity = 0
        weather_desc = "晴天"
        
        # 溫度
        if "AirTemperature" in weather_element:
            try:
                temp_value = weather_element["AirTemperature"]
                if temp_value and temp_value != "-":
                    temperature = float(temp_value)
            except (ValueError, TypeError):
                temperature = 0
        
        # 濕度
        if "RelativeHumidity" in weather_element:
            try:
                humidity_value = weather_element["RelativeHumidity"]
                if humidity_value and humidity_value != "-":
                    humidity = float(humidity_value)
            except (ValueError, TypeError):
                humidity = 0
        
        # 天氣狀況
        if "Weather" in weather_element:
            weather_value = weather_element["Weather"]
            if weather_value and weather_value != "-":
                weather_desc = str(weather_value)
        
        # 取得天氣圖示
        weather_icon = "🌤️"
        for key, icon in WEATHER_ICONS.items():
            if key in weather_desc:
                weather_icon = icon
                break
        
        # 台灣時間 (UTC+8)
        taiwan_tz = timezone(timedelta(hours=8))
        current_time = datetime.now(taiwan_tz)
        
        weather_info = {
            "location": "台北市中山區",
            "station": taipei_station.get("StationName", "台北"),
            "county": geo_info.get("CountyName", ""),
            "town": geo_info.get("TownName", ""),
            "temperature": temperature,
            "humidity": humidity,
            "weather": weather_desc,
            "icon": weather_icon,
            "wind_speed": weather_element.get("WindSpeed", "-"),
            "wind_direction": weather_element.get("WindDirection", "-"),
            "air_pressure": weather_element.get("AirPressure", "-"),
            "uv_index": weather_element.get("UVIndex", "-"),
            "precipitation": weather_element.get("Now", {}).get("Precipitation", "-"),
            "visibility": weather_element.get("VisibilityDescription", "-"),
            "sunshine_duration": weather_element.get("SunshineDuration", "-"),
            "daily_high": weather_element.get("DailyExtreme", {}).get("DailyHigh", {}).get("TemperatureInfo", {}).get("AirTemperature", "-"),
            "daily_low": weather_element.get("DailyExtreme", {}).get("DailyLow", {}).get("TemperatureInfo", {}).get("AirTemperature", "-"),
            "obs_time": taipei_station.get("ObsTime", {}).get("DateTime", ""),
            "update_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": current_time.isoformat(),
            "status": "success"
        }
        
        print(f"✅ 成功取得天氣資料: {temperature}°C, {weather_desc} ({taipei_station.get('StationName')})")
        return weather_info
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 網路請求錯誤: {e}")
        return create_error_response(f"網路請求失敗: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析錯誤: {e}")
        return create_error_response(f"資料格式錯誤: {str(e)}")
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return create_error_response(f"抓取失敗: {str(e)}")

def get_taipei_forecast():
    """
    抓取台北市天氣預報
    """
    try:
        # 抓取台北市未來3天天氣預報
        forecast_url = f"{CWA_BASE_URL}/v1/rest/datastore/F-D0047-061"
        params = {
            "Authorization": CWA_API_KEY,
            "format": "JSON"
        }
        
        print(f"正在抓取台北市天氣預報...")
        response = requests.get(forecast_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("success") != "true":
            print(f"⚠️ 預報資料取得失敗: {data.get('message', '未知錯誤')}")
            return None
        
        records = data.get("records", {})
        locations = records.get("locations", [])
        
        if not locations:
            print("⚠️ 無法取得台北市天氣預報")
            return None
            
        location = locations[0]
        districts = location.get("location", [])
        
        if not districts:
            print("⚠️ 無法取得預報資料")
            return None
        
        # 取得中正區的預報（作為台北市代表）
        district = districts[0]
        weather_elements = district.get("weatherElement", [])
        
        forecast_data = {}
        for element in weather_elements:
            element_name = element.get("elementName")
            if element_name in ["Wx", "T", "RH"]:  # 天氣現象、溫度、濕度
                times = element.get("time", [])
                if times:
                    forecast_data[element_name] = times[0].get("elementValue", [{}])[0].get("value", "")
        
        print(f"✅ 成功取得預報資料")
        return {
            "forecast_weather": forecast_data.get("Wx", ""),
            "forecast_temp": forecast_data.get("T", ""),
            "forecast_humidity": forecast_data.get("RH", "")
        }
        
    except Exception as e:
        print(f"⚠️ 預報資料抓取失敗: {e}")
        return None

def create_error_response(error_msg):
    """
    建立錯誤回應
    """
    taiwan_tz = timezone(timedelta(hours=8))
    current_time = datetime.now(taiwan_tz)
    
    return {
        "location": "台北市中山區",
        "station": "台北",
        "temperature": 0,
        "humidity": 0,
        "weather": "資料取得失敗",
        "icon": "❌",
        "update_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": current_time.isoformat(),
        "status": "error",
        "error": error_msg
    }

def save_weather_data(weather_data, forecast_data=None):
    """
    儲存天氣資料到 JSON 檔案
    """
    try:
        output_data = weather_data.copy()
        
        # 加入預報資料（如果有的話）
        if forecast_data:
            output_data.update(forecast_data)
        
        # 確保輸出目錄存在 - 根據執行環境決定輸出路徑
        if Path(__file__).parent.name == 'scripts':
            # 在 scripts 目錄下執行，輸出到父目錄（本地開發）
            output_file = Path(__file__).parent.parent / "weather.json"
        else:
            # 在根目錄執行（GitHub Actions）
            output_file = Path.cwd() / "weather.json"
        
        print(f"💾 輸出檔案路徑: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 天氣資料已儲存到 {output_file}")
        print(f"📊 資料內容: {output_data['temperature']}°C, {output_data['weather']}")
        
    except Exception as e:
        print(f"❌ 儲存失敗: {e}")

def main():
    """
    主程式
    """
    print("🌤️ 開始抓取台北市天氣資料...")
    print("=" * 50)
    
    # 抓取即時天氣
    weather_data = get_taipei_weather()
    
    # 抓取天氣預報
    forecast_data = get_taipei_forecast()
    
    # 儲存資料
    save_weather_data(weather_data, forecast_data)
    
    print("=" * 50)
    print("🎉 天氣資料抓取完成！")

if __name__ == "__main__":
    main()
