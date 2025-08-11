/**
 * 前端直接解析中央氣象署 RSS 天氣資料
 */

class WeatherRSSParser {
    constructor() {
        // 中央氣象署台北市天氣預報 RSS
        this.rssUrl = 'https://www.cwa.gov.tw/rss/forecast/36_01.xml';
        
        // CORS 代理服務選項
        this.corsProxies = [
            'https://api.allorigins.win/raw?url=',
            'https://cors-anywhere.herokuapp.com/',
            'https://api.codetabs.com/v1/proxy?quest='
        ];
    }

    /**
     * 使用 CORS 代理獲取 RSS 資料
     */
    async fetchRSSWithProxy(proxyIndex = 0) {
        if (proxyIndex >= this.corsProxies.length) {
            throw new Error('所有 CORS 代理都無法使用');
        }

        const proxy = this.corsProxies[proxyIndex];
        const proxyUrl = proxy + encodeURIComponent(this.rssUrl);

        try {
            console.log(`🌐 嘗試使用代理 ${proxyIndex + 1}: ${proxy}`);
            
            const response = await fetch(proxyUrl, {
                method: 'GET',
                headers: {
                    'Accept': 'application/xml, text/xml, */*'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const xmlText = await response.text();
            return this.parseWeatherXML(xmlText);

        } catch (error) {
            console.warn(`代理 ${proxyIndex + 1} 失敗:`, error.message);
            
            // 嘗試下一個代理
            return this.fetchRSSWithProxy(proxyIndex + 1);
        }
    }

    /**
     * 解析天氣 XML 資料
     */
    parseWeatherXML(xmlText) {
        try {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(xmlText, 'text/xml');

            // 檢查解析錯誤
            const parseError = xmlDoc.querySelector('parsererror');
            if (parseError) {
                throw new Error('XML 解析錯誤');
            }

            const items = xmlDoc.querySelectorAll('item');
            const weatherData = [];

            items.forEach(item => {
                const title = item.querySelector('title')?.textContent || '';
                const description = item.querySelector('description')?.textContent || '';
                const pubDate = item.querySelector('pubDate')?.textContent || '';

                // 解析標題中的地區和天氣資訊
                const locationMatch = title.match(/(.+?)(?:今|明|後|一週)/);
                const location = locationMatch ? locationMatch[1].trim() : '台北市';

                // 解析標題中的溫度和天氣狀況（RSS 格式：溫度: 31 ~ 35）
                const tempMatch = title.match(/溫度:\s*(\d+)\s*~\s*(\d+)/);
                const weatherMatch = title.match(/(?:今日白天|白天|晚上)\s*(.+?)\s*溫度/);
                const rainMatch = title.match(/降雨機率:\s*(\d+)%/);

                // 如果標題沒有，嘗試從描述中解析
                let minTemp = tempMatch ? tempMatch[1] : null;
                let maxTemp = tempMatch ? tempMatch[2] : null;
                let weather = weatherMatch ? weatherMatch[1].trim() : null;
                let rainChance = rainMatch ? rainMatch[1] : null;

                // 從描述中補充資訊
                if (!minTemp || !maxTemp) {
                    const descTempMatch = description.match(/溫度:\s*(\d+)\s*~\s*(\d+)/);
                    if (descTempMatch) {
                        minTemp = minTemp || descTempMatch[1];
                        maxTemp = maxTemp || descTempMatch[2];
                    }
                }

                if (!weather) {
                    const descWeatherMatch = description.match(/(?:白天|晚上)\s*(.+?)(?:\s*溫度|\s*<|$)/);
                    if (descWeatherMatch) {
                        weather = descWeatherMatch[1].trim();
                    }
                }

                if (!rainChance) {
                    const descRainMatch = description.match(/降雨機率:\s*(\d+)%/);
                    if (descRainMatch) {
                        rainChance = descRainMatch[1];
                    }
                }

                weatherData.push({
                    location: location,
                    title: title,
                    description: description,
                    pubDate: pubDate,
                    minTemp: tempMatch ? tempMatch[1] : null,
                    maxTemp: tempMatch ? tempMatch[2] : null,
                    weather: weatherMatch ? weatherMatch[1] : null,
                    rainChance: rainMatch ? rainMatch[1] : null
                });
            });

            return weatherData;

        } catch (error) {
            console.error('解析 XML 失敗:', error);
            throw error;
        }
    }

    /**
     * 獲取台北市天氣資料
     */
    async getTaipeiWeather() {
        try {
            const weatherData = await this.fetchRSSWithProxy();
            
            // 尋找台北市相關的天氣資料
            const taipeiWeather = weatherData.find(item => 
                item.location.includes('台北') || 
                item.title.includes('台北')
            );

            if (taipeiWeather) {
                return this.formatWeatherData(taipeiWeather);
            } else {
                // 如果沒找到台北市，使用第一筆資料
                return weatherData.length > 0 ? this.formatWeatherData(weatherData[0]) : null;
            }

        } catch (error) {
            console.error('獲取天氣資料失敗:', error);
            throw error;
        }
    }

    /**
     * 格式化天氣資料
     */
    formatWeatherData(rawData) {
        const weather = rawData.weather || '多雲';
        const icon = this.getWeatherIcon(weather);

        return {
            location: rawData.location || '台北市',
            weather: weather,
            icon: icon,
            minTemp: rawData.minTemp,
            maxTemp: rawData.maxTemp,
            temperature: rawData.maxTemp || '--', // 使用最高溫作為當前溫度
            rainChance: rawData.rainChance,
            humidity: '--', // RSS 中沒有濕度資訊
            updateTime: new Date().toLocaleString('zh-TW'),
            source: 'CWA RSS',
            rawTitle: rawData.title,
            rawDescription: rawData.description
        };
    }

    /**
     * 根據天氣狀況返回對應圖示
     */
    getWeatherIcon(weather) {
        const iconMap = {
            '晴': '☀️',
            '多雲': '⛅',
            '陰': '☁️',
            '雨': '🌧️',
            '雷雨': '⛈️',
            '雪': '❄️',
            '霧': '🌫️',
            '晴時多雲': '🌤️',
            '多雲時晴': '⛅',
            '多雲時陰': '☁️',
            '陰時多雲': '☁️'
        };

        for (const [key, icon] of Object.entries(iconMap)) {
            if (weather.includes(key)) {
                return icon;
            }
        }

        return '🌤️'; // 預設圖示
    }
}

/**
 * 整合到現有的天氣系統
 */
async function loadWeatherDataFromRSS() {
    const weatherParser = new WeatherRSSParser();
    
    try {
        console.log('🌤️ 開始從 RSS 載入天氣資料...');
        
        const weatherData = await weatherParser.getTaipeiWeather();
        
        if (weatherData) {
            console.log('✅ RSS 天氣資料載入成功:', weatherData);
            updateWeatherUI(weatherData);
        } else {
            throw new Error('無法解析天氣資料');
        }

    } catch (error) {
        console.error('❌ RSS 天氣載入失敗:', error);
        
        // 回退到原本的 JSON 方式
        console.log('🔄 回退到 JSON 天氣資料...');
        loadWeatherData();
    }
}

// 導出給全域使用
window.WeatherRSSParser = WeatherRSSParser;
window.loadWeatherDataFromRSS = loadWeatherDataFromRSS;