# PowerPOI
**Project Leader** : Prof. Chia-Hui Chang
**Team members** : Hsiu-Min Chuang, Ting-Yao Kao, Chung-Ting Cheng, Ya-Yun Huang, Guo-Bin Chang,
Kai-Chien Yang, Chien-Fu Ling, Yuan-Hao Lin, Hung-Wei Chang
**Abstract**
With the popularity of mobile devices and smartphones, we have witnessed rapid growth in mobile applications and services, especially in location-based services (LBS). According to a mobile marketing survey, maps/location searches are among the most utilized services on smartphones. Points of interest (POIs), such as stores, shops, gas stations, parking lots, and bus stops, are particularly important for maps/location searches. Existing map services such as Google Maps and Wikimapia are constructed manually either professionally or with crowdsourcing. However, manual annotation is costly and limited in current POI search services. With the abundance of information on the Web, many business POIs can be extracted from the Web.
In this project, we focus on automatically constructing a POI database to enable business POI map searches. We propose techniques that are required to construct a POI database, including focused crawling, information extraction, and information retrieval techniques. We first crawl Yellow Page websites to obtain vocabularies of business names. These vocabularies are then investigated with search engines to obtain sentences containing these business names from search snippets in order to train a business-name recognition model. To extract POIs scattered across the Web, we propose a query-based crawler to find address-bearing pages that might be used to extract addresses and business names. We crawled 1.25 million distinct POI pairs scattered across the Web and implemented a POI search service via Apache Lucent's search platform, called Solr. The experimental results demonstrate that the proposed geographical information retrieval model outperforms Wikimapia and a commercial app called "What's the Number?"
[: (in Chinese)](https://www.google.com/url?q=https%3A%2F%2Fpowerpoi.widm.csie.ncu.edu.tw%2Fdashboard&sa=D&sntz=1&usg=AOvVaw0TgHtKfYowWmR72-XiMMVi)
[![https://itunes.apple.com/tw/app/id1057491998](https://lh3.googleusercontent.com/sitesv/AA5AbUBIdio1oHApKTn285qJDhYoXMYYl7BY7DETe1mS8SNRkjAs-_y7iYWpfMBBJfX0xEEpLxh1uVUkjTKLAQQWdH10VEJNjab-X0iFcTVyzY5beCuCT5OIQkJA-ZcXUYeTyFjZpUYCV_2HFdb180UBQyaRQNUXEhq_3uq68EHaH_kfQ5IjTMbolmEQwPrKMUZK-Sw=w1280)](https://www.google.com/url?q=https%3A%2F%2Fitunes.apple.com%2Ftw%2Fapp%2Fid1057491998&sa=D&sntz=1&usg=AOvVaw3dpTar0dnttCxOr5087pd-)
> Image-1:
>
> ### 1. 圖片類型與主旨
> 這是一張截取自 Apple iTunes (App Store) 網頁介面的軟體產品描述區塊，展示了名為「疾疾店家現身」應用程式的圖示與功能介紹文字。
>
> ### 2. 核心視覺元素與文字
> *   **主要物件/特徵：**
>     *   **App 圖示：** 位於左側，呈圓角正方形，背景為亮紫色。圖示中心為白色房屋形狀輪廓，內嵌一個紫色的中文「店」字。
>     *   **文字內容：** 位於右側，包含一個深灰色標題與兩段淺灰色內文。
>     *   **頁首提示：** 位於畫面最頂部的一行細小灰色文字。
> *   **提取文字 (OCR)：**
>     *   **頂部提示：** Open iTunes to buy and download apps.
>     *   **標題：** Description
>     *   **段落一：** 疾疾店家現身 (PowerPOI) 讓您對於「找店家」這件事情變得簡單！去到外地時人生地不熟，東問西問還找不到店家，您還在擔心這類問題嗎？就讓疾疾店家現身讓您三秒化身在地人！
>     *   **段落二：** 資料內容包含了全台灣各式各樣的店家，食衣住行應有盡有，並結合地圖服務，介面簡單易懂，不需繁雜的使用教學，輕鬆讓您一手掌握！
>
> ### 3. 綜合場景敘述
> 這張圖片呈現了典型的行動應用程式商店網頁版佈局。畫面左側以鮮明的紫色 App 圖示作為視覺焦點，該圖示結合了房屋與「店」字的意象，直觀地傳達了該程式與商店搜尋相關的功能。整體背景為純白色，營造出乾淨、專業的 UI 設計感。
>
> 在空間佈局上，資訊由左至右、由上而下排列。右側的「Description（描述）」區塊詳細說明了產品名稱「疾疾店家現身 (PowerPOI)」及其核心價值，強調解決使用者在陌生環境尋找店家的痛點。內文提到該應用程式涵蓋全台灣的食衣住行資訊，並具備地圖整合功能與簡單直覺的操作介面。整個畫面反映出一個典型的電商或軟體下載頁面的局部視圖。

[**Download PowerPOI (疾疾店家現身) APP from Apple Store**](https://www.google.com/url?q=https%3A%2F%2Fitunes.apple.com%2Ftw%2Fapp%2Fid1057491998&sa=D&sntz=1&usg=AOvVaw3dpTar0dnttCxOr5087pd-)
**Publication**
  * H.-M. Chuang, C.-H. Chang, Ting-Yao Kao, Chung-Ting Cheng and Ya-Yun Huang, K.-P. Cheong, [Enabling Maps/Location Searches on Mobile Devices: Constructing a POI Database via Focused Crawling and Information Extraction](http://www.google.com/url?q=http%3A%2F%2Fwww.tandfonline.com%2Fdoi%2Fpdf%2F10.1080%2F13658816.2015.1133820&sa=D&sntz=1&usg=AOvVaw2FpGoHb11sbU_2roMnclis), International Journal of Geographical Information Science, Volume 30, Issue 7, pp 1405-1425, 2016.
  * C.-H. Chang, H.-M. Chuang, C.-Y. Huang, Y.-S. Su, S.-Y. Li. [Enhancing POI Search on Maps via Online Address Extraction and Associated Information Extraction](http://www.google.com/url?q=http%3A%2F%2Flink.springer.com%2Farticle%2F10.1007%252Fs10489-015-0707-5&sa=D&sntz=1&usg=AOvVaw1Fb21IPlPSRZNPj08uiqJa), Applied Intelligence, Volume 44, [Issue 3](http://www.google.com/url?q=http%3A%2F%2Flink.springer.com%2Fjournal%2F10489%2F44%2F3%2Fpage%2F1&sa=D&sntz=1&usg=AOvVaw1YS-DldVUYmTJdHcOOn63e), pp 539–556, 2015.
  * H.-M. Chuang and C.-H. Chang, Verification of POI and Location Pairs via Weakly Labeled Web Data. LocWeb (WWW workshop), Italy, May 18-22, 2015. ()
  * H.-M. Chuang, C.-H. Chang, and T.-Y. Kao, Effective Web Crawling for Chinese Addresses and Associated Information, The 15th International Conference on Electronic Commerce and Web Technologies (ECWeb 2014), Munich, Germany, Sep. 1-5, 2014. ()
  * C.-H. Chang, C.-Y. Huang, and Y.-Y. Su: On Chinese Postal Address and Associated Information Extraction, [JSAI IOS: Special Session on Web Intelligence & Data Mining, June 13-15, 2012.](http://www.google.com/url?q=http%3A%2F%2Fwww.ai-gakkai.or.jp%2Fconf%2F2012%2F%3Fpage_id%3D154&sa=D&sntz=1&usg=AOvVaw2U4kzdp7nUZY9giSJhS8-w)
  * C.-H. Chang and S.-Y. Lee. MapMarker: Extraction of Postal Addresses And Associated Information for General Web Pages, [IEEE/WIC/ACM International Joint Conferences on Web Intelligence and Intelligent Agent Technologies (WI-IAT 2010)](http://www.google.com/url?q=http%3A%2F%2Fwww.yorku.ca%2Fwiiat10%2F&sa=D&sntz=1&usg=AOvVaw2zwJ10tSMN8JHIvkRqVxps), Toronto, Canada. Sep. 1-3, 2010.


**Related Technologies (Provide the training datasets for download)**
  * Address extraction: ( for Chinese; [Collection](https://www.google.com/url?q=https%3A%2F%2Fweb.cs.dal.ca%2F~zyu%2Fresearch%2F&sa=D&sntz=1&usg=AOvVaw04qptrRsKlE0XiyL8OggzV) for English provided by Z. Yu)
  * Business-name recognition: ()
  * Address-POI name pairing: (, window size=100)
  * Address-POI name verification: ()


**Acknowledgement**
This project is partially sponsored by the Ministry of Science and Technology in Taiwan under grant MOST103-2221-E-008-094
