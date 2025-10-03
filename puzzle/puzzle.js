// 拼圖遊戲主程式
class PuzzleGame {
    constructor() {
        this.currentImage = null;
        this.difficulty = 'easy';
        this.gridSize = 3;
        this.pieces = [];
        this.correctPositions = [];
        this.selectedPiece = null;
        this.gameStartTime = null;
        this.timerInterval = null;
        this.gameId = null;

        this.difficultySettings = {
            easy: { size: 3, name: '簡單' },
            medium: { size: 4, name: '中等' },
            hard: { size: 5, name: '困難' },
            expert: { size: 6, name: '專家' }
        };

        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadImageFromURL();
        this.loadSavedGames();
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

        // 儲存遊戲
        document.getElementById('saveGameBtn').addEventListener('click', () => {
            this.saveGame();
        });

        // 載入遊戲
        document.getElementById('loadGameBtn').addEventListener('click', () => {
            this.showLoadGameDialog();
        });

        // 難度選擇
        document.querySelectorAll('input[name="difficulty"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.difficulty = e.target.value;
                this.gridSize = this.difficultySettings[this.difficulty].size;
            });
        });

        // 完成後的按鈕
        document.getElementById('playAgainBtn').addEventListener('click', () => {
            this.hideCompletionModal();
            this.showSetupPanel();
        });

        document.getElementById('backToMainBtn').addEventListener('click', () => {
            window.location.href = '../index.html';
        });
    }

    // 從 URL 參數載入圖片，如果沒有則隨機選擇
    async loadImageFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const imageUrl = urlParams.get('image');

        if (imageUrl) {
            let decodedUrl = decodeURIComponent(imageUrl);

            // 確保使用完整的 domain URL
            if (!decodedUrl.startsWith('http')) {
                // 如果是相對路徑，轉換為完整 URL
                const baseUrl = 'https://future801113.github.io/i-love-col/';
                if (decodedUrl.startsWith('./')) {
                    decodedUrl = baseUrl + decodedUrl.substring(2);
                } else if (decodedUrl.startsWith('/')) {
                    decodedUrl = baseUrl + decodedUrl.substring(1);
                } else {
                    decodedUrl = baseUrl + decodedUrl;
                }
            }

            this.currentImage = decodedUrl;
            console.log('載入圖片 URL:', this.currentImage);
            this.displaySelectedImage();
        } else {
            // 沒有指定圖片，從主頁圖片庫隨機選擇
            await this.loadRandomImageFromGallery();
        }
    }

    // 從主頁圖片庫隨機選擇圖片
    async loadRandomImageFromGallery() {
        try {
            // 隨機選擇一個帳號
            const accounts = ['ice_deliverer', 'colne_icol'];
            const selectedAccount = accounts[Math.floor(Math.random() * accounts.length)];
            
            // 載入對應的圖片清單
            const jsonPath = selectedAccount === 'ice_deliverer' 
                ? '../images/images.json' 
                : '../colne_icol_images/images.json';
            
            console.log(`從 ${selectedAccount} 載入圖片清單:`, jsonPath);
            
            const response = await fetch(jsonPath);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const imageList = await response.json();
            
            if (imageList && imageList.length > 0) {
                // 隨機選擇一張圖片
                const randomIndex = Math.floor(Math.random() * imageList.length);
                const imageData = imageList[randomIndex];
                
                this.currentImage = imageData.url;
                console.log('隨機選擇圖片:', this.currentImage);
                this.displaySelectedImage();
            } else {
                console.error('圖片清單為空');
                this.showImageError('圖片清單為空');
            }
        } catch (error) {
            console.error('載入圖片清單失敗:', error);
            this.showImageError('無法載入圖片，請稍後再試');
        }
    }

    // 顯示圖片載入錯誤
    showImageError(message) {
        const placeholder = document.getElementById('imagePlaceholder');
        placeholder.innerHTML = `<p>❌ ${message}</p>`;
        placeholder.style.display = 'flex';
    }

    // 顯示選擇的圖片
    displaySelectedImage() {
        const img = document.getElementById('selectedImage');
        const placeholder = document.getElementById('imagePlaceholder');

        if (this.currentImage) {
            console.log('設定預覽圖片 URL:', this.currentImage);
            img.src = this.currentImage;
            img.style.display = 'block';
            placeholder.style.display = 'none';

            // 添加圖片載入錯誤處理
            img.onerror = () => {
                console.error('圖片載入失敗:', this.currentImage);
                placeholder.innerHTML = '<p>圖片載入失敗，請檢查 URL 是否正確</p>';
                img.style.display = 'none';
                placeholder.style.display = 'flex';
            };

            img.onload = () => {
                console.log('圖片載入成功:', this.currentImage);
            };
        } else {
            img.style.display = 'none';
            placeholder.style.display = 'flex';
        }
    }

    // 顯示設定面板
    showSetupPanel() {
        document.getElementById('setupPanel').style.display = 'block';
        document.getElementById('gameArea').style.display = 'none';
        this.stopTimer();
    }

    // 開始遊戲
    startGame() {
        if (!this.currentImage) {
            alert('請先選擇圖片！');
            return;
        }

        this.gameId = Date.now().toString();
        document.getElementById('setupPanel').style.display = 'none';
        document.getElementById('gameArea').style.display = 'block';

        this.setupGame();
        this.startTimer();
    }

    // 設定遊戲
    setupGame() {
        // 更新遊戲資訊
        document.getElementById('currentDifficulty').textContent =
            `${this.difficultySettings[this.difficulty].name} (${this.gridSize}×${this.gridSize})`;
        document.getElementById('gameProgress').textContent = '0%';

        // 設定參考圖片
        document.getElementById('referenceImg').src = this.currentImage;

        // 建立拼圖
        this.createPuzzle();
    }

    // 建立拼圖
    createPuzzle() {
        const board = document.getElementById('puzzleBoard');
        board.innerHTML = '';
        board.style.gridTemplateColumns = `repeat(${this.gridSize}, 1fr)`;

        // 建立拼圖片段
        this.pieces = [];
        this.correctPositions = [];

        console.log('開始建立拼圖，使用圖片:', this.currentImage);

        for (let i = 0; i < this.gridSize * this.gridSize; i++) {
            const piece = document.createElement('div');
            piece.className = 'puzzle-piece';
            piece.dataset.index = i;
            piece.dataset.correctIndex = i;

            // 計算背景位置
            const row = Math.floor(i / this.gridSize);
            const col = i % this.gridSize;
            const bgPosX = -(col * 80);
            const bgPosY = -(row * 80);

            piece.style.backgroundImage = `url(${this.currentImage})`;
            piece.style.backgroundSize = `${this.gridSize * 80}px ${this.gridSize * 80}px`;
            piece.style.backgroundPosition = `${bgPosX}px ${bgPosY}px`;

            // 添加點擊事件
            piece.addEventListener('click', () => this.handlePieceClick(piece));

            board.appendChild(piece);
            this.pieces.push(piece);
            this.correctPositions.push(i);
        }

        // 打亂拼圖
        this.shufflePuzzle();
    }

    // 打亂拼圖
    shufflePuzzle() {
        const indices = [...Array(this.gridSize * this.gridSize).keys()];

        // Fisher-Yates 洗牌算法
        for (let i = indices.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [indices[i], indices[j]] = [indices[j], indices[i]];
        }

        // 重新排列拼圖片段
        indices.forEach((newIndex, currentIndex) => {
            this.pieces[currentIndex].dataset.index = newIndex;
        });

        this.updatePuzzleDisplay();
    }

    // 更新拼圖顯示
    updatePuzzleDisplay() {
        const board = document.getElementById('puzzleBoard');
        const sortedPieces = [...this.pieces].sort((a, b) =>
            parseInt(a.dataset.index) - parseInt(b.dataset.index)
        );

        board.innerHTML = '';
        sortedPieces.forEach(piece => board.appendChild(piece));

        this.checkProgress();
    }

    // 處理拼圖片段點擊
    handlePieceClick(piece) {
        if (this.selectedPiece === piece) {
            // 取消選擇
            piece.classList.remove('selected');
            this.selectedPiece = null;
        } else if (this.selectedPiece === null) {
            // 選擇片段
            piece.classList.add('selected');
            this.selectedPiece = piece;
        } else {
            // 交換片段
            this.swapPieces(this.selectedPiece, piece);
            this.selectedPiece.classList.remove('selected');
            this.selectedPiece = null;
        }
    }

    // 交換拼圖片段
    swapPieces(piece1, piece2) {
        const temp = piece1.dataset.index;
        piece1.dataset.index = piece2.dataset.index;
        piece2.dataset.index = temp;

        this.updatePuzzleDisplay();
    }

    // 檢查遊戲進度
    checkProgress() {
        let correctCount = 0;

        this.pieces.forEach(piece => {
            const currentIndex = parseInt(piece.dataset.index);
            const correctIndex = parseInt(piece.dataset.correctIndex);

            if (currentIndex === correctIndex) {
                piece.classList.add('correct');
                correctCount++;
            } else {
                piece.classList.remove('correct');
            }
        });

        const progress = Math.round((correctCount / this.pieces.length) * 100);
        document.getElementById('gameProgress').textContent = `${progress}%`;

        // 檢查是否完成
        if (correctCount === this.pieces.length) {
            this.completeGame();
        }
    }

    // 完成遊戲
    completeGame() {
        this.stopTimer();
        const finalTime = document.getElementById('gameTimer').textContent;
        document.getElementById('finalTime').textContent = finalTime;
        document.getElementById('completionModal').style.display = 'flex';

        // 清除儲存的遊戲
        this.clearSavedGame();
    }

    // 隱藏完成提示
    hideCompletionModal() {
        document.getElementById('completionModal').style.display = 'none';
    }

    // 開始計時器
    startTimer() {
        this.gameStartTime = Date.now();
        this.timerInterval = setInterval(() => {
            const elapsed = Date.now() - this.gameStartTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            document.getElementById('gameTimer').textContent =
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    // 停止計時器
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    // 儲存遊戲
    saveGame() {
        if (!this.gameId) {
            alert('沒有進行中的遊戲可以儲存！');
            return;
        }

        const gameState = {
            id: this.gameId,
            image: this.currentImage,
            difficulty: this.difficulty,
            gridSize: this.gridSize,
            pieces: this.pieces.map(piece => ({
                correctIndex: parseInt(piece.dataset.correctIndex),
                currentIndex: parseInt(piece.dataset.index)
            })),
            startTime: this.gameStartTime,
            savedAt: Date.now()
        };

        const savedGames = JSON.parse(localStorage.getItem('puzzleGames') || '[]');
        const existingIndex = savedGames.findIndex(game => game.id === this.gameId);

        if (existingIndex >= 0) {
            savedGames[existingIndex] = gameState;
        } else {
            savedGames.push(gameState);
        }

        // 只保留最近的 5 個遊戲
        if (savedGames.length > 5) {
            savedGames.sort((a, b) => b.savedAt - a.savedAt);
            savedGames.splice(5);
        }

        localStorage.setItem('puzzleGames', JSON.stringify(savedGames));
        alert('遊戲已儲存！');
    }

    // 載入儲存的遊戲
    loadSavedGames() {
        const savedGames = JSON.parse(localStorage.getItem('puzzleGames') || '[]');
        return savedGames.sort((a, b) => b.savedAt - a.savedAt);
    }

    // 顯示載入遊戲對話框
    showLoadGameDialog() {
        const savedGames = this.loadSavedGames();

        if (savedGames.length === 0) {
            alert('沒有儲存的遊戲！');
            return;
        }

        let dialogHTML = '<div style="max-height: 300px; overflow-y: auto;">';
        savedGames.forEach((game, index) => {
            const saveDate = new Date(game.savedAt).toLocaleString('zh-TW');
            const difficultyName = this.difficultySettings[game.difficulty].name;
            dialogHTML += `
                <div style="border: 1px solid #ddd; margin: 10px 0; padding: 10px; border-radius: 5px; cursor: pointer;" 
                     onclick="puzzleGame.loadGame('${game.id}')">
                    <strong>遊戲 ${index + 1}</strong><br>
                    難度: ${difficultyName} (${game.gridSize}×${game.gridSize})<br>
                    儲存時間: ${saveDate}
                </div>
            `;
        });
        dialogHTML += '</div>';

        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>選擇要載入的遊戲</h2>
                ${dialogHTML}
                <button class="btn btn-secondary" onclick="this.parentElement.parentElement.remove()">取消</button>
            </div>
        `;

        document.body.appendChild(modal);
    }

    // 載入指定遊戲
    loadGame(gameId) {
        const savedGames = this.loadSavedGames();
        const game = savedGames.find(g => g.id === gameId);

        if (!game) {
            alert('找不到指定的遊戲！');
            return;
        }

        // 移除載入對話框
        document.querySelector('.modal').remove();

        // 載入遊戲狀態
        this.gameId = game.id;
        this.currentImage = game.image;
        this.difficulty = game.difficulty;
        this.gridSize = game.gridSize;
        this.gameStartTime = game.startTime;

        // 顯示遊戲區域
        document.getElementById('setupPanel').style.display = 'none';
        document.getElementById('gameArea').style.display = 'block';

        // 設定遊戲資訊
        document.getElementById('currentDifficulty').textContent =
            `${this.difficultySettings[this.difficulty].name} (${this.gridSize}×${this.gridSize})`;
        document.getElementById('referenceImg').src = this.currentImage;

        // 重建拼圖
        this.createPuzzleFromSave(game.pieces);
        this.startTimer();

        alert('遊戲已載入！');
    }

    // 從儲存資料建立拼圖
    createPuzzleFromSave(savedPieces) {
        const board = document.getElementById('puzzleBoard');
        board.innerHTML = '';
        board.style.gridTemplateColumns = `repeat(${this.gridSize}, 1fr)`;

        this.pieces = [];

        savedPieces.forEach((pieceData, i) => {
            const piece = document.createElement('div');
            piece.className = 'puzzle-piece';
            piece.dataset.index = pieceData.currentIndex;
            piece.dataset.correctIndex = pieceData.correctIndex;

            // 計算背景位置
            const row = Math.floor(pieceData.correctIndex / this.gridSize);
            const col = pieceData.correctIndex % this.gridSize;
            const bgPosX = -(col * 80);
            const bgPosY = -(row * 80);

            piece.style.backgroundImage = `url(${this.currentImage})`;
            piece.style.backgroundSize = `${this.gridSize * 80}px ${this.gridSize * 80}px`;
            piece.style.backgroundPosition = `${bgPosX}px ${bgPosY}px`;

            piece.addEventListener('click', () => this.handlePieceClick(piece));

            this.pieces.push(piece);
        });

        this.updatePuzzleDisplay();
    }

    // 清除儲存的遊戲
    clearSavedGame() {
        if (!this.gameId) return;

        const savedGames = this.loadSavedGames();
        const filteredGames = savedGames.filter(game => game.id !== this.gameId);
        localStorage.setItem('puzzleGames', JSON.stringify(filteredGames));
    }
}

// 初始化遊戲
const puzzleGame = new PuzzleGame();