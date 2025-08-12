/**
 * 訪客追蹤 JavaScript 類別
 * 用於整合到 i-love-col 網站
 */

class VisitorTracker {
    constructor(apiBaseUrl) {
        this.apiBaseUrl = apiBaseUrl;
        this.sessionId = this.generateSessionId();
        this.visitorId = null;
        this.startTime = Date.now();
        this.currentMode = 'gallery';
        this.initialized = false;
        
        // 初始化
        this.init();
    }

    /**
     * 初始化追蹤器
     */
    async init() {
        try {
            // 防止重複初始化
            if (this.initialized) {
                console.log('⚠️ 追蹤器已經初始化，跳過');
                return;
            }
            
            // 記錄初始訪客
            await this.recordVisitor(this.currentMode);
            
            // 設定頁面離開事件
            this.setupBeforeUnloadHandler();
            
            // 設定定期心跳（可選）
            this.setupHeartbeat();
            
            this.initialized = true;
            console.log('✅ 訪客追蹤器初始化成功');
        } catch (error) {
            console.warn('⚠️ 訪客追蹤器初始化失敗:', error);
        }
    }

    /**
     * 生成會話 ID（使用 localStorage 確保同一瀏覽器會話使用相同 ID）
     */
    generateSessionId() {
        // 檢查是否已有 session ID
        let sessionId = localStorage.getItem('visitor_session_id');
        
        if (!sessionId) {
            // 生成新的 session ID
            sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0;
                const v = c == 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
            
            // 儲存到 localStorage
            localStorage.setItem('visitor_session_id', sessionId);
            console.log('🆕 生成新的 Session ID:', sessionId);
        } else {
            console.log('♻️ 使用現有 Session ID:', sessionId);
        }
        
        return sessionId;
    }

    /**
     * 記錄訪客
     */
    async recordVisitor(pageMode = 'gallery') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/visitors`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    page_mode: pageMode,
                    user_agent: navigator.userAgent,
                    referer: document.referrer
                })
            });

            const data = await response.json();
            if (data.success) {
                this.visitorId = data.data.visitor_id;
                console.log('✅ 訪客記錄成功:', data.data);
                return data.data;
            } else {
                throw new Error(data.message || '記錄失敗');
            }
        } catch (error) {
            console.warn('⚠️ 訪客記錄失敗:', error);
            return null;
        }
    }

    /**
     * 記錄頁面瀏覽
     */
    async recordPageView(pageMode, duration = null) {
        if (!this.visitorId) {
            console.warn('⚠️ 訪客 ID 不存在，跳過頁面瀏覽記錄');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/page-views`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    visitor_id: this.visitorId,
                    page_mode: pageMode,
                    view_duration: duration || Math.floor((Date.now() - this.startTime) / 1000)
                })
            });

            const data = await response.json();
            if (data.success) {
                console.log('✅ 頁面瀏覽記錄成功:', data.data);
                return data.data;
            } else {
                throw new Error(data.message || '記錄失敗');
            }
        } catch (error) {
            console.warn('⚠️ 頁面瀏覽記錄失敗:', error);
            return null;
        }
    }

    /**
     * 切換模式時調用
     */
    async switchMode(newMode) {
        if (this.currentMode !== newMode) {
            // 記錄舊模式的瀏覽時間
            await this.recordPageView(this.currentMode);
            
            // 更新當前模式和開始時間
            this.currentMode = newMode;
            this.startTime = Date.now();
            
            console.log(`📱 模式切換: ${newMode}`);
        }
    }

    /**
     * 獲取統計資料
     */
    async getStats(period = 'today') {
        try {
            const response = await fetch(`${this.apiBaseUrl}/stats?period=${period}`);
            const data = await response.json();
            
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.message || '獲取失敗');
            }
        } catch (error) {
            console.warn('⚠️ 統計資料獲取失敗:', error);
            return null;
        }
    }

    /**
     * 獲取即時統計
     */
    async getRealtimeStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/stats/realtime`);
            const data = await response.json();
            
            if (data.success) {
                return data.data;
            } else {
                throw new Error(data.message || '獲取失敗');
            }
        } catch (error) {
            console.warn('⚠️ 即時統計獲取失敗:', error);
            return null;
        }
    }

    /**
     * 更新統計顯示
     */
    async updateStatsDisplay() {
        const stats = await this.getRealtimeStats();
        if (stats) {
            // 更新頁面上的統計顯示
            const todayElement = document.getElementById('todayVisitors');
            const totalElement = document.getElementById('totalVisitors');
            const onlineElement = document.getElementById('onlineVisitors');
            
            if (todayElement) todayElement.textContent = stats.today_visitors;
            if (totalElement) totalElement.textContent = stats.total_visitors;
            if (onlineElement) onlineElement.textContent = stats.online_visitors;
        }
    }

    /**
     * 設定頁面離開處理
     */
    setupBeforeUnloadHandler() {
        window.addEventListener('beforeunload', () => {
            // 使用 sendBeacon 確保資料能送出
            if (this.visitorId && navigator.sendBeacon) {
                const data = JSON.stringify({
                    visitor_id: this.visitorId,
                    page_mode: this.currentMode,
                    view_duration: Math.floor((Date.now() - this.startTime) / 1000)
                });
                
                navigator.sendBeacon(`${this.apiBaseUrl}/page-views`, data);
            }
        });
    }

    /**
     * 設定心跳機制（可選）
     */
    setupHeartbeat() {
        // 每 5 分鐘更新一次統計顯示
        setInterval(() => {
            this.updateStatsDisplay();
        }, 5 * 60 * 1000);
    }
}

// 使用範例和整合代碼
document.addEventListener('DOMContentLoaded', function() {
    // 初始化訪客追蹤器
    const tracker = new VisitorTracker('https://i-love-col.zeabur.app/api/v1');
    
    // 將追蹤器設為全域變數，方便其他函數使用
    window.visitorTracker = tracker;
    
    // 修改原有的 switchMode 函數
    const originalSwitchMode = window.switchMode;
    window.switchMode = function(mode) {
        // 記錄模式切換
        if (window.visitorTracker) {
            window.visitorTracker.switchMode(mode);
        }
        
        // 執行原有的模式切換邏輯
        if (originalSwitchMode) {
            originalSwitchMode(mode);
        }
    };
    
    // 初始化統計顯示更新
    setTimeout(() => {
        tracker.updateStatsDisplay();
    }, 2000);
});

// 導出類別（如果使用模組系統）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VisitorTracker;
}