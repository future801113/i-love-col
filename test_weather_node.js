// Node.js 環境下測試天氣 RSS 解析
const https = require('https');
const { JSDOM } = require('jsdom');

// 模擬瀏覽器環境
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
    url: 'http://localhost:8000',
    pretendToBeVisual: true,
    resources: 'usable'
});

global.window = dom.window;
global.document = dom.window.document;
global.DOMParser = dom.window.DOMParser;
global.fetch = require('node-fetch');

// 載入我們的天氣解析器
const fs = require('fs');
const weatherCode = fs.readFileSync('weather_rss_frontend.js', 'utf8');
eval(weatherCode);

async function testWeatherParsing() {
    console.log('🌤️ 開始測試天氣 RSS 解析...');
    
    try {
        const parser = new WeatherRSSParser();
        console.log('✅ WeatherRSSParser 初始化成功');
        
        // 直接獲取 RSS 資料進行測試
        const rssUrl = 'https://www.cwa.gov.tw/rss/forecast/36_01.xml';
        
        console.log('📡 正在獲取 RSS 資料...');
        const response = await fetch(rssUrl);
        const xmlText = await response.text();
        
        console.log('📊 RSS 資料長度:', xmlText.length);
        console.log('📋 RSS 前 200 字元:', xmlText.substring(0, 200));
        
        // 解析 XML
        console.log('🔍 開始解析 XML...');
        const weatherData = parser.parseWeatherXML(xmlText);
        
        console.log('📊 解析結果數量:', weatherData.length);
        
        if (weatherData.length > 0) {
            console.log('\n🎯 第一筆資料:');
            console.log('   標題:', weatherData[0].title);
            console.log('   描述:', weatherData[0].description);
            console.log('   地點:', weatherData[0].location);
            console.log('   最低溫:', weatherData[0].minTemp);
            console.log('   最高溫:', weatherData[0].maxTemp);
            console.log('   天氣:', weatherData[0].weather);
            console.log('   降雨機率:', weatherData[0].rainChance);
            
            // 格式化資料
            const formattedData = parser.formatWeatherData(weatherData[0]);
            console.log('\n🎨 格式化後的資料:');
            console.log('   地點:', formattedData.location);
            console.log('   溫度:', formattedData.temperature);
            console.log('   天氣:', formattedData.weather);
            console.log('   圖示:', formattedData.icon);
            console.log('   降雨機率:', formattedData.rainChance);
            console.log('   來源:', formattedData.source);
        }
        
        // 測試完整的 getTaipeiWeather 方法
        console.log('\n🏙️ 測試 getTaipeiWeather 方法...');
        const taipeiWeather = await parser.getTaipeiWeather();
        
        if (taipeiWeather) {
            console.log('✅ 成功獲取台北天氣:');
            console.log('   地點:', taipeiWeather.location);
            console.log('   溫度:', taipeiWeather.temperature);
            console.log('   天氣:', taipeiWeather.weather);
            console.log('   圖示:', taipeiWeather.icon);
            console.log('   降雨機率:', taipeiWeather.rainChance);
        } else {
            console.log('❌ 無法獲取台北天氣');
        }
        
    } catch (error) {
        console.error('❌ 測試失敗:', error.message);
        console.error('詳細錯誤:', error);
    }
}

// 檢查是否有 node-fetch 和 jsdom
try {
    require('node-fetch');
    require('jsdom');
    testWeatherParsing();
} catch (error) {
    console.log('⚠️ 缺少依賴套件，使用簡化測試...');
    
    // 簡化測試 - 直接使用 https 模組
    const rssUrl = 'https://www.cwa.gov.tw/rss/forecast/36_01.xml';
    
    https.get(rssUrl, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => {
            console.log('✅ 成功獲取 RSS 資料');
            console.log('📊 資料長度:', data.length);
            
            // 簡單的正則解析
            const titleMatches = data.match(/<title><!\[CDATA\[\s*(.+?)\s*\]\]><\/title>/g);
            const descMatches = data.match(/<description><!\[CDATA\[\s*([\s\S]+?)\s*\]\]><\/description>/g);
            
            console.log('📰 找到標題數量:', titleMatches ? titleMatches.length : 0);
            console.log('📝 找到描述數量:', descMatches ? descMatches.length : 0);
            
            if (titleMatches && titleMatches.length > 1) {
                // 跳過第一個（通常是頻道標題）
                const weatherTitle = titleMatches[1].replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]*>/g, '');
                console.log('🌤️ 天氣標題:', weatherTitle);
                
                // 解析溫度
                const tempMatch = weatherTitle.match(/溫度:\s*(\d+)\s*~\s*(\d+)/);
                if (tempMatch) {
                    console.log('🌡️ 溫度範圍:', tempMatch[1] + '~' + tempMatch[2] + '°C');
                }
                
                // 解析降雨機率
                const rainMatch = weatherTitle.match(/降雨機率:\s*(\d+)%/);
                if (rainMatch) {
                    console.log('💧 降雨機率:', rainMatch[1] + '%');
                }
            }
            
            if (descMatches && descMatches.length > 0) {
                const weatherDesc = descMatches[0].replace(/<!\[CDATA\[|\]\]>/g, '').replace(/<[^>]*>/g, '');
                console.log('📋 天氣描述:', weatherDesc.substring(0, 100) + '...');
            }
        });
    }).on('error', (err) => {
        console.error('❌ 獲取 RSS 失敗:', err.message);
    });
}