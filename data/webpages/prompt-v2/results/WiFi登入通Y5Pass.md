# WiFi登入通/Y5Pass
**Team members** : Yu-Wei Hu (胡育維) Pei-Ru (湯珮茹) Chia-Hui Chang
**Abstract**
Taiwan is one of the top countries to provide free WiFi access points for all visitors. However, connecting to open WiFi (obtaining an IP) usually takes long time when there are a lot of users around. Besides, a second step to pass through the authentication with users' accounts and passwords also require users' intervention since most WiFi login systems do not allow the browsers to remember the account and passwords. In this project, we developed an Android App, called WiFiPass, to automatically sign in an open WiFi network on behalf of the user via executing a login script recorded when users login the WiFi system for the first time.
智慧型手機經過五年才達到第一個十億的出貨量，但是只花了兩年就達到第二個十億的出貨量，在2014單一年即有十億的出貨量。爆增的行動裝置也使得行動數據流量不斷地創下新高，因而導致3G網路壅塞，也因此電信業者不得不積極佈建Wi-Fi無線熱點來疏解網路流量。根據網路熱點營運商iPass提出的全球性公共熱點的調查報告，全球公共Wi-Fi熱點到了2014年年底預計會有4,770萬個，平均每150個人共享一個熱點，但到了2018年將會增加到3.4億個，平均每20個人就有一個熱點，熱點數量在四年內將會成長7倍。
根據Informa的統計，現今大部分智慧型手機的數據流量是藉由Wi-Fi無線網路來傳遞，這反應現實社會大部份使用者即使擁有3G或4G的行動寬頻，但基於成本的考量，仍會尋找免費的Wi-Fi無線網路以節省個人支出。另一方面，許多電信廠商也透過Wi-Fi熱點的佈建，來疏解3G的壅塞。例如西班牙的FON和美國Comcast兩家公司合力推出的社區熱點，即是讓全球公共熱點數量大幅增長的一大推手。不過社區熱點只限於同一家電信廠商的會員登入使用，透過EAP-SIM機制，提供其他該電信廠商網路服務的使用者無縫切換至無線熱點。
相對於其他國家，台灣政府一開始在公共Wi-Fi無線網路的建置上，有著更為開放的政策。開放式無線網路成為縣市政府的共同推行的政策，除iTaiwan之外，六都直轄市相繼推出TPEFree、iTaiChung、iKaohsiung、iHsinchui、Taoyuan；而學術網路TANETRoaming也致力於校園無線網路的共用，提供學生跨校園的漫遊。不過這項有利於使用者的服務，如果一直由縣市政府買單，對於經費有限的縣市政府，很難長期提供這項便民的措施。因此引入廣告行銷、建構可行的經濟循環，是技術層面之外在營運模式上可以考慮的要素。
引入廣告的營運模式是相當自然的發展。早期無線電視節目，近代網路服務如Google搜尋、臉書、LINE免費APP等服務等，已經應用的相當成熟。但是在電信服務上一直處於向消費者付費的B2C (Business to Consumer)營運模式，很少有系統業者會去開拓與廣告業務相關的B2B (Business to Business)系統。國內只有統一7-11的電信服務，在全省四千多家門市提供Wi-Fi上網服務，提供每日3次免費30分鐘上網，藉以吸引顧客提高回店率，也透過消費者的行動裝置推播廣告、進行產品的行銷。
而就國內目前的情況，即使政府提供許多公共Wi-Fi無線網路，使用者的上網體驗仍然有相當大的改進空間。不少人一坐下來即開始搜尋無線網路，詢問登入密碼。在人潮擁擠之處，光是取得IP都要耗費數十秒之久，更遑論等待登入頁面出現的時間，以及密碼輸入錯誤或是忘記密碼等其他問題，因此解決使用者登入的順暢度是重要的問題。而更進階的期待，則是能做到透過Wi-Fi網路達到B2B的商業模式以求系統的永續。
我們提出一個Wi-Fi分享平台以及其搭配的APP，稱為「Wi-Fi登入通」。使用者可以透過APP (1)連網並儲存上鎖Wi-Fi的密碼、(2)替需要進行網頁登入的Wi-Fi熱點製作登入腳本並(3)儲存、管理以及分享密碼或者登入腳本並透過(4)計點機制賺取上網時間或者免費上網。透過Wi-Fi分享平台我們可以替使用者節省行動上網的費用、替分享者獲得利益(替店家行銷，客戶統計或分析)、創造與使用者的接觸機會和替電信業者舒緩行動上網流量的壅塞。
![](https://lh3.googleusercontent.com/sitesv/AA5AbUBdJd9zA8IFcP00z2Di0Z6fyzXOiGGdYTwqp5FlONFnUvRfIW8dQPTJJcpLPtcjpt5ZUadIjbR8EqO-R_ltkRPGTkIr7tfqdRfol-OURbMQ6k2nzG33HVyfWAF6zXmZxtFqpeSMfdP1713bHTqxN-N-EV8uc6wh2Ug9uJ1Flf1srPB1yT4OLtWV_90LXz95ji2BjHjp=w1280)
> Image-1:
>
> ### 1. 圖片類型與主旨
> 這是一張 Google Play 商店應用程式下載頁面的介面截圖，展示了名為「Wi-Fi 登入通 (Wi-Fi Pass)」的 Android 工具類 App 資訊與預覽圖。
>
> ### 2. 核心視覺元素與文字
> *   **主要物件/特徵：**
>     *   **App 圖示：** 位於左上角，為綠色圓角矩形背景，包含 Android 機器人頭部標誌，上方有「Wi-Fi」字樣，下方有「PASS」字樣。
>     *   **評分與按鈕：** 右側顯示星級評分、評論數（22人）以及綠色的「Install (安裝)」按鈕。
>     *   **警示標誌：** 一個紅色三角形感嘆號，提示設備不相容。
>     *   **應用程式預覽圖：** 底部排列三個手機介面截圖，顯示 Wi-Fi 熱點列表與中央大學無線網路服務的登入介面。
> *   **提取文字 (OCR)：**
>     *   **標題：** Wi-Fi登入通 (Wi-Fi Pass)
>     *   **開發者與分類：** WIDM lab, Tools
>     *   **警告訊息：** You don't have any devices
>     *   **功能按鈕：** Add to Wishlist, Install
>     *   **預覽圖內文字：** 可用的Wi-Fi熱點、TANetRoaming、NCUWL、中央大學無線網路服務、使用者登入 (User Login)。
>
> ### 3. 綜合場景敘述
> 這張圖片呈現了典型早期 Android 版本的 Google Play 商店介面。畫面上方橫向排列著 App 的核心資訊：左側為醒目的綠色圖示，右側則由上而下標示了應用程式名稱、開發團隊「WIDM lab」以及功能分類。在安裝按鈕上方，系統顯示一條警示語「You don't have any devices」，表明當前登入的帳戶尚未連結任何可安裝此程式的相容裝置。
>
> 畫面下方提供了三張應用程式的操作截圖，展示了其實際功能。介面顯示該程式具備掃描周邊 Wi-Fi 熱點的功能，清單中列出了如 TANetRoaming 與 NCUWL 等校園常見網路，並以綠色進度條與圖示顯示連線狀態與訊號強度。最右側的截圖則顯示一個彈出式視窗，提示為「中央大學無線網路服務」的使用者登入介面，說明該 App 旨在協助使用者簡化校園無線網路的驗證流程。

[Download WiFiPass (WiFi登入通) APP from Google Play](https://play.google.com/store/apps/details?id=com.project.twwifipass&hl=en)
![](https://lh3.googleusercontent.com/sitesv/AA5AbUBNCbEYeiiMEsVEwLNiGoaunwSKQjmJElWACwx6KPCvEm8csiyV2lOiDLytcpJN-rAkHBbjcm13I0NMq5OvtbN3fzFO-QfMycbSftQZduuITsaUbSkMrq-5mmKm78Fqr7LxbVoNmORaAA55kAzqMv4oGOR7uBCAevgnTt67F1biogtZ3NCrpA-ZG2can-4-66EjPQ=w1280)
> Image-2:
>
> 根據您的要求，我已完成對該圖片的結構化分析與無障礙掃描，以下是詳細報告：
>
> ### 1. 圖片類型與主旨
> 這是一張 Android 手機系統（Google Play 商店環境）中應用程式安裝頁面的 UI 截圖，展示了名為「Y5PASS」的 App 資訊。
>
> ### 2. 核心視覺元素與文字
> *   **主要物件/特徵：**
>     *   **頂部狀態列：** 包含鬧鐘、同步、Wi-Fi、收訊、電量（74%）與時間（21:42）圖示。
>     *   **應用程式橫幅：** 藍綠色背景，左側有巨大的白色圓環與圓點組成的 Logo 局部。
>     *   **應用程式圖示：** 位於左下角，由藍綠色的同心圓環與中心點構成，類似無線訊號標誌。
>     *   **控制按鈕：** 底部有兩個橫向排列的按鈕，分別為白底綠框的「解除安裝」與綠底白字的「開啟」。
>     *   **操作圖示：** 頂部橫幅右側有搜尋（放大鏡）與更多（三個垂直點）圖示。
>
> *   **提取文字 (OCR)：**
>     *   應用程式名稱：Y5PASS
>     *   開發者/提供者：WIDM lab
>     *   分級資訊：3+
>     *   按鈕文字：解除安裝、開啟
>     *   狀態列時間：21:42
>     *   狀態列百分比：74%
>
> ### 3. 綜合場景敘述
> 這張圖片呈現了一個行動裝置應用程式在應用程式商店中的詳情介面。畫面分為上下兩大區塊：上半部為藍綠色調的品牌視覺橫幅，左側裝飾有放大的 App 標誌圖案，右側則標示了黑色字體的應用程式名稱「Y5PASS」，並配有搜尋與設置的功能鍵。
>
> 下半部則呈現了具體的應用程式資訊與互動選項。左側顯示了完整的 App Logo，右側則由上而下排列著名稱「Y5PASS」、開發團隊「WIDM lab」以及分級標籤。最下方提供了兩個主要的互動按鈕，左側為「解除安裝」，右側為已反白強調的「開啟」，顯示該應用程式目前已成功安裝於裝置中。整體佈局簡潔直觀，符合標準的行動介面設計規範。

[Download Y5Pass APP from Google Play](https://play.google.com/store/apps/details?id=tw.edu.ncu.wifipass&hl=en)
