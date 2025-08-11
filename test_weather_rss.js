// Node.js 測試腳本 - 測試天氣 RSS 解析
const https = require('https');
const http = require('http');

// 測試中央氣象署 RSS URL
const rssUrl = 'https://www.cwa.gov.tw/rss/forecast/36_01.xml';

console.log('🌤️ 測試中央氣象署 RSS...');
console.log('📡 URL:', rssUrl);

// 測試直接訪問
https.get(rssUrl, (res) => {
    console.log('✅ 直接訪問狀態:', res.statusCode);
    console.log('📋 回應標頭:', res.headers);
    
    let data = '';
    res.on('data', (chunk) => {
        data += chunk;
    });
    
    res.on('end', () => {
        console.log('📊 資料長度:', data.length);
        
        if (data.length > 0) {
            // 簡單解析 XML
            const titleMatches = data.match(/<title[^>]*>([^<]+)<\/title>/g);
            const descMatches = data.match(/<description[^>]*>([^<]+)<\/description>/g);
            
            console.log('📰 找到的標題數量:', titleMatches ? titleMatches.length : 0);
            console.log('📝 找到的描述數量:', descMatches ? descMatches.length : 0);
            
            if (titleMatches && titleMatches.length > 0) {
                console.log('\n🎯 前3個標題:');
                titleMatches.slice(0, 3).forEach((title, index) => {
                    const cleanTitle = title.replace(/<[^>]*>/g, '');
                    console.log(`${index + 1}. ${cleanTitle}`);
                });
            }
            
            if (descMatches && descMatches.length > 0) {
                console.log('\n📋 第一個描述:');
                const cleanDesc = descMatches[0].replace(/<[^>]*>/g, '');
                console.log(cleanDesc.substring(0, 200) + '...');
            }
        }
        
        console.log('\n✅ RSS 測試完成');
    });
    
}).on('error', (err) => {
    console.error('❌ 直接訪問失敗:', err.message);
    
    // 測試 CORS 代理
    testCorsProxy();
});

function testCorsProxy() {
    console.log('\n🌐 測試 CORS 代理...');
    
    const proxies = [
        'https://api.allorigins.win/raw?url=',
        'https://cors-anywhere.herokuapp.com/',
        'https://api.codetabs.com/v1/proxy?quest='
    ];
    
    let proxyIndex = 0;
    
    function testNextProxy() {
        if (proxyIndex >= proxies.length) {
            console.log('❌ 所有代理都無法使用');
            return;
        }
        
        const proxy = proxies[proxyIndex];
        const proxyUrl = proxy + encodeURIComponent(rssUrl);
        
        console.log(`🔗 測試代理 ${proxyIndex + 1}: ${proxy}`);
        
        const request = proxyUrl.startsWith('https') ? https : http;
        
        request.get(proxyUrl, (res) => {
            console.log(`   狀態: ${res.statusCode}`);
            
            if (res.statusCode === 200) {
                let data = '';
                res.on('data', (chunk) => {
                    data += chunk;
                });
                
                res.on('end', () => {
                    console.log(`   ✅ 代理 ${proxyIndex + 1} 成功，資料長度: ${data.length}`);
                    
                    if (data.includes('<rss') || data.includes('<title>')) {
                        console.log('   🎉 成功獲取 RSS 資料！');
                    } else {
                        console.log('   ⚠️ 資料格式可能有問題');
                    }
                });
            } else {
                console.log(`   ❌ 代理 ${proxyIndex + 1} 失敗`);
                proxyIndex++;
                testNextProxy();
            }
            
        }).on('error', (err) => {
            console.log(`   ❌ 代理 ${proxyIndex + 1} 錯誤: ${err.message}`);
            proxyIndex++;
            testNextProxy();
        });
    }
    
    testNextProxy();
}