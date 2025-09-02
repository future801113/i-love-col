// 圖片猜謎遊戲主程式
class GuessImageGame {
    constructor() {
        this.difficulty = 'easy';
        this.gameMode = 'single';
        this.imageSource = 'mixed';
        this.availableImages = [];
        this.currentImage = null;
        this.guessOptions = [];
        this.currentRound = 1;
        this.score = 0;
        this.streak = 0;
        this.revealLevel = 1;
        this.maxRevealLevel = 5;
        this.gameStartTime = null;
        this.timerInterval = null;
        this.timeLeft = 60;
        this.isGameActive = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadImageResources();
    }
    
    bindEvents() {
        // 返回主頁
        document.getElementById('backBtn').addEventListener('click', () => {
            window.location.href = '../index.html';
        });
        
        // 新遊戲
        document.getElementById('newGameBtn').addEventListener('click', () => {
            this.showSetupPanel();
        });
        
        // 開始遊戲
        document.getElementById('startGameBtn').addEventListener('click', () => {
            this.startGame();
        });
        
        // 提示按鈕
        document.getElementById('hintBtn').addEventListener('click', () => {
            this.showHint();
        });
        
        // 顯示更多
        document.getElementById('revealMoreBtn').addEventListener('click', () => {
            this.revealMore();
        });
        
        // 跳過
        document.getElementById('skipBtn').addEventListener('click', () => {
            this.skipRound();
        });
        
        // 設定選項變更
        document.querySelectorAll('input[name="difficulty"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.difficulty = e.target.value;
            });
        });
        
        document.querySelectorAll('input[name="gameMode"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.gameMode = e.target.value;
            });
        });
        
        document.querySelectorAll('input[name="imageSource"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.imageSource = e.target.value;
            });
        });
        
        // 結果模態框按鈕
        document.getElementById('nextRoundBtn').addEventListener('click', () => {
            this.nextRound();
        });
        
        document.getElementById('endGameBtn').addEventListener('click', () => {
            this.endGame();
        });
        
        // 遊戲結束按鈕
        document.getElementById('playAgainBtn').addEventListener('click', () => {
            this.hideGameOverModal();
            this.showSetupPanel();
        });
        
        document.getElementById('backToMainBtn').addEventListener('click', () => {
            window.location.href = '../index.html';
        });
    }
    
    // 載入圖片資源
    async loadImageResources() {
        this.showLoadingModal();
        
        try {
            const images = [];
            
            // 載入 ice_deliverer 圖片
            if (this.imageSource === 'mixed' || this.imageSource === 'ice_deliverer') {
                const iceImages = await this.loadImagesFromSource('../images/images.json');
                images.push(...iceImages);
            }
            
            // 載入 colne_icol 圖片
            if (this.imageSource === 'mixed' || this.imageSource === 'colne_icol') {
                const colneImages = await this.loadImagesFromSource('../colne_icol_images/images.json');
                images.push(...colneImages);
            }
            
            this.availableImages = images;
            console.log(`載入了 ${images.length} 張圖片`);
            
            this.hideLoadingModal();
            
            if (images.length < 4) {
                alert(`圖片數量不足！需要至少 4 張圖片，但只找到 ${images.length} 張。`);
            }
            
        } catch (error) {
            console.error('載入圖片失敗:', error);
            this.hideLoadingModal();
            alert('載入圖片失敗，請檢查網路連線或重新整理頁面。');
        }
    }
    
    // 從指定來源載入圖片
    async loadImagesFromSource(jsonPath) {
        try {
            const response = await fetch(jsonPath);
            const data = await response.json();
            
            return data.map(item => ({
                url: this.buildImageUrl(item.url, jsonPath),
                filename: item.filename
            }));
            
        } catch (error) {
            console.error(`載入 ${jsonPath} 失敗:`, error);
            return [];
        }
    }
    
    // 建立完整的圖片 URL
    buildImageUrl(relativeUrl, jsonPath) {
        const baseUrl = 'https://future801113.github.io/i-love-col/';
        
        // 如果已經是完整 URL，直接返回
        if (relativeUrl.startsWith('http')) {
            return relativeUrl;
        }
        
        // 根據 JSON 路徑判斷圖片目錄
        if (jsonPath.includes('colne_icol_images')) {
            return baseUrl + 'colne_icol_images/' + relativeUrl.replace(/^.*\//, '');
        } else {
            return baseUrl + 'images/' + relativeUrl.replace(/^.*\//, '');
        }
    }
    
    // 顯示設定面板
    showSetupPanel() {
        document.getElementById('setupPanel').style.display = 'block';
        document.getElementById('gameArea').style.display = 'none';
        document.getElementById('hintBtn').style.display = 'none';
        this.stopTimer();
        this.isGameActive = false;
    }
    
    // 開始遊戲
    async startGame() {
        if (this.availableImages.length < 4) {
            alert('圖片數量不足！需要至少 4 張圖片。');
            return;
        }
        
        // 重新載入圖片資源（以防設定變更）
        await this.loadImageResources();
        
        document.getElementById('setupPanel').style.display = 'none';
        document.getElementById('gameArea').style.display = 'block';
        document.getElementById('hintBtn').style.display = 'inline-block';
        
        this.initializeGame();
        this.startNewRound();
        
        if (this.gameMode === 'time') {
            this.startTimer();
        }
    }
    
    // 初始化遊戲狀態
    initializeGame() {
        this.currentRound = 1;
        this.score = 0;
        this.streak = 0;
        this.timeLeft = 60;
        this.isGameActive = true;
        
        // 顯示/隱藏時間顯示
        const timeDisplay = document.getElementById('timeDisplay');
        if (this.gameMode === 'time') {
            timeDisplay.style.display = 'flex';
        } else {
            timeDisplay.style.display = 'none';
        }
        
        this.updateUI();
    }
    
    // 開始新回合
    startNewRound() {
        this.revealLevel = 1;
        this.selectRandomImage();
        this.generateGuessOptions();
        this.updateImageMask();
        this.updateUI();
    }
    
    // 選擇隨機圖片
    selectRandomImage() {
        const randomIndex = Math.floor(Math.random() * this.availableImages.length);
        this.currentImage = this.availableImages[randomIndex];
        
        // 設定目標圖片
        const targetImage = document.getElementById('targetImage');
        targetImage.src = this.currentImage.url;
        targetImage.alt = this.currentImage.filename;
    }
    
    // 生成猜測選項
    generateGuessOptions() {
        // 確保正確答案包含在選項中
        const options = [this.currentImage];
        
        // 隨機選擇其他 3 個選項
        const otherImages = this.availableImages.filter(img => img !== this.currentImage);
        const shuffled = [...otherImages];
        this.shuffleArray(shuffled);
        
        options.push(...shuffled.slice(0, 3));
        
        // 洗牌選項
        this.shuffleArray(options);
        this.guessOptions = options;
        
        this.renderGuessOptions();
    }
    
    // 渲染猜測選項
    renderGuessOptions() {
        const container = document.getElementById('guessOptions');
        container.innerHTML = '';
        
        this.guessOptions.forEach((option, index) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'guess-option';
            optionElement.dataset.index = index;
            
            optionElement.innerHTML = `
                <img src="${option.url}" alt="${option.filename}" loading="lazy">
                <div class="filename">${option.filename}</div>
            `;
            
            optionElement.addEventListener('click', () => this.handleGuess(index));
            container.appendChild(optionElement);
        });
    }
    
    // 處理猜測
    handleGuess(optionIndex) {
        if (!this.isGameActive) return;
        
        const selectedOption = this.guessOptions[optionIndex];
        const isCorrect = selectedOption === this.currentImage;
        
        // 視覺反饋
        const optionElements = document.querySelectorAll('.guess-option');
        optionElements[optionIndex].classList.add(isCorrect ? 'correct' : 'wrong');
        
        // 禁用所有選項
        optionElements.forEach(el => {
            el.style.pointerEvents = 'none';
        });
        
        if (isCorrect) {
            this.handleCorrectGuess();
        } else {
            this.handleWrongGuess();
        }
        
        // 顯示結果
        setTimeout(() => {
            this.showResult(isCorrect);
        }, 1000);
    }
    
    // 處理正確猜測
    handleCorrectGuess() {
        // 計算得分
        const baseScore = 100;
        const revealBonus = Math.max(0, (this.maxRevealLevel - this.revealLevel + 1) * 20);
        const streakBonus = this.streak * 10;
        const roundScore = baseScore + revealBonus + streakBonus;
        
        this.score += roundScore;
        this.streak++;
        
        console.log(`正確！得分: ${roundScore} (基礎: ${baseScore}, 顯示獎勵: ${revealBonus}, 連擊獎勵: ${streakBonus})`);
    }
    
    // 處理錯誤猜測
    handleWrongGuess() {
        this.streak = 0;
        console.log('答錯了！連擊中斷。');
    }
    
    // 顯示更多圖片
    revealMore() {
        if (this.revealLevel < this.maxRevealLevel) {
            this.revealLevel++;
            this.updateImageMask();
            this.updateUI();
        }
    }
    
    // 更新圖片遮罩
    updateImageMask() {
        const image = document.getElementById('targetImage');
        const sizes = this.getRevealSizes();
        const size = sizes[this.revealLevel - 1];
        
        image.style.clipPath = `circle(${size}px at 50% 50%)`;
    }
    
    // 獲取不同難度的顯示大小
    getRevealSizes() {
        const baseSizes = {
            easy: [100, 140, 180, 220, 300],    // 簡單：顯示較大區域
            medium: [70, 100, 130, 160, 200],   // 中等：適中區域
            hard: [40, 60, 80, 100, 140]        // 困難：顯示較小區域
        };
        
        return baseSizes[this.difficulty] || baseSizes.medium;
    }
    
    // 跳過回合
    skipRound() {
        if (!this.isGameActive) return;
        
        this.streak = 0;
        this.showResult(false, true);
    }
    
    // 顯示提示
    showHint() {
        if (this.revealLevel < this.maxRevealLevel) {
            this.revealMore();
        } else {
            // 高亮正確答案
            const correctIndex = this.guessOptions.indexOf(this.currentImage);
            const optionElements = document.querySelectorAll('.guess-option');
            optionElements[correctIndex].style.border = '3px solid #48bb78';
            optionElements[correctIndex].style.boxShadow = '0 0 15px rgba(72, 187, 120, 0.5)';
        }
    }
    
    // 顯示結果
    showResult(isCorrect, isSkipped = false) {
        const modal = document.getElementById('resultModal');
        const title = document.getElementById('resultTitle');
        const image = document.getElementById('resultImage');
        const stats = document.getElementById('resultStats');
        
        // 設定標題
        if (isSkipped) {
            title.textContent = '⏭️ 已跳過';
        } else if (isCorrect) {
            title.textContent = '🎉 答對了！';
        } else {
            title.textContent = '❌ 答錯了';
        }
        
        // 顯示完整圖片
        image.src = this.currentImage.url;
        image.alt = this.currentImage.filename;
        
        // 顯示統計
        const revealPercent = Math.round((this.revealLevel / this.maxRevealLevel) * 100);
        stats.innerHTML = `
            <div class="stat-row">
                <span>圖片檔名:</span>
                <span>${this.currentImage.filename}</span>
            </div>
            <div class="stat-row">
                <span>顯示程度:</span>
                <span>${revealPercent}%</span>
            </div>
            <div class="stat-row">
                <span>當前得分:</span>
                <span>${this.score}</span>
            </div>
            <div class="stat-row">
                <span>連續答對:</span>
                <span>${this.streak}</span>
            </div>
        `;
        
        modal.style.display = 'flex';
    }
    
    // 下一回合
    nextRound() {
        document.getElementById('resultModal').style.display = 'none';
        
        // 檢查遊戲是否應該結束
        if (this.gameMode === 'time' && this.timeLeft <= 0) {
            this.endGame();
            return;
        }
        
        this.currentRound++;
        this.startNewRound();
    }
    
    // 開始計時器
    startTimer() {
        this.gameStartTime = Date.now();
        this.timerInterval = setInterval(() => {
            if (this.isGameActive) {
                this.timeLeft--;
                document.getElementById('timeLeft').textContent = this.timeLeft;
                
                if (this.timeLeft <= 0) {
                    this.endGame();
                }
            }
        }, 1000);
    }
    
    // 停止計時器
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    // 結束遊戲
    endGame() {
        this.isGameActive = false;
        this.stopTimer();
        document.getElementById('resultModal').style.display = 'none';
        
        const modal = document.getElementById('gameOverModal');
        const title = document.getElementById('gameOverTitle');
        const stats = document.getElementById('gameOverStats');
        
        title.textContent = '🏁 遊戲結束！';
        
        const accuracy = this.currentRound > 1 ? Math.round((this.streak / (this.currentRound - 1)) * 100) : 0;
        
        stats.innerHTML = `
            <div class="stat-row">
                <span>總得分:</span>
                <span>${this.score}</span>
            </div>
            <div class="stat-row">
                <span>完成回合:</span>
                <span>${this.currentRound - 1}</span>
            </div>
            <div class="stat-row">
                <span>最高連擊:</span>
                <span>${this.streak}</span>
            </div>
            <div class="stat-row">
                <span>準確率:</span>
                <span>${accuracy}%</span>
            </div>
            ${this.gameMode === 'time' ? `
            <div class="stat-row">
                <span>遊戲時間:</span>
                <span>60 秒</span>
            </div>
            ` : ''}
        `;
        
        modal.style.display = 'flex';
    }
    
    // 更新 UI
    updateUI() {
        document.getElementById('currentScore').textContent = this.score;
        document.getElementById('currentRound').textContent = this.currentRound;
        document.getElementById('streak').textContent = this.streak;
        
        // 更新顯示進度
        const revealPercent = Math.round((this.revealLevel / this.maxRevealLevel) * 100);
        document.getElementById('revealBar').style.width = revealPercent + '%';
        document.getElementById('revealText').textContent = `${revealPercent}% 已顯示`;
        
        // 更新按鈕狀態
        const revealBtn = document.getElementById('revealMoreBtn');
        if (this.revealLevel >= this.maxRevealLevel) {
            revealBtn.textContent = '🔍 已全部顯示';
            revealBtn.disabled = true;
        } else {
            revealBtn.textContent = '🔍 顯示更多';
            revealBtn.disabled = false;
        }
    }
    
    // 洗牌算法
    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }
    
    // 顯示載入提示
    showLoadingModal() {
        document.getElementById('loadingModal').style.display = 'flex';
        
        // 模擬載入進度
        let progress = 0;
        const progressFill = document.getElementById('progressFill');
        const loadingText = document.getElementById('loadingText');
        
        const progressInterval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress > 100) progress = 100;
            
            progressFill.style.width = progress + '%';
            
            if (progress < 30) {
                loadingText.textContent = '載入圖片資源...';
            } else if (progress < 60) {
                loadingText.textContent = '處理圖片資料...';
            } else if (progress < 90) {
                loadingText.textContent = '準備遊戲...';
            } else {
                loadingText.textContent = '即將完成...';
            }
            
            if (progress >= 100) {
                clearInterval(progressInterval);
            }
        }, 100);
    }
    
    // 隱藏載入提示
    hideLoadingModal() {
        document.getElementById('loadingModal').style.display = 'none';
    }
    
    // 隱藏遊戲結束提示
    hideGameOverModal() {
        document.getElementById('gameOverModal').style.display = 'none';
    }
}

// 初始化遊戲
const guessImageGame = new GuessImageGame();