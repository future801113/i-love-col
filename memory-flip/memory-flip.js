// 記憶翻翻樂遊戲主程式
class MemoryFlipGame {
    constructor() {
        this.cardCount = 8;
        this.gameMode = 'single';
        this.imageSource = 'mixed';
        this.gameBoard = [];
        this.flippedCards = [];
        this.matchedPairs = 0;
        this.currentPlayer = 1;
        this.players = {
            1: { score: 0, pairs: 0 },
            2: { score: 0, pairs: 0 }
        };
        this.gameStartTime = null;
        this.timerInterval = null;
        this.flipCount = 0;
        this.isGamePaused = false;
        this.isProcessing = false;
        this.availableImages = [];
        
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
        
        // 暫停遊戲
        document.getElementById('pauseBtn').addEventListener('click', () => {
            this.togglePause();
        });
        
        // 設定選項變更
        document.querySelectorAll('input[name="cardCount"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.cardCount = parseInt(e.target.value);
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
        
        // 遊戲結束後的按鈕
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
            
            if (images.length < this.cardCount) {
                alert(`圖片數量不足！需要 ${this.cardCount} 張，但只找到 ${images.length} 張。`);
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
        document.getElementById('pauseBtn').style.display = 'none';
        this.stopTimer();
    }
    
    // 開始遊戲
    async startGame() {
        if (this.availableImages.length < this.cardCount) {
            alert(`圖片數量不足！需要 ${this.cardCount} 張圖片。`);
            return;
        }
        
        // 重新載入圖片資源（以防設定變更）
        await this.loadImageResources();
        
        document.getElementById('setupPanel').style.display = 'none';
        document.getElementById('gameArea').style.display = 'block';
        document.getElementById('pauseBtn').style.display = 'inline-block';
        
        this.initializeGame();
        this.createGameBoard();
        this.startTimer();
    }
    
    // 初始化遊戲狀態
    initializeGame() {
        this.gameBoard = [];
        this.flippedCards = [];
        this.matchedPairs = 0;
        this.currentPlayer = 1;
        this.players = {
            1: { score: 0, pairs: 0 },
            2: { score: 0, pairs: 0 }
        };
        this.flipCount = 0;
        this.isGamePaused = false;
        this.isProcessing = false;
        
        // 更新 UI
        this.updatePlayerInfo();
        this.updateGameStats();
        
        // 顯示/隱藏玩家二資訊
        const player2Info = document.getElementById('player2Info');
        if (this.gameMode === 'versus') {
            player2Info.style.display = 'block';
        } else {
            player2Info.style.display = 'none';
        }
    }
    
    // 建立遊戲板
    createGameBoard() {
        const board = document.getElementById('gameBoard');
        board.innerHTML = '';
        
        // 隨機選擇圖片
        const selectedImages = this.selectRandomImages(this.cardCount);
        
        // 建立卡片對（每張圖片兩張卡片）
        const cards = [];
        selectedImages.forEach((image, index) => {
            cards.push({ id: index, image: image, matched: false });
            cards.push({ id: index, image: image, matched: false });
        });
        
        // 洗牌
        this.shuffleArray(cards);
        
        // 設定網格佈局
        this.setGridLayout(cards.length);
        
        // 建立卡片元素
        cards.forEach((card, index) => {
            const cardElement = this.createCardElement(card, index);
            board.appendChild(cardElement);
            this.gameBoard.push({
                element: cardElement,
                card: card,
                index: index,
                flipped: false
            });
        });
        
        this.updateGameStats();
    }
    
    // 隨機選擇圖片
    selectRandomImages(count) {
        const shuffled = [...this.availableImages];
        this.shuffleArray(shuffled);
        return shuffled.slice(0, count);
    }
    
    // 洗牌算法
    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }
    
    // 設定網格佈局
    setGridLayout(cardCount) {
        const board = document.getElementById('gameBoard');
        board.className = 'game-board';
        
        if (cardCount <= 16) {
            board.classList.add('grid-4x4');
        } else if (cardCount <= 24) {
            board.classList.add('grid-4x6');
        } else if (cardCount <= 36) {
            board.classList.add('grid-6x6');
        } else {
            board.classList.add('grid-6x8');
        }
    }
    
    // 建立卡片元素
    createCardElement(card, index) {
        const cardElement = document.createElement('div');
        cardElement.className = 'memory-card';
        cardElement.dataset.index = index;
        
        cardElement.innerHTML = `
            <div class="card-inner">
                <div class="card-front">
                    🃏
                </div>
                <div class="card-back">
                    <img src="${card.image.url}" alt="${card.image.filename}" loading="lazy">
                </div>
            </div>
        `;
        
        cardElement.addEventListener('click', () => this.handleCardClick(index));
        
        return cardElement;
    }
    
    // 處理卡片點擊
    handleCardClick(index) {
        if (this.isGamePaused || this.isProcessing) return;
        
        const boardCard = this.gameBoard[index];
        
        // 檢查卡片是否已翻開或已配對
        if (boardCard.flipped || boardCard.card.matched) return;
        
        // 檢查是否已翻開兩張卡片
        if (this.flippedCards.length >= 2) return;
        
        // 翻開卡片
        this.flipCard(index);
        this.flippedCards.push(index);
        this.flipCount++;
        this.updateGameStats();
        
        // 檢查是否翻開了兩張卡片
        if (this.flippedCards.length === 2) {
            this.isProcessing = true;
            setTimeout(() => this.checkMatch(), 1000);
        }
    }
    
    // 翻開卡片
    flipCard(index) {
        const boardCard = this.gameBoard[index];
        boardCard.element.classList.add('flipped');
        boardCard.flipped = true;
    }
    
    // 翻回卡片
    flipBackCard(index) {
        const boardCard = this.gameBoard[index];
        boardCard.element.classList.remove('flipped');
        boardCard.flipped = false;
    }
    
    // 檢查配對
    checkMatch() {
        const [index1, index2] = this.flippedCards;
        const card1 = this.gameBoard[index1];
        const card2 = this.gameBoard[index2];
        
        if (card1.card.id === card2.card.id) {
            // 配對成功
            this.handleMatch(index1, index2);
        } else {
            // 配對失敗
            this.handleMismatch(index1, index2);
        }
        
        this.flippedCards = [];
        this.isProcessing = false;
    }
    
    // 處理配對成功
    handleMatch(index1, index2) {
        const card1 = this.gameBoard[index1];
        const card2 = this.gameBoard[index2];
        
        // 標記為已配對
        card1.card.matched = true;
        card2.card.matched = true;
        card1.element.classList.add('matched');
        card2.element.classList.add('matched');
        
        // 更新分數
        this.players[this.currentPlayer].pairs++;
        this.players[this.currentPlayer].score += 10;
        this.matchedPairs++;
        
        this.updatePlayerInfo();
        this.updateGameStats();
        
        // 檢查遊戲是否結束
        if (this.matchedPairs === this.cardCount) {
            this.endGame();
        } else if (this.gameMode === 'single') {
            // 單人模式繼續
        } else {
            // 雙人模式，配對成功繼續當前玩家的回合
        }
    }
    
    // 處理配對失敗
    handleMismatch(index1, index2) {
        // 翻回卡片
        this.flipBackCard(index1);
        this.flipBackCard(index2);
        
        // 雙人模式切換玩家
        if (this.gameMode === 'versus') {
            this.switchPlayer();
        }
    }
    
    // 切換玩家
    switchPlayer() {
        this.currentPlayer = this.currentPlayer === 1 ? 2 : 1;
        this.updatePlayerInfo();
    }
    
    // 更新玩家資訊顯示
    updatePlayerInfo() {
        // 更新分數顯示
        document.getElementById('player1Score').textContent = this.players[1].score;
        document.getElementById('player1Pairs').textContent = this.players[1].pairs;
        document.getElementById('player2Score').textContent = this.players[2].score;
        document.getElementById('player2Pairs').textContent = this.players[2].pairs;
        
        // 更新當前玩家高亮
        const player1Info = document.getElementById('player1Info');
        const player2Info = document.getElementById('player2Info');
        
        if (this.currentPlayer === 1) {
            player1Info.classList.add('active');
            player2Info.classList.remove('active');
        } else {
            player1Info.classList.remove('active');
            player2Info.classList.add('active');
        }
    }
    
    // 更新遊戲統計
    updateGameStats() {
        document.getElementById('flipCount').textContent = this.flipCount;
        document.getElementById('remainingPairs').textContent = this.cardCount - this.matchedPairs;
    }
    
    // 開始計時器
    startTimer() {
        this.gameStartTime = Date.now();
        this.timerInterval = setInterval(() => {
            if (!this.isGamePaused) {
                const elapsed = Date.now() - this.gameStartTime;
                const minutes = Math.floor(elapsed / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                document.getElementById('gameTimer').textContent = 
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
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
    
    // 切換暫停狀態
    togglePause() {
        this.isGamePaused = !this.isGamePaused;
        const pauseBtn = document.getElementById('pauseBtn');
        
        if (this.isGamePaused) {
            pauseBtn.textContent = '▶️ 繼續';
            // 隱藏所有卡片內容
            document.querySelectorAll('.memory-card').forEach(card => {
                card.style.opacity = '0.3';
            });
        } else {
            pauseBtn.textContent = '⏸️ 暫停';
            // 顯示所有卡片內容
            document.querySelectorAll('.memory-card').forEach(card => {
                card.style.opacity = '1';
            });
        }
    }
    
    // 結束遊戲
    endGame() {
        this.stopTimer();
        
        const finalTime = document.getElementById('gameTimer').textContent;
        const gameOverTitle = document.getElementById('gameOverTitle');
        const gameOverStats = document.getElementById('gameOverStats');
        
        let statsHTML = '';
        
        if (this.gameMode === 'single') {
            gameOverTitle.textContent = '🎉 恭喜完成！';
            statsHTML = `
                <div class="stat-row">
                    <span>完成時間:</span>
                    <span>${finalTime}</span>
                </div>
                <div class="stat-row">
                    <span>翻牌次數:</span>
                    <span>${this.flipCount}</span>
                </div>
                <div class="stat-row">
                    <span>配對數量:</span>
                    <span>${this.cardCount}</span>
                </div>
                <div class="stat-row">
                    <span>最終得分:</span>
                    <span>${this.players[1].score}</span>
                </div>
            `;
        } else {
            const winner = this.players[1].score > this.players[2].score ? 1 : 
                          this.players[2].score > this.players[1].score ? 2 : 0;
            
            if (winner === 0) {
                gameOverTitle.textContent = '🤝 平手！';
            } else {
                gameOverTitle.textContent = `🏆 玩家${winner}獲勝！`;
            }
            
            statsHTML = `
                <div class="stat-row">
                    <span>遊戲時間:</span>
                    <span>${finalTime}</span>
                </div>
                <div class="stat-row">
                    <span>玩家一得分:</span>
                    <span>${this.players[1].score} (${this.players[1].pairs}對)</span>
                </div>
                <div class="stat-row">
                    <span>玩家二得分:</span>
                    <span>${this.players[2].score} (${this.players[2].pairs}對)</span>
                </div>
                <div class="stat-row">
                    <span>總翻牌次數:</span>
                    <span>${this.flipCount}</span>
                </div>
            `;
        }
        
        gameOverStats.innerHTML = statsHTML;
        this.showGameOverModal();
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
    
    // 顯示遊戲結束提示
    showGameOverModal() {
        document.getElementById('gameOverModal').style.display = 'flex';
    }
    
    // 隱藏遊戲結束提示
    hideGameOverModal() {
        document.getElementById('gameOverModal').style.display = 'none';
    }
}

// 初始化遊戲
const memoryFlipGame = new MemoryFlipGame();