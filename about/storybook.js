// 故事書互動程式
class StoryBook {
    constructor() {
        this.totalPages = 10; // book01 到 book10
        this.currentPage = 1;
        this.pageAnimation = 'slide';

        this.init();
    }

    init() {
        this.bindEvents();
        this.showLoadingModal();
        this.preloadImages();
    }

    bindEvents() {
        // 返回主頁
        document.getElementById('backBtn').addEventListener('click', () => {
            window.location.href = '../index.html';
        });



        // 打開書本
        document.getElementById('bookCover').addEventListener('click', () => {
            this.openBook();
        });

        // 翻頁控制
        document.getElementById('prevBtn').addEventListener('click', () => {
            this.previousPage();
        });

        document.getElementById('nextBtn').addEventListener('click', () => {
            this.nextPage();
        });

        // 左右點擊區域
        document.getElementById('leftClickArea').addEventListener('click', () => {
            this.previousPage();
        });

        document.getElementById('rightClickArea').addEventListener('click', () => {
            this.nextPage();
        });

        // 工具列按鈕
        document.getElementById('backToCoverBtn').addEventListener('click', () => {
            this.backToCover();
        });

        document.getElementById('shareBtn').addEventListener('click', () => {
            this.showSharePanel();
        });

        // 關閉面板
        document.getElementById('closeShareBtn').addEventListener('click', () => {
            this.hideSharePanel();
        });



        // 分享按鈕
        document.querySelectorAll('.share-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.shareStory(e.target.dataset.platform);
            });
        });

        // 鍵盤控制
        document.addEventListener('keydown', (e) => {
            if (document.getElementById('bookReader').style.display !== 'none') {
                switch (e.key) {
                    case 'ArrowLeft':
                        this.previousPage();
                        break;
                    case 'ArrowRight':
                        this.nextPage();
                        break;
                }
            }
        });
    }

    // 預載入圖片
    async preloadImages() {
        const loadPromises = [];

        // 載入封面
        loadPromises.push(this.loadImage('https://future801113.github.io/i-love-col/about/images/book00.png'));

        // 載入所有頁面
        for (let i = 1; i <= this.totalPages; i++) {
            const pageNum = i.toString().padStart(2, '0');
            loadPromises.push(this.loadImage(`https://future801113.github.io/i-love-col/about/images/book${pageNum}.png`));
        }

        try {
            await Promise.all(loadPromises);
            console.log('所有圖片載入完成');
            this.hideLoadingModal();
        } catch (error) {
            console.error('圖片載入失敗:', error);
            this.hideLoadingModal();
            alert('部分圖片載入失敗，但您仍可以閱讀故事書。');
        }
    }

    // 載入單張圖片
    loadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => reject(new Error(`Failed to load ${src}`));
            img.src = src;
        });
    }

    // 打開書本
    openBook() {
        document.getElementById('bookCover').style.display = 'none';
        document.getElementById('bookReader').style.display = 'block';
        document.getElementById('toolbar').style.display = 'flex';

        this.currentPage = 1;
        this.updatePages();
        this.updateControls();
    }

    // 更新頁面顯示
    updatePages() {
        const currentPageImage = document.getElementById('currentPageImage');

        // 顯示當前頁面
        if (this.currentPage <= this.totalPages) {
            const pageNum = this.currentPage.toString().padStart(2, '0');
            currentPageImage.src = `https://future801113.github.io/i-love-col/about/images/book${pageNum}.png`;
            currentPageImage.alt = `故事第 ${this.currentPage} 頁`;
        }

        // 添加翻頁動畫
        this.addPageAnimation();

        // 更新進度
        this.updateProgress();
    }

    // 添加翻頁動畫
    addPageAnimation() {
        const pages = document.querySelectorAll('.page');
        pages.forEach(page => {
            page.classList.remove('page-transition-slide', 'page-transition-fade', 'page-transition-flip');
            page.classList.add(`page-transition-${this.pageAnimation}`);
        });
    }

    // 更新頁碼顯示
    updatePageNumbers() {
        const leftPageNumber = document.getElementById('leftPageNumber');
        const rightPageNumber = document.getElementById('rightPageNumber');

        if (this.showPageNumbers) {
            leftPageNumber.textContent = this.currentPage;
            leftPageNumber.style.display = 'block';
        } else {
            leftPageNumber.style.display = 'none';
        }

        // 隱藏右頁頁碼
        rightPageNumber.style.display = 'none';
    }

    // 更新控制按鈕
    updateControls() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const currentPageInfo = document.getElementById('currentPageInfo');

        // 更新按鈕狀態
        prevBtn.disabled = this.currentPage <= 1;
        nextBtn.disabled = this.currentPage >= this.totalPages;

        // 更新頁面資訊
        currentPageInfo.textContent = `第 ${this.currentPage} 頁`;
    }

    // 更新進度條
    updateProgress() {
        const progress = (this.currentPage / this.totalPages) * 100;
        document.getElementById('progressFill').style.width = progress + '%';
    }

    // 上一頁
    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage -= 1; // 每次翻一頁
            this.updatePages();
            this.updateControls();
        }
    }

    // 下一頁
    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.currentPage += 1; // 每次翻一頁
            this.updatePages();
            this.updateControls();
        }
    }

    // 跳到指定頁面
    goToPage(pageNumber) {
        if (pageNumber >= 1 && pageNumber <= this.totalPages) {
            this.currentPage = pageNumber;
            this.updatePages();
            this.updateControls();
        }
    }

    // 回到封面
    backToCover() {
        document.getElementById('bookReader').style.display = 'none';
        document.getElementById('toolbar').style.display = 'none';
        document.getElementById('bookCover').style.display = 'block';
    }





    // 顯示分享面板
    showSharePanel() {
        document.getElementById('sharePanel').style.display = 'flex';
    }

    // 隱藏分享面板
    hideSharePanel() {
        document.getElementById('sharePanel').style.display = 'none';
    }

    // 分享故事
    shareStory(platform) {
        const url = 'https://future801113.github.io/i-love-col/about';
        const text = '來看看我的故事書，裡面有精彩的內容！';

        switch (platform) {
            case 'line':
                window.open(`https://social-plugins.line.me/lineit/share?url=${encodeURIComponent(url)}`);
                break;
            case 'copy':
                navigator.clipboard.writeText(url).then(() => {
                    alert('連結已複製到剪貼簿！');
                });
                break;
        }

        this.hideSharePanel();
    }



    // 顯示載入提示
    showLoadingModal() {
        document.getElementById('loadingModal').style.display = 'flex';
    }

    // 隱藏載入提示
    hideLoadingModal() {
        document.getElementById('loadingModal').style.display = 'none';
    }
}

// 初始化故事書
const storyBook = new StoryBook();