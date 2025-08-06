#!/usr/bin/env python3
"""
尋找台北市測站
"""
import requests
import json

CWA_API_KEY = "CWA-350559E8-7237-49BA-9260-794B9A578D74"

def find_taipei_stations():
    try:
        weather_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
        params = {
            "Authorization": CWA_API_KEY,
            "format": "JSON"
        }
        
        response = requests.get(weather_url, params=params, timeout=30)
        data = response.json()
        
        stations = data.get("records", {}).get("Station", [])
        
        print("台北相關測站:")
        for station in stations:
            station_name = station.get("StationName", "")
            county = station.get("CountyName", "")
            town = station.get("TownName", "")
            station_id = station.get("StationId", "")
            
            if ("台北" in station_name or "台北" in county or 
                "北市" in county or "信義" in town or "中正" in town):
                
                temp = station.get("AirTemperature", "-")
                humidity = station.get("RelativeHumidity", "-")
                weather = station.get("Weather", "-")
                
                print(f"  {station_name} ({station_id})")
                print(f"    位置: {county} {town}")
                print(f"    溫度: {temp}°C, 濕度: {humidity}%, 天氣: {weather}")
                print()
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    find_taipei_stations()
