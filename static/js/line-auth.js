// LINE認証用の共通JavaScriptファイル
class LineAuth {
  constructor(liffId) {
    this.liffId = liffId;
    this.lineId = null;
    this.profile = null;
    this.isInitialized = false;
  }

  // LIFFの初期化
  async init() {
    try {
      await liff.init({ liffId: this.liffId });
      this.isInitialized = true;
      
      if (!liff.isLoggedIn()) {
        // ログイン後に現在のページに戻るように設定
        liff.login({
          redirectUri: window.location.href
        });
        return false;
      } else {
        // ログイン済みの場合はプロフィールを取得
        this.profile = await liff.getProfile();
        this.lineId = this.profile.userId;
        console.log('LINE ID:', this.lineId);
        console.log('Profile:', this.profile);
        return true;
      }
    } catch (error) {
      console.error('LIFF初期化エラー:', error);
      return false;
    }
  }

  // line_idを取得
  getLineId() {
    return this.lineId;
  }

  // プロフィールを取得
  getProfile() {
    return this.profile;
  }

  // ログイン状態をチェック
  isLoggedIn() {
    return this.isInitialized && this.lineId !== null;
  }

  // URLにline_idパラメータを追加
  addLineIdToUrl(url) {
    if (!this.lineId) return url;
    
    const separator = url.includes('?') ? '&' : '?';
    return url + separator + 'line_id=' + this.lineId;
  }

  // 要素のhref属性にline_idを追加
  addLineIdToElement(element, baseUrl) {
    if (!this.lineId) return;
    
    const url = this.addLineIdToUrl(baseUrl);
    element.href = url;
  }

  // フォームのaction属性にline_idを追加
  addLineIdToForm(form, baseUrl) {
    if (!this.lineId) return;
    
    const url = this.addLineIdToUrl(baseUrl);
    form.action = url;
  }

  // ショップリンクを更新
  updateShopLinks() {
    if (!this.lineId) return;
    
    const links = document.querySelectorAll(".shop-product-link");
    links.forEach((link) => {
      const shopId = link.dataset.shopId;
      if (shopId) {
        const baseUrl = `/line/product/${shopId}/`;
        this.addLineIdToElement(link, baseUrl);
      }
    });
  }

  // カートリンクを更新
  updateCartLinks() {
    if (!this.lineId) return;
    
    const links = document.querySelectorAll(".cart-link");
    links.forEach((link) => {
      this.addLineIdToElement(link, '/line/cart/');
    });
    // バッジ初期化（cart-link 内の badge があれば維持）
  }

  // 注文履歴リンクを更新
  updateOrderHistoryLinks() {
    if (!this.lineId) return;
    
    const links = document.querySelectorAll(".order-history-link");
    links.forEach((link) => {
      this.addLineIdToElement(link, '/line/order/history/');
    });
  }

  // ログイン状態を表示
  showLoginStatus(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (this.isLoggedIn()) {
      container.innerHTML = `
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            <span class="font-semibold">LINEログイン済み</span>
          </div>
          <p class="text-sm mt-1">ユーザー名: ${this.profile.displayName}</p>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
            </svg>
            <span class="font-semibold">LINEログインが必要です</span>
          </div>
          <p class="text-sm mt-1">LINEアプリからアクセスしてください</p>
        </div>
      `;
    }
  }

  // ページ全体の初期化
  async initializePage(options = {}) {
    const isLoggedIn = await this.init();
    
    if (isLoggedIn) {
      // 各種リンクを更新
      if (options.updateShopLinks !== false) this.updateShopLinks();
      if (options.updateCartLinks !== false) this.updateCartLinks();
      if (options.updateOrderHistoryLinks !== false) this.updateOrderHistoryLinks();
      
      // ログイン状態を表示
      if (options.showLoginStatus !== false && options.loginStatusContainerId) {
        this.showLoginStatus(options.loginStatusContainerId);
      }
    }
    
    return isLoggedIn;
  }
}

// グローバル変数として利用可能にする
window.LineAuth = LineAuth; 