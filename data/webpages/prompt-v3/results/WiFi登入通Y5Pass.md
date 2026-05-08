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
![](https://lh3.googleusercontent.com/sitesv/AA5AbUBmI43tgPUx0IQSFepqyjpmjD-M9oto-9hmMEU5D0Xy3LaeMYtvJYyGF_d66JD7bPMTfkyrjYVnCh1ZO57OpXq-HahBxcSicmhebTesyGnoQaBj2a5oKcGxkHqod9Scdyu5BDA1zniaTcz50cXUSpCmHg7FNc4lUijGgx1scTROLeMCO9kaoOdO14sgVAy3l7xlOqML=w1280)
> # Image-1
>
> **圖片摘要：**
> Wi-Fi登入通應用程式商店頁面，上方顯示應用程式圖示與名稱，下方並列展示三個包含熱點清單與登入介面的操作示範截圖。
>
> **主要元素：**
> 1. 實體: Wi-Fi登入通, WIDM lab, Google Play, Android, 中央大學無線網路服務
> 2. OCR文字:
> Wi-Fi登入通 (Wi-Fi Pass)
> WIDM lab Tools
> 22
> 3+
> You don't have any devices
> Add to Wishlist
> Install
> Wi-Fi登入通
> 可用的Wi-Fi熱點
> Wi-Fi名稱 狀態 訊號
> TANetRoaming
> 已連線(限制連線)
> NCUWL
> OPEN
> Wi-Fi登入通
> 可用的Wi-Fi熱點
> Wi-Fi名稱 狀態 訊號
> NCUWL
> 連線中
> dlink@dblab
> WPA
> 中央大學無線網路服務
> 使用者登入
> User Login
> username
> 3. 主題標籤: 網路工具, 行動應用程式, Wi-Fi認證, 中央大學
>
> **頁面關聯：**
> 本圖片為 Wi-Fi登入通 應用程式於 Google Play 商店的產品介紹頁面。

[Download WiFiPass (WiFi登入通) APP from Google Play](https://play.google.com/store/apps/details?id=com.project.twwifipass&hl=en)
![](https://lh3.googleusercontent.com/sitesv/AA5AbUDdhVMFt_WrCDrRMasP4sRhrEalKfTgmD0D_VR4D62f6Q7Er7RewZ2gNoxpBR3nowCdKL4wZ6UyZaajlgXs9mRVJGEUGBmxQsIWGVr5RbC0GamE7tKdnkrIFKlWPP00yYdzJUgjxlKGKvp_4wAPlx0S7tx5DkBsl72h7Cfg5bRcz9Zlp2EcO5y11vTzfYBOe7XE1A=w1280)
> # Image-2
>
> **圖片摘要：**
> Y5PASS 應用程式介面顯示藍色圖示，下方排列解除安裝與開啟按鈕。
>
> **主要元素：**
> 1. 實體: Y5PASS, WIDM lab, 應用程式圖示, 解除安裝按鈕, 開啟按鈕
> 2. OCR文字:
> Y5PASS
> Y5PASS
> WIDM lab
> 3+
> 解除安裝
> 開啟
> 3. 主題標籤: 軟體應用, 行動裝置, Y5PASS, WIDM lab
>
> **頁面關聯：**
> 本圖為 Google Play 商店中的 Y5PASS 產品頁面，由 WIDM lab 開發。

[Download Y5Pass APP from Google Play](https://play.google.com/store/apps/details?id=tw.edu.ncu.wifipass&hl=en)
