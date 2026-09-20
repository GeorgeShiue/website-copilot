# A/B 比較報告：min_word_threshold 效果驗證

**日期**: 2026-09-16 17:20
**站點**: nculab (https://sites.google.com/site/nculab/labintro)
**Baseline**: 無 min_word_threshold（PruningContentFilter 預設行為）
**Experiment**: min_word_threshold=10

## 總覽

| 指標 | 值 |
|------|-----|
| 頁面數（Baseline） | 52 |
| 頁面數（Experiment） | 52 |
| 總行數（Baseline） | 1434 |
| 總行數（Experiment） | 692 |
| 被移除行數 | 742 |

## 逐頁比較

### 頁面: `advisor`

**差異**: Baseline 26 行 → Experiment 3 行（移除 17 行）

**短文本雜訊（預期移除）**:

- 「# Advisor」（9 字）

**其他被移除行（需人工審核）**:

- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXHipUN8ErQU6ldBhojUvvf9YFvxAWkK9Zrj5FZpsY4iygt_WbFih8w4R-MvIOmITrvJqOcmROTYD3NzKR3XYhz1Of6F52TpceuWakIXbADniTy-SKDKo8lb4FlQ0Bvlcl6qrXl-ioikQ0e9dKZLxPl5ROO9xhnnto_gQkfOCRVPxEQc_nBMIMXpxTCyZENm1ZZ503624HnBPPj0zmzyQ-EW2SGmEk42U4DXZmSG6g=w1280)」（291 字）
- 「[0000-0002-1101-6337](https://www.google.com/url?q=https%3A%2F%2Forcid.org%2F0000-0002-1101-6337&sa=D&sntz=1&usg=AOvVaw3wPdd5E5dDAlO-souovXb2) chiahui@g.ncu.edu.tw」（163 字）
- 「+886-3-422-7151 #35302 Engineering Building 5, B302 Jhongda Road, Jhongli Dist. Taoyuan, Taiwan [個人首頁 / Personal Website](https://sites.google.com/site/jahuichang/)」（164 字）
- 「## Chia-Hui Chang (張嘉惠) Professor」（33 字）
- 「Dr. Chia-Hui Chang is a Professor in the Department of Computer Science and Information Engineering at National Central University, Taiwan. Her research focuses on web intelligence, natural language processing, agentic AI, and physical intelligence, with applications spanning conversational systems, educational AI, and human-computer interaction. She has been recognized in Stanford's Top 2% Scientists (Career Impact) rankings since 2021. Dr. Chang has served in leadership roles at major AI and NLP conferences, including General Chair for ROCLING 2021 and TAAI 2020, and Area Co-Chair for ACL 2017 and NAACL 2018. She served as President of the Taiwan Association for Artificial Intelligence (2020-2022) and the Association for Computational Linguistics and Chinese Language Processing (2019-2021). She has served as the Convener of the Intelligent Computing Discipline at Taiwan's National Science and Technology Council since 2024 and as Vice Convener of the Taiwan AI Center of Excellence since 2025. 張嘉惠博士是國立中央大學資訊工程系教授。她的研究方向包括Web智慧、自然語言處理、智慧代理 和實體機器人，應用領域涵蓋對話系統、教育人工智慧、法學和人機互動。自2021年以來，她一直位列史丹佛大學「頂尖2%科學家（職業影響力）」榜單。張博士曾在多個重要的人工智慧和自然語言處理會議上擔任領導職務，包括2021年ROCLING會議和2020年TAAI會議的總主席，以及2017年ACL會議和2018年NAACL會議的領域聯合主席。她曾任中華民國人工智慧學會會長（2020-2022年）和中華民國計算語言學與中文語言處理學會會長（2019-2021年）。自 2024 年起，她擔任台灣國家科學技術委員會智慧計算學科召集人；自 2025 年起，她擔任台灣人工智慧卓越中心副總召。」（1345 字）
- 「## SUSTAINABLE DEVELOPMENT GOALS」（32 字）
- 「- 3 Good Health and Well Being」（30 字）
- 「- 4 Quality Education」（21 字）
- 「- 5 Gender Equality」（19 字）
- 「- 9 Industry, Innovation and Infrastructure」（43 字）
- 「- 17 Partnerships for the Goals」（31 字）
- 「## FIELDS OF RESEARCH」（21 字）
- 「- Agentic AI and AI for Robotics」（32 字）
- 「- Machine Learning and Data Mining」（34 字）
- 「- Natural language understanding」（32 字）
- 「- Web intelligence」（18 字）

### 頁面: `labintro`

**差異**: Baseline 64 行 → Experiment 3 行（移除 35 行）

**短文本雜訊（預期移除）**:

- 「# 【最新消息】」（8 字）

**其他被移除行（需人工審核）**:

- 「## Web 智慧與資料探勘實驗室」（17 字）
- 「## Web Intelligence and Data Mining Laboratory」（46 字）
- 「### 【Research Interests】」（24 字）
- 「The Web Intelligence and Data Mining Laboratory at National Central University is dedicated to researching and developing intelligent systems to address complex real-world problems. Our research spans Web information extraction, machine learning, data mining, conversational agents, and knowledge graphs, with applications in web intelligence, information integration, legal AI, human-computer interaction, and educational systems. Check some of our projects below.」（465 字）
- 「- ​​​​​​​​Agentic AI, GUI Automation ​」（38 字）
- 「- ​Legal AI: Legal Judgement Predication, [Collision Care Guide chatbot](http://140.115.54.36:8230/login), Legigation Visualization」（131 字）
- 「- [​Meetup Event Extraction](https://eventgo.widm.csie.ncu.edu.tw), Point-of-Interest Extraction​」（97 字）
- 「- ​AI for Education: [EduACT](https://eduact.csie.ncu.edu.tw), Storybot」（71 字）
- 「- ​Smart campus: NCUFree, WiFiPass, Mobile Advertising​​」（56 字）
- 「- ​Web Information Extraction and Text Mining ​」（47 字）
- 「- ​Web intelligence: [Mobile Web Creator](http://140.115.54.44:8001/), Opinion mining for social study ​」（104 字）
- 「- Data Mining, e.g. ​Periodic pattern mining」（44 字）
- 「- ​Web data extraction: IEPAD, FiVaTech, [Data API Creator ](http://140.115.54.44:8001/)」（88 字）
- 「[校外奬項](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85?authuser=0)[校內奬項](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%85%A7%E5%A5%AC%E9%A0%85?authuser=0)[大專生專題研究](https://sites.google.com/site/nculab/news/%E5%9C%8B%E7%A7%91%E6%9C%83%E5%A4%A7%E5%B0%88%E7%94%9F%E5%B0%88%E9%A1%8C%E7%A0%94%E7%A9%B6%E8%A8%88%E7%95%AB?authuser=0)計畫 [研討會](https://sites.google.com/site/nculab/news/%E7%A0%94%E8%A8%8E%E6%9C%83?authuser=0)[徵人](https://sites.google.com/site/nculab/news/page-4?authuser=0)」（521 字）
- 「恭賀研究生 廖梓逸、簡資烜、張彣謙參加 [2025 NSF HDR (Scientific-Mood) ](https://indico.cern.ch/event/1610056/page/41091-taiwan-local-winners-announcement)榮獲台灣區第一名」（144 字）
- 「【恭賀】張嘉惠教授指導實驗室團隊大學部李倬安、資電學士班葉展維以[ #基於深度學習的跨多輸入法編輯器整合系統](https://www.facebook.com/hashtag/%E5%9F%BA%E6%96%BC%E6%B7%B1%E5%BA%A6%E5%AD%B8%E7%BF%92%E7%9A%84%E8%B7%A8%E5%A4%9A%E8%BC%B8%E5%85%A5%E6%B3%95%E7%B7%A8%E8%BC%AF%E5%99%A8%E6%95%B4%E5%90%88%E7%B3%BB%E7%B5%B1?__eep__=6&__cft__%5B0%5D=AZVRmV1EX5WZyKDHzDnMXs7C6NpV1-3qLhqguqRhKLPD-BMrfGVLSSJ5nmbomtcx0MwZzml311mEZ6a5gIwLKI4HxfGCyr4nPvnD3ubAlq_U6bdgYdd3pWIBXvMvkch8VI8HxDkdaXYFljIyhtpKczUQroqp5sv2a7xXTwreBkeJbQ&__tn__=*NK-R)榮獲國科會𝟏𝟏𝟑年度大專學生研究計畫研究創作獎!!! - June 2025」（512 字）
- 「恭喜！ 專題生[張勛皓、孫詠淳](https://sites.google.com/d/1BfrQkppHi-99yVwtdiVffZ5cO0r7nMcn/p/167PSuk63tIKcwCJ6WZG13sYm-bCOryMa/edit)參加【[2024和泰MaaS黑客松](https://ht-hackathon.tw/tw/home/)】獲冠軍、獨具匠心獎」（181 字）
- 「恭喜！ 專題生[李倬安、葉展維](https://sites.google.com/d/1BfrQkppHi-99yVwtdiVffZ5cO0r7nMcn/p/1xdXUQzCJ_-8-y2hnM2qrKmeruOZ5QwPP/edit)[參加第29屆人工智慧與應用研討會榮獲The Appier-Sponsored Award](https://taai2024.org/) - Dec. 2024」（200 字）
- 「恭喜！ [張嘉惠老師指導 黃懷萱 等同學 論文 獲選 ROCLING 2024 Best Paper Award](https://sites.google.com/site/nculab/news/%E6%81%AD%E5%96%9C-%E5%BC%B5%E5%98%89%E6%83%A0%E8%80%81%E5%B8%AB%E6%8C%87%E5%B0%8E-%E9%BB%83%E6%87%B7%E8%90%B1%E5%90%8C%E5%AD%B8%E8%AB%96%E6%96%87-%E7%8D%B2%E9%81%B8-rocling-2024-best-paper-award) - Oct. 2024」（308 字）
- 「恭喜！ 專題生張勛皓、沈哲寬、曾廷綸同學2024第29屆InnoServe大專校院資訊應用服務創新競賽【[資安技術組 第三名](https://www.youtube.com/watch?v=ZC3L94U0_sc)】- Nov. 2024」（120 字）
- 「恭喜！[張嘉惠老師指導 碩一生 許耀文同學及陳冠蓉同學以](https://sites.google.com/site/nculab/news/%E6%81%AD%E5%96%9C%E5%BC%B5%E5%98%89%E6%83%A0%E8%80%81%E5%B8%AB%E6%8C%87%E5%B0%8E-%E8%A8%B1%E8%80%80%E6%96%87-%E9%99%B3%E5%86%A0%E8%93%89%E5%90%8C%E5%AD%B8) ESGenius: 永續報告生成AI顧問 [入圍](https://sites.google.com/site/nculab/news/%E6%81%AD%E5%96%9C%E5%BC%B5%E5%98%89%E6%83%A0%E8%80%81%E5%B8%AB%E6%8C%87%E5%B0%8E-%E8%A8%B1%E8%80%80%E6%96%87-%E9%99%B3%E5%86%A0%E8%93%89%E5%90%8C%E5%AD%B8)2024年「[中技社AI創意競賽](https://www.ctci.org.tw/8838/talent/41184/45319/45320/)」決賽」（529 字）
- 「[【 人工智慧浪潮下之資訊科學與數位學習之變革與挑戰】論壇](https://sites.google.com/site/nculab/news/%E4%BA%BA%E5%B7%A5%E6%99%BA%E6%85%A7%E6%B5%AA%E6%BD%AE%E4%B8%8B%E4%B9%8B%E8%B3%87%E8%A8%8A%E7%A7%91%E5%AD%B8%E8%88%87%E6%95%B8%E4%BD%8D%E5%AD%B8%E7%BF%92%E4%B9%8B%E8%AE%8A%E9%9D%A9%E8%88%87%E6%8C%91%E6%88%B0%E8%AB%96%E5%A3%87) - Oct. 4-5, 2024」（316 字）
- 「賀！實驗室團隊參與[2024 法律x 法遵科技黑客松 -獲得 Lawsnote 法遵/公司治理特別獎](https://sites.google.com/site/nculab/news/2024-%E6%B3%95%E5%BE%8Bx-%E6%B3%95%E9%81%B5%E7%A7%91%E6%8A%80%E9%BB%91%E5%AE%A2%E6%9D%BE-lawsnote) - Aug. 31, 2024」（208 字）
- 「賀！[學士班葉展維同學 獲選2024 時代基金會 Epoch School實習計畫的參訪代表](https://sites.google.com/site/nculab/news/%E6%81%AD%E5%96%9C%E5%BC%B5%E5%98%89%E6%83%A0%E8%80%81%E5%B8%AB%E6%8C%87%E5%B0%8E-%E8%91%89%E5%B1%95%E7%B6%AD%E5%90%8C%E5%AD%B8)」（218 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQVw9wUts5dVoPOQ87kYnppgjtLaKQiRT-eQRYYq3JUOFmwzZfjpFUiUceKtLBPOUdwYe3ErfVJ4kNOtjMdVCRbjGnVey0qJypr2CKoO-4_5nw8YAUmThnjLcbZDlvN7VFTIpIn-TaYbT-pAUWqY2a6CbPEz3XplbK3iENI1OofNoxxG88cgmiPfyOvF1GM=w1280)」（247 字）
- 「[EduACT](https://eduact.csie.ncu.edu.tw)」（40 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQX9CDkdHsWVLvI_Y-f6MtOr4SrDhbJEPaiIAj5l5h1LHc7sDPuFOPTq4DnfLzetz9lZd7ScuQhYs6fN9aeZHf1XJIEU00BVhrC1E8pEPMuSt8FgX1PYLnxyX5moroo1jJR_RT3Wxtem5DLjCwNMp1Jg8VT9rMiZ3lax61g2xeqYxMrQ9v3w6REmeMPg73A=w1280)」（247 字）
- 「### Legal AI」（12 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUh6yuO-_qW0Z_BIuRC7bDel-lssvgFtm7Bepzme9LlS3vtbZfVGwO-1KH1tds228ix1BzV52wC9AzO3KcjogBy_vL6qTYAkEpzPI7lgAkESWkoIwMCpLiwQR5Ylxs7cnGcG3doih966usSyAOwwr7fbfSYNM8NhEcRgsuG2BbL9FEtIiQQdmb6YcdlD5nfDt_l7qU5IJh7w0tocFI=w1280)」（267 字）
- 「[EventGo!](https://eventgo.widm.csie.ncu.edu.tw)」（48 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUxUOO__8imlHvwE6CxCNQlo574DXgrl77u3pghrEOpa6lszI5pQyHovMvCZIb2aCRk7O0EObS9GumMD1ElIr-YwG35mDzDcwiHvEkJiCNQpUOMeCD7b0m5foxH4DzkhcGJ8p86MRyjeBq2BIlwRDnpCKWOP-5d2JDsi8bQtpfJzd2jqYlmVpo0UMB0vvjj87Ma3xiLX1uI7UBNZ1IHhblIUnW7apbqDVXrU9ZCUvQ=w1280)」（291 字）
- 「[Data API Creator](http://140.115.54.44:8001/)」（46 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUMU8DlBuAV9o7MxJdZ4xOyUwCRElNG4BAiaF9lYVDLAit8y-WJuRnaPqOVCceRuI4NVQkQ1-oJr-APXOrKpI80z_jhGSW5z5SMtnNDTvPgJ7ji5wSOu9v3YrxnzWJrvCb_YnawgEmIKVZQ0d0dubfTYdBIWc9tXv1BGye5IgaGCfvA5w-7psSfHjGxbRltFwlSeSlp5yODaU9u_nddTonZAFKEIxeMyfLba9e2ZxI=w1280)」（291 字）
- 「[Mobile Web Creator](http://140.115.54.44:8000/)」（48 字）

### 頁面: `members`

**差異**: Baseline 66 行 → Experiment 1 行（移除 43 行）

**短文本雜訊（預期移除）**:

- 「## Alumni」（9 字）

**其他被移除行（需人工審核）**:

- 「## Members」（10 字）
- 「## PHD Students & Project Assistants」（36 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQV10fuE8MoEK0anQyFfLeb8AunaLusaT2jdn2KXCLizLRRL1R00XyaC5j-qmleRg9uJerM90fWwDgGeh7828Exv4PgfEipV4A3IINpj9OCrmAssY07nNOUhBCOfZqo_Fmx5WtkoU0_p02JqlBSjKqiZ1JWX-xEcP_yqE3PSHDvYSfeaoyej_rKyJi_YBpJYKZzeTovTvoUuKyI-=w1280)」（264 字）
- 「林圓皓 Yuan-Hao Lin PHD Students NLP, Meetup Event Extraction, Named Entity Recognition, Event Extraction」（102 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWG2RielUVg-H5EJqNfhRJvK9bSQuXz8bpxfq32uN5VBkcCt6noS17r0sNn_DpkrhnP-yNVRLBV3C2MO8oRaxcGc6fmSbsPv9n8e0etNOk5Uobg5vHKvt1FcyZwcWCECcgxfuVqLWgXg2SjjfjShGkXUSgj8vVu-mElG4Qlw3B6YAdXeDp9EtukNauVIRspEN3hyrrwXyC94M_ryCZUGSsr3NGbZjr1E43UyKas=w1280)」（288 字）
- 「簡國峻 Kuo-Chun Chien PHD Students NLP, Named Entity Recognition, Legal AI」（71 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQVun2NFubOBwPDRGjNljcNuOsUlbkBL8AdSZ5WMMbQ-6B-p1OhopcbcXO7WHO5M4UlyKgH58Lfq0byj3e2wUlVY15TJMJQcZ6yrd0c5btuj3XD_7K2FRiVOYiWMzouZVugy1QvXdTKHQIQug9nEooGJFfDO_PzQnFEKfcORkscJlg1pEt22QpDcdjakxxYyR-hXMT3RoJPgfazliJwgXV2gyLpvWx5WX9RsIO5o6a8=w1280)」（291 字）
- 「李翊翎 Yi-Ling Lee ProjectAssistant Education : 國立中央大學網路學習科技研究所碩士 Specialty : 英語閱讀、網路學習 email：white52035@g.ncu.edu.tw」（114 字）
- 「## Master Students (碩二)」（23 字）
- 「[](https://sites.google.com/site/nculab/members#h.p_Vf-CDrVIdNSX)」（65 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQU5YYJ5TXQ03I_S-5BElurz-w3slQuA9qhq2mJ88woSqBaSx0bX1az5vojSA7hM3TdKcsEcP91ucpmENKb42mJfkFdh4BLMKC5be09m6Xt6U2s6wCtZUI5OHwB6os1Dv8T4upu8gZPzWpEY-mAE3jdq4_Ox2KMxl6XZV2ZnR1_eFglEFG1VW4QIeWxjwynW5x2h8pvP254N7HfK8cX_BH_K9GHEjzEHti7_yHaUlGg=w1280)」（291 字）
- 「龔若齊 Jo-ChiKung Master Students 半夜十點後不要打給我，因為我睡了...」（50 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXPetKipCT9vJrl5d2gTlYI9NdLlMPlrGKz_A6Di40EhF2hoMGPDMNzHIIfVl2uRM3ggVpk7tENtXWyTQWslCeIZbZf4gJ-SzhwZ5AnGK4alEJhtIBy2O5rX9_gKFlSS7Wi5WCk3TX-j1ke63nh3nEDeFd9BGMIz0fN5SHKSaB-oOxEuzQ4K8IJ2UtJbTBb_UsXB15PgM34kxFqLLjOnc4O0JJiwNUntnHF401AmAA=w1280)」（291 字）
- 「謝程偉 Cheng-Wei Hsieh Master Students NLP, Fact Checking, Web, Embedding model」（76 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUNX6oLlUUsnU0Xaac5enc5l8KqxoyCVW3_H1K00l5fsNVMYv6VpiWUDxWBWVmy0NsINOBWyCM7_ikG_8CDDWv1KjWX8FfmflOPsNmxDgO6-JfT2DfgSuPc0CSkX-1u3Q49VQFhoQQIq1BLjA8Vaps84ocv25YDI05myB9A7PZKSdmGQnY1bz8v4Fq2X5G-CbstwDHeTGiC6gB4HWwM-a0iAAp5flcDEx6sf8Fb=w1280)」（288 字）
- 「丁仕杰 Shi-Jie Ding Master Students NLP, Web, Space AI」（51 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXqsygGd8RT5lO-gH8eDzIM3S3q2nwVbBTY54m7S7CCv_07aQL8VTfUBwL2MDoNfiSwMKypeYdhbl7sRCrW-gHFEtRjbMFYBNWJfozCb6ry3kchk8ynN7ydqWZhuOAB1yvIKnbgq1mBaE0dlUhIbp-IEDTum9bDlR88cmMCm4Ne894_UP4BHl25UBkRsZ_jJLK4knrIcUSnr9IZk8KUMUVIAqMf6Q-tI1jCY0OL=w1280)」（288 字）
- 「黃懷萱 Huai-Hsuan Huang Master Students NLP, Web, Automatic Annotation」（67 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXiYPRtLPHFQUHZ3Rl48fcqHMNDGKF3CITaALs8TRIhTiz9kdIMDKbTNoDjoVD9CkR6jVhl0NAIq2PUj-DNZFGziuv2mlmMK9MFBs4BS4t2gwUmYupn_oxQ8rRnt0J3TpRCoEaPrkf-AJ2ry8cvWg-6SgYOJoj3-Gb_dITO5s9iZbBs7dDNI-zM5xyGCpns1pEiqQAQP-iAbrxduBe40YiSpSMz-5s75fbz7ZqNwuY=w1280)」（291 字）
- 「葉季儒 Chi-JuYeh Master Students NLP, web development, cloud programming」（69 字）
- 「## Master Students (碩一)」（23 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUGx3bQaVMP9mLYyIcFrS0Q7I1VdT4R3nqh3b06sjdVLboTAmn3VC6VfImutiix8f5cKpSskxrd5p5hfGMMsZZJ_ri_bZ6FrHZo0ksdcd4kJVw1iP4H2EnsClVhxO8UUtqt9iTO7w99287LvhvW_sBDVOIB8CWgkdyuBqHMu4l7sIlh3XI2FVyJfewD1NQ=w1280)」（247 字）
- 「陳冠蓉 Kuan-Jung, Chen Master Students NLP, Web| project : ESG, Eduact」（67 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQW44AdO7Oeg5Z9Mx6pLOUBUG99qjJFvmOomYjS4fZNzm-anP1bAuyXXytuo4BUnFiS-zpWqCB3DPXOKs5BPCWyRekmAutk7NSoneZCVhVL0xUPuSwftkGbWIcDLZq7yQT7dsvXV2PdXKLHfCf1NsJgY3RjdHqFKOLl7lJoL_a0Tz-8doE3Pb0KeY0iQWSU=w1280)」（247 字）
- 「許耀文 Yao-Wen Hsu Master Students ESG, LLMOps, Retrieval-augmented generation, Chain of Thought, Task Agents | Project: ESGenius: AI-Driven ESG Reporting Consultant」（162 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQVPRsCv2unb_59yRdD4KzMO6k_0fyRZaBLAzWIaRUtm0TXCZ8hbvLIEKJpoNLJzKuXVXOhKWzFk3Yubu7qR07vA_WX-JZIhv2Gtu4zE7h-wbJgFrOJVICLnb9d3MOO97bGk0m6UdGa7G0v2albDLd6wA3S9dgWbio0gMyCgWUGios9GMD9m_3XzvZcDJr8_RADKwT4inz3VNIFGMTNYKN6m306oSOWuJg_xDcThGBU=w1280)」（291 字）
- 「施冠宏 Guan-Hong Shi Master Students Fintech, Judgement correction」（63 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXX7aCMZ947hSMzyconIKbE7xTKTo_hAw16CHEoxCbndfH6-145k6bx6zSgpIP3SRzq7xWAWeLU_qSk8YX70uAdMUa5L-PTLhXP0XyPpBCp8Kc0ddJ7OYH0OIj5bmGlss9vkvRPuSMTH-kkm1PUvJ3Ceh17AFoxfup-eqoVIJErxJw2o9Re-vRI3E5bbOm4Q-yfdcALTi9yOGUg1HE6sIDZ0BwkWhliccHD52uWkk4=w1280)」（291 字）
- 「陳楷勲 Kai-Hsun Chen Master Students NLP, Web, Space AI, EduACT」（60 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXhR1lP6cb8epNR1AyrU2EYgVgh0fGiVpg3Ip2dGINYiJtOFHnpg8KW_xigOLjvqqb2TCmtU6P10bUbyDTjdjxPpjjy5vFhfZngQLUJWO_ACAihRaFusuBkMxDG-lqUGNOTAUpLs-KhUqFONwcjcb7fKi1CS5nuLbQwBmI-txwEUgJINPsI1I2dn4wBRoW247et1Rgal70rf3MoUgRVdT-NiwoYOeSgPfHtQLeA=w1280)」（288 字）
- 「陳柏安 Po-An Chen Master Students NLP, Fintech, Judgement correction」（65 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXdT1TO0jnkuF4xRTzfIfWQiT4QY6zX4zvb6oArXl2zDAFLPtup8t6RUOmsVlRjkHJWqzpwaCPINvX2-R4MbKhw7rolHs9-3MGbHsIcHCyOiVBkpesQ-4FVB4Vb7OZZZNzOsAVkgRvIIRw_OArCE6pHYo21IsPy9PBsdYeF6RMMAdDg7Ebq-aRsdzLYc9t1lveyD5DoP-fL3i9C9UamSyeaWgW_x6jkbKWXUZ_V=w1280)」（288 字）
- 「熊偉如 Leonard Valentino Jusuf Master Students Fintech, Judgement Correction」（73 字）
- 「[Thesis Advised](https://sites.google.com/site/nculab/publication/thesisadvised)」（80 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQVukUZj8NZ_5yDB4km2EqMwV9cTbUx3Vm-WjKMc6qlYOKvBmDnHEzDW2dHr-VSNGAsh0NAqD7-RxNH_AyzRXuIwTwKweglezCTfbyLu2ByVRDWnXY4MRRPUdRZZjg7D6fCrktY3qhGJqUFxtSlRnGn8WnxEDU666rt_MBYLoGFOr1j6XBVqZbzY8GpsKl6irkF9bnrS7KzclMTzvzmNdCQ30Kd57YjBOAGtHNk0KUI=w1280)」（291 字）
- 「黃冠傑 Guan-JieHuang Master Students」（33 字）
- 「"WIDM是你唯一的歸宿"」（13 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUoGwzYfSi1PG8-dvHfUHzf47GJkeNPmA75m6m0b6Umb1I4SL7xGcG0eQ9Y5oOhqG1Vo7t4BVvNvb7gkH3Vo74gponORbZx-8T9zPwksmK-wAHLDHT6tMxOx9PJeiNe9uo_Mxp7DbZDh5ZOfPW7wp272qaXUJZHI0g_xHNbd6QMlc7E6mr_myvHmOAu1MPcP4CNaHAJvRd8OxBig2bj6DIbWjlgZHyeLYVC3pos68E=w1280)」（291 字）
- 「黃淯銘 Yu-Ming Huang Master Students NLP, Event/Relation Extraction, Question Generation」（85 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQVSmjTr_omauFELH2MTEO7SI6tk08a1qzS2zIM7K9o33NOStZtll8JxIMd6lG52q_u-6KSJm6eun91ksqY6cDmU7Y4FXxQ3vd9ICvl5WSBeLjdqAUZy60VorrshmxqX2WXjMf1EBhkAQM1SiKxo8chUeOeyehyIpopSiH-NJJOt1t9-z26trhJTxh7zVMMLVOmu6QNPS4FRW9hGyXQ0tcoEi42KmdmY7rmjMjGN=w1280)」（288 字）
- 「洪閔昭 Min-Chao Hung Master Students NLP, Relation Extraction, Factchecking, Named Entity Recognition」（98 字）

### 頁面: `members_activities`

**差異**: Baseline 51 行 → Experiment 0 行（移除 32 行）

**短文本雜訊（預期移除）**:

- 「2020/7/18」（9 字）
- 「2017/7/14」（9 字）
- 「2017/4/4」（8 字）
- 「2014/9/26」（9 字）
- 「2014/9/23」（9 字）
- 「2014/4/2」（8 字）

**其他被移除行（需人工審核）**:

- 「## Activities」（13 字）
- 「[Album](https://www.google.com/url?q=https%3A%2F%2Fwww.flickr.com%2Fgp%2F187371809%40N06%2F91adf8&sa=D&sntz=1&usg=AOvVaw0wj30FvANaxN2VY2Bw6aSp)」（143 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQV2X-2PO3IOmkUpn1fc5iG5L8__olOhw7GSX0cdlW0kJ-he6VYiiNr0oqqS_UuJ-NH49eYs4pVGN9wglxxLfPCdT_cX8-PpuW33v9cglkuvJlXQ0-KEgqLX6opUOOI_PWd6KXkg5yMgV2Kw8pnPf4snGgNP78JB0mJvXHlWfOmjfC7WHCb1Rs2vhsCLOtCTdPaWDYwrC0MVSlqxJhF12dgOpWn-q82m-tzFE1pe=w1280)」（288 字）
- 「### 2025/1/16」（13 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQV2RuTOMJh1Hchjj3neHk-2n7O6SmKtYRvOrlRJcpipk5zATMcgH7WFGUzeoU42JAuepXFpkYEXah7dQjfn3EwZttneGGaTlBKy0-aj1wAffGyuGMi_Es3L2wsUSrDIltiFXGeSwxqXSnPiPbvy5AOrcBR45JzqAuTfl5Jq0IHLGXE7h6JFTsNrgARfOavqZHd72ZN7UlsQjx22tavortNRdJknFVrMpksu6R8W75Q=w1280)」（291 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXPhArmVQpdlzvyZxuiK73MblcYa9yV6jgoSuYYYzox4zth_J1YWL4Gz-Dq1s7s8HLqSatNKQuOhUPj-sJ43XNhIGpfSBVTxFZVfdf7koftbXIzxQIxz0ToqDOemhRESle1_pRhREdLiD8jvI1mnKPoKbJGVjrz11QExj6_nZX88OU3AWAF6P8_cOSugETGyLRAvMLh4RoZsGs27qXiSX7CfZxJ13aHihmEXDsF=w1280)」（288 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUvCX9U5r1A9GOBE5XxfaBI4MzPPEIKI4j4fI6FmXob9_riDntTGT3iTxyH3oidi-5O48u6yDav-ZsdhENF-U9CS_7TR_QU8nl6F2_6rLHxfJts6-mSmPR_ALfcKZ5ADTNzxCgMrlN70tAv74yFziD2g0FeVRuHPXQFuGyWQOV5ZA5I2TptXsrPu8rAjZLTnSauluKdCe0ptz3Qza6Bu_4wkbLwIkIVDt85ghWXOZQ=w1280)」（291 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQV_m9LE6miP8_DWD6o5SHVkSwSUZOM7t96Evd8ksIj7feeFAF1Zoks_pydsvLrqeAfv-xNu-zjZX9F7YvUidbkf80pZUwt-Z6pqmffwrMGotL4nFjbSxl8CSsdl5-UneMSs8OSHXBbkCrRw4JzMMgkTLeSqwE5N3TI8SCztcapTxr449NLHuzEM1BjCfPrsBCNSWeG0nj2DnIJrUCmqQ6UtSkAJq9nXm6RGZjz0=w1280)」（288 字）
- 「### 2023/6/2」（12 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQVkC1398z8_6D0SrL2KF5l3Akg8bgyg8WS2AhexvHgwj45tcNQ3F-0Ssn87luxNrJbUk6oKeIJPS5gp7pLsrhw7PsYpOETzlt-QbBmfPBfWyBNcyxu9cfiwgCPkxO9D2KUjJA-9cVxlhiYHoCtBprhNQ-v_m-quAuzABUoIdRABINPoOI2mA1xifSIbqLC4vP2zEwxuJ7DTvegGY_ZhAkAgLN36c5dzht9RaA=w1280)」（286 字）
- 「### 2022/8/18」（13 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQV1WUnrn7YBFoD1kDgSLVjGhICS09j5NMIqztyqJSWMnI-f4OR1FNfchoptamWD70D_3raO3nvigI-5kK6S5QMfm91gvwU7mk6DyiUU_Q_I578EpVdlAJv8xb4fi4x3lLUaTwPr-oExITlKQ9Pid4UM0AqbRDSfEwUmUnNKOya6HITT2H8L7fQZXZHcueUnnR5QOTr6JBvWXeJP-TbMviMmoJmc0ppReU3CG6dW=w1280)」（288 字）
- 「### 2022/3/31」（13 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQVmEhAJb5HMpxoE8RePhnVgQVwwFht-Lrd9G8qEGkHl-9PlIH2aP-uGmG0zL6_aWOsl_8cXhYbDuolj040BQBydO_3OotYU8wSkyHJdkdAUq3epaioaIzQjXo3sSQoQ-MtpsqvpIR-R7eXUi2NjocEFZ23OTJ-O1Lea5vQXYTvvD4GeIZbZf4o4Zi3c4WDLJqPNYEmPZXckInTFRT-6MMvxAKskywFkyTvJUGD03gk=w1280)」（291 字）
- 「### 2022/1/14」（13 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXTWBa2qC2U284V455XDFIdjkZTx2k1eiEhPsr9osxGtE0VNDYrXcLzT4hVWuU3t3BCicr8nx0MTsryi9BJJXT1Ji0XUx7E1FbGEJfArEo4Cn3RZL3qIxXJVi19Mz5YAkc0Upp_2jn8FWHbIUda7ThzLxf9XWQ3il6WaMLbJBaatpTilDC5z5s0MySAAjkQ96ARUt1NXVthzzvo-HI=w1280)」（267 字）
- 「### 2020/9/28」（13 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUiIahwtNlCvsiICEKw6Gy0zi6Six5q6aRiIvOAB-JRe-K2kgt-Z4obwhI-gz_0z8cjcmZ8DB6FrvaA7k6mPXeLjEcwGbNdDlQ4JAKwvXSrBwDQ3eiSmgQ32gcbUY9Np9Z33NsINIHv7OlqIpWHIjd9ha25FWv8CNak4h-j9i2YJ4WK5abbAf0u5Ky2IxiVAlOy5_a__CT51UvrtHc=w1280)」（267 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWlzxINvXmQRJdLrRAplfv1d_bGTLrbMUeAlIDkADd8jKb8LCDkicAWsjGfqFgkGl6Pd9B1YRwcm2qpsZpKDwPc0qOxZQkTZboA_GLzeopw5l-5q9TnoznjYjG53bDaLHmox33Dm-CHHQdebgH3ZpgdQ8tudP_lSHbeO_0-NTDptcZYkQsztcHhC3DmUQha8L-4GzLgpxtqOaQt=w1280)」（264 字）
- 「2019/11/20」（10 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWG_KLDfdQ_4M63uZJHi5MwkdnitDNWEKYp9th1974ph3UTtob4QMiQC9NqbadfsyO_NoGmyl6j8IiPoqIzGPbS990Jq5F-U2WrOMlAQjP8G4Yx19WdPgx_x8KdbLLlxaL-VIiW4WEE9L9CCA79wD-adq7V4q-yEj_tAwNFVkjZdyxQR2t1IS4mdh_WuwqjpPzXVmGG8GUq=w1280)」（260 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQVl0hwtJblTMVIZ6XTPRkoT5r8WHZsqndkeMac8aAT-XLmyJeZm7hlQ770OXLpJRk58hOIbq7aF-vgGOkR6PuEGhnrrs9b484xs1dkr27Zqwhbl6kwQAYM62CdwcvYvPLYJUL6WOcLDa2xMUYmatwYD7_tPQAfBfc5j1lc7fsAP2I4A4-PmcKRqYInso4bR_HcIsns1VHmL=w1280)」（260 字）
- 「![2014/9/26](https://lh3.googleusercontent.com/sitesv/AG8ngQVeywfueHIf613OowWSZ3VyNyL5i6aSksbg2qVzd46EOd2O-B0B7m74kwTkr2X1qQ4anH8mjqoGK-v8h-gL1Q17vIghOCmto4i_gpSwr0xbXGogArT3hpg52bNJBuJyxbR6umgrNz37HuXXRqgTXU-VNt6l3X-v3CdTx7qawMZxnxqMyYlY_Siu7FkJ6faU6O2PQzBDE_en=w1280)」（269 字）
- 「![2014年9月23日 ](https://lh3.googleusercontent.com/sitesv/AG8ngQVUgnaacfQERpKMU0f7dKmnA2sgJk63giIAnjsbdPYB_W60BmG2277sGdDRRxtMCtRuDusoqgDG63c-tFXUVNoeh2mz_o-O7-UDcKT5QXBiiR5BA7gOa-1_vuqvtaEHiH8kPnGDrbbX0t_POuqsGimstFTNeNTwaerQZ0OCn3Y6y3JWp8i2GScCuhTeertnMkQyiDJUgDgF=w1280)」（271 字）
- 「![2014年4月22日 ](https://lh3.googleusercontent.com/sitesv/AG8ngQUnzy2N56jEoIGMS95LTjOhW9DkRzLcL_tAFaOlssPRDPIHIMb4CIA28YeDw_EcrL_H4ZJxwCDnXzJk_iQLZodnbYCueCOYZzvgkirZs9-MxCk981xaSH-_dyIgHisWaCKoMH4nABQlnAxHnpYn8uXG88XAN5f4jHosFK7qkXKi34QPR-h1PmY8Wy4HNLknC2f-LJI4vKAV=w1280)」（271 字）

### 頁面: `members_letter-to-potential-students`

**差異**: Baseline 26 行 → Experiment 0 行（移除 16 行）

**短文本雜訊（預期移除）**:

- 「## 申請所需材料」（9 字）
- 「1. 學業成績單」（8 字）
- 「## 專題研究期待」（9 字）

**其他被移除行（需人工審核）**:

- 「# Prospective Students」（22 字）
- 「## 專題生/研究生找指導教授的說明」（18 字）
- 「## 研究方向與申請流程」（12 字）
- 「請仔細檢視LAB的研究領域及近期的發表論文，以確保你的研究意向與實驗室我們的研究活動相符。」（45 字）
- 「請通過電子郵件將以下材料發送給指導教授：」（20 字）
- 「1. 個人履歷（CV）含參與過的專案及成果」（21 字）
- 「1. 簡短的研究計書」（10 字）
- 「這些資料將幫助我們評估你的背景和研究潛力。」（21 字）
- 「## 面試與回覆政策」（10 字）
- 「1. 有關實驗室研究進行方式請先詢問助教及實驗室專題生。」（28 字）
- 「1. 如果有意加入實驗室，將再安排與教師面談。曾經修過張教授課程的同學將會優先考慮。」（42 字）
- 「參加比賽、申請國科會大專生專題計畫、投稿。」（21 字）

### 頁面: `members_page-4`

**差異**: Baseline 5 行 → Experiment 1 行（移除 4 行）

**其他被移除行（需人工審核）**:

- 「### 歡迎加入WIDM 實驗室」（16 字）
- 「## Prospective students」（23 字）
- 「Please carefully review WIDM LAB's research areas and recent published papers to ensure that your research direction are consistent with our research activities in the laboratory. Please send your personal resume (CV), academic transcript, and short research proposal to Prof. Chang [chiahui at g dot ncu dot edu dot tw] to schedule an interview. Priority will be given to students who have taken Professor Chang's courses. Post date: Sep 3, 2017 12:46:12 AM」（458 字）

### 頁面: `news`

**差異**: Baseline 25 行 → Experiment 21 行（移除 12 行）

**其他被移除行（需人工審核）**:

- 「## Latest News」（14 字）
- 「[校外奬項](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85) [校內奬項](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%85%A7%E5%A5%AC%E9%A0%85) [大專生專題研究](https://sites.google.com/site/nculab/news/%E5%9C%8B%E7%A7%91%E6%9C%83%E5%A4%A7%E5%B0%88%E7%94%9F%E5%B0%88%E9%A1%8C%E7%A0%94%E7%A9%B6%E8%A8%88%E7%95%AB)計畫 [研討會](https://sites.google.com/site/nculab/news/%E7%A0%94%E8%A8%8E%E6%9C%83) [徵人](https://sites.google.com/site/nculab/members/page-4)」（472 字）
- 「- Congratulations to Graduate students Huang Huaixuan, Gong Ruoqi and Chien Kuochun for winning the ROCLING 2024 Best Paper Award — Oct. 17, 2024」（145 字）
- 「- Congratulations to undergraduate students Chang Xunhao and Sun Yongchun for participating in the 2024 Hetai MaaS Hackathon and winning the championship and the Ingenuity Award — Oct. 17, 2024」（193 字）
- 「- Congratulations! Undergraduate student Ye Zhanwei was selected as a visiting representative for the 2024 Epoch School Internship Program of the Epoch Foundation」（162 字）
- 「- Congratulations to undergraduate students Chang Xunhao, Shen Zhekuan, and Zeng Tinglun for winning third place in the Information Security Technology Group in the 2024 29th InnoServe College Information Application Service Innovation Competition」（247 字）
- 「- Congratulations to undergraduate student Chang Xunhao [Communication Innovation Energy Saving Optimization Competition | 2024 Communications Competition]」（155 字）
- 「- Congratulations! Graduate students Xu Yaowen and Chen Guanrong were shortlisted for the 2024 "Central Technology Society AI Creative Competition" finals [03]ESGenius: Sustainability Report Generation AI Consultant」（215 字）
- 「- Congratulations! Graduate students Huang Guanjie and Huang Yuming's paper "Improving Control over Question Answer Generation via Entity and Event Relationship Labeling" was selected as the best paper of NCS2023. — Oct. 14, 2023」（229 字）
- 「- Congratulations! Undergraduate student Li Yukai's paper "Story Co-Telling Dialogue Generation via Reinforcement Learning and Knowledge Graph" won the ROCLING 2023 Best Paper Award. — Oct. 21, 2023」（198 字）
- 「- Thanks to QSAN for donating dual-controller network storage devices — Dec 4, 2015 2:23:10 PM」（94 字）

### 頁面: `news_%E5%9C%8B%E7%A7%91%E6%9C%83%E5%A4%A7%E5%B0%88%E7%94%9F%E5%B0%88%E9%A1%8C%E7%A0%94%E7%A9%B6%E8%A8%88%E7%95%AB`

**差異**: Baseline 5 行 → Experiment 0 行（移除 4 行）

**其他被移除行（需人工審核）**:

- 「# 國科會大專生專題研究計畫」（14 字）
- 「[國科會大專學生研究計畫補助查詢](https://wsts.nstc.gov.tw/STSWeb/Award/AwardMultiQuery.aspx) 113 李倬安 國立中央大學資訊工程學系 計畫名稱：基於深度學習的跨多輸入法編輯器整合系統 計畫編號：113-2813-C-008-024-E 執行起迄：2024/07/01~2025/02/28 指導教授：張嘉惠 核定金額：58,000元 113 張勛皓 國立中央大學財務金融學系 計畫名稱：基於評價理論與圖神經網路預測匯率之研究 計畫編號：113-2813-C-008-073-E 執行起迄：2024/07/01~2025/02/28 指導教授：葉錦徽 核定金額：58,000元 113 江宗翰​ 國立中央大學資訊工程學系 基於語音指令的語音辨識修正系統​ 111 林書宇 國立中央大學資訊工程學系 計畫名稱：應用先進的時空圖預測模型到多個台灣的數據集 計畫編號：111-2813-C-008-021-E 執行起迄：2022/07/01~2023/02/28 指導教授：張嘉惠 核定金額：48,000元 108 吳宗育 國立中央大學資訊工程學系 計畫名稱：食譜自動問答系統 計畫編號：108-2813-C-008-007-E 執行起迄：2019/07/01~2020/02/28 指導教授：張嘉惠 核定金額：48,000元」（591 字）
- 「108 趙昱傑 國立中央大學資訊工程學系 計畫名稱：基於深度學習與關注機制之標點符號填補與文字校正 計畫編號：108-2813-C-008-008-E 執行起迄：2019/07/01~2020/02/28 指導教授：張嘉惠 核定金額：48,000元 107 謝献爵 國立中央大學資訊工程學系 計畫名稱：應用深度學習於社群網路活動文本分類 計畫編號：107-2813-C-008-035-E 執行起迄：2018/07/01~2019/02/28 指導教授：張嘉惠 核定金額：48,000元 107 黃悅文 國立中央大學資訊工程學系 計畫名稱：應用排序學習模型於社群網路活動搜尋結果之改善 計畫編號：107-2813-C-008-034-E 執行起迄：2018/07/01~2019/02/28 指導教授：張嘉惠 核定金額：48,000元 106 邱威誠 國立中央大學資訊工程學系 計畫名稱：互動式廣告的節能設計Design of Energy-saving interactive advertisement 計畫編號：106-2813-C-008-022-E 執行起迄：2017/07/01~2018/02/28 核定金額：48,000元」（519 字）

### 頁面: `news_%E6%A0%A1%E5%85%A7%E5%A5%AC%E9%A0%85`

**差異**: Baseline 10 行 → Experiment 0 行（移除 10 行）

**短文本雜訊（預期移除）**:

- 「## 校內奬項」（7 字）

**其他被移除行（需人工審核）**:

- 「- 賀！[113年資電院大學部專題競賽獲獎名單 張嘉惠老師指導 李倬安同學、葉展維同學榮獲「特優」獎殊榮](https://sites.google.com/site/nculab/news/113%E5%B9%B4%E8%B3%87%E9%9B%BB%E9%99%A2%E5%A4%A7%E5%AD%B8%E9%83%A8%E5%B0%88%E9%A1%8C%E7%AB%B6%E8%B3%BD%E7%8D%B2%E7%8D%8E%E5%90%8D%E5%96%AE)！」（236 字）
- 「- 賀！[實驗室專題生參與113學年度專題競賽 全部獲奬](https://sites.google.com/site/nculab/news/%E6%81%AD%E5%96%9C%E5%B0%88%E9%A1%8C%E7%94%9F%E5%8F%83%E8%88%87113%E5%B9%B4%E5%B0%88%E9%A1%8C%E7%AB%B6%E8%B3%BD%E5%85%A8%E9%83%A8%E7%8D%B2%E5%A5%AC)！」（221 字）
- 「- [賀！葉庭榮獲本系巴哈姆特獎學金](https://www.csie.ncu.edu.tw/announcement/6d08752a55e66d91373e3d9206861545) — Dec. 10, 2022」（110 字）
- 「- [賀！大學部專題生洪裕翔、林書宇、鄭少騏以"深度學習於法律文本之應用"獲得2022年資電院大學部專題競賽優等奬](http://www.ceecs.ncu.edu.tw/NewsDetail.aspx?ID=242&ItemType=AnnouncementData) - Jun 14, 2022」（151 字）
- 「- [賀！林子平榮獲本系巴哈姆特獎學金](https://www.csie.ncu.edu.tw/announcement/a01b1d417a6d777ce9294ea9a38d4282) — Apr 22, 2022」（110 字）
- 「- [賀！張嘉惠老師指導學生何驊益、劉至咸、及張國斌以行動中大於103學年度第七屆大學部專題製作競賽榮獲佳作](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%85%A7%E5%A5%AC%E9%A0%85/hezhangjiahuilaoshizhidaoxueshengyu103xueniandudiqijiedaxuebuzhuantizhizuojingsaironghuojiazuo) — Sep 23, 2015 11:27:02 AM」（257 字）
- 「- [賀！張嘉惠老師指導學生張國斌以疾疾店家現身於103學年度第七屆大學部專題製作競賽榮獲佳作](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%85%A7%E5%A5%AC%E9%A0%85/hezhangjiahuilaoshizhidaoxueshengyu103xueniandudiqijiedaxuebuzhuantizhizuojingsaironghuojiazuo) — Sep 23, 2015 11:27:02 AM」（250 字）
- 「- [賀！張嘉惠老師指導學生郭泰麟以聖劍語錄於103學年度第七屆大學部專題製作競賽榮獲佳作](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%85%A7%E5%A5%AC%E9%A0%85/hezhangjiahuilaoshizhidaoxueshengyu103xueniandudiqijiedaxuebuzhuantizhizuojingsaironghuojiazuo) — Sep 23, 2015 11:27:02 AM」（248 字）

### 頁面: `news_%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85`

**差異**: Baseline 24 行 → Experiment 1 行（移除 22 行）

**短文本雜訊（預期移除）**:

- 「## 校外奬項」（7 字）

**其他被移除行（需人工審核）**:

- 「恭賀研究生 廖梓逸、簡資烜、張彣謙參加 [2025 NSF HDR (Scientific-Mood) ](https://indico.cern.ch/event/1610056/page/41091-taiwan-local-winners-announcement)榮獲台灣區第一名 — Jan. 17, 2026」（160 字）
- 「恭賀張嘉惠教授指導實驗室團隊大學部李倬安、資電學士班葉展維以[ #基於深度學習的跨多輸入法編輯器整合系統](https://www.facebook.com/hashtag/%E5%9F%BA%E6%96%BC%E6%B7%B1%E5%BA%A6%E5%AD%B8%E7%BF%92%E7%9A%84%E8%B7%A8%E5%A4%9A%E8%BC%B8%E5%85%A5%E6%B3%95%E7%B7%A8%E8%BC%AF%E5%99%A8%E6%95%B4%E5%90%88%E7%B3%BB%E7%B5%B1?__eep__=6&__cft__%5B0%5D=AZVRmV1EX5WZyKDHzDnMXs7C6NpV1-3qLhqguqRhKLPD-BMrfGVLSSJ5nmbomtcx0MwZzml311mEZ6a5gIwLKI4HxfGCyr4nPvnD3ubAlq_U6bdgYdd3pWIBXvMvkch8VI8HxDkdaXYFljIyhtpKczUQroqp5sv2a7xXTwreBkeJbQ&__tn__=*NK-R)榮獲國科會𝟏𝟏𝟑年度大專學生研究計畫研究創作獎 !!! - June 2025」（511 字）
- 「- 恭喜 李倬安、葉展維同學第29屆人工智慧與應用研討會[ (TAAI 2024)](https://taai2024.org/)以「基於深度學習的跨多輸入法編輯整合系統」榮獲The Appier-Sponsored Award — Dec. 5, 2024」（129 字）
- 「- 恭喜黃懷萱、龔若齊、簡國峻獲選 ROCLING 2024 Best Paper Award — Oct. 17, 2024」（63 字）
- 「- 恭喜張勛皓、孫詠淳同學參加2024和泰MaaS黑客松 榮獲冠軍、獨具匠心獎 — Oct. 17, 2024」（55 字）
- 「- 賀！ [葉展維同學 獲選2024 時代基金會 Epoch School實習計畫的參訪代表](https://sites.google.com/site/nculab/news/%E6%81%AD%E5%96%9C%E5%BC%B5%E5%98%89%E6%83%A0%E8%80%81%E5%B8%AB%E6%8C%87%E5%B0%8E-%E8%91%89%E5%B1%95%E7%B6%AD%E5%90%8C%E5%AD%B8)」（218 字）
- 「- 恭喜張勛皓、沈哲寬、曾廷綸同學參加2024第29屆InnoServe大專校院資訊應用服務創新競賽獲資安技術組第三名」（59 字）
- 「- 恭喜張勛皓同學 【通訊創新節能優化大賽| 2024 通訊大賽】」（33 字）
- 「- 恭喜！[張嘉惠老師指導 碩一生 許耀文同學及陳冠蓉同學入圍](https://sites.google.com/site/nculab/news/%E6%81%AD%E5%96%9C%E5%BC%B5%E5%98%89%E6%83%A0%E8%80%81%E5%B8%AB%E6%8C%87%E5%B0%8E-%E8%A8%B1%E8%80%80%E6%96%87-%E9%99%B3%E5%86%A0%E8%93%89%E5%90%8C%E5%AD%B8)2024年「[中技社AI創意競賽](https://www.ctci.org.tw/8838/talent/41184/45319/45320/)」決賽 [03]ESGenius: 永續報告生成AI顧問」（332 字）
- 「- 賀！WIDM團隊參加[2024 法律x 法遵科技黑客松 - Lawsnote 獲得法遵/公司治理特別獎](https://sites.google.com/site/nculab/news/2024-%E6%B3%95%E5%BE%8Bx-%E6%B3%95%E9%81%B5%E7%A7%91%E6%8A%80%E9%BB%91%E5%AE%A2%E6%9D%BE-lawsnote) - Aug. 31, 2024」（211 字）
- 「- 賀 ！簡國峻、龔若齊、黃懷萱、鄭世翊參加2023法律x法遵黑客松獲得理律學堂跨領域特別獎、司法院教育特別獎、理慈獎三個獎項，奬金五萬元」（69 字）
- 「- 賀！黃冠傑、黃淯銘論文"通過實體和事件關係標記改進問題答案對生成的控制"獲選[NCS2023最佳論文](https://tanet2023.nccu.edu.tw/ncs-award/)。 — Oct. 14, 2023」（112 字）
- 「- 賀！李聿鎧論文"Story Co-Telling Dialogue Generation via Reinforcement Learning and Knowledge Graph"獲選[ROCLING 2023 Best Paper Award](https://rocling2023.github.io/) 。 — Oct. 21, 2023」（177 字）
- 「- [賀！張嘉惠教授指導碩士在職專班學生廖勳 榮獲TANET 2021佳作論文奬](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85/%E8%B3%80-%E7%A2%A9%E5%A3%AB%E5%9C%A8%E8%81%B7%E5%B0%88%E7%8F%AD%E5%AD%B8%E7%94%9F%E5%BB%96%E5%8B%B3-%E6%A6%AE%E7%8D%B2tanet-2021%E4%BD%B3%E4%BD%9C%E8%AB%96%E6%96%87%E5%A5%AC)— Dec. 27, 2021」（311 字）
- 「- [賀！張嘉惠老師指導實驗室團隊邱威誠同學榮獲科技部108年度產學合作計畫成果發表暨績效考評會產學成果海報展示優良獎](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85/%E8%B3%80%E9%82%B1%E5%A8%81%E8%AA%A0%E5%90%8C%E5%AD%B8%E7%8D%B2%E7%A7%91%E6%8A%80%E9%83%A8108%E5%B9%B4%E5%BA%A6%E7%94%A2%E5%AD%B8%E5%90%88%E4%BD%9C%E8%A8%88%E7%95%AB%E6%88%90%E6%9E%9C%E7%99%BC%E8%A1%A8%E6%9A%A8%E7%B8%BE%E6%95%88%E8%80%83%E8%A9%95%E6%9C%83%E7%94%A2%E5%AD%B8%E6%88%90%E6%9E%9C%E6%B5%B7%E5%A0%B1%E5%B1%95%E7%A4%BA%E5%84%AA%E8%89%AF%E7%8D%8E) — Mar 5, 2020 2:25:00 PM」（520 字）
- 「- [賀！張嘉惠教授指導研究生劉至咸榮獲自然語言與語音處理研討會最佳論文獎](https://www.csie.ncu.edu.tw/announcement/3689275e8f3be9673691d8eb041bcdf0) — Oct 16, 2019 5:33:48 AM」（139 字）
- 「- [賀！張嘉惠教授指導大三專題生趙昱傑、吳宗育參與104黑客松獲 AI Chatbot 組第二名](https://www.csie.ncu.edu.tw/announcement/66f04e93f5dd1286684c975e65393644) — July 27, 2018 13:35:08 PM」（153 字）
- 「- [賀！鄭仲庭、莊秀敏獲2015人工智慧研討會國內議程論文奬佳作!](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85/page-2) — Nov 22, 2015 1:11:00 PM」（148 字）
- 「- [賀！陳天盛、陳明權獲2014人工智慧研討會國內議程最佳論文奬!](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85/page-1) — Sep 30, 2015 3:48:15 PM」（148 字）
- 「- [賀！林柏翰榮獲TCGA2015 最佳碩士論文獎](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85/page) — Sep 30, 2015 3:43:28 PM」（138 字）

### 頁面: `news_%E7%A0%94%E8%A8%8E%E6%9C%83`

**差異**: Baseline 19 行 → Experiment 0 行（移除 13 行）

**其他被移除行（需人工審核）**:

- 「## Web 智慧與資料探勘實驗室」（17 字）
- 「## Web Intelligence and Data Mining Laboratory」（46 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQV9eufwWBzd__tH0zk8qERdBgkk21ffIMM9Ls1s6msF3b4wP1tqcbhGrWw0d58XuHJIPx86dJ1BNhPkhuwkiC49IlJ4V_8-4u-erzB-ULePN6W8uNS6vH7HPBiHD22tl7dh3tlKhRvXn0AN_Rb9yWrREDzdCIyrTsClXSWzj5YeFUt79fcUX9lOQuAuES2PbB8jucttFzFKddWUaDqou0nYDO1uAYCq0-SeD5Cshk8=w1280)」（291 字）
- 「## 人工智慧浪潮下之資訊科學與數位學習之變革與挑戰」（26 字）
- 「地點：台南 日期：2024/10/4-5 主辦單位：[國立中央大學資訊工程學系](https://www.csie.ncu.edu.tw/) 協辦單位：國科會智慧計算學門、國科會資教學門」（93 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXM2B0gmeY696frw9Bhu76tZZz10qbnMQjtLVZPR7MNKRUf5muZtT36cgoUMOzxzF-tiMMuPl0v9PwAfq_7iks47H8WwY5Nhe-VgmH6aUklreK3vaUDDjg3itAk7Xt_hTWcP2SJHqRdyuWsOdz2Db5sMP9i54vyw5NQfUClEq80Un4x3z2kzm3gLL01lUda9k_vc0jLWJKmhBd0SbO5BSI-OU03y8rpLSBZCHPEMkM=w1280)」（291 字）
- 「[人本AI與教育論壇](https://sites.google.com/view/aiedunccu/) 地點：國立中央大學工程五館B220 日期：2023/7/20（四） 報名連結：[https://forms.gle/gz9AMjmnyanMrKQL6](https://forms.gle/gz9AMjmnyanMrKQL6) 主辦單位：[國立中央大學資訊工程學系](https://www.csie.ncu.edu.tw/) 協辦單位：[國立政治大學英國語文學系](https://english.nccu.edu.tw/)、[國立中央大學中國文學系](https://www.chinese.ncu.edu.tw/) [![](https://lh3.googleusercontent.com/sitesv/AG8ngQVPdjAFrPlic8ba4jad2UKPKbPhusi1IV2iScMewpifAxH9A3ayRGojY2FPuO9IHYb9Mf3YDRuYzz78B9dCzhmOgN_G3Y5-gouGAHz4JGShDm646VEWCk-brm4n4NowpR6oZw5ysJiXq1qHbgnvXqFalEQmj0QPw2n2Ek1UH3ZsSc_A68dL3Madgjt0iYpYaI89xqXFjPoLE76uK5b9eebXQhb27qLOebrFoV_x2S0=w1280)」（607 字）
- 「](https://www.google.com/url?q=https%3A%2F%2Ftaai2020.github.io%2F&sa=D&sntz=1&usg=AOvVaw1cinqoogrXfz9br6fcnFNg)」（112 字）
- 「# TAAI 2020」（11 字）
- 「人工智慧技術與應用會議（TAAI）系列是台灣人工智慧領域一年一度的領先會議，TAAI 2020 由台灣人工智慧學會（TAAI）與國立中央大學主辦。會議為研究人員提供一個平台，分享他們對人工智慧各個方面（包括理論、技術、應用和實施）的見解。」（119 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWhGmw1juZEoadwcriKtKsMZTMS5blFV3MHwq3rkya7_WJ0X6r4Ud0V-KDbchjWNgxziWDmKU0vQoU_3ohFmD3wOpoFv5uK9pfLEKPMYUqir_3P3Y0wNZcpZrDyrbaRqnufnLhb75Aqxa3vSaXRT9SCxG2E8NXvxcirjEpWoDgK-49CKKYR171C3U8m7wN7REumQOkWFe58eVsBKVoKwWB1wJksYsVU1tivoIdY2Z0=w1280)」（291 字）
- 「[教育部4G行動寬頻創新應用服務研討會](https://sites.google.com/site/nculab/news/%E7%A0%94%E8%A8%8E%E6%9C%83/jiaoyubu4gxingdongkuanpinchuangxinyingyongfuwuyantaohuixiangguanzixun) [研討會簡介] 隨著行動寛頻與智慧手機快速蓬勃的發展，資通訊科技已全面性跨入行動世代，智慧型手機、穿載裝置不僅融入每個人的日常生活之中，也改變訊息傳播的方式，因此無論是政府、企業都希望掌握這波行動的變革與重新洗牌的機會，開創新的應用服務。[智慧生活與行動創新應用研討會](https://goo.gl/FdAPMJ)是中央大學資工系執行教育部委辦校園雲端創新應用計畫所舉辦的研討會，內容包括無線網路分享平台、地圖搜尋服務、穿載復建、智慧照護等計畫成果展之外，也邀請學界、業界分享行動廣告平台的趨勢。歡迎各界踴躍參加，共同描繪未來智慧生活的創新應用！ 會議時間：104年12月22日(週二) 會議地點：國立中央大學 客家學院國際會議廳 主辦單位：中央大學資工系 協辦單位：教育部4G行動寬頻創新應用服務計畫辦公室」（517 字）

### 頁面: `news_%E7%A2%A9%E8%AB%96%E5%8F%A3%E8%A9%A6`

**差異**: Baseline 6 行 → Experiment 3 行（移除 5 行）

**短文本雜訊（預期移除）**:

- 「## 碩論口試」（7 字）

**其他被移除行（需人工審核）**:

- 「- [WIDM 2021 Master Thesis Oral Defense](https://sites.google.com/site/nculab/news/%E7%A2%A9%E8%AB%96%E5%8F%A3%E8%A9%A6/widm-2021-master-thesis-oral-defense) — Jun 25, Jul 14, Jul 16, Aug 4, 2021」（195 字）
- 「- [WIDM 2020 Master Thesis Oral Defense](https://sites.google.com/site/nculab/news/%E7%A2%A9%E8%AB%96%E5%8F%A3%E8%A9%A6/widm-2020-master-thesis-oral-defense) — Jul 2, 2020 2:15:43 PM」（182 字）
- 「- [WIDM Lab Tutorial 2016](https://sites.google.com/site/nculab/news/%E7%A2%A9%E8%AB%96%E5%8F%A3%E8%A9%A6/widmlabtutorial2016) — Jul 27, 2016 4:06:25 AM」（152 字）

### 頁面: `news_page-3`

**差異**: Baseline 7 行 → Experiment 0 行（移除 5 行）

**其他被移除行（需人工審核）**:

- 「### 感謝QSAN捐贈雙控網路儲存設備」（20 字）
- 「Post date: Dec 4, 2015 2:23:10 PM」（33 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXv8RpvMfSWxvb2uLp8X9LOknQCTlimocEuntPmiVBMmgiHTyyY98b76_o5zAFOstNMTj6UERFmnn1vp88hif1xquPLElEdR-hAHbMywDyTo65JPURtrEgZbxWmp8HvvinildfN84GscZLH8NEBvg0bOsiWG0fY-HOSELw8ttwYA0UVMGLTBsODll1tPDKACVPpwoLQo_vm=w1280)」（260 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXhVmPwov05FnfOPGBfy-0QSo-DuDGofxZWZik_B5Q4PIc8bUYBEu7ekIdsWRwk0RUpEpocfJqJagYwcIwrq_nlvylqWr78HqlXPOP5Sssx5PZTaPERasXESbY2CzlJCOjGrB8WUyngQ25iuts0D8G6dUGFcF1MaKsv6ZLOLYCmchLTr4Mj5lAbuKr3Yr9yY3wHkI2Mdw=w1280)」（258 字）

### 頁面: `news_國科會大專生專題研究計畫`

**差異**: Baseline 5 行 → Experiment 0 行（移除 4 行）

**其他被移除行（需人工審核）**:

- 「# 國科會大專生專題研究計畫」（14 字）
- 「[國科會大專學生研究計畫補助查詢](https://wsts.nstc.gov.tw/STSWeb/Award/AwardMultiQuery.aspx) 113 李倬安 國立中央大學資訊工程學系 計畫名稱：基於深度學習的跨多輸入法編輯器整合系統 計畫編號：113-2813-C-008-024-E 執行起迄：2024/07/01~2025/02/28 指導教授：張嘉惠 核定金額：58,000元 113 張勛皓 國立中央大學財務金融學系 計畫名稱：基於評價理論與圖神經網路預測匯率之研究 計畫編號：113-2813-C-008-073-E 執行起迄：2024/07/01~2025/02/28 指導教授：葉錦徽 核定金額：58,000元 113 江宗翰​ 國立中央大學資訊工程學系 基於語音指令的語音辨識修正系統​ 111 林書宇 國立中央大學資訊工程學系 計畫名稱：應用先進的時空圖預測模型到多個台灣的數據集 計畫編號：111-2813-C-008-021-E 執行起迄：2022/07/01~2023/02/28 指導教授：張嘉惠 核定金額：48,000元 108 吳宗育 國立中央大學資訊工程學系 計畫名稱：食譜自動問答系統 計畫編號：108-2813-C-008-007-E 執行起迄：2019/07/01~2020/02/28 指導教授：張嘉惠 核定金額：48,000元」（591 字）
- 「108 趙昱傑 國立中央大學資訊工程學系 計畫名稱：基於深度學習與關注機制之標點符號填補與文字校正 計畫編號：108-2813-C-008-008-E 執行起迄：2019/07/01~2020/02/28 指導教授：張嘉惠 核定金額：48,000元 107 謝献爵 國立中央大學資訊工程學系 計畫名稱：應用深度學習於社群網路活動文本分類 計畫編號：107-2813-C-008-035-E 執行起迄：2018/07/01~2019/02/28 指導教授：張嘉惠 核定金額：48,000元 107 黃悅文 國立中央大學資訊工程學系 計畫名稱：應用排序學習模型於社群網路活動搜尋結果之改善 計畫編號：107-2813-C-008-034-E 執行起迄：2018/07/01~2019/02/28 指導教授：張嘉惠 核定金額：48,000元 106 邱威誠 國立中央大學資訊工程學系 計畫名稱：互動式廣告的節能設計Design of Energy-saving interactive advertisement 計畫編號：106-2813-C-008-022-E 執行起迄：2017/07/01~2018/02/28 核定金額：48,000元」（519 字）

### 頁面: `news_校內奬項`

**差異**: Baseline 10 行 → Experiment 0 行（移除 10 行）

**短文本雜訊（預期移除）**:

- 「## 校內奬項」（7 字）

**其他被移除行（需人工審核）**:

- 「- 賀！[113年資電院大學部專題競賽獲獎名單 張嘉惠老師指導 李倬安同學、葉展維同學榮獲「特優」獎殊榮](https://sites.google.com/site/nculab/news/113%E5%B9%B4%E8%B3%87%E9%9B%BB%E9%99%A2%E5%A4%A7%E5%AD%B8%E9%83%A8%E5%B0%88%E9%A1%8C%E7%AB%B6%E8%B3%BD%E7%8D%B2%E7%8D%8E%E5%90%8D%E5%96%AE)！」（236 字）
- 「- 賀！[實驗室專題生參與113學年度專題競賽 全部獲奬](https://sites.google.com/site/nculab/news/%E6%81%AD%E5%96%9C%E5%B0%88%E9%A1%8C%E7%94%9F%E5%8F%83%E8%88%87113%E5%B9%B4%E5%B0%88%E9%A1%8C%E7%AB%B6%E8%B3%BD%E5%85%A8%E9%83%A8%E7%8D%B2%E5%A5%AC)！」（221 字）
- 「- [賀！葉庭榮獲本系巴哈姆特獎學金](https://www.csie.ncu.edu.tw/announcement/6d08752a55e66d91373e3d9206861545) — Dec. 10, 2022」（110 字）
- 「- [賀！大學部專題生洪裕翔、林書宇、鄭少騏以"深度學習於法律文本之應用"獲得2022年資電院大學部專題競賽優等奬](http://www.ceecs.ncu.edu.tw/NewsDetail.aspx?ID=242&ItemType=AnnouncementData) - Jun 14, 2022」（151 字）
- 「- [賀！林子平榮獲本系巴哈姆特獎學金](https://www.csie.ncu.edu.tw/announcement/a01b1d417a6d777ce9294ea9a38d4282) — Apr 22, 2022」（110 字）
- 「- [賀！張嘉惠老師指導學生何驊益、劉至咸、及張國斌以行動中大於103學年度第七屆大學部專題製作競賽榮獲佳作](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%85%A7%E5%A5%AC%E9%A0%85/hezhangjiahuilaoshizhidaoxueshengyu103xueniandudiqijiedaxuebuzhuantizhizuojingsaironghuojiazuo) — Sep 23, 2015 11:27:02 AM」（257 字）
- 「- [賀！張嘉惠老師指導學生張國斌以疾疾店家現身於103學年度第七屆大學部專題製作競賽榮獲佳作](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%85%A7%E5%A5%AC%E9%A0%85/hezhangjiahuilaoshizhidaoxueshengyu103xueniandudiqijiedaxuebuzhuantizhizuojingsaironghuojiazuo) — Sep 23, 2015 11:27:02 AM」（250 字）
- 「- [賀！張嘉惠老師指導學生郭泰麟以聖劍語錄於103學年度第七屆大學部專題製作競賽榮獲佳作](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%85%A7%E5%A5%AC%E9%A0%85/hezhangjiahuilaoshizhidaoxueshengyu103xueniandudiqijiedaxuebuzhuantizhizuojingsaironghuojiazuo) — Sep 23, 2015 11:27:02 AM」（248 字）

### 頁面: `news_校內奬項_hezhangjiahuilaoshizhidaoxueshengyu103xueniandudiqijiedaxuebuzhuantizhizuojingsaironghuojiazuo`

**差異**: Baseline 19 行 → Experiment 0 行（移除 12 行）

**短文本雜訊（預期移除）**:

- 「- 疾疾店家現身：」（9 字）

**其他被移除行（需人工審核）**:

- 「## 賀！張嘉惠老師指導學生於103學年度第七屆大學部專題製作競賽榮獲佳作」（37 字）
- 「Post date: Sep 23, 2015 11:27:02 AM」（35 字）
- 「- 賀！張嘉惠教授指導大學部學生郭泰麟、何驊益、劉至咸、及張國斌。榮獲『第七屆大學部專題製作競賽榮獲佳作』。」（54 字）
- 「- 行動中大： 何驊益、劉至咸、及張國斌」（20 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXsULvULY9EjVuvbKmK8Gm8248kpE_RXOPgG98cSYy3SVRps21L5eZWV7Lb0J5FHB3JqWb1OI-dInKT-86zazIUedvsESKCCSHswkbyF3hQIi7VCgy_VKReYXFTgeOHDpACn7oAWRUMxslWpUgjSrJ7eVoVD1del5rfL5uKPvkWMx5CW0hbWdpT-aHYLoXPwl3U8-35NA=w1280)」（258 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWAl2yAJZOelryW7g6SPZo60kC42JGRkuSKENuz81HojeDC6_UOAfIt77QnrV-G2t5jSCnaJq1SwDHUZ3gL7w7V4kyzbBFzQ0YYVP-hcN7msuKqUE3F4Ektxz4TBodiWWJW7CzKA46hKdbtGvO7pXK_6bdsiV4PJ7cz4lUlxe2dV_amI0WW_uOV3al6-UVbKzIF0I6KA2yW=w1280)」（260 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQU4Oj9lcwpk9Zl_vycQXeKAh7_Jtg51WCQxjOwglwHHfdqvHO9cQYvTy2KzUGauM0WE2kyqTrJi8Rtf6emrTXQsc7MBew7aV320RV2L_z9JRXETXDvOWoveQdwdmBXGDMBkgasI7WVc_oTRh31UwWeHXyuJmxSlKEVYBzvxCQhaev1RHR1cjx9NkpXK-lvlw5VpXSdP73HA=w1280)」（260 字）
- 「- 聖劍語錄：郭泰麟」（10 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQVLcZJjkPmb5TcMUvDlYgrLSsRBKc-qT53VgW-sEKyvfMk4z6JaG6z9zmbq8LcogJ1cRJZyChE9Aflv8McF49WFvXRPcSAdoXFVC8d-kMbh_ZOtTPyJeUKbh-5JbNV6hIeWusvp2d_H_P6DNyyYrGe9pXGL550KkR1WlNB5Un6P0hmcCQtxARZf-YmvDRXhmqj5sjTyQtxy=w1280)」（260 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUtQO9wszeeYcsPObSGlcuHnhdnffZN0RMYuHvnm7ZdSMM_DJs6aaasL-V2xrDGwhnIjnOq0GfY83BZfpS6F2bs8TzSYZkyFfUfGFwXsir93TqTn7LqS8yWcLU7RdnK5zaUl__vbbXsSOa4shrCwkbV90rBsj5DgxIB7FUrWIwJim1PuXL9qRlCGDHoUBYkU-L5_Rd-dQ=w1280)」（258 字）

### 頁面: `news_校外奬項`

**差異**: Baseline 24 行 → Experiment 1 行（移除 22 行）

**短文本雜訊（預期移除）**:

- 「## 校外奬項」（7 字）

**其他被移除行（需人工審核）**:

- 「恭賀研究生 廖梓逸、簡資烜、張彣謙參加 [2025 NSF HDR (Scientific-Mood) ](https://indico.cern.ch/event/1610056/page/41091-taiwan-local-winners-announcement)榮獲台灣區第一名 — Jan. 17, 2026」（160 字）
- 「恭賀張嘉惠教授指導實驗室團隊大學部李倬安、資電學士班葉展維以[ #基於深度學習的跨多輸入法編輯器整合系統](https://www.facebook.com/hashtag/%E5%9F%BA%E6%96%BC%E6%B7%B1%E5%BA%A6%E5%AD%B8%E7%BF%92%E7%9A%84%E8%B7%A8%E5%A4%9A%E8%BC%B8%E5%85%A5%E6%B3%95%E7%B7%A8%E8%BC%AF%E5%99%A8%E6%95%B4%E5%90%88%E7%B3%BB%E7%B5%B1?__eep__=6&__cft__%5B0%5D=AZVRmV1EX5WZyKDHzDnMXs7C6NpV1-3qLhqguqRhKLPD-BMrfGVLSSJ5nmbomtcx0MwZzml311mEZ6a5gIwLKI4HxfGCyr4nPvnD3ubAlq_U6bdgYdd3pWIBXvMvkch8VI8HxDkdaXYFljIyhtpKczUQroqp5sv2a7xXTwreBkeJbQ&__tn__=*NK-R)榮獲國科會𝟏𝟏𝟑年度大專學生研究計畫研究創作獎 !!! - June 2025」（511 字）
- 「- 恭喜 李倬安、葉展維同學第29屆人工智慧與應用研討會[ (TAAI 2024)](https://taai2024.org/)以「基於深度學習的跨多輸入法編輯整合系統」榮獲The Appier-Sponsored Award — Dec. 5, 2024」（129 字）
- 「- 恭喜黃懷萱、龔若齊、簡國峻獲選 ROCLING 2024 Best Paper Award — Oct. 17, 2024」（63 字）
- 「- 恭喜張勛皓、孫詠淳同學參加2024和泰MaaS黑客松 榮獲冠軍、獨具匠心獎 — Oct. 17, 2024」（55 字）
- 「- 賀！ [葉展維同學 獲選2024 時代基金會 Epoch School實習計畫的參訪代表](https://sites.google.com/site/nculab/news/%E6%81%AD%E5%96%9C%E5%BC%B5%E5%98%89%E6%83%A0%E8%80%81%E5%B8%AB%E6%8C%87%E5%B0%8E-%E8%91%89%E5%B1%95%E7%B6%AD%E5%90%8C%E5%AD%B8)」（218 字）
- 「- 恭喜張勛皓、沈哲寬、曾廷綸同學參加2024第29屆InnoServe大專校院資訊應用服務創新競賽獲資安技術組第三名」（59 字）
- 「- 恭喜張勛皓同學 【通訊創新節能優化大賽| 2024 通訊大賽】」（33 字）
- 「- 恭喜！[張嘉惠老師指導 碩一生 許耀文同學及陳冠蓉同學入圍](https://sites.google.com/site/nculab/news/%E6%81%AD%E5%96%9C%E5%BC%B5%E5%98%89%E6%83%A0%E8%80%81%E5%B8%AB%E6%8C%87%E5%B0%8E-%E8%A8%B1%E8%80%80%E6%96%87-%E9%99%B3%E5%86%A0%E8%93%89%E5%90%8C%E5%AD%B8)2024年「[中技社AI創意競賽](https://www.ctci.org.tw/8838/talent/41184/45319/45320/)」決賽 [03]ESGenius: 永續報告生成AI顧問」（332 字）
- 「- 賀！WIDM團隊參加[2024 法律x 法遵科技黑客松 - Lawsnote 獲得法遵/公司治理特別獎](https://sites.google.com/site/nculab/news/2024-%E6%B3%95%E5%BE%8Bx-%E6%B3%95%E9%81%B5%E7%A7%91%E6%8A%80%E9%BB%91%E5%AE%A2%E6%9D%BE-lawsnote) - Aug. 31, 2024」（211 字）
- 「- 賀 ！簡國峻、龔若齊、黃懷萱、鄭世翊參加2023法律x法遵黑客松獲得理律學堂跨領域特別獎、司法院教育特別獎、理慈獎三個獎項，奬金五萬元」（69 字）
- 「- 賀！黃冠傑、黃淯銘論文"通過實體和事件關係標記改進問題答案對生成的控制"獲選[NCS2023最佳論文](https://tanet2023.nccu.edu.tw/ncs-award/)。 — Oct. 14, 2023」（112 字）
- 「- 賀！李聿鎧論文"Story Co-Telling Dialogue Generation via Reinforcement Learning and Knowledge Graph"獲選[ROCLING 2023 Best Paper Award](https://rocling2023.github.io/) 。 — Oct. 21, 2023」（177 字）
- 「- [賀！張嘉惠教授指導碩士在職專班學生廖勳 榮獲TANET 2021佳作論文奬](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85/%E8%B3%80-%E7%A2%A9%E5%A3%AB%E5%9C%A8%E8%81%B7%E5%B0%88%E7%8F%AD%E5%AD%B8%E7%94%9F%E5%BB%96%E5%8B%B3-%E6%A6%AE%E7%8D%B2tanet-2021%E4%BD%B3%E4%BD%9C%E8%AB%96%E6%96%87%E5%A5%AC)— Dec. 27, 2021」（311 字）
- 「- [賀！張嘉惠老師指導實驗室團隊邱威誠同學榮獲科技部108年度產學合作計畫成果發表暨績效考評會產學成果海報展示優良獎](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85/%E8%B3%80%E9%82%B1%E5%A8%81%E8%AA%A0%E5%90%8C%E5%AD%B8%E7%8D%B2%E7%A7%91%E6%8A%80%E9%83%A8108%E5%B9%B4%E5%BA%A6%E7%94%A2%E5%AD%B8%E5%90%88%E4%BD%9C%E8%A8%88%E7%95%AB%E6%88%90%E6%9E%9C%E7%99%BC%E8%A1%A8%E6%9A%A8%E7%B8%BE%E6%95%88%E8%80%83%E8%A9%95%E6%9C%83%E7%94%A2%E5%AD%B8%E6%88%90%E6%9E%9C%E6%B5%B7%E5%A0%B1%E5%B1%95%E7%A4%BA%E5%84%AA%E8%89%AF%E7%8D%8E) — Mar 5, 2020 2:25:00 PM」（520 字）
- 「- [賀！張嘉惠教授指導研究生劉至咸榮獲自然語言與語音處理研討會最佳論文獎](https://www.csie.ncu.edu.tw/announcement/3689275e8f3be9673691d8eb041bcdf0) — Oct 16, 2019 5:33:48 AM」（139 字）
- 「- [賀！張嘉惠教授指導大三專題生趙昱傑、吳宗育參與104黑客松獲 AI Chatbot 組第二名](https://www.csie.ncu.edu.tw/announcement/66f04e93f5dd1286684c975e65393644) — July 27, 2018 13:35:08 PM」（153 字）
- 「- [賀！鄭仲庭、莊秀敏獲2015人工智慧研討會國內議程論文奬佳作!](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85/page-2) — Nov 22, 2015 1:11:00 PM」（148 字）
- 「- [賀！陳天盛、陳明權獲2014人工智慧研討會國內議程最佳論文奬!](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85/page-1) — Sep 30, 2015 3:48:15 PM」（148 字）
- 「- [賀！林柏翰榮獲TCGA2015 最佳碩士論文獎](https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%A4%96%E5%A5%AC%E9%A0%85/page) — Sep 30, 2015 3:43:28 PM」（138 字）

### 頁面: `news_校外奬項_page`

**差異**: Baseline 5 行 → Experiment 0 行（移除 4 行）

**其他被移除行（需人工審核）**:

- 「## 恭賀林柏翰榮獲TCGA2015 最佳碩士論文獎」（26 字）
- 「Post date: Sep 30, 2015 3:43:28 PM」（34 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXzysHX7FslKciEKQPoy4QBJ3a5U9KVbF5tMM4cZc_4e_sJWL_32tjKZjBpzuBT37MqcKBc_JbOi7fh_rSIpyQYqTWGsx2IDMvvvVcdAeQG1_F6FHO5FXDdFO4AqyL1tjhQ2wAXExexpKYfqk7RLUAOgd1rJowww-V0kxwGJjvOM7DorFLEtAgR5Wxeh9gnS1rxt_iGpg=w1280)」（258 字）

### 頁面: `news_校外奬項_page-1`

**差異**: Baseline 5 行 → Experiment 0 行（移除 4 行）

**其他被移除行（需人工審核）**:

- 「## 賀陳天盛、陳明權獲2014人工智慧研討會國內議程最佳論文奬!」（33 字）
- 「Post date: Sep 30, 2015 3:48:15 PM」（34 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXv-dSh_J35uy99gt4nYYXPbeTrBHEp0K0Q0T4eMcsxCEvSleCnwIuQWdEV-OGA76X1blKHv84GmNo8VAU2NUs1LL6lZnkuBvIp7KezNxZoie_88rx6NcboDxBitshExt6nagmPvaoqBtw1SIUcB4xWXOyko5QGLQzLJ0mV6g9_x51JBoGGMOFuSG8TOBdrmHIoMQhk0Q=w1280)」（258 字）

### 頁面: `news_校外奬項_page-2`

**差異**: Baseline 5 行 → Experiment 0 行（移除 4 行）

**其他被移除行（需人工審核）**:

- 「## 賀鄭仲庭、莊秀敏獲2015人工智慧研討會國內議程論文奬佳作!」（33 字）
- 「Post date: Nov 22, 2015 1:11:00 PM 論文題目：整合多種搜尋結果以提高 POI 搜尋的準確性」（62 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXJ84V0Eo0WxeuPaTS_IaZRpmCSUNY04PMe9i9kQ6it-4K7uJpbaNbp-stOVG5Ba6v1Do-ntqjwcIrT-Ol1jkQaMYX980kZZn8eias2A_CvfFSsGQlVqeq6znk2VaOGS83AO6Qon27bdUIUgqqFXrulDWuHME0HWmfyVrMkdzwwbmMef-5a2fFh3Wsv4CGSy2aGN8r8CilR=w1280)」（260 字）

### 頁面: `news_校外奬項_賀-碩士在職專班學生廖勳-榮獲tanet-2021佳作論文奬`

**差異**: Baseline 5 行 → Experiment 0 行（移除 4 行）

**其他被移除行（需人工審核）**:

- 「# 賀!! 碩士在職專班學生廖勳 榮獲TANET 2021佳作論文奬」（34 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQX8Hqbtnm-fuoCWVyjhRfheMa9IRIrPvjiJdaDbCRzMIAYBBQ1j8eHDEYkqLzuFG7Ph2hoG2I7sxxbhUuB8GPsnkWmhbrWRILS5LXBarGQHNl-VaBNQpr2MoxTX-HdOPG6fluiG7K6iyV6po7iXDKg0X4HX5wQms-BJPFC_U5d96R3FfzemcQPb6rnmDyZ7YIJPTMVT5wC2rK-2H4tEaUvCqdGnJXPBzOEejqra=w1280)」（288 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXvaRcRmUKV4GAfOBAlYMWLuxHWP_0TW-o06QyO0_QLOthGjxco8-At64detI876ea4jP0LwZ0rBk1kZ56AVnZ5R_BIHedv1Q0Rc1Jsn-wkrVk2XZQ5HC8vtTUIedxjj9u5F2g7BjLecWAl-nBzJAKb20fp1zW8sJyljD4385j5LrhQHniBSK87KIlcN1gTvhtc_jfA0Nfa8bRgj6kyqXS63qTR3AOGqIGkV90ZDQ4=w1280)」（291 字）

### 頁面: `news_校外奬項_賀邱威誠同學獲科技部108年度產學合作計畫成果發表暨績效考評會產學成果海報展示優良獎`

**差異**: Baseline 11 行 → Experiment 0 行（移除 7 行）

**其他被移除行（需人工審核）**:

- 「## 賀！張嘉惠老師指導實驗室團隊邱威誠同學榮獲科技部108年度產學合作計畫成果發表暨績效考評會」（48 字）
- 「## 產學成果海報展示優良獎」（14 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUdz9r15czPjk1GCPTiUZPq-EUbmDgweI-Q4cCVphaMDvpnMWPviukLBw08i9SbyDioga8LO3FkUfqUKeLNEuQc_SnFUNLu9iGh2JVMG1SfNGUwP9LHNW4iwwxR1laytC6ExV0Mib82pQuA8T5ahF6oT-4sITwVB4USZ_MOA4y6-vUQIHIpEfSyIOOi4KDRWQs2YGVILGj9EiD-U3g=w1280)」（267 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWUQFq-dzevmzhLrWdE83-yTLOJwyfUVbdA6oJpuVOZO7rU6F3Kj40z8i9VKxNRh38NHbYf3U8yDjiHT7vfKKZzOIlNkVr1K0Nz4LRFpt4XpOrXcy4rGIvAjLqHcqzdaKh-vDRJoayKxIyx_wF0vTyww7hAOksRYLP_tjGW_mPJi10So9CuADPkSa3vARnOzX4GpmIOF5dp1Wxpquo=w1280)」（267 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUprVqmuOS2HnLETlWxwPOC9bNKy28FxbF3S5WZoEZKWTPEym_c0MLjNn2amMVFvEBw-Z6TWTeaM5ud81nTlcSdEo4j_V3nEAQkM4LkxkYJwvFlTbtkZFTvpSm27iZZudkFqIkZcT6KYbNNhHQekh1cU1NrcgWKTurO1maZ5neBEWluxMbdUGPOxr6HfGND5rlxNO5_SQ1sPAhSrYE=w1280)」（267 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQU2Vlg7yLWza8WInhjBJ2ylKj6XQ4PdLHSafAeSxYyVWUhXOGuWjuIQz22ttrNQkFySM8pL49k2QMbc-J-NM4Ta_ZrvxewkZWN3S9DWiG4ENO36_gIDYM571f5j0h3ebPY9WQZ9XnBKGiNznrjNfRO7scYnlX377AHuYms8jafoZQyrcL2cQQznPVrbyrOxbRRawnwUikhlWVPxh1g=w1280)」（267 字）

### 頁面: `news_研討會`

**差異**: Baseline 19 行 → Experiment 0 行（移除 13 行）

**其他被移除行（需人工審核）**:

- 「## Web 智慧與資料探勘實驗室」（17 字）
- 「## Web Intelligence and Data Mining Laboratory」（46 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQV9eufwWBzd__tH0zk8qERdBgkk21ffIMM9Ls1s6msF3b4wP1tqcbhGrWw0d58XuHJIPx86dJ1BNhPkhuwkiC49IlJ4V_8-4u-erzB-ULePN6W8uNS6vH7HPBiHD22tl7dh3tlKhRvXn0AN_Rb9yWrREDzdCIyrTsClXSWzj5YeFUt79fcUX9lOQuAuES2PbB8jucttFzFKddWUaDqou0nYDO1uAYCq0-SeD5Cshk8=w1280)」（291 字）
- 「## 人工智慧浪潮下之資訊科學與數位學習之變革與挑戰」（26 字）
- 「地點：台南 日期：2024/10/4-5 主辦單位：[國立中央大學資訊工程學系](https://www.csie.ncu.edu.tw/) 協辦單位：國科會智慧計算學門、國科會資教學門」（93 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXM2B0gmeY696frw9Bhu76tZZz10qbnMQjtLVZPR7MNKRUf5muZtT36cgoUMOzxzF-tiMMuPl0v9PwAfq_7iks47H8WwY5Nhe-VgmH6aUklreK3vaUDDjg3itAk7Xt_hTWcP2SJHqRdyuWsOdz2Db5sMP9i54vyw5NQfUClEq80Un4x3z2kzm3gLL01lUda9k_vc0jLWJKmhBd0SbO5BSI-OU03y8rpLSBZCHPEMkM=w1280)」（291 字）
- 「[人本AI與教育論壇](https://sites.google.com/view/aiedunccu/) 地點：國立中央大學工程五館B220 日期：2023/7/20（四） 報名連結：[https://forms.gle/gz9AMjmnyanMrKQL6](https://forms.gle/gz9AMjmnyanMrKQL6) 主辦單位：[國立中央大學資訊工程學系](https://www.csie.ncu.edu.tw/) 協辦單位：[國立政治大學英國語文學系](https://english.nccu.edu.tw/)、[國立中央大學中國文學系](https://www.chinese.ncu.edu.tw/) [![](https://lh3.googleusercontent.com/sitesv/AG8ngQVPdjAFrPlic8ba4jad2UKPKbPhusi1IV2iScMewpifAxH9A3ayRGojY2FPuO9IHYb9Mf3YDRuYzz78B9dCzhmOgN_G3Y5-gouGAHz4JGShDm646VEWCk-brm4n4NowpR6oZw5ysJiXq1qHbgnvXqFalEQmj0QPw2n2Ek1UH3ZsSc_A68dL3Madgjt0iYpYaI89xqXFjPoLE76uK5b9eebXQhb27qLOebrFoV_x2S0=w1280)」（607 字）
- 「](https://www.google.com/url?q=https%3A%2F%2Ftaai2020.github.io%2F&sa=D&sntz=1&usg=AOvVaw1cinqoogrXfz9br6fcnFNg)」（112 字）
- 「# TAAI 2020」（11 字）
- 「人工智慧技術與應用會議（TAAI）系列是台灣人工智慧領域一年一度的領先會議，TAAI 2020 由台灣人工智慧學會（TAAI）與國立中央大學主辦。會議為研究人員提供一個平台，分享他們對人工智慧各個方面（包括理論、技術、應用和實施）的見解。」（119 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWhGmw1juZEoadwcriKtKsMZTMS5blFV3MHwq3rkya7_WJ0X6r4Ud0V-KDbchjWNgxziWDmKU0vQoU_3ohFmD3wOpoFv5uK9pfLEKPMYUqir_3P3Y0wNZcpZrDyrbaRqnufnLhb75Aqxa3vSaXRT9SCxG2E8NXvxcirjEpWoDgK-49CKKYR171C3U8m7wN7REumQOkWFe58eVsBKVoKwWB1wJksYsVU1tivoIdY2Z0=w1280)」（291 字）
- 「[教育部4G行動寬頻創新應用服務研討會](https://sites.google.com/site/nculab/news/%E7%A0%94%E8%A8%8E%E6%9C%83/jiaoyubu4gxingdongkuanpinchuangxinyingyongfuwuyantaohuixiangguanzixun) [研討會簡介] 隨著行動寛頻與智慧手機快速蓬勃的發展，資通訊科技已全面性跨入行動世代，智慧型手機、穿載裝置不僅融入每個人的日常生活之中，也改變訊息傳播的方式，因此無論是政府、企業都希望掌握這波行動的變革與重新洗牌的機會，開創新的應用服務。[智慧生活與行動創新應用研討會](https://goo.gl/FdAPMJ)是中央大學資工系執行教育部委辦校園雲端創新應用計畫所舉辦的研討會，內容包括無線網路分享平台、地圖搜尋服務、穿載復建、智慧照護等計畫成果展之外，也邀請學界、業界分享行動廣告平台的趨勢。歡迎各界踴躍參加，共同描繪未來智慧生活的創新應用！ 會議時間：104年12月22日(週二) 會議地點：國立中央大學 客家學院國際會議廳 主辦單位：中央大學資工系 協辦單位：教育部4G行動寬頻創新應用服務計畫辦公室」（517 字）

### 頁面: `news_研討會_jiaoyubu4gxingdongkuanpinchuangxinyingyongfuwuyantaohuixiangguanzixun`

**差異**: Baseline 6 行 → Experiment 0 行（移除 5 行）

**其他被移除行（需人工審核）**:

- 「## 教育部4G行動寬頻創新應用服務研討會」（21 字）
- 「Post date: Dec 3, 2015 7:00:23 AM 會議時間：104年12月22日(週二) 會議地點：國立中央大學 客家學院國際會議廳 議程、線上報名、[交通資訊](http://www.ncu.edu.tw/visitors/traffic)、[講者介紹](https://sites.google.com/site/nculab/news/%E7%A0%94%E8%A8%8E%E6%9C%83/jiaoyubu4gxingdongkuanpinchuangxinyingyongfuwuyantaohuixiangguanzixun/speakers)、[照片集](https://www.dropbox.com/sh/0or1k7m38u5eoh7/AABvPkHbpwEkTbTkBWVJXrGBa?dl=0)、[演講投影片下載](https://sites.google.com/site/nculab/news/%E7%A0%94%E8%A8%8E%E6%9C%83/jiaoyubu4gxingdongkuanpinchuangxinyingyongfuwuyantaohuixiangguanzixun/download-ppt) [研討會簡介] 隨著行動寛頻與智慧手機快速蓬勃的發展，資通訊科技已全面性跨入行動世代，智慧型手機、穿載裝置不僅融入每個人的日常生活之中，也改變訊息傳播的方式，因此無論是政府、企業都希望掌握這波行動的變革與重新洗牌的機會，開創新的應用服務。[智慧生活與行動創新應用研討會](https://goo.gl/FdAPMJ)是中央大學資工系執行教育部委辦校園雲端創新應用計畫所舉辦的研討會，內容包括無線網路分享平台、地圖搜尋服務、穿載復建、智慧照護等計畫成果展之外，也邀請學界、業界分享行動廣告平台的趨勢。歡迎各界踴躍參加，共同描繪未來智慧生活的創新應用！」（807 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWT_G680JZGqXL0ObTqBMTPp3kG1biAd9nXJ86fMI_ZJUyGS4GQ-njTJ1AUXDBSzbIWJSGxdJkasTaHmiNDonSDJ_xhXLhhKVwAPdrdAmE4x5l5j5eTgBnZ8Qz6PHyZldJYVgIRqIwrOYdvS_t8s2Ru6G3ImBzJqnTlatePK9aey_G6nxluEbrFweaG4eH86dZ-NB8h7FzF=w1280)」（260 字）
- 「報名網址：[https://goo.gl/9tsAbr](https://docs.google.com/forms/d/1O_yZwnbraXw6XL8w7jVT1IqL2JOC20ME5OoFy8wHutg/viewform) 主辦單位：中央大學資工系 協辦單位：教育部4G行動寬頻創新應用服務計畫辦公室 ＊＊特別感謝[成功大學黃仁暐教授](http://office.ee.ncku.edu.tw/NCKUEECHINESE/professor/T213-jwhuang/T0000000c.htm)及[中研院陳昇瑋研究員](http://www.iis.sinica.edu.tw/pages/swc/index_zh.html)協助邀請業界講者！＊＊ [](https://drive.google.com/folderview?id=0B2XRm-m6dNA8eGtJSXhiV0JHTm8 "Open Drive Folder in new window")」（436 字）

### 頁面: `news_碩論口試`

**差異**: Baseline 6 行 → Experiment 3 行（移除 5 行）

**短文本雜訊（預期移除）**:

- 「## 碩論口試」（7 字）

**其他被移除行（需人工審核）**:

- 「- [WIDM 2021 Master Thesis Oral Defense](https://sites.google.com/site/nculab/news/%E7%A2%A9%E8%AB%96%E5%8F%A3%E8%A9%A6/widm-2021-master-thesis-oral-defense) — Jun 25, Jul 14, Jul 16, Aug 4, 2021」（195 字）
- 「- [WIDM 2020 Master Thesis Oral Defense](https://sites.google.com/site/nculab/news/%E7%A2%A9%E8%AB%96%E5%8F%A3%E8%A9%A6/widm-2020-master-thesis-oral-defense) — Jul 2, 2020 2:15:43 PM」（182 字）
- 「- [WIDM Lab Tutorial 2016](https://sites.google.com/site/nculab/news/%E7%A2%A9%E8%AB%96%E5%8F%A3%E8%A9%A6/widmlabtutorial2016) — Jul 27, 2016 4:06:25 AM」（152 字）

### 頁面: `news_碩論口試_widm-2020-master-thesis-oral-defense`

**差異**: Baseline 11 行 → Experiment 1 行（移除 7 行）

**其他被移除行（需人工審核）**:

- 「## WIDM 2020 Master Thesis Oral Defense」（39 字）
- 「[第一場] 時間：7/14(二) 下午14:00-15:00 地點：國立中央大學 - 工程五館B棟 - B323教室 學生：黃晨郁 主題：A Hierarchical Decomposable Attention Model for News Stance Detection (應用階層可解構式注意力模型於新聞立場辨識任務)」（163 字）
- 「[第二場] 時間：7/14(二) 下午15:00-16:00 地點：國立中央大學 - 工程五館B棟 - B323教室 學生：陳震瑜 主題：Playback Prediction Based on Singer Popularity and Aspect-based Sentiment Analysis from Social Network （網路聲量分析與意見目標情感分析於歌曲點播量預測之應用）」（200 字）
- 「[第三場] 時間：7/14(二) 下午16:00-17:00 地點：國立中央大學 - 工程五館B棟 - B323教室 學生：邱威誠 主題：Joint Learning of Aspect-level Sentiment Analysis and Singer Name Recognition from Social Networks （應用歌手辨識及情感分析於目標情感偵測與分析之研究）」（194 字）
- 「[第四場] 時間：7/16(四) 下午14:00-15:00 地點：國立中央大學 - 工程五館B棟 - B323教室 學生：林政憲 主題：Adaptive Portfolio Optimization Based on Stock Rank Prediction from News Sentiment and Technical Indicators（新聞情緒及技術指標於股票排名預測之動態投資組合最佳化）」（204 字）
- 「[第五場] 時間：7/16(四) 下午15:00-16:00 地點：國立中央大學 - 工程五館B棟 - B323教室 學生：Naufal Said 主題：Toward Efficient Unsupervised Web Data Extraction: From Unsupervised to Self-Trained Wrappers（朝向有效率的非監督式網頁資料擷取：從非監督到自我訓練Wrapper）」（205 字）

### 頁面: `news_碩論口試_widm-2021-master-thesis-oral-defense`

**差異**: Baseline 25 行 → Experiment 1 行（移除 14 行）

**短文本雜訊（預期移除）**:

- 「### [第一場]」（9 字）
- 「### [第二場]」（9 字）
- 「### [第三場]」（9 字）
- 「### [第四場]」（9 字）
- 「### [第五場]」（9 字）
- 「### [第六場]」（9 字）

**其他被移除行（需人工審核）**:

- 「# WIDM 2021 Master Thesis Oral Defense」（38 字）
- 「時間：6/25(二) 上午10:00-11:00 學生：吳昱豪 主題：Multi-Task Neural Sequence Labeling for Zero-shot Cross-Lingual Boilerplate Removal (應用多任務序列標記模型於零樣本跨語言網頁模板移除之研究)」（148 字）
- 「時間：7/14(三) 學生：Thamolwan Poopradubsil 主題：Context-Aware Question-Answer Pairing and Dialogue Act Tagging from Instant Messaging Chatlog」（133 字）
- 「時間：7/16(五) 學生：廖于晴 主題：Event Source Page Discovery via Reinforcement Learning (應用強化式學習探勘活動來源網頁)」（93 字）
- 「時間：7/16(五) 學生：吳承儒 主題：Large Scale Web Data API Creation via Automatic Pagination Recognition - A Case Study on Event Extraction (基於自動分頁偵測之資料應用程式介面建置 - 以活動擷取為例)」（158 字）
- 「時間：8/4(二) 下午14:00-15:00 學生：甘岱融 主題：Home Appliance Review Research Via Adversarial Reptile (應用對抗式Reptile 於家電產品網路評論之研究)」（116 字）
- 「時間：8/4(二) 下午15:00-16:00 學生：曾筱雯 主題：Aspect-Based Sentiment Analysis and Singer Name Recognition using Parameter Generation Network Based Transfer Learning (基於參數生成網絡的遷移學習進行情感分析和歌手命名識別)」（181 字）

### 頁面: `news_碩論口試_widmlabtutorial2016`

**差異**: Baseline 6 行 → Experiment 0 行（移除 5 行）

**其他被移除行（需人工審核）**:

- 「# WIDM Lab Tutorial 2016」（24 字）
- 「Post date: Jul 27, 2016 4:06:25 AM 歡迎WIDM新同學加入! 為幫助新同學熟悉Web Mining相關的資料分析工具， 實驗室成員於2016年暑期安排了一連串Tutorial， 我們的初衷是讓同學們在資料處理上更上手， 能夠更加專注於問題的探究與應用服務的設計。 Agenda」（155 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXk01kZL0X_RW45EdNr6epvPeG490eNJjQjc0uvCa0kh7RXi8ZObaTvdHPXdJgbZ3xjkOeUMdUeb4KagHNEw9lxTmE_QFeQdz1Gro3eIfNYcRSAhcek7ywMpZS2rASr086NsBJOU1CCxfDfg2Bs_-BtaFOYeMczk_w3hx2h20emZQfuEux-6HpKzSSrHP11gJZ5-l8PXt0K=w1280)」（260 字）
- 「Download Lectures & Watch Videos」（32 字）

### 頁面: `projects`

**差異**: Baseline 41 行 → Experiment 7 行（移除 32 行）

**其他被移除行（需人工審核）**:

- 「## Projects」（11 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUDZTiZevosTz5on91pYkI-Vbhcn4vYLK87NtxzvT3f5OIWd6-lmGRhgZYAbPJQ3d0no4V4ISKNyjHkiGtvJwfF_GZ7_Hsumb9zU-cxMYwdBSgb7aRmHIkGSO7uLCYyjbwstomwxXYINPV3rmWUtn1rynJl0z99znpUd2W2Eb4nrHU4inMJRMfHN74jPuj0scX9F5_maPTOmE6va_y7_5QeY5rnVkGEerTfK-xsYgg=w1280)」（291 字）
- 「[StoryBot](https://sites.google.com/site/nculab/projects/storychatbot) / [EduACT](https://eduact.csie.ncu.edu.tw/)」（114 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWedVDmNuY95eFIw-uwfonIrjNp8Z2VCS5keI711UUtXVw0VjLnOr2-E-Ka4bixZpJRgFegGN8AF0K3kP02N4T4VjdV5pgMDPPidsutDNGDO6HivVgb8bpOTfpqlLQpMqIX0bIcyJdQtn8xunSnyUENWk34ADNNod_FGCMeshdVqs8TH9pz4FG_-wnFTvdwOInv829qUMo8d8xQIl5QHFsNiIkHNDJv9RMnVVEOuMY=w1280)」（291 字）
- 「[Legal AI / CCG](https://ccg.csie.ncu.edu.tw:8443/login)」（56 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQV6Db-jQFLI2Qkx3zWka_Y9TrmsQkKKItKjhUifOMJkVfzReE8wMXGGZOAcmMAIyDgE7n56eotBQPyUt0UZmUwpgNOyc3V_LfDBQZ5MkP5Szs1S8G7lGB7SDVzt4rTaT5xuTzy-niLammKMHXvtoHvwUbCxQeR6lEXAumSeWRMPPGbJLQkFcr4Gt9rhoaWgvaXrsdW8Vsw9lypsaPu0NUExq-RuxWu-QHZFTOgZkmk=w1280)」（291 字）
- 「[EventGo!](http://140.115.54.49:8080/#/home)」（44 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUxUOO__8imlHvwE6CxCNQlo574DXgrl77u3pghrEOpa6lszI5pQyHovMvCZIb2aCRk7O0EObS9GumMD1ElIr-YwG35mDzDcwiHvEkJiCNQpUOMeCD7b0m5foxH4DzkhcGJ8p86MRyjeBq2BIlwRDnpCKWOP-5d2JDsi8bQtpfJzd2jqYlmVpo0UMB0vvjj87Ma3xiLX1uI7UBNZ1IHhblIUnW7apbqDVXrU9ZCUvQ=w1280)」（291 字）
- 「[Data API Creator](http://140.115.54.44:8001/)」（46 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQUlgc_KC4FpnY5f8kVNglbL7GItfTWLfib-JCEi1ReKAhCQbv7ucYzxwkptf55vwmUpgZGX1mvjUJJC-sjFL2XyTBf141VSiuxrCop00NVF5TxhIMK5crD-CEF2hn34p8R1ZboFgveyY2_dBzuSmI21OjMP5WqcVSQ6Nj9DzvhE45qelYYvrLnEhCT0HZEG2LqQ6i2Aux5BG_wG5stzeegjgrLwz9jyz7fMEziQ_5w=w1280)」（291 字）
- 「[Mobile Web Creator](http://140.115.54.44:8000/)」（48 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQVg65718DSVvAMDzxhTuNiy8Sy9g5fbhzOi6uuHbW0Rz_PVgU4w9lS27BVkvdF6O5JuiwdtX4XD5rrcYzEaHw4FvK_UaQ_3FpgLNyz9jFZvUM1N2jJpw6b2ajkq3OmYIsCqmmH8YpBXMRJXa682oP1x9bxUtBE6Cb5z56264Yq4zBMYmUSy_jiFIWl_AC4GbYn3gJS-zFS2BlEAGVNpmTjj5XvI9NB6UHTBWXUL=w1280)」（288 字）
- 「[DS4NER](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner) 基於知識圖譜與蒙地卡羅樹策略搜尋的網頁自動化代理研究 (2025/08/01~2028/07/31) 這個計畫在探討AI在人機介面上的應用與未來發展趨勢，我們將以大型語言模型為核心，結合視覺模型、語音輸入、以及電腦操作等其他工具，實現複雜任務自動化。從命令列的互動(Gorilla CLI), 瀏覽器的代理操作(WebVoyager), 以及桌面上跨應用程式的操作(Claude Computer Use), 近期頂級會議上發表的相關研究可以看到未來的AI PC發展方向。透過此計畫我們希望創造四個Agentic AI系統。(1) WebPilot: 透過自然語言操作瀏覽器, 自動完成中文網站的操作, (2) MRAG powered WebPilot: 透過資訊系統的使用手冊以及RAG的輔助, 自動完成 Web-Based 資訊系統的操作, (3)Interactive Voice RPA Agent: 透過語音互動釐清使用者的需求, 創建工作流程自動化RPA (Robotic Process Automation)，(4) CrossAPP PCPilot: 透過API串接及AutoHotkey 等腳本自動化電腦桌面端的操作, 自動完成跨應用程式的操作。對於上述每個AI代理人系統，我們將採兩階段模型來創建: 初期我們將以現有OpenAI、Anthropic等LLM來快速佈建Agentic AI系統, 第二階段則透過第一階段的測試資料, 訓練地端的模型, 確保資料的收集以及主權的AI. 我們也將訓練地端的模型, 確保資料的收集以及主權的AI. 我們希望透過這個計畫創造AI賦能的人機互動，提供更直覺、更人性化的使用者體驗，降低使用者操作、管理電腦的障礙, 提升台灣使用者在AI powered資訊發展的優勢。」（839 字）
- 「This project investigates the application and future trends of AI in human-computer interfaces. Centered on large language models, it integrates visual models, voice input, and computer operations to automate complex tasks. From command-line interactions (Gorilla CLI) and browser agent operations (WebVoyager) to cross-application desktop operations (Claude Computer Use), recent studies presented at top conferences highlight the future trajectory of AI-driven PCs. Through this project, we aim to develop four Agentic AI Systems: (1) WebPilot: Automates interactions with Chinese websites via natural language commands. (2) MRAG-powered WebPilot: Uses information system manuals and Retrieval-Augmented Generation (RAG) to automate operations on web-based information systems. (3) Interactive Voice RPA Agent: Leverages voice interaction technology to clarify user needs to create automated workflows through Robotic Process Automation (RPA). (4) CrossAPP PCPilot: Automates cross-application operations on the desktop using APIs and tools like AutoHotkey based scripts. For each of the above AI agent systems, we will adopt a two-phase model development approach: In the initial phase, we will rapidly deploy the Agentic AI systems using existing LLMs such as those provided by OpenAI and Anthropic. In the second phase, we will train on-premise models using test data collected during the first phase to ensure data sovereignty and ownership of the AI systems. Through this project, we hope to create AI-enabled human-computer interaction, provide a more intuitive and humane user experience, reduce barriers to user operation and computer management, and enhance the advantages of Taiwanese users in AI-powered information development.」（1741 字）
- 「- Character Relation Extraction 人物關係擷取 (2024/01/01 ~ 2024/11/30)」（64 字）
- 「- [Constructing Story Chatbots based on Automatic Content Extraction and Common Sense Knowledge Graphs](https://sites.google.com/site/nculab/projects/storychatbot) ([基於資訊擷取及常識圖譜聊故事機器人之研究](https://sites.google.com/site/nculab/projects/storychatbot)) (2022/08/01 ~ 2025/07/31)」（274 字）
- 「- Efficient Cross-Domain Aspect-based Sentiment Analysis and Knowledge Base Construction for Conversational Smart Devices (網路輿情面向分析與知識圖譜建構系統之開發研究) (2021/06/01 ~ 2022/08/31)」（172 字）
- 「- [EventGo: Constructing an Event Search Engine via Event Extraction from Social-Media Posts and Event Source Discovery](https://sites.google.com/site/nculab/projects/eventgo) ([EventGo! 社群媒體貼文中探索城市的活動事件動態與活動熱門度預測之研究](https://sites.google.com/site/nculab/projects/eventgo)) (2020/08/01 ~ 2023/07/31)」（299 字）
- 「- 影劇歌曲活動事件與歌手網路聲量關係之擷取與分析(2/2) (2020/06/01 ~ 2021/08/31)」（56 字）
- 「- 影劇歌曲活動事件與歌手網路聲量關係之擷取與分析(1/2) (2019/06/01 ~ 2020/05/31)」（56 字）
- 「- [Web命名實體辨識模型建構工具之研究與開發](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner) (2018/08/01 ~ 2020/07/31)」（118 字）
- 「- 應用社群網路分析暨影劇歌曲名稱辨識於熱門歌曲預測之研究 (106-2622-E-008-027-CC2)」（54 字）
- 「- [免標記且高效率之完整網要推導與資料擷取方法之研究](https://sites.google.com/site/nculab/projects/WDEMS/efficientandscalablewebdataextractionforannotation-freefullschemainduction)(105-2628-E-008-004-MY2)— Jul 27, 2016 3:40:05 AM」（205 字）
- 「- [NCUFree](https://sites.google.com/site/nculab/projects/past-projects/ncufree-mobileadvertisingplatformbasedoncampuswirelessnetwork) — Jul 27, 2015 5:06:45 AM」（160 字）
- 「- [Unsupervised Page-Level Wrapper Induction](https://sites.google.com/site/nculab/projects/WDEMS/unsupervisedpage-levelwrapperinduction) — Jul 20, 2015 9:00:12 AM」（163 字）
- 「- [行動廣告平台：植基於環境、內容與使用者導向的廣告配置研究](https://sites.google.com/site/nculab/projects/past-projects/page-1) — Oct 2, 2012 7:04:40 PM」（125 字）
- 「- [FiVaTech: Page-Level Web Data Extraction from Template Pages](https://sites.google.com/site/nculab/projects/WDEMS/fivatechfixedvariantapproachtowebdataextraction) — Feb 18, 2011 9:08:46 AM」（191 字）
- 「- [Sentiment-Oriented Contextual Advertising](https://sites.google.com/site/nculab/projects/past-projects/blogger-centriccontextualadvertising) — Jul 7, 2010 9:15:35 AM」（168 字）
- 「- [Learning to Predict Ad Clicks Based on Boosted Collaborative Filtering](https://sites.google.com/site/nculab/projects/past-projects/learningtopredictadclicksbasedonboostedcollaborativefiltering) — Jul 7, 2010 9:11:19 AM」（222 字）
- 「- [MapMarker: Extraction of Postal Addresses And Associated Information for General Web Pages](https://sites.google.com/site/nculab/projects/powerpoi/mapmarkerextractionofpostaladdressesandassociatedinformationforgeneralwebpages) — Jul 7, 2010 6:45:53 AM」（254 字）
- 「- [線上拍賣網站中銷售策略的研究](https://sites.google.com/site/nculab/projects/past-projects/page) — Aug 3, 2009 8:40:47 AM」（109 字）
- 「基於知識圖譜與蒙地卡羅樹策略搜尋的網頁自動化代理研究 (2025/08/01~2028/07/31)」（50 字）

### 頁面: `projects_WDEMS`

**差異**: Baseline 12 行 → Experiment 5 行（移除 8 行）

**其他被移除行（需人工審核）**:

- 「## DeXaR: Data eXtraction and Reuse Project」（43 字）
- 「**Project Title** : Efficient and Scalable Web Data Extraction for Annotation-Free Full Schema Induction **Project Number** : MOST105-2628-E-008-004-MY2 **Leader** : Prof. Chia-Hui Chang **Team Members** : Tzu-Ping Lin (2021-2023), 張智鈞(2020-2022), Chen-Yu Wu (2019-2021) Oviliani Yenty Yuliana, Yu-An Chou, Yan-Kai Lai (2016-2018) **Abstract** Unsupervised Web data extraction from annotation-free Web pages has been one of the main research topics in Web data extraction. Page-level web data extraction provides a complete solution for various kinds of extraction needs. However, very few researchers focus on this task because of the difficulties and complexities in the problem. On the other hands, previous page-level IE systems focus on how to achieve unsupervised data extraction and pay less attention to schema verification, i.e. how to extract data by matching testing pages with an existing schema. In this project, we emphasize the importance of schema verification for large-scale extraction tasks. Given a large number of web pages for data extraction, the system uses part of the input pages for training the schema without supervision and then extracts data from the rest of the input pages through schema verification. While the process feels like a supervised training process, the approach is actually unsupervised since users do not need to label the input pages. Therefore, we call it annotation-free schema training. The benefit of schema verification is the quick extraction of data from testing pages without complex analysis and immediate report of schema change if the website has changed its template or schema. Thus, annotation-free schema training and schema-guided extraction could achieve efficient and scalable Web data extraction. In addition to the issue of extraction efficiency, web data extraction for singleton pages is also more challenging than list pages because more data chunks need to be aligned. In this project, we use leaf nodes of the input DOM trees as the basic processing units and dynamically adjust the encoding for better alignment to speed up the processing. We define landmark equivalence class (LEC) as leaf nodes with the same text content and similar paths and use them for template mining. We then prioritize the discovery of templates in order of mandatory and optional via occurrence vectors and ensure the consistency of such templates through LIS (longest increasing sequence). Another challenge is multi-order attribute-value pairs, which is rare for list pages and has a serious effect on the design of the alignment algorithm for schema induction and verification. We develop a Web-based service to allow better manipulation of Web data for data reuse. The proposed alignment algorithm will serve as a core technology for the Web ETL tool to provide efficient and effective extraction, transformation, and loading of the data from the Web. **Publications**」（2922 字）
- 「- Oviliani Yenty Yuliana and Chia-Hui Chang, [DCADE: divide and conquer alignment with dynamic encoding for full page data extraction](http://www.google.com/url?q=http%3A%2F%2Flink.springer.com%2Farticle%2F10.1007%2Fs10489-019-01499-0&sa=D&sntz=1&usg=AOvVaw2nkB0jK22KkvL_fYKf8JwN), Applied Intelligence, 50(2), 271-295. 2020.」（325 字）
- 「- Oviliani Yenty Yuliana, Chia-Hui Chang, **A novel alignment algorithm for effective web data extraction from singleton pages** , Journal of Applied Intelligence, 48(11), 4355–4370. 2018. **DOI: 10.1007/s10489-018-1208-0** , [Data Download](https://sites.google.com/site/nculab/projects/WDEMS/dca)」（298 字）
- 「- Oviliani Yenty Yuliana, Chia-Hui Chang, **AFIS: Aligning Detail-Pages for Full Schema Induction** , TAAI 2016, pp. 220-227, DOI: [10.1109/TAAI.2016.7880164](https://www.google.com/url?q=https%3A%2F%2Fdoi.org%2F10.1109%2FTAAI.2016.7880164&sa=D&sntz=1&usg=AOvVaw1zWbJfcA8lnGQuepnUVEsp)」（285 字）
- 「**Applications**」（16 字）
- 「- [**Data API Creator: Web Data ETL System**](http://www.google.com/url?q=http%3A%2F%2F140.115.54.44%3A8001%2F&sa=D&sntz=1&usg=AOvVaw1CtJ7ujgFZiXGyKHy4kdJS)」（156 字）
- 「- [**Mobile Web Creator**](http://www.google.com/url?q=http%3A%2F%2F140.115.54.44%3A8000%2F&sa=D&sntz=1&usg=AOvVaw3bztHNr_SMocmtb6H66izM)**(**[**Demonstration**](https://www.youtube.com/watch?v=3YpQgIWtJgc)**)**」（211 字）

### 頁面: `projects_WDEMS_dafis`

**差異**: Baseline 3 行 → Experiment 0 行（移除 3 行）

**其他被移除行（需人工審核）**:

- 「## DAFIS: Dynamic Encoding for Annotation-Free Induction of Schema」（66 字）
- 「**ABSTRACTION** **EXECUTABLE PROGRAM DOWNLOAD** **DATASETS AND GOLDEN ANSWERS**」（79 字）

### 頁面: `projects_WDEMS_dca`

**差異**: Baseline 3 行 → Experiment 0 行（移除 3 行）

**其他被移除行（需人工審核）**:

- 「# DCADE: Divide and Conquer Alignment with Dynamic Encoding」（59 字）
- 「**Introduction** **Executable Program Download** **Datasets and Golden Answer**」（79 字）

### 頁面: `projects_WDEMS_efficientandscalablewebdataextractionforannotation-freefullschemainduction`

**差異**: Baseline 3 行 → Experiment 1 行（移除 3 行）

**其他被移除行（需人工審核）**:

- 「# 免標記且高效率之完整網要推導與資料擷取方法之研究」（26 字）
- 「Post date: Jul 27, 2016 3:40:05 AM 摘要：Web資料擷取是Web智慧及資訊整合的關鍵技術，免標記的資料擷取方法更是WWW、KDD等頂尖會議的重要研究主題之一。網頁層次(Page-level)的綱要推導相對於記錄層次(Record-level)的資料擷取，可以對Deep Web中相同樣版網頁產生完整網頁資料綱要，滿足對各種不同資料擷取的需求，可以說是資料擷取的完整解決方案。不過由於問題相對較複雜，因此相關研究相對較少。另一方面，過去網頁層級的資料擷取系統，僅著眼在達成非監督式的資料擷取，也就是從無標記的輸入網頁中，逕行擷取內嵌的資料，對於網頁綱要的維護與驗證較無著墨，事實上對於測試網頁的資料擷取與網頁綱頁的驗證是一體兩面的程序，同時可以節省大量網頁的資料擷取時間。在本計畫中，我們預計提出一套免標記的網頁層次的綱要推導系統，利用大量網頁中的部份網頁推導出網頁的完整綱要，繼而應用綱要驗證擷取網頁中內嵌的資料。在第一年中，我們將針對列表網頁(List pages)可以達到完整綱要的推導；第二年則對於詳細網要(Detail pages)的資料，運用HTML5 class ID、屬性等資訊，提出更精準的多序列排列(Multiple sequence alignment)；最後一年，我們將建構一個Web Data Manipulation Service，整合所發展的資料擷取，提供一般使用者可以方便對深網資料進行資料的擷取、轉換及儲存等不同的操作。 **Efficient and Scalable Web Data Extraction for Annotation-Free Full Schema Induction** **Abstract** : Unsupervised Web data extraction from annotation-free Web pages has been one of the main research topics for WWW and KDD conference. Page-level web data extraction provides a complete solution for various kinds of extraction needs, however very few researches focus on this task because of the difficulties and complexities in the problem. On the other hands, previous page-level systems focus on how to achieve unsupervised data extraction and pay less attention on schema verification, i.e. how to extract data by matching testing pages with an existing schema. In this project, we emphasize the importance of schema verification for large-scale extraction tasks. Given a large amount of web pages for data extraction, the system uses part of the input pages for training the schema without supervision, and then extracts data from the rest of the input pages through schema verification. While the process feels like a supervised training process, the approach is actually unsupervised since users do not need to label the input pages. Therefore, we also call it annotation-free schema training. The benefit of such annotation-free schema training is the quick extraction of data from testing pages with the same template and immediate report of schema change if the website has changed its template or schema. Thus, annotation-free schema training and verification could achieve efficient and scalable Web data extraction. In addition to the concern of extraction efficiency, schema induction for detail pages is also challenging since the number of data items is much larger than the case for record alignment of list pages. In this project, we utilize leaf nodes of the input DOM trees as the basic processing units and dynamically adjust the encoding for better alignment to speed up the processing. Meanwhile, the system also needs to deal with multi-order attribute-value pairs, which is rare for list pages and has serious effect on the design of the wrapper generation and verification. In the last year of this project, we plan to provide a Web-based service to allow better manipulation of Web data for data reuse. By integrating the full schema induction from the first two years, we can facilitate any desired data extraction and crawling for general users. We expect the proposed system to work better than other page-level extraction systems in terms of schema accuracy and extraction efficiency. The proposed WDMS can also serve as a Web ETL tool to provide efficient and effective extraction, transformation, and loading of the data from the Web.」（3314 字）

### 頁面: `projects_WDEMS_fivatechfixedvariantapproachtowebdataextraction`

**差異**: Baseline 3 行 → Experiment 1 行（移除 3 行）

**其他被移除行（需人工審核）**:

- 「# FiVaTech: Page-Level Web Data Extraction from Template Pages」（62 字）
- 「Post date: Feb 18, 2011 9:08:46 AM Web data extraction has been an important part for many Web data analysis applications. In this paper, we formulate the data extraction problem as the decoding process of page generation based on structured data and tree templates. We propose an unsupervised, page-level data extraction approach to deduce the schema and templates for each individual Deep Website, which contains either singleton or multiple data records in one Webpage. FiVaTech applies tree matching, tree alignment, and mining techniques to achieve the challenging task. In experiments, FiVaTech has much higher precision than EXALG and is comparable with other record-level extraction systems like ViPER and MSE. The experiments show an encouraging result for the test pages used in many state-of-the-art Web data extraction works. [](https://drive.google.com/folderview?id=0B2XRm-m6dNA8UHBpcEZRSVdMUVU "Open Drive Folder in new window")」（943 字）

### 頁面: `projects_WDEMS_plde`

**差異**: Baseline 11 行 → Experiment 6 行（移除 7 行）

**短文本雜訊（預期移除）**:

- 「# UWIDE」（7 字）

**其他被移除行（需人工審核）**:

- 「**Title** : Unsupervised Wrapper Induction and Data Extraction **Leader** : Prof. Chia-Hui Chang **Team members** : Tian-Sheng Chen, Ming-Chuang Chan, Jhong-Li Ding **Abstract** The problem of web data extraction has been studied more than ten years. Because of the structural complexity and diversity in web pages, existing researches are limited to record-level data extraction. Beside, demand of extracting data from large amount of web pages make it a challenging task for researchers. Although the web data extracted by page-level approach is more complete than record-level approach, very few researches focus on this task because of the difficulties and complexities in the problem. On the other hands, existing web data extraction systems need IT background users, because these systems have not provide friendly GUI for users. In this project, we provide a web data extraction systems based on M.-C. Chen and T.-S. Chen. We provide a friendly GUI for users to improve the training procedure of the schema induction process. The experimental results show that the performance on list page websites remain high and the performance on detail pages are increased precision 33.08% and recall 32.4%. In addition, improved system get highest recall than other systems. For accuracy, our system is higher than TEX with default threshold. If we adjust the threshold of models, we can improve the overall accuracy form 94.5% to 98.8%; Overall accuracy is 27% higher than TEX. **Download Program** : [Download](http://goo.gl/4YGPM4) **Demo** : (In Chinese) **Publication**」（1570 字）
- 「- 陳明權, 陳天盛, 張嘉惠, "應用路徑資訊輔助樣板探勘於網頁層級之資料擷取研究", Conference on Technologies and Applications of Artificial Intelligence, 2013. [(pdf)](https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6N2NjZWMyNzdmOWIzNzI3Yw)」（237 字）
- 「- 陳天盛, 陳明權, 張嘉惠, "基於頁面層級之快速網頁資料擷取與綱要驗證", Conference on Technologies and Applications of Artificial Intelligence, 2014. [(pdf)](https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6NTIyZGJiM2Q2NTQ4N2VjYw)」（233 字）
- 「- 丁中立, 張嘉惠, 張淵琮, "詳細網頁完整綱要推導之改進", National Conference on Web Intelligence and Applications, 2015. )」（99 字）
- 「- **Example set** : s1~s9 from ExAlg, s10~s49 from WIER」（55 字）
- 「[](https://drive.google.com/folderview?id=0B2XRm-m6dNA8U1BwX3RrYzM4ZDA "Open Drive Folder in new window")」（105 字）

### 頁面: `projects_WDEMS_unsupervisedpage-levelwrapperinduction`

**差異**: Baseline 9 行 → Experiment 5 行（移除 6 行）

**其他被移除行（需人工審核）**:

- 「# UWIDE: Unsupervised Page-Level Wrapper Induction」（50 字）
- 「Post date: Jul 20, 2015 9:00:12 AM **Project Leader** : Prof. Chia-Hui Chang **Team members** : Tian-Sheng Chen, Ming-Chuang Chan, Jhong-Li Ding **Abstract** The problem of web data extraction has been studied more than ten years. Because of the structural complexity and diversity in web pages, existing researches are limited to record-level data extraction. Beside, demand of extracting data from large amount of web pages make it a challenging task for researchers.Although the web data extracted by page-level approach is more complete than record-level approach, very few researches focus on this task because of the difficulties and complexities in the problem. On the other hands, existing web data extraction systems need IT background users, because these systems have not provide friendly GUI for users.In this pager, we provide a web data extraction systems based on M.-C. Chen and T.-S. Chen. We provide a friendly GUI for users to improve the training procedure of the schema induction process. The experimental results show that the performance on list page websites remain high and the performance on detail pages are increased precision 33.08% and recall 32.4%. In addition, improved system get highest recall than other systems. For accuracy, our system is higher than TEX with default threshold. If we adjust the threshold of models, we can improve the overall accuracy form 94.5% to 98.8%; Overall accuracy is 27% higher than TEX. **Download Program** : Download **Demo** : [video](https://www.youtube.com/watch?v=vaHt47rXYTg) (Chinese) **Publication**」（1572 字）
- 「- 陳明權, 陳天盛, 張嘉惠, "應用路徑資訊輔助樣板探勘於網頁層級之資料擷取研究", Conference on Technologies and Applications of Artificial Intelligencester, 2013. [(pdf)](https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6N2NjZWMyNzdmOWIzNzI3Yw)」（241 字）
- 「- 陳天盛, 陳明權, 張嘉惠, "基於頁面層級之快速網頁資料擷取與綱要驗證", Conference on Technologies and Applications of Artificial Intelligencester, 2014. [(pdf)](https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6NTIyZGJiM2Q2NTQ4N2VjYw)」（237 字）
- 「- 丁中立, 張嘉惠, 張淵琮, "詳細網頁完整綱要推導之改進", National Conference on Web Intelligence and Applications, 2015. [(pdf)](https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6NzMwMmYyMmQyMWQ4N2Q3ZQ)」（212 字）
- 「[](https://drive.google.com/folderview?id=0B2XRm-m6dNA8U1BwX3RrYzM4ZDA "Open Drive Folder in new window")」（105 字）

### 頁面: `projects_eventgo`

**差異**: Baseline 33 行 → Experiment 15 行（移除 21 行）

**短文本雜訊（預期移除）**:

- 「## Demo」（7 字）

**其他被移除行（需人工審核）**:

- 「# EventGo!(2020-2023)」（21 字）
- 「## Team member:」（15 字）
- 「林圓皓、吳昱豪、吳承儒、廖于晴、程祥恩、黃悅文、謝献爵」（27 字）
- 「## Abstract」（11 字）
- 「Finding activities to attend has been the prelude in our leisure time. Meanwhile, people also make use of social network such as Facebook or blogs to post event news. Unfortunately, the search interface of Facebook event pages only covers official events. In this case, WIDM lab developed a better tool for event search, called EventGO! The backend of EventGO! contains a web crawler, two IE (information extraction) models for activity name and location recognition as well as a search engine for event search. The frontend is an android application to present the search result in list or map view. The web crawler collects information from both Facebook and Google search engine. The former make use of Facebook Graph API to monitor 230K fan pages in Taiwan to collect posts, while the later query Google search engine with event relevant keywords such as exhibition, concert, workshop, etc. to gather web pages. Second, the IE models recognize activity name and location with pre-trained model and extract start and end date via regular expression. Note that the performance of location recognition is enhanced with 2.45 million FB places to locate the GPS position. Finally, these structured data would be stored into a Solr database for the IR search module. Note that FB event API also contribute one fourth of the events in Solr database. EventGo! android application provides a conversational search to avoid manual setting of location and temporal constraint, and present the search result from three different views: map, calendar or list. Last but not least, users can add a event as well as its details to their calendar in just a single click. EventGO!, an brilliant way to search for events.」（1706 字）
- 「[Web Demonstration](https://eventgo.widm.csie.ncu.edu.tw/#/) [Download (Android)](https://play.google.com/store/apps/details?id=com.widmlab.eventgo&hl=zh_TW) [![https://play.google.com/store/apps/details?id=com.widmlab.eventgo&hl=zh_TW](https://lh3.googleusercontent.com/sitesv/AG8ngQUpElwfpqbz8uhe1f6TUflujZg9ByhXNGAeNe_KHrbgMPzU4p1AqVa9p0CsaKEf1bWgaq9Xpw7x8oK0L6V6nchetNuMeiH4zvWEv8VXO60mrtmSMIvFUwZPFhOCFUwdyF1U-018L-VnWpJuo6yEy8bBHUiq2BHvXZov1zOTH8l0otLaFbDXJ8nJMzIPThsaGNdu-r7vKxKY=w1280)」（493 字）
- 「](https://play.google.com/store/apps/details?id=com.widmlab.eventgo&hl=zh_TW)」（77 字）
- 「## Publication」（14 字）
- 「- Yuan-Hao Lin; Chia-Hui Chang; Hsiu-Min Chuang: [Fine-Grained Meetup Events Extraction Through Context-Aware Event Argument Positioning and Recognition](https://link.springer.com/article/10.1007/s44196-024-00697-0), International Journal of Computational Intelligence Systems 17, 296 2024. [https://doi.org/10.1007/s44196-024-00697-0](https://doi.org/10.1007/s44196-024-00697-0)」（379 字）
- 「- Yuan-Hao Lin; Chia-Hui Chang; Hsiu-Min Chuang; Xiang-Shun Lin; Ting Yeh; Min-Jhao Hong: [Cost-Effective Event Mining on the Web via Event Source Page Discovery and Data API Construction](https://ieeexplore.ieee.org/document/10638638/authors#authors),[IEEE Access 12](https://dblp.org/db/journals/access/access12.html#LinCCLYH24): 115981-115993 (19 August 2024)DOI: [10.1109/ACCESS.2024.3445448](https://doi.org/10.1109/ACCESS.2024.3445448)」（441 字）
- 「- Chia-Hui Chang, Yu-Ching Liao and Ting Yeh:[Event Source Page Discovery via Policy-based RL with Multi-Task Neural Sequence Model](https://link.springer.com/chapter/10.1007/978-3-031-20891-1_42), [WISE 2022](https://wise2022.sigappfr.org/).」（242 字）
- 「- Chia-Hui Chang, Cheng-Ju Wu and Tzu-Ping Lin:[Automatic Web Data API Creation via Cross-Lingual Neural Pagination Recognition](https://link.springer.com/chapter/10.1007/978-3-031-09917-5_8), ICWE 2022.」（203 字）
- 「- Yuan-Hao Lin, Chia-Hui Chang, Hsiu-Min Chuang: [EventGo! Mining Events through Semi-Supervised Event Title Recognition and Pattern-based Venue/Date Couplin](https://www.airitilibrary.com/Publication/alDetailedMesh?DocID=10162364-202305-202212270003-202212270003-655-670)g, Journal of Information Science and Engineering, May 2023 (Accepted).」（343 字）
- 「- Yu-Hao Wu and Chia-Hui Chang: [Multi-Task Neural Sequence Labeling for Zero-Shot Cross-Language Boilerplate Removal](https://dl.acm.org/doi/10.1145/3486622.3493938). Web Intelligence 2021.」（190 字）
- 「- Chia-Hui Chang,[Yuan-Hao Lin](https://dblp.uni-trier.de/pid/193/3553.html),[Hsiu-Min Chuang](https://dblp.uni-trier.de/pid/150/5799.html): [EventGo! Exploring Event Dynamics from Social-Media Posts](https://ieeexplore.ieee.org/document/9359024).[ICS 2020](https://dblp.uni-trier.de/db/conf/intcompsymp/ics2020.html#ChangLC20): 548-552」（336 字）
- 「- [Yuan-Hao Lin](https://dblp.uni-trier.de/pid/193/3553.html), Chia-Hui Chang,[Hsiu-Min Chuang](https://dblp.uni-trier.de/pid/150/5799.html): [Mining Events through Activity Title Extraction and Venue Coupling](https://ieeexplore.ieee.org/document/9382472).[TAAI 2020](https://dblp.uni-trier.de/db/conf/taai/taai2020.html#LinCC20): 136-141」（339 字）
- 「- Y. H. Lin, C.-H. Chang, “[Facebook Activity Event Extraction System](https://aclanthology.org/O16-1022.pdf),” Proceedings of the 28th Conference on Computational Linguistics and Speech Processing, pp. 229–243, 2016.」（217 字）
- 「## Related Technologies」（23 字）
- 「1. Named Entity Recognition: Auto labeling activity name: ([Data](https://goo.gl/X2QLr6))」（89 字）
- 「1. Temporal Tagger Module - Heideltime」（38 字）

### 頁面: `projects_past-projects__draft_post-1`

**差異**: Baseline 3 行 → Experiment 1 行（移除 3 行）

**短文本雜訊（預期移除）**:

- 「# COBRA」（7 字）

**其他被移除行（需人工審核）**:

- 「Post date: Feb 15, 2011 3:16:55 AM In this work, we study the problem of closed sequential pattern mining. We propose a novel approach which extends a frequent sequence with closed itemsets instead of single items. The motivation is that closed sequential patterns are composed of only closed itemsets. Hence, unnecessary item extensions which generates non-closed sequential patterns can be avoided. Experimental evaluation shows that the proposed approach is two orders of magnitude faster than previous works with a modest memory cost.」（538 字）

### 頁面: `projects_past-projects_blogger-centriccontextualadvertising`

**差異**: Baseline 6 行 → Experiment 1 行（移除 5 行）

**其他被移除行（需人工審核）**:

- 「# Sentiment-Oriented Contextual Advertising」（43 字）
- 「Post date: Jul 7, 2010 9:15:35 AM Web advertising (Online advertising), a form of advertising that uses the World Wide Web to attract customers, has become one of the world’s most important marketing channels. This paper addresses the mechanism of Content-based advertising (Contextual advertising), which refers to the assignment of relevant ads to a generic web page, e.g. a blog post. As blogs become a platform for expressing personal opinion, they naturally contain various kinds of expressions, including both facts and comments of both a positive and negative nature. Besides, in line with the major tenet of Web 2.0 (i.e., user-centric), we believe that the web-site owners would be willing to be in charge of the ads which are positively related to their contents. Hence, in this paper, we propose the utilization of sentiment detection to improve Web-based contextual advertising. The proposed SOCA (Sentiment-Oriented Contextual Advertising) framework aims to combine contextual advertising matching with sentiment analysis to select ads that are related to the positive (and neutral) aspects of a blog and rank them according to their relevance. We experimentally validate our approach using a set of data that includes both real ads and actual blog pages. The results indicate that our proposed method can effectively identify those ads that are positively correlated with the given blog pages. Data:」（1413 字）
- 「- Advertisments: 104,094 crawled from Google AdSense」（52 字）
- 「- epinion.com: 32,304 reviews (938,621 sentences)」（49 字）

### 頁面: `projects_past-projects_learningtopredictadclicksbasedonboostedcollaborativefiltering`

**差異**: Baseline 3 行 → Experiment 3 行（移除 1 行）

**其他被移除行（需人工審核）**:

- 「Post date: Jul 7, 2010 9:11:19 AM This paper addresses the topic of social advertising, which refers to the allocation of ads based on individual user social information and behaviors. As social network services (e.g., Facebook and Morgenstern) are becoming the main platform for social activities, more than 20% of online advertisements appear on social network sites. The allocation of advertisements based on both individual information and social relationships is becoming ever more important. In this study, we first propose the notion of social filtering and compare it with content-based filtering and collaborative filtering for advertisement allocation in a social network. Second, we apply content-boosted and social-boosted methods to enhance existing collaborating filtering models. Finally, an effective learning-based framework is proposed to combine filtering models to improve social advertising. The experiments are conducted based on datasets collected from a social finance web site called Morgenstern. We performed a series of comparison experiments between filtering approaches. The experimental results indicate that the learning-based framework is able to achieve better performance results than fundamental filtering and boosted filtering mechanisms alone. Data: Contact G5.」（1298 字）

### 頁面: `projects_past-projects_ncufree-mobileadvertisingplatformbasedoncampuswirelessnetwork`

**差異**: Baseline 10 行 → Experiment 1 行（移除 8 行）

**短文本雜訊（預期移除）**:

- 「# NCUFree」（9 字）

**其他被移除行（需人工審核）**:

- 「Post date: Jul 27, 2015 5:06:45 AM **Title: Mobile Advertising Platform Based on Campus Wireless Network** **Team members** : Chin-Lin Hsu, Chia-Hui Chang The rapid growth of the mobile devices in recent years has made the demand for wireless network more important. Although the 4G broadband communication technology has been deployed, the cost of personal mobile communications has made young generations to look for free wireless hotspots such as state-owned iTaiwan, TPE-Free, iToayuan hotspots as well as the TANETROAMING system provided by MOE via campus wireless WiFi. These wifi hotspots are the infrastructure for building a future mobile market. However, the sudden increase in the number of people using smart phones to access the campus WiFi has made it relatively difficult to log on to campus networks and visitors who do not have TANET accounts cannot use campus networks. On the other hand, providing free WiFi access could not last for long as the expenditure costs could not be self-sustained. In order to solve this problem, we have developed a new type of wireless network visitor system that allows users to gain access to the Internet through the application of the mobile phone. At the same time, with the push of messages and the sending of news, the free mobile communication service has reasonable business model. Users do not need to enter account passwords or registration procedures for document registration. Instead, they use the application program to read the serial number of the SIM card of the mobile phone as a security control to ensure that users can be recorded and receive push messages. In this way, O2O (Online to Offline) offline consumption will be promoted to promote mutually beneficial action market. In a word, we provide user-friendly wireless network services in combination with message push. Users do not need to go through the tedious log-in process and just download the NCUFree APP to use the wireless network at the alliance store. **計畫背景：** 近年來智慧型手持裝置產業成長相當的快速，使得行動通訊的需求益發重要。雖然4G寬頻已然開台，然而個人行動通訊費用的增加，使得大部份年輕族群的使用者都會設法尋找免費的無線網路熱點。考慮未來行動市場所能帶來的經濟效益，因此全台國營事業單位所提供的iTaiwan熱點、各縣市政府廣設的無線網路基地台，以及教育部聯合各校園無線WiFi所提供的TANETROAMING，都是希望將無線WiFi所提供的行動通訊視為公共基礎建設，鋪設未來的行動市場。然而全台校園內使用手機上網的人數的俱然驟增，使得校園網路登入變得相對困難；同時對於沒有TANET帳號的校園訪客而言，也無法使用校園網路。另一方面，提供免費上網可能導致資源的浮用，更大的困難是，支出成本沒有相對應的回饋，終難長久支持。為解決此一問題，我們開發新型態的無線網路訪客系統，讓使用者得以透過手機的應用程式取得上網權限，同時配合訊息的推播逹到消息的發送的目的，讓免費行動 通訊有合理的營運模式。使用者不需要傳統輸入帳號密碼或是持證件登記的登入手續，而是利用應用程式讀取手機SIM卡序號做為安全性控管，確保使用者能夠被 記錄，並且收到訊息的推播，藉以帶動O2O (Online to Offline)離線消費，促進雙方互利的行動市場。綜合言之，我們結合訊息推播來提供使用者便利的無線網路服務，使用者無需繁瑣的登入流程，僅需下載 NCUFree APP即可在結盟的店家使用無線網路。」（2608 字）
- 「![NCUFree Poster](https://lh3.googleusercontent.com/sitesv/AG8ngQVD0RkHeoUXGuhqfGdGPNwK8M0MAdVMKkdENc8qPUOjEId3ycV66_NLQhOF0D7a0IhCWBb37EiLKvJ7twhaj586AQUrrfjAzl3EUy1jyczOWsxGsIFZX6Z3fbptPQXifP9LdTSpCbkOA0sE2escpR7yaodWtHSg_s6STArDiOEzjF2RN6jtASSiP-hiK5MPjkfSJPEVMg=w1280)」（272 字）
- 「中央大學免費無線網路APP 本計畫由教育部推廣4G創新應用服務所贊助，為資工系WIDM實驗室所開發。本計畫提供具有SIM卡的裝置或中大計中帳號（其他系統iTaiwan或TANetRomaing帳號請連線NCUWL）的使用者，透過NCUFree APP登入使用，希望可提供校園訪客及校內生師快速連線無線網路。」（153 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQXsqsOXB_jjeDYd_x111nQEWIUqp9jWJfzy22DZuMFHB6cavltP90KjPeKTRclzK5_5_dbrrKksBQPX-BJwl0U5vYrDVB7shU2tqrUEmVNprPnhc3G-nBbiaryLSpOPOOEaV1syTVz6lIipFa2062tDPaWiAIH3=w1280)」（216 字）
- 「[![](https://lh3.googleusercontent.com/sitesv/AG8ngQXTTxjXNIdQzXFB-DkNM3_lBqdjwJLd99JWwd3ocGu1FEea9f74ClfrU1gUCjuAw6b16UrXlrjb_yHkqZGS9Erffs2gFXLh4A8HoJKCZ0qDG_kJOAQmTuKmZQozaRSXuMnrDJoZe-RXqwyRan582UuMxwVhU-FY=w1280)」（217 字）
- 「](https://www.google.com/url?q=https%3A%2F%2Fappsto.re%2Ftw%2Fvj5Dfb.i&sa=D&sntz=1&usg=AOvVaw3_r8jw93ZN1gtqCk2zrgt1) [NCUFree 安裝暨使用方法](http://www.google.com/url?q=http%3A%2F%2Fncufree.widm.csie.ncu.edu.tw%2FNCufree_V2%2FDefault.aspx&sa=D&sntz=1&usg=AOvVaw2be2dwHOIvCx0POaRkGHG4)」（278 字）

### 頁面: `projects_past-projects_page`

**差異**: Baseline 3 行 → Experiment 0 行（移除 3 行）

**其他被移除行（需人工審核）**:

- 「# 線上拍賣網站中銷售策略的研究」（16 字）
- 「Post date: Aug 3, 2009 8:40:47 AM 線上拍賣是近年來相當盛行的C2C 網路交易方式，由於進入市場的門檻低，造成相當多的賣家競相投入創業。對於拍賣新手而言，常常因為不熟悉市場資訊而造成經營上的損失；也有些賣家只憑直覺經營，難以控制成本而且風險很高；又或是以試驗多種銷售策略以找到好的方式，造成不必要的損失，如此方法，皆不利長久經營。 目前賣家的解決方法，有些是自行查詢歷史拍賣網頁，也有些是購買市場調查公司的服務，或是模仿他人的銷售策略。自行查詢歷史拍賣網頁，必須花費大量的時間自行分析未整理過的資訊；市調公司的資訊常是僅限於單一因素對結標價和售出機率的統計資料；而模仿他人的銷售策略，則不見得適用，因為同一銷售策略的拍賣結果隨賣家及商品內容而有所不同。 有鑑於此，這個計畫收集了eBay 拍賣網站的拍賣資料，預測商品的售出機率及結標價，進而推論出賣家的期望獲利，作為賣家銷售商品的參考。除此之外，我們也透過關聯規則探勘來找出多樣的銷售策略，尤其是高獲利的銷售策略，以滿足不同賣家的經營需求。」（461 字）

### 頁面: `projects_past-projects_page-1`

**差異**: Baseline 3 行 → Experiment 0 行（移除 3 行）

**其他被移除行（需人工審核）**:

- 「# 行動廣告平台：植基於環境、內容與使用者導向的廣告配置研究」（30 字）
- 「Post date: Oct 2, 2012 7:04:40 PM」（33 字）

### 頁面: `projects_past-projects_wifipass`

**差異**: Baseline 9 行 → Experiment 1 行（移除 7 行）

**其他被移除行（需人工審核）**:

- 「# WiFi登入通/Y5Pass」（16 字）
- 「**Team members** : Yu-Wei Hu (胡育維) Pei-Ru (湯珮茹) Chia-Hui Chang **Abstract** Taiwan is one of the top countries to provide free WiFi access points for all visitors. However, connecting to open WiFi (obtaining an IP) usually takes long time when there are a lot of users around. Besides, a second step to pass through the authentication with users' accounts and passwords also require users' intervention since most WiFi login systems do not allow the browsers to remember the account and passwords. In this project, we developed an Android App, called WiFiPass, to automatically sign in an open WiFi network on behalf of the user via executing a login script recorded when users login the WiFi system for the first time. 智慧型手機經過五年才達到第一個十億的出貨量，但是只花了兩年就達到第二個十億的出貨量，在2014單一年即有十億的出貨量。爆增的行動裝置也使得行動數據流量不斷地創下新高，因而導致3G網路壅塞，也因此電信業者不得不積極佈建Wi-Fi無線熱點來疏解網路流量。根據網路熱點營運商iPass提出的全球性公共熱點的調查報告，全球公共Wi-Fi熱點到了2014年年底預計會有4,770萬個，平均每150個人共享一個熱點，但到了2018年將會增加到3.4億個，平均每20個人就有一個熱點，熱點數量在四年內將會成長7倍。 根據Informa的統計，現今大部分智慧型手機的數據流量是藉由Wi-Fi無線網路來傳遞，這反應現實社會大部份使用者即使擁有3G或4G的行動寬頻，但基於成本的考量，仍會尋找免費的Wi-Fi無線網路以節省個人支出。另一方面，許多電信廠商也透過Wi-Fi熱點的佈建，來疏解3G的壅塞。例如西班牙的FON和美國Comcast兩家公司合力推出的社區熱點，即是讓全球公共熱點數量大幅增長的一大推手。不過社區熱點只限於同一家電信廠商的會員登入使用，透過EAP-SIM機制，提供其他該電信廠商網路服務的使用者無縫切換至無線熱點。 相對於其他國家，台灣政府一開始在公共Wi-Fi無線網路的建置上，有著更為開放的政策。開放式無線網路成為縣市政府的共同推行的政策，除iTaiwan之外，六都直轄市相繼推出TPEFree、iTaiChung、iKaohsiung、iHsinchui、Taoyuan；而學術網路TANETRoaming也致力於校園無線網路的共用，提供學生跨校園的漫遊。不過這項有利於使用者的服務，如果一直由縣市政府買單，對於經費有限的縣市政府，很難長期提供這項便民的措施。因此引入廣告行銷、建構可行的經濟循環，是技術層面之外在營運模式上可以考慮的要素。 引入廣告的營運模式是相當自然的發展。早期無線電視節目，近代網路服務如Google搜尋、臉書、LINE免費APP等服務等，已經應用的相當成熟。但是在電信服務上一直處於向消費者付費的B2C (Business to Consumer)營運模式，很少有系統業者會去開拓與廣告業務相關的B2B (Business to Business)系統。國內只有統一7-11的電信服務，在全省四千多家門市提供Wi-Fi上網服務，提供每日3次免費30分鐘上網，藉以吸引顧客提高回店率，也透過消費者的行動裝置推播廣告、進行產品的行銷。 而就國內目前的情況，即使政府提供許多公共Wi-Fi無線網路，使用者的上網體驗仍然有相當大的改進空間。不少人一坐下來即開始搜尋無線網路，詢問登入密碼。在人潮擁擠之處，光是取得IP都要耗費數十秒之久，更遑論等待登入頁面出現的時間，以及密碼輸入錯誤或是忘記密碼等其他問題，因此解決使用者登入的順暢度是重要的問題。而更進階的期待，則是能做到透過Wi-Fi網路達到B2B的商業模式以求系統的永續。 我們提出一個Wi-Fi分享平台以及其搭配的APP，稱為「Wi-Fi登入通」。使用者可以透過APP (1)連網並儲存上鎖Wi-Fi的密碼、(2)替需要進行網頁登入的Wi-Fi熱點製作登入腳本並(3)儲存、管理以及分享密碼或者登入腳本並透過(4)計點機制賺取上網時間或者免費上網。透過Wi-Fi分享平台我們可以替使用者節省行動上網的費用、替分享者獲得利益(替店家行銷，客戶統計或分析)、創造與使用者的接觸機會和替電信業者舒緩行動上網流量的壅塞。」（2165 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWpF_1uDRT0G10o-55vz45kdwcAeGweKAEt4Vz0My_NjEuRq7mYPnJgYyv4d1tHm-XkOXfnpSawDg2JM5Tz0qMu6zaXpkGZpYMiSu8Ww8lM1Sj967Uyz4Iem5SjRTQV07AZfSXlIqGqKnX1y6aaiPcM87D13Vu2HEbU5O7OGtOrVPoiFMaQWDVyR9MlV8xj7H9cGn7-LEkZ=w1280)」（260 字）
- 「[Download WiFiPass (WiFi登入通) APP from Google Play](https://play.google.com/store/apps/details?id=com.project.twwifipass&hl=en)」（126 字）
- 「![](https://lh3.googleusercontent.com/sitesv/AG8ngQWukuOkbNxSi8lUu_zAhzyNt6V_lMEGEGV3QDON5l4j8lE6PWtYTy-Ux7xfY5GAvZy_kL6E2kbjqWbgicGjTl3Z1r2PpKm2W5gy2i79w_yYOhbnCIB-dixmAo03QcwH3klzbP4y1syHZjh0IE4CIgwFwyhOZySBcMOH3KpFaR08NYHEDfUMPdp-dxkq5QdzPY5D6nsiOA=w1280)」（258 字）
- 「[Download Y5Pass APP from Google Play](https://play.google.com/store/apps/details?id=tw.edu.ncu.wifipass&hl=en)」（111 字）

### 頁面: `projects_powerpoi`

**差異**: Baseline 20 行 → Experiment 10 行（移除 10 行）

**其他被移除行（需人工審核）**:

- 「# PowerPOI」（10 字）
- 「**Project Leader** : Prof. Chia-Hui Chang **Team members** : Hsiu-Min Chuang, Ting-Yao Kao, Chung-Ting Cheng, Ya-Yun Huang, Guo-Bin Chang, Kai-Chien Yang, Chien-Fu Ling, Yuan-Hao Lin, Hung-Wei Chang **Abstract** With the popularity of mobile devices and smartphones, we have witnessed rapid growth in mobile applications and services, especially in location-based services (LBS). According to a mobile marketing survey, maps/location searches are among the most utilized services on smartphones. Points of interest (POIs), such as stores, shops, gas stations, parking lots, and bus stops, are particularly important for maps/location searches. Existing map services such as Google Maps and Wikimapia are constructed manually either professionally or with crowdsourcing. However, manual annotation is costly and limited in current POI search services. With the abundance of information on the Web, many business POIs can be extracted from the Web. In this project, we focus on automatically constructing a POI database to enable business POI map searches. We propose techniques that are required to construct a POI database, including focused crawling, information extraction, and information retrieval techniques. We first crawl Yellow Page websites to obtain vocabularies of business names. These vocabularies are then investigated with search engines to obtain sentences containing these business names from search snippets in order to train a business-name recognition model. To extract POIs scattered across the Web, we propose a query-based crawler to find address-bearing pages that might be used to extract addresses and business names. We crawled 1.25 million distinct POI pairs scattered across the Web and implemented a POI search service via Apache Lucent's search platform, called Solr. The experimental results demonstrate that the proposed geographical information retrieval model outperforms Wikimapia and a commercial app called "What's the Number?" [: (in Chinese)](https://www.google.com/url?q=https%3A%2F%2Fpowerpoi.widm.csie.ncu.edu.tw%2Fdashboard&sa=D&sntz=1&usg=AOvVaw0TgHtKfYowWmR72-XiMMVi) [![https://itunes.apple.com/tw/app/id1057491998](https://lh3.googleusercontent.com/sitesv/AG8ngQV5gwp0DaFsi8T1uaM3zoBj-BaBV5ik4H6891sKk_ykQ3udm5DXlAEA0SntFqituxVCDkVqvI2pI2jFa1oFZ2Z9fMR-AAT94vQnfTEkOXiCQz9O5_E_8SJs178zThMbeODlhNDNLtdBTqIObLLReeBF_2svqxkJ12xIhzigXJYdjZ_G7tgSZrPfvNJQ2oTgud9nFaU=w1280)」（2414 字）
- 「](https://www.google.com/url?q=https%3A%2F%2Fitunes.apple.com%2Ftw%2Fapp%2Fid1057491998&sa=D&sntz=1&usg=AOvVaw3dpTar0dnttCxOr5087pd-) [**Download PowerPOI (疾疾店家現身) APP from Apple Store**](https://www.google.com/url?q=https%3A%2F%2Fitunes.apple.com%2Ftw%2Fapp%2Fid1057491998&sa=D&sntz=1&usg=AOvVaw3dpTar0dnttCxOr5087pd-) **Publication**」（335 字）
- 「- C.-H. Chang, H.-M. Chuang, C.-Y. Huang, Y.-S. Su, S.-Y. Li. [Enhancing POI Search on Maps via Online Address Extraction and Associated Information Extraction](http://www.google.com/url?q=http%3A%2F%2Flink.springer.com%2Farticle%2F10.1007%252Fs10489-015-0707-5&sa=D&sntz=1&usg=AOvVaw1Fb21IPlPSRZNPj08uiqJa), Applied Intelligence, Volume 44, [Issue 3](http://www.google.com/url?q=http%3A%2F%2Flink.springer.com%2Fjournal%2F10489%2F44%2F3%2Fpage%2F1&sa=D&sntz=1&usg=AOvVaw1YS-DldVUYmTJdHcOOn63e), pp 539–556, 2015.」（513 字）
- 「**Related Technologies (Provide the training datasets for download)**」（69 字）
- 「- Address extraction: ( for Chinese; [Collection](https://www.google.com/url?q=https%3A%2F%2Fweb.cs.dal.ca%2F~zyu%2Fresearch%2F&sa=D&sntz=1&usg=AOvVaw04qptrRsKlE0XiyL8OggzV) for English provided by Z. Yu)」（204 字）
- 「- Business-name recognition: ()」（31 字）
- 「- Address-POI name pairing: (, window size=100)」（47 字）
- 「- Address-POI name verification: ()」（35 字）
- 「**Acknowledgement** This project is partially sponsored by the Ministry of Science and Technology in Taiwan under grant MOST103-2221-E-008-094」（142 字）

### 頁面: `projects_powerpoi_mapmarkerextractionofpostaladdressesandassociatedinformationforgeneralwebpages`

**差異**: Baseline 9 行 → Experiment 3 行（移除 5 行）

**其他被移除行（需人工審核）**:

- 「Post date: Jul 7, 2010 6:45:53 AM Address information is essential for people’s daily life. People often need to query addresses of unfamiliar location through Web and then use map services to mark down the location for direction purpose. Although both address information and map services are available online, they are not well combined. Users usually need to copy individual address from a Web site and paste it to another Web site with map services to locate its direction. Such copy and paste operations have to be repeated if multiple addresses are listed on a single page such as public school list or apartment list. Furthermore, associated information with individual address has to be copied and included on each marker for better comprehension. Our research is devoted to automate the above process and make the combination an easier task for users. The main techniques applied here include postal address extraction and associated information extraction. We apply sequence labeling algorithm based on Conditional Random Fields (CRFs) to train models for address extraction. Meanwhile, using the extracted addresses as landmarks, we apply pattern mining to identify the boundaries of address blocks and extract associated information with each individual address. The experimental result shows high F-score at 91% for postal address extraction and 87% accuracy for associated information extraction.」（1410 字）
- 「- Slides Download」（17 字）
- 「- DataSet Download：[Data Set](http://www.google.com/url?q=http%3A%2F%2F140.115.51.19%2FDataset.rar&sa=D&sntz=1&usg=AOvVaw3m4ngn75SnTaIzUVwrDp2A) (From[ Zheyuan Yu's Research](http://www.google.com/url?q=http%3A%2F%2Fweb.cs.dal.ca%2F%257Ezyu%2Fresearch%2F&sa=D&sntz=1&usg=AOvVaw0ND36bi1UCmDZSl53ErV0z))」（301 字）
- 「- Demonstration web site：[http://140.115.51.18/MapMarker.html](http://www.google.com/url?q=http%3A%2F%2F140.115.51.18%2FMapMarker.html&sa=D&sntz=1&usg=AOvVaw2uZ_lvg8OXhDjLrOxb-D-i)」（180 字）
- 「[](https://drive.google.com/folderview?id=0B2XRm-m6dNA8b2kwTzRLQ2E3ZnM "Open Drive Folder in new window")」（105 字）

### 頁面: `projects_storychatbot`

**差異**: Baseline 26 行 → Experiment 1 行（移除 16 行）

**短文本雜訊（預期移除）**:

- 「##」（2 字）

**其他被移除行（需人工審核）**:

- 「# Story ChatBot (2022-2025)」（27 字）
- 「## PI & Co-PI: 張嘉惠、劉晨鐘、鐘曉芳、鄭芳祥」（30 字）
- 「## Team member:」（15 字）
- 「2021-2022 黃紫嫺、黃覺修、高愷言、陳臆玄 2022-2023 林子平、李聿鎧、黃冠傑、黃淯銘 2023-2024 黃冠傑、黃淯銘、龔若齊、丁仕杰、謝程偉」（81 字）
- 「## Abstract」（11 字）
- 「溝通技巧是學業成功和健康關係的重要組成部分。傳統以教師為中心的教學方式通常是單向的知識傳遞, 課堂上留給學生互動討論的時間很有限。為了提高學齡兒童的口語敘述能力, 本計畫希望構建一個聊故事機器人，可以與小學生（用中文）談論他們讀到的英語故事、透過互動練習來表達他們所閱讀、感受和發現的內容，以支持他們的觀點或建立他們對生活的態度。我們將使用資訊擷取作為機器人理解故事的基礎，透過4F（Fact、Fact、Feeling、Discovery、Future）提問引導學童回答故事相關問題，以及感受、發現、與預測故事的可能發展。除了引導學童回顧所閱讀的故事，聊故事機器人也要能回應學童的問題，同時也能基於常識知識圖譜（CSKG）理解學童的感受，給予同理心回覆。希望透過互動提高學習者的敘述技巧，並鼓勵他們表達自己的觀點。」（357 字）
- 「## Publications:」（16 字）
- 「1. 黃冠傑、黃淯銘、張嘉惠、黃覺修、鍾曉芳、鄭芳祥, 通過實體和事件關係標記改進問題答案對生成的 控制 , NCS2023.」（63 字）
- 「1. 許志仲、朱翊瑄、劉晨鐘、張嘉惠、温采婷, 基於生成式語言模型之科學探究教學代理之提示詞框架與系統設計, NCS2023.」（63 字）
- 「1. 李聿鎧 、應用強化學習與知識圖譜於故事共述生成之研究, ROCLING 2023 （最佳論文奬）」（51 字）
- 「1. 林子平、張嘉惠、劉晨鐘: 基於大型語言模型應用指示詞打造無程式碼對話系統平台 - 以聊故事機器人為例,TAAI 2023」（63 字）
- 「1. 黃紫嫺、張嘉惠: [基於常識知識的移情對話回覆生成](https://aclanthology.org/2022.rocling-1.37.pdf), ROCLING 2022」（91 字）
- 「1. 高愷言、張嘉惠: [應用自動資訊擷取於故事書問答之研究](https://aclanthology.org/2022.rocling-1.36.pdf),ROCLING2022」（91 字）
- 「[EduACT (Educational Agent Crafting Tool)](https://eduact.csie.ncu.edu.tw/)」（75 字）

### 頁面: `projects_web-ner-tool`

**差異**: Baseline 13 行 → Experiment 7 行（移除 6 行）

**其他被移除行（需人工審核）**:

- 「# Web NER ToolKit」（17 字）
- 「**Project Leader** : Prof. Chia-Hui Chang **Team members** : Chien-Lung Chou, Yuan-Hao Lin, Kuo-Chun Chien, Ya-Yun Huang **Abstract** Named entity recognition (NER) is of vital importance in information extraction and natural language processing. Current NER research are trained mainly on journalistic documents such as news articles for person names, location names, and organization names recognition. Since such NER models are trained to deal with informal documents, the performance drops on Web documents which are less structured and contain noise. When users want to recognize named entity from Web documents, they certainly have to retrain the new model. Retraining a new model is labor intensive and time consuming. The preparatory work includes preparing a large set of training data, labeling named entity, selecting an appropriate segmentation, symbols unification, normalization, designing feature, preparing dictionary, and so on. The pre-processing work is very complicated. Besides, users need to repeat the previous work for different languages or different recognition types. In this research, we propose a NER model generation tool for effective Web entity extraction. We propose a semi-supervised learning approach for NER via automatic labeling and tri-training which makes use of unlabeled data and structured resources containing known named entities. Experiments confirmed that the use of this tool can be applied in different languages for various types of named entities. 在過去，命名實體辨識（NER）研究都以新聞報導等正式文章中的人名、地名、組織名稱為主，相對地以網路的非正式文章則著墨較少。因此，現有的辨識模組對於網頁內容的辨識效果顯得較差，當需要辨識網頁內容中的命名實體時，勢必要重新訓練辨識模組。然而，訓練一個模型的時間和人力成本非常高，包含前置的大量訓練資料準備、人工收集及標記答案，且為了提升模組辨識效果，必須要為資料做適當切割、符號統一、正規化，以及特徵值的設計、準備已知關鍵詞庫（Dictionary）等，工作非常瑣碎複雜。此外，對於不同語言或不同辨識主題則需重複上述工作。本論文的目的，期能解決上述命名實體辨識工作過於費力耗時的問題，經由給定已知實體名稱的搜尋結果來自動標記訓練資料，並結合Tri-training半監督式訓練來產生NER模組。實驗證實，使用本工具可以套用在不同語言及類型的命名實體辨識，在中文組織名稱辨識的效能可達到86.1%，在日文組織名稱辨識的效能可達到80.3%，在英文組織名稱辨識的效能可達到83.2%，辨識不同主題的中文地點名稱辨識效能可達到84.5%，另外，辨識較長的命名實體如中文地址及英文地址辨識效能也可達到97.2%及94.8%。 [**DS4NER Package Download**](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner) **Publication**」（2118 字）
- 「- Chien-Lung Chou, Chia-Hui Chang, Ya-Yun Huang: [Boosted Web Named Entities Recognition via Tri-Training](http://www.google.com/url?q=http%3A%2F%2Fdl.acm.org%2Fcitation.cfm%3Fid%3D2963100&sa=D&sntz=1&usg=AOvVaw1mLZABYX3wUFfLf6pHnFwG), Transactions on Asian and Low-Resource Language Information Processing, Volume 16 Issue 2, November 2016.」（341 字）
- 「- [Chien-Lung Chou](http://www.google.com/url?q=http%3A%2F%2Fwww.informatik.uni-trier.de%2F%257Eley%2Fpers%2Fhd%2Fc%2FChou%3AChien%3DLung.html&sa=D&sntz=1&usg=AOvVaw3GEZVvy4h7XR-iMDBsn1Xz), Chia-Hui Chang: Named Entity Extraction via Automatic Labeling and Tri-training: Comparison of Selection Methods. [AIRS 2014](http://www.google.com/url?q=http%3A%2F%2Fwww.informatik.uni-trier.de%2F%257Eley%2Fdb%2Fconf%2Fairs%2Fairs2014.html%23ChouC14&sa=D&sntz=1&usg=AOvVaw23SbQAbEG_FzTN9HKoqzMk): 244-25.」（495 字）
- 「**Datasets**」（12 字）
- 「- Person name recognition\*\*:\*\*[https://drive.google.com/open?id=0Bw1kEtCT1xvKTUtzbE8xVTBRS00](https://www.google.com/url?q=https://drive.google.com/open?id%3D0Bw1kEtCT1xvKTUtzbE8xVTBRS00&sa=D&ust=1467819881025000&usg=AFQjCNEAYfqA7OxeB595t46h-iEgPRwSsQ)」（256 字）

### 頁面: `projects_web-ner-tool_ds4ner`

**差異**: Baseline 112 行 → Experiment 40 行（移除 57 行）

**其他被移除行（需人工審核）**:

- 「### DS4NER: Distant Supervision for Named Entity Recognition」（60 字）
- 「**Introduction** DS4NER is a simple, customizable implementation of Distant Supervision for Named entity recognition. DS4NER is designed for preparing training data for Named Entity Recognition.」（194 字）
- 「- Written in Java」（17 字）
- 「- Can specify source other than Web」（35 字）
- 「- Ready for error analysis」（26 字）
- 「- Available as an open source software」（38 字）
- 「**Table of contents**」（21 字）
- 「- [Installation](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（83 字）
- 「- [Getting started](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（86 字）
- 「- [Main Modules](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（83 字）
- 「- [File formats](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（83 字）
- 「- [Automatic labeling](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（89 字）
- 「- [Dictionary mining](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（88 字）
- 「- [Feature generation](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（89 字）
- 「- [Model training & testing with CRF++](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（106 字）
- 「- [Data crawling](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（84 字）
- 「- [Release history and download](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（99 字）
- 「- [References](https://sites.google.com/site/nculab/projects/web-ner-tool/ds4ner)」（81 字）
- 「**Installation**」（16 字）
- 「**Getting started**」（19 字）
- 「- **Data preparation and model training:**」（42 字）
- 「**training.cmd (for Windows) or training.sh (for Linux)** This batch includes Pre-Processing, Automatic Labeling, Dictionary Mining, Feature Generation and CRF Training. The input is two files: Corpus.txt and Seeds.txt under the "Corpus\\Training directory" where the former is the sentence corpus needs to be labeled while the later is a list of seed entities. The output is the NER model, "Corpus.model", in the "Corpus\\Training" directory.」（443 字）
- 「**extractor.cmd or extractor.sh** This batch file uses the trained model "Corpus.model" in the "Corpus\\Training" directory and the test corpus "UnLabeledExtractorCorpus.txt" in the "Corpus\\Testing" directory as input. Recognized named entities will be labeled with paired <NE></NE> tags with a new file name UnLabeledExtractorCorpus_Output.txt in the same "Corpus\\Testing" directory.」（386 字）
- 「- **Model testing and performance evaluation with labeled test set**」（68 字）
- 「**evaluation.cmd or evaluation.sh** This batch file uses the trained model "Corpus.model" in the "Corpus\\Training" directory and the test corpus "LabeledExtractorCorpus.txt" in the "Corpus\\Testing" directory as input. The output is shown in "WorkFolder\\Eva_Exact" and "WorkFolder\\Eva_Partial" directories, representing the performance evaluation in terms of exact match and partial match. Note that the batch also includes Pre-Processing, Feature Generation, CRF Testing. **File formats**」（492 字）
- 「- Seed file: Every line is an entity.」（37 字）
- 「王建民 林書豪 李安」（10 字）
- 「- Corpus: Each line represents a sentence.」（42 字）
- 「郭泓志、羅嘉仁也可能搶進最後名單，還有18歲超級新秀曾仁和等，都是重點討論人選。 猿隊甫給「小飛機」陳冠任一紙3年總值936萬元的合約，正好成為周思齊的最佳比較指標。」（83 字）
- 「在今年全英羽球公開賽前，「世界球后」<NE>戴資穎</NE>的世界排名積分，僅領先第2名、日本好手<NE>山口茜</NE>5826分，理論上尋求衛冕的<NE>戴資穎</NE>，是有可能在打不好的情況下，被<NE>山口茜</NE>取代球后寶座，不過這一切隨著<NE>戴資穎</NE>順利闖進今年全英羽球公開賽 4強而宣告破滅，<NE>戴資穎</NE>確定將續坐球后寶座。」（184 字）
- 「- Config.ini contains the following parameters:」（47 字）
- 「**Automatic labeling** Java –cp NER.jar PrepareData.AutoLabeling -strInput_S <Input Corpus> -strSeeds_S <Seed File> -strOutput_L <Output Corpus> -bFilterNegExamples True -bPreProcessing True」（190 字）
- 「- Use "-bFilterNegExamples True" to remove sentences not containing entities.」（77 字）
- 「- Use "-bPreProcessing True" to show the preprocessing time.」（60 字）
- 「**Dictionary mining** java -cp NER.jar PrepareData.MineDict -strInput_L <Labeled Corpus> -strMethod Supp -fThreshold 0.5f」（121 字）
- 「**Feature generation** java -cp NER.jar PrepareData.GenFeature -strInput_L <Labeled Corpus> -strOutput_F <Labeled Matrix> -strType Training -bPreProcessing False」（161 字）
- 「- 特徵擷取使用「WorkFolder\\Training」目錄下的Corpus_L.txt，以及「WorkFolder\\Dictionary」 下的字典檔做為輸入，產生特徵矩陣標記資料檔案Corpus_F.txt。」（109 字）
- 「- 可以透過-strInput_L、-strOutput_F、strType改變<Labeled Corpus>輸入及<Labeled Matrix>輸出檔名以及此特徵矩陣標記檔案的用途(Training、Testing…)。輸入檔案為包含標記的文件。」（126 字）
- 「- -bPreProcessing: 輸入檔案是否需執行前處理，依據-StrType以及-bPreProcessing兩個參數決定資料來源，細節請參考文件。」（78 字）
- 「**Model training & testing with CRF++** java -cp NER.jar Training.CRF -strInput_F <Labeled Matrix> -strModel <Model Name>」（121 字）
- 「- 訓練模型使用Automatic labeling產出的已標記資料，預設輸入檔案預設位置為:「WorkFolder\\Training\\Corpus_F.txt」，輸出模型檔案位置為「WorkFolder\\Training\\Corpus.model」（128 字）
- 「- strInput_F: 輸入檔案格式為Feature Generation的輸出Labeled Matrix，預設檔案放置目錄為「WorkFolder\\Training」。」（89 字）
- 「- strModel: 輸出模型的檔案名稱，使用方法「-strModel Corpus.model」。預設輸出檔案放置目錄為「WorkFolder\\Training」。」（85 字）
- 「java -cp NER.jar PrepareData.GenFeature -strInput_L <Labeled Corpus> -strOutput_F <Labeled Matrix> -strType Testing -bPreProcessing True」（136 字）
- 「- strInput_L: 輸入檔案格式為Feature Generation的輸出<Labeled Matrix>，預設位置為: 「Corpus\\Testing\\TestCorpus_F.txt」。」（102 字）
- 「- strOutput_F: 轉成特徵矩陣標記格式的輸出，預設輸出檔案放置目錄為「WorkFolder\\Testing」。」（62 字）
- 「java -cp NER.jar Testing.Evaluation -strModel Corpus.model -strMethod <Method> -strOutput_Dir <Folder Name>」（107 字）
- 「- strMethod: 評估方式有兩種分別是「Exact」和「Partial」，使用方法「- strMethod Partial or Exact」。」（76 字）
- 「- strOutput_Dir: 評估結果的輸出目錄，使用方法「-strOutput_Dir Eva_Partial」。預設輸出目錄位於「WorkFolder」目錄下。」（84 字）
- 「**Data crawling** java -cp NER.jar Crawler.WebCrawler -strSeeds <Seed File> -strOutput <Output File>」（100 字）
- 「- 爬取語料庫: 若使用者有興趣自行收集資料，DS4NER亦提供一支Crawler (網路爬蟲)，可自Google的搜尋結果中擷取包含seed的句子作為語料。」（79 字）
- 「- strSeeds: 關鍵字清單的檔案名稱，檔案格式參考Seed file。預設實體列表檔案放置路徑為「Corpus\\Training」。」（71 字）
- 「- strOutput: 輸出語料庫的檔案名稱，檔案格式參考Corpus format。預設輸出檔案放置路徑為「Corpus\\Training」。」（74 字）
- 「**Release history and download**」（32 字）
- 「- 2018-05-02: [DS4NER v1.00](https://drive.google.com/open?id=1ENKhjkxcf_hcGtUTZSPNDg4o4tU_Oo7B) Released」（105 字）
- 「- 2018-06-03: [DS4NER v1.01](https://drive.google.com/open?id=12Vy-KckbVUaPaAu40CnvaP_dPAcUhUbL) Released」（105 字）
- 「**References**」（14 字）

### 頁面: `publication`

**差異**: Baseline 215 行 → Experiment 255 行（移除 178 行）

**其他被移除行（需人工審核）**:

- 「# Publication」（13 字）
- 「### Journal Papers」（18 字）
- 「[](https://sites.google.com/site/nculab/publication#h.p_ID_34)」（62 字）
- 「1. Chung-Yu Shih, Shi-Jie Ding, Cissi Ying-tsen Lin, Chia-Hui Chang, Feng-Nan Hwang: Near real-time high-accuracy GPS orbit correction with deep learning, submitted to ION NAVIGATION, 2026 (submitted).」（201 字）
- 「1. Yuan-Hao Lin; Chia-Hui Chang; Hsiu-Min Chuang: [Fine-Grained Meetup Events Extraction Through Context-Aware Event Argument Positioning and Recognition](https://link.springer.com/article/10.1007/s44196-024-00697-0), International Journal of Computational Intelligence Systems 17, 296 2024. [https://doi.org/10.1007/s44196-024-00697-0](https://doi.org/10.1007/s44196-024-00697-0)」（380 字）
- 「1. Liu, CC., Chiu, C.W., Chang, CH. et al. Analysis of a chatbot as a dialogic reading facilitator: its influence on learning interest and learner interactions. Education Tech Research Dev72, 2103–2131 (2024). [https://doi.org/10.1007/s11423-024-10370-0](https://doi.org/10.1007/s11423-024-10370-0)」（298 字）
- 「1. Yuan-Hao Lin; Chia-Hui Chang; Hsiu-Min Chuang; Xiang-Shun Lin; Ting Yeh; Min-Jhao Hong: [Cost-Effective Event Mining on the Web via Event Source Page Discovery and Data API Construction](https://ieeexplore.ieee.org/document/10638638/authors#authors),[IEEE Access 12](https://dblp.org/db/journals/access/access12.html#LinCCLYH24): 115981-115993 (19 August 2024)DOI: [10.1109/ACCESS.2024.3445448](https://doi.org/10.1109/ACCESS.2024.3445448)」（442 字）
- 「1. Chung-Yu Shih, Cissi Ying-tsen Lin, Shu-Yu Lin, Cheng-Hung Yeh, Yu-Ming Huang, Feng-Nan Hwang, Chia-Hui Chang: [Forecasting of Global Ionosphere Maps With Multi-Day Lead Time Using Transformer-Based Neural Networks](https://ieeexplore.ieee.org/document/10638638), Space Weather, Volume 22, Issue 2, Jan. 2024.[https://doi.org/10.1029/2023SW003579](https://doi.org/10.1029/2023SW003579)」（388 字）
- 「1. Shih, C. Y., Chang, C. M., Wu, B. F., [Chang, C. H.](https://scholars.ncu.edu.tw/zh/persons/chia-hui-chang) & [Hwang, F. N.](https://scholars.ncu.edu.tw/zh/persons/feng-nan-hwang): [Data-driven numerical simulation with extended Kalman filtering and long short-term memory networks for highway traffic flow prediction](https://academic.oup.com/jom/article/doi/10.1093/jom/ufad046/7480256), [Journal of Mechanics](https://academic.oup.com/jom/). Vol. 40, p. 31-43. 2024.」（472 字）
- 「1. Kuo-Chun Chien, Chia-Hui Chang, R. D. Sun:[Legal Knowledge Management for Prosecutors based on Judgement Prediction and Error Analysis from Indictments](https://www.sciencedirect.com/science/article/abs/pii/S0267364923001127), Computer Law & Security Review: The International Journal of Technology Law and Practice. Nov. 2023.」（330 字）
- 「1. Yu-Xiang Hong, Chia-Hui Chang: [Improving Colloquial Case Legal Judgment Prediction via Abstractive Text Summarization](https://www.sciencedirect.com/science/article/abs/pii/S0267364923000730), Computer Law & Security Review: The International Journal of Technology Law and Practice, Nov. 2023.」（297 字）
- 「1. Yuan-Hao Lin, Chia-Hui Chang, Hsiu-Min Chuang: [EventGo! Mining Events through Semi-Supervised Event Title Recognition and Pattern-based Venue/Date Coupling](https://doi.org/10.6688/JISE.202305_39%283%29.0013), Journal of Information Science and Engineering, Vol. 39, No. 3, pp.655 - 670, 2023. [10.6688/JISE.202305_39(3).0013](https://doi.org/10.6688/JISE.202305_39%283%29.0013)」（382 字）
- 「1. 張嘉惠,葉丞鴻, 李聿鎧: 多領域任務導向一對一用戶對話收集系統, International Journal of Computational Linguistics & Chinese Language Processing (IJCLCLP), 2023」（133 字）
- 「1. 張嘉惠,陳臆玄,劉晨鐘,鄭芳祥:聊故事機器人對話回應模組選擇之研究, Submitted to International Journal of Computational Linguistics & Chinese Language Processing (Under Revision)」（148 字）
- 「1. [Chen-Chung Liu](https://dblp.org/pid/76/122.html), [Mo-Gang Liao](https://dblp.org/pid/328/8100.html), Chia-Hui Chang, [Hung-Ming Lin](https://dblp.org/pid/38/7288.html): [An analysis of children' interaction with an AI chatbot and its impact on their interest in reading](https://www.sciencedirect.com/science/article/abs/pii/S0360131522001476#:~:text=It%20was%20found%20that%20students,with%20the%20chatbot%20faded%20significantly.).[Comput. Educ. 189](https://dblp.org/db/journals/ce/ce189.html#LiuLCL22): 104576 (2022)」（526 字）
- 「1. Chen-Chung Liu, [Tsun-Wei Lin](https://dblp.org/pid/316/5127.html), [Chia-Hui Cheng](https://dblp.org/pid/23/11310.html), [Cai-Ting Wen](https://dblp.org/pid/205/6234.html), [Ming-Hua Chang](https://dblp.org/pid/17/4802.html), [Shih-Hsun Fan Chiang](https://dblp.org/pid/98/8648.html), [Meng-Jung Tsai](https://dblp.org/pid/63/379.html), [Hung-Ming Lin](https://dblp.org/pid/38/7288.html), [Fu-Kwun Hwang](https://dblp.org/pid/93/7708.html): The impact of functional interdependencies of computer simulations on collaborative learning: Evidence from multiple sources.[J. Comput. Assist. Learn. 38(2)](https://dblp.org/db/journals/jcal/jcal38.html#LiuLCWCCTLH22): 455-469 (2022)」（680 字）
- 「1. [Chun-Nan Hsu](https://www.prophy.science/author/6665029/Chun-Nan-Hsu), [Chia-Hui Chang](https://www.prophy.science/author/7880155/Chia-Hui-Chang), [Thamolwan Poopradubsil](https://www.prophy.science/author/56085830/Thamolwan-Poopradubsil), [Amanda Lo](https://www.prophy.science/author/4631575/Amanda-Lo), [Karen A. William](https://www.prophy.science/author/37384906/Karen-A-William), [Ko-Wei Lin](https://www.prophy.science/author/4494245/Ko-Wei-Lin), [Anita Bandrowski](https://www.prophy.science/author/759591/Anita-Bandrowski), [Ibrahim Burak Ozyurt](https://www.prophy.science/author/591672/Ibrahim-Burak-Ozyurt), [Jeffrey S. Grethe](https://www.prophy.science/author/1040933/Jeffrey-S-Grethe), [Maryann E. Martone](https://www.prophy.science/author/834956/Maryann-E-Martone): [Antibody Watch: Text Mining Antibody Specificity from the Literature](https://europepmc.org/article/med/34043624), [arXiv:2008.01937v1](https://arxiv.org/abs/2008.01937v1). Plos Computational Biology, 17(5):e1008967 (2021)」（1010 字）
- 「1. Chien-Lung Chou, Chia-Hui Chang, Yuan-Hao Lin, Kuo-Chun Chien: [On the Construction of Web NER Model Training Tool based on Distant Supervision](https://dl.acm.org/doi/10.1145/3422817), Transactions on Asian and Low-Resource Language Information Processing, Transactions on Asian and Low-Resource Language Information Processing, 19(6), 1-28. (2020)」（352 字）
- 「1. Oviliani Yenty Yuliana and Chia-Hui Chang, [DCADE: divide and conquer alignment with dynamic encoding for full page data extraction](http://link.springer.com/article/10.1007/s10489-019-01499-0), Applied Intelligence, 50(2), 271-295 (2020).」（242 字）
- 「1. H.-M. Chuang, C.-H. Chang, W.-C. Lee, [Detecting Outdated POI Relations via Web-derived Features](https://onlinelibrary.wiley.com/doi/abs/10.1111/tgis.12461?af=R), Trans. on GIS, 22(5), 1238-1256 (2018).」（206 字）
- 「1. O. Yuliana, C.-H. Chang\*, [A novel alignment algorithm for effective web data extraction from singleton pages](https://link.springer.com/article/10.1007/s10489-018-1208-0), Applied Intelligence, 48(11), 4355-4370 (2018).」（224 字）
- 「1. Chien-Lung Chou, Chia-Hui Chang\*, Ya-Yun Huang: [Boosted Named Entities Recognition via Tri-Training](https://dl.acm.org/ft_gateway.cfm?id=2963100&ftid=1801771&dwn=1&CFID=3884938&CFTOKEN=e292d63443924021-FCA6A7CE-B4C7-C442-3E595871FF6C7249), [ACM Transactions on Asian and Low-Resource Language Information Processing 16(2)](http://dl.acm.org/citation.cfm?id=2963100) (2016) \[[pdf](https://dl.acm.org/ft_gateway.cfm?id=2963100&ftid=1801771&dwn=1&CFID=3884938&CFTOKEN=e292d63443924021-FCA6A7CE-B4C7-C442-3E595871FF6C7249)\].」（528 字）
- 「1. H.-M. Chuang, C.-H. Chang\*, Ting-Yao Kao, Chung-Ting Cheng and Ya-Yun Huang, K.-P. Cheong: [Enabling Maps/Location Searches on Mobile Devices: Constructing a POI Database via Focused Crawling and Information Extraction](http://www.tandfonline.com/doi/full/10.1080/13658816.2015.1133820), International Journal of Geographical Information Science, 30(7): 1405-1425 (2016) \[[pdf](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MzIxMjllNmM2ZWNmNDE3ZQ)\]」（506 字）
- 「1. C.-H. Chang\*, H.-M. Chuang, C.-Y. Huang, Y.-S. Su, S.-Y. Li: [Enhancing POI Search on Maps via Online Address Extraction and Associated Information Extraction](https://doi.org/10.1007/s10489-015-0707-5), Applied Intelligence. 44(3): 539-556 (2016) \[[pdf](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MzIxMjllNmM2ZWNmNDE3ZQ)\]」（383 字）
- 「1. J.-R. Chang, Y.-H. Jheng, C.-H. Chanag\*, C.-Y. Lo: [An efficient algorithm for vehicle guidance combining the Dijkstra and A\* algorithm with fuzzy inference theory](http://jit.ndhu.edu.tw/jitcontent.php?getserial=1159&Vol2=16&No2=2), Journal of Internet Technology, 16(2):189-200 (2015)」（291 字）
- 「1. J.-C. Chen, I.-C. Wu, W.-J. Tseng, B.-H. Lin, C.-H. Chang: [Job-Level Alpha-Beta Search](http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=6785996), IEEE Transactions on Computational Intelligence and AI in Game, 7(1): 28-38 (2015) 10.1109/TCIAIG.2014.2316314 \[[pdf](http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6785996)\]」（340 字）
- 「1. Q. Chen and C.-H. Chang\*: [Enhancement of Kernel Dependency Estimation with Information Generalization and Case Study on Skewed Data](http://dx.doi.org/10.1007/s10489-014-0539-8), [Applied Intelligence](http://link.springer.com/journal/10489), Vol. 41, Issue 2, pp. 582-593. (2014). 10.1007/s10489-014-0539-8」（312 字）
- 「1. M.-L. Wu and C.-H. Chang\*: [Integrating Content-Based Filtering with Collaborative Filtering using Co-Clustering with Augmented Matrices](https://www.sciencedirect.com/science/article/pii/S0957417413008130), [Expert Systems With Applications](http://www.sciencedirect.com/science/journal/09574174), Vol. 41, Iss. 6, pp. 2754-2761. ( 2014) [10.1016/j.eswa.2013.10.008](http://www.sciencedirect.com/science/article/pii/S0957417413008130)」（439 字）
- 「1. M.-L. Wu, C.-H. Chang\*, R.-Z. Liu: [Co-clustering with Augmented Data Matrix](https://link.springer.com/chapter/10.1007/978-3-642-23544-3_22). [Applied Intelligence](http://link.springer.com/journal/10489). 39(1): 153-164 (2013).」（233 字）
- 「1. C.-H. Chang\*, S.-Y. Lin, M.-F. Tsai, S.-P. Li, H.-M. Liao, and N. E. Huang:[ Phonetic Component Ranking and Pronunciation Rule Mining for Chinese Picto-phonetic Compounds](http://www.aclclp.org.tw/clclp/v17n3/v17n3a2.pdf). [International Journal of Computational Linguistics & Chinese Language Processing](http://www.aclclp.org.tw/journal/), 17(3):29-44 (2012).」（365 字）
- 「1. M.-L. Wu, C.-H. Chang\*, R.-Z. Liu, T.-K. Fan: [Aggregate Two-way Co-Clustering of Ads and User Data for Online Advertisements](http://www.iis.sinica.edu.tw/page/jise/2012/201201_06.html), Journal of Information Science and Engineering, Vol. 28 No. 1. Pages 83-97 (January 2012) \[[pdf](http://www.iis.sinica.edu.tw/page/jise/2012/201201_06.pdf)\]」（350 字）
- 「1. T.-K. Fan and C.-H. Chang\*: [Blogger-Centric Contextual Advertising](http://www.sciencedirect.com/science?_ob=ArticleURL&_udi=B6V03-50PVFX4-C&_user=2489623&_coverDate=03%2F31%2F2011&_rdoc=56&_fmt=high&_orig=browse&_origin=browse&_zone=rslt_list_item&_srch=doc-info%28%23toc%235635%232011%23999619996%232568736%23FLA%23display%23Volume%29&_cdi=5635&_sort=d&_docanchor=&_ct=178&_acct=C000057545&_version=1&_urlVersion=0&_userid=2489623&md5=33221c946d28a0e2b86ab69fe812ebf3&searchtype=a). Journal of Expert Systems With Applications (SCI), Vol.38, Issue 3, pp. 1777-1788, Mar, 2011. (IF:2.908)」（594 字）
- 「1. Q.-X. Lin, C.-H. Chang\*, and J.-L. Chen: [A Simple and Effective Closed Test for Chinese Word Segmentation Based on Sequence Labeling](http://www.aclclp.org.tw/clclp/v15n34/v15n34a1.pdf). International Journal of Computational Linguistics & Chinese Language Processing, Vol. 15, No. 3-4, 2010.」（297 字）
- 「1. T.-K. Fan and C.-H. Chang\*: [Sentiment Oriented Contexture Advertising](http://dx.doi.org/10.1016/j.eswa.2010.07.105). [Journal of Knowledge and Information System](http://www.cs.uvm.edu/%7Ekais/).Vol. 23, No. 3, pp. 321-344, 2010.」（235 字）
- 「1. M. Kayed and C.-H. Chang\*: [FiVaTech: Page-Level Web Data Extraction from Template Pages](http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4476640). [IEEE Trans. Knowl. Data Eng. Vol. 22. No. 2, pp. 249-263](http://ieeexplore.ieee.org/document/4476640/), 2010. \[[pdf](http://staff.csie.ncu.edu.tw/chia/pub/FiVaTechCameraReady.pdf)\]」（344 字）
- 「1. T.-K. Fan and C.-H. Chang\*: [Exploring Evolutionary Technical Trends From Academic Research Papers](http://www.csie.ncu.edu.tw/%7Echia/pub/JISE-97-044.pdf). Journal of Information Science Engineering.Vol. 26, No. 1, pp. 97-117, 2010. \[[pdf](http://www.csie.ncu.edu.tw/%7Echia/pub/JISE-97-044.pdf)\]」（303 字）
- 「1. C.-H. Chang\*, S.-Y. Lin, S.-Y. Li, M.-F. Tsai, S.-P. Li, H.-M. Liao, C.-W. Sun, N. E. Huang: Annotating Phonetic Component of Chinese Characters Using Constrained Optimization and Pronunciation Distribution. [International Journal of Computational Linguistics & Chinese Language Processing, Vol. 15, No. 2, Pages 145-159 (June 2010)](http://www.aclclp.org.tw/clclp/v15n2.htm).」（380 字）
- 「1. K.-Y. Huang and C.-H. Chang\*: [Efficient Mining of Frequent Episodes from Complex Sequences](http://dx.doi.org/10.1016/j.is.2007.07.003), Information Systems, Vol. 33. No. 1, pp. 96-114 (2008). \[[pdf](http://www.csie.ncu.edu.tw/%7Echia/pub/emma.pdf)\]」（256 字）
- 「1. K.-Y. Huang, C.-H. Chang\*, and Kuo-Zui Lin: [EfficientDiscovery of Frequent Continuities by Projected Window List Technology](http://www.iis.sinica.edu.tw/page/jise/2008/200807_03.html), Journal of Information Science and Engineering, Vol. 24, No. 4, pp. 1041-1064, 2008.」（275 字）
- 「1. Y.C. Wu and C.-H. Chang: [Efficient Text Chunking using Linear Kernelwith Mask Method](http://dx.doi.org/10.1016/j.knosys.2006.04.016), Knowledge Based Systems, Vol. 20, Issue 3, pp. 209-219, 2007. \[[pdf](http://www.csie.ncu.edu.tw/%7Echia/pub/KNOSYS1593.pdf)\] [doi:10.1016/j.knosys.2006.04.016](http://dx.doi.org/10.1016/j.knosys.2006.04.016)」（348 字）
- 「1. C.-H. Chang\*, M. Kayed, M. R. Girgis, K. Shaalan: [A Survey of Web Information ExtractionSystems](http://ieeexplore.ieee.org/document/1683775/), IEEE TKDE (SCI, EI), Vol. 18, No. 10, pp. 1411-1428, Oct. 2006. \[[pdf](http://www.csie.ncu.edu.tw/%7Echia/pub/iesurvey2006.pdf)\]」（279 字）
- 「1. K.-Y. Huang and C.-H. Chang\*: [SMCA: A General Model for Mining Asynchronous Periodic Patternsin Temporal Databases](http://ieeexplore.ieee.org/document/1423978/), IEEE Transactions on Knowledge and Data Engineering (SCI, EI), Vol. 17, No. 6, pp. 774-785, June 2005. \[[pdf](http://www.csie.ncu.edu.tw/%7Echia/pub/TKDE-0147-0504-2.pdf)\]」（341 字）
- 「1. C.-H. Chang\* and Z.-K. Ding: [Categorical Data Visualization and Clustering Using Subjective Factors](http://www.sciencedirect.com/science/article/pii/S0169023X04001405023X04001405&usg=AOvVaw314jq750ivw6frJyzLQ1wU), Data and Knowledge Engineering (SCI expanded), Vol. 53, Issue 3, pp. 243-262, June 2005. \[[pdf](http://www.csie.ncu.edu.tw/%7Echia/pub/article_proof.pdf)\] [doi:10.1016/datak.2004.09.001](http://dx.doi.org/10.1016/j.datak.2004.09.001)」（455 字）
- 「1. C.-N. Hsu, C.-H. Chang, C.-H. Hsieh, J.-J. Lu, and C.-C. Chang: [Reconfigurable Web Wrapper Agents for Biological Information Integration](http://www3.interscience.wiley.com/cgi-bin/fulltext/109865531/PDFSTART), [JASIST](http://www3.interscience.wiley.com/cgi-bin/jtoc?ID=76501873)[ Special Issue on Bioinformatics](http://ils.unc.edu/bmh/JASIST-CFP.doc), Vol. 56, No. 5, pp. 505--517, March 2005.」（400 字）
- 「1. C.-H. Chang\* and S.-C. Kuo: [OLERA: A semi-supervised approach for Web data extraction with visualsupport](https://csdl.computer.org/csdl/mags/ex/2004/06/x6056.html), IEEE Intelligent Systems (SCI, EI), Vol. 19, No. 6, pp. 56--64, Dec. 2004. \[[pdf](http://www.csie.ncu.edu.tw/%7Echia/pub/56-65.pdf)\]」（305 字）
- 「1. C.-H. Chang, J.-J. Chiou, H. Siek, J.-J. Lu, and C.-N. Hsu: [Reconfigurable Web Wrapper Agents](http://ieeexplore.ieee.org/document/1234767/), IEEE Intelligent Systems (SCI, EI), Vol. 18, No. 5, pp. 34--40, Oct. 2003. \[[pdf](http://www.csie.ncu.edu.tw/%7Echia/pub/ieeeis.pdf)\]」（281 字）
- 「1. C.-H. Chang\*, C.-N. Hsu, and S.-C. Lui: [Automatic Information Extraction FromSemi-Structured Web Pages By Pattern Discovery](http://dx.doi.org/10.1016/S0167-9236%2802%2900100-8), Decision Support Systems Journal (SCI expanded), Vol. 35, Issue 1, pp. 129--147, Apr. 2003. \[[pdf](http://www.csie.ncu.edu.tw/%7Echia/pub/IEPAD.pdf)\] [doi:10.1016/S0167-9236(02)00100-8](http://dx.doi.org/10.1016/S0167-9236%2802%2900100-8)」（424 字）
- 「1. C.-C. Hsu and C.-H. Chang\*: [WebYacht: A Concept-based Search Tool for WWW](http://www.worldscientific.com/doi/abs/10.1142/S0218213099000105), International Journal on Artificial Intelligence Tools, 2000. \[[pdf](http://www.csie.ncu.edu.tw/%7Echia/pub/ijait.zip)\]」（268 字）
- 「1. C.-H. Chang and C.-C. Hsu: [Enabling concept-based relevance feedback on World Wide Web](http://ieeexplore.ieee.org/document/790812/), In IEEE Transactions on Knowledge and Data Engineering (SCI), Special Issue on Web Technologies, Vol.11, No.4, pp. 595-609, July/August 1999.」（279 字）
- 「1. C.-H. Chang and C.-C. Hsu: [Integrating query expansion and conceptual relevance feedback for personalized Web information retrieval](http://linkinghub.elsevier.com/retrieve/pii/S0169755298000762), Computer Networks and ISDN Systems, Vol. 30, pp.621-623, 1998.」（263 字）
- 「1. C.-H. Chang and C.-C. Hsu: [Customizable Multi-Engine Search Tool based on Clustering, In Computer Networks and ISDN Systems](https://ac.els-cdn.com/S0169755297000536/1-s2.0-S0169755297000536-main.pdf?_tid=694615e6-f03e-11e7-8652-00000aab0f27&acdnat=1514953830_fe05213b8a76f9a11d95910fe122cefd), Vol. 29, pp.1217-1224, 1997.」（327 字）
- 「### International Conference Papers」（35 字）
- 「1. Kuo-Chun Chien, Chia-Hui Chang: MECE-Driven Neuro-Symbolic Framework for Explainable Legal Inference, ICAIL2026, Singapore, June 8-12, 2026」（142 字）
- 「1. Cissi LIN, Chung-yu SHIH, Hsiang-wen CHENG, Shu-Chih YANG, Chia-Hui CHANG, Feng-Nan HWANG: Superrefraction Detection with FORMOSAT-7/COSMIC-2 GNSS-RO Observations, 23rd Annual Meeting of the Asia Oceania Geosciences Society (AOGS2026), Aug. 2-7, 2026」（253 字）
- 「1. Hsiang-Wen CHENG,Shu-Chih YANG, Chia-Hui CHANG, Yingtsen LIN, Chung-yu SHIH, Kai-Hsun CHEN, Wen-Chien CHANG, Cheng-Yung HUANG, Yi-Hsiu CHEN, Feng-Nan HWANG: Deep Learning for Detecting Super-refraction in GNSS RO Data, 23rd Annual Meeting of the Asia Oceania Geosciences Society (AOGS2026), Aug. 2-7, 2026」（308 字）
- 「1. Sji-Jie Ding, Chia-Hui Chang: Voice-Controlled Text Correction System for Chinese ASR Errors, ICASSP,Barcelona, Spain, May 4-8, 2026」（135 字）
- 「1. Chi-Ru Yeh, Chia-Hui Chang: PagePilot: web assistant based on natural language, International AAAI Conference on Web and Social Media (ICWSM 2026)」（149 字）
- 「1. Cheng Wei Xie, Kuan-Jung Chen, Kai-Hsun Chen, Chia-Hui Chang, Siaw-Fong Chung, Fang-Hsiang Cheng, Hui-Chun Hung, and Chen-Chung Liu: Understanding Students Through Dialogue: A Dialogue Knowledge Tracing System for Learning Analytics, CIKM 2025 Workshop on ProActLLM: Conversational Information Seeking with Large Language Models, Nov. 14, Coex, Seoul, South Korea.」（367 字）
- 「1. Kuo-Chun Chien, Chia-Hui Chang, Huai-Hsuan Huang and Jo-Chi Kung: Prosecutorial Outcome Predication with LoRA and QLoRA, 37th International Conference on Legal Knowledge and Information Systems​ ([JURIX 2024](https://jurix2024.law.muni.cz/)). Brno, Czech Republic. December 11-13, 2024」（288 字）
- 「1. Jo-Chi Kung, Huai-Hsuan Huang, Kuo-Chun Chien and Chia-Hui Chang: A Narrative Assistant for Traffic Accidents Based on Large Language Models (LLM), 37th International Conference on Legal Knowledge and Information Systems​ ([JURIX 2024](https://jurix2024.law.muni.cz/)). Brno, Czech Republic. December 11-13, 2024」（315 字）
- 「1. Ren-Der Sun, Chia-Hui Chang, and Kuo-Chun Chien: [New Horizons of Legal Judgement Predication via Multi-Task Learning and LoRA](https://www.researchgate.net/publication/376429858_New_Horizons_of_Legal_Judgement_Predication_via_Multi-Task_Learning_and_LoRA), 36th International Conference on Legal Knowledge and Information Systems ([Jurix 2023](https://jurix23.maastrichtlawtech.eu/)). Maastricht, the Netherlands, 18-20 December 2023.」（438 字）
- 「1. [Yong Ting Feng](https://dblp.org/pid/358/1480.html), Chen-Chung Liu, [Chia-Hui Chang](https://dblp.org/pid/84/3307.html): The Design and Analysis of a Storytelling Chatbot with Natural Language Processing Techniques for Enhancing EFL Reading.[ICALT 2023](https://dblp.org/db/conf/icalt/icalt2023.html#FengLC23): 250-251」（323 字）
- 「1. Yu-Kai Lee and Chia-Hui Chang: [Story Co-telling Dialogue Generation based on Multi-Agent Reinforcement Learning and Story Highlights](https://alta2023.alta.asn.au/files/6.pdf), The 21st Annual Workshop of the Australasian Language Technology Association ([ALTA 2023](https://alta2023.alta.asn.au/)), Melbourne, Australia, Nov. 29-Dec. 1, 2023.」（347 字）
- 「1. Yu-Yen Ting and Chia-Hui Chang: Improving Chinese Fact Checking via Prompt Based Learning and Low Rank Adaptation, The 2023 IEEE/ACM International Conference on Advances in Social Networks Analysis and Mining ([ASONAM 2023](https://asonam.cpsc.ucalgary.ca/2023/)).Kusadasi, Turkey, 6-9 November 2023」（302 字）
- 「1. Thamolwan Poopradubsil andChia-Hui Chang:[Question-answer pairing from IM conversations via message merging and reply-to prediction](https://aclanthology.org/2022.paclic-1.2/), [PACLIC 2022](https://www.paclic2022.net/papers.html).」（234 字）
- 「1. Chia-Hui Chang, Zhi-Xian Liu, Yu-Ching Liao, Yu-Hao Wu , Thamolwan Poopradubsil: [Chat-log Disentanglement via Same-Thread Classification and Direct-Reply Prediction](https://aclanthology.org/2022.paclic-1.11/), accepted by [PACLIC 2022](https://www.paclic2022.net/papers.html).」（281 字）
- 「1. Chia-Hui Chang, Yu-Ching Liao and Ting Yeh:[Event Source Page Discovery via Policy-based RL with Multi-Task Neural Sequence Model](https://drive.google.com/file/d/1zalwnKtxsF7bpJceB7Tsw-uxH0c1noNh/view?usp=sharing), accepted by[WISE 2022](https://wise2022.sigappfr.org/).」（274 字）
- 「1. Chia-Hui Chang, Cheng-Ju Wu and Tzu-Ping Lin: [Automatic Web Data API Creation via Cross-Lingual Neural Pagination Recognition](https://drive.google.com/file/d/1h2NxZqgz7xdizQ4BPnSCtQxRovnqiewv/view?usp=sharing), ICWE 2022.」（226 字）
- 「1. Tai-Jung Kan and Chia-Hui Chang: [Home Appliance Review Analysis Via Adversarial Reptile](https://dl.acm.org/doi/abs/10.1145/3486622.3493958). Web Intelligence 2021.」（168 字）
- 「1. Yu-Hao Wu and Chia-Hui Chang: [Multi-Task Neural Sequence Labeling for Zero-Shot Cross-Language Boilerplate Removal](https://dl.acm.org/doi/10.1145/3486622.3493938). Web Intelligence 2021.」（191 字）
- 「1. [Yu-Chieh Chao](https://dblp.uni-trier.de/pid/277/4976.html), Chia-Hui Chang:[Automatic Spelling Correction for ASR Corpus in Traditional Chinese Language using Seq2Seq Models](https://ieeexplore.ieee.org/document/9359053).[ICS 2020](https://dblp.uni-trier.de/db/conf/intcompsymp/ics2020.html#ChaoC20a): 553-558」（314 字）
- 「1. Chia-Hui Chang, [Yuan-Hao Lin](https://dblp.uni-trier.de/pid/193/3553.html), [Hsiu-Min Chuang](https://dblp.uni-trier.de/pid/150/5799.html): EventGo! Exploring Event Dynamics from Social-Media Posts. [ICS 2020](https://dblp.uni-trier.de/db/conf/intcompsymp/ics2020.html#ChangLC20): 548-552」（292 字）
- 「1. [Yu-Chieh Chao](https://dblp.uni-trier.de/pid/277/4976.html), Chia-Hui Chang: Automatic Punctuation Restoration for corpus in Traditional Chinese Language using Deep Learning. [TAAI 2020](https://dblp.uni-trier.de/db/conf/taai/taai2020.html#ChaoC20): 91-96」（259 字）
- 「1. [Yuan-Hao Lin](https://dblp.uni-trier.de/pid/193/3553.html), Chia-Hui Chang, [Hsiu-Min Chuang](https://dblp.uni-trier.de/pid/150/5799.html): Mining Events through Activity Title Extraction and Venue Coupling. [TAAI 2020](https://dblp.uni-trier.de/db/conf/taai/taai2020.html#LinCC20): 136-141」（294 字）
- 「1. [Gui-Ru Li](https://dblp.uni-trier.de/pers/hd/l/Li:Gui=Ru), Chia-Hui Chang: Semantic role labeling for opinion target extraction from chinese social network. [ASONAM 2019](https://dblp.uni-trier.de/db/conf/asunam/asonam2019.html#LiC19): 1042-1047」（249 字）
- 「1. [Hsiang-En Cherng](https://dblp.uni-trier.de/pers/hd/c/Cherng:Hsiang=En), Chia-Hui Chang: Short Text Conversation Based on Deep Neural Network and Analysis on Evaluation Measures. [CoRR abs/1907.03070](https://dblp.uni-trier.de/db/journals/corr/corr1907.html#abs-1907-03070) (2019)」（284 字）
- 「1. Yu-Ching Chen, Chia-Ching Yang, Yan-Jian Liau, Chia-Hui Chang, Pin-Liang Chen, Ping-Che Yang, Tsun Ku: [User Behavior Analysis and Commodity Recommendation for Point-Earning Apps](https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&matchBoolean=true&queryText=%28%22Document%20Title%22:User%20Behavior%20Analysis%20and%20Commodity%20Recommendation%20for%20Point%20Earning%20Apps%29%20AND%20%28%22Publication%20Title%22:TAAI%29), TAAI 2016.」（456 字）
- 「1. Oviliani Yenty Yuliana, Chia-Hui Chang, AFIS: Aligning Detail-Pages for Full Schema Induction, TAAI 2016, pp. 220-227, DOI: [10.1109/TAAI.2016.7880164](https://doi.org/10.1109/TAAI.2016.7880164)」（197 字）
- 「1. Hsiu-Min Chuang, Chia-Hui Chang, Chung-Ting Cheng: [Improving the effectiveness of POI search by associated information summarization](http://ieeexplore.ieee.org/document/7876000/). [IALP2016](http://dblp.uni-trier.de/db/conf/ialp/ialp2016.html#ChuangCC16): 336-339 \[[pdf](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6YmM1NDExNjRkYTk3ODg5)\]」（398 字）
- 「1. C.-H. Chang, T.-S. Chen, M.-C. Chen, J.-L. Ding: [Efficient Page-Level Data Extraction ViaSchema Induction and Verification](https://link.springer.com/chapter/10.1007/978-3-319-31750-2_38). PAKDD 2016 \[[pdf](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MTAzZDY4MzI5OWJlZWRmZg)\]」（335 字）
- 「1. H.-M. Chuang, C.-H. Chang: [Verification of POI and Location Pairs via Weakly Labeled Web Data](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6NjgyOWVmZGZkY2NlMzRhYQ). WWW Workshop on Location Web 2015:743-748.」（264 字）
- 「1. [C.-L. Chou](http://www.informatik.uni-trier.de/%7Eley/pers/hd/c/Chou:Chien=Lung.html), C.-H. Chang: [Named Entity Extraction via Automatic Labeling and Tri-training: Comparison of Selection Methods](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MmRmYTM4NWY0YzFiOTE0Zg). [AIRS 2014](http://www.informatik.uni-trier.de/%7Eley/db/conf/airs/airs2014.html#ChouC14): 244-255」（424 字）
- 「1. [C.-L. Chou](http://www.informatik.uni-trier.de/~ley/pers/hd/c/Chou:Chien=Lung.html), C.-H. Chang, Shin-Yi Wu: Semi-supervised Sequence Labeling for Named Entity Extraction based on Tri-Training: Case Study on Chinese Person Name Extraction. Proceedings of Third Workshop on Semantic Web and Information Extraction, pages 33–40, Dublin, Ireland, August 24, 2014.」（365 字）
- 「1. [H.-M. Chuang](http://dblp.uni-trier.de/pers/hd/c/Chuang:Hsiu=Min), C.-H. Chang, and T.-Y. Kao: [Effective Web Crawling for Chinese Addresses and Associated Information](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MTY4YmQyNTNjNWVmZDlhMA), The 15th International Conference on Electronic Commerce and Web Technologies (ECWeb 2014), Munich, Germany, Sep. 1-5, 2014. (Acceptance rate: 24%).」（444 字）
- 「1. M.-L. Wu, C.-H. Chang: [Parallel co-clustering with augmented matrices algorithm with Map-Reduce](http://link.springer.com/chapter/10.1007%2F978-3-319-10160-6_17), The 16th International Conference on Data Warehousing and Knowledge Discovery (DaWaK 2014), Munich, Germany, Sep. 1-5, 2014. 10.1007/978-3-319-10160-6_17 \[[pdf](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MjE2NzQwMTM1Y2Q3ZjY4NQ)\]」（452 字）
- 「1. C.-L. Chen and C.-H. Chang: [Evaluation of Session-Based Recommendation Systems for Social Networks](http://ieeexplore.ieee.org/document/6753997/), [Data Mining Workshops (ICDMW)](http://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=6732242), 2013, pp. 758-765. [10.1109/ICDMW.2013.86](http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6753997) 1. N.-H. Chen and C.-H. Chang: [Evaluation of Social, Geography, Location Effects for Point-of-Interest Recommendation](http://ieeexplore.ieee.org/document/6753998/), [Data Mining Workshops (ICDMW)](http://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=6732242), 2013, pp. 766-772. [10.1109/ICDMW.2013.77](http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6753998)」（737 字）
- 「1. C.-L. Chen and C.-H. Chang: [Session-Based Recommendation System for Social Network – Case Study on Tencent Weibo](http://ieeexplore.ieee.org/document/6783868/), The 18th Conference on Artificial Intelligence (TAAI 2013), Dec. 6-8, 2013. \[[pdf](http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6783868)\]」（315 字）
- 「1. C.-H. Chang, [Y.-L. Lin](http://www.informatik.uni-trier.de/~ley/pers/hd/l/Lin:Yen=Ling.html), [K.-C. Lin](http://www.informatik.uni-trier.de/~ley/pers/hd/l/Lin:Kuan=Chen.html), [M. Kayed](http://www.informatik.uni-trier.de/~ley/pers/hd/k/Kayed:Mohammed.html): [Page-Level Wrapper Verification for Unsupervised Web Data Extraction](http://link.springer.com/chapter/10.1007%2F978-3-642-41230-1_38). [WISE (1) 2013](http://www.informatik.uni-trier.de/~ley/db/conf/wise/wise2013-1.html#ChangLLK13): 454-467. 10.1007/978-3-642-41230-1_38 [pdf]」（542 字）
- 「1. M.-F. Tsai, C.-H. Hsu, C.-H. Chang, H.-M. Liao, S.-P. Li, D. H. Wu: [Primary Chinese Semantic-Phonetic Compounds Pronunciation Rules Mining and Visualization](http://aclweb.org/anthology/O/O13/O13-1020.pdf), the 25th conference on Computational Linguistics and Speech Processing ([ROCLING 2013](https://sites.google.com/site/rocling2013/)), Oct. 4-5, 2013.」（359 字）
- 「1. C.-H. Chang, J.-M. Chen: [Automatic Extraction of Blog Post from Diverse Blog Pages](http://ieeexplore.ieee.org/document/6511875/). [Web Intelligence 2012](http://www.informatik.uni-trier.de/~ley/db/conf/webi/webi2012.html#ChangC12): 129-136. 10.1109/WI-IAT.2012.25 \[[pdf](http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6511875)\]」（343 字）
- 「1. C.-H. Chang, K.-H. Huo: [Increasing Broadband Subscriptions for Telecom Carriers through Mobile Advertising](http://link.springer.com/chapter/10.1007%2F978-3-642-25631-8_12). [AIRS 2011](http://www.informatik.uni-trier.de/%7Eley/db/conf/airs/airs2011.html#ChangH11): 127-136. [10.1007/978-3-642-25631-8_12](http://dx.doi.org/10.1007/978-3-642-25631-8_12) \[[pdf](https://link.springer.com/content/pdf/10.1007%2F978-3-642-25631-8.pdf)\]」（438 字）
- 「1. M.-L. Wu, C.-H. Chang, R.-Z. Liu: [Co-clustering with Augmented Data Matrix](http://dx.doi.org/10.1007/978-3-642-23544-3_22). [DaWaK 2011](http://www.informatik.uni-trier.de/%7Eley/db/conf/dawak/dawak2011.html#WuCL11): 289-300. 10.1007/978-3-642-23544-3_22 \[[pdf](https://link.springer.com/content/pdf/10.1007%2F978-3-642-23544-3.pdf)\]」（340 字）
- 「1. C.-H. Chang, Kuan-Hua Huo: Mobile Advertising: Triple-win for Consumers, Advertisers and Telecom Carriers, [SIGIR 2011 Workshop: Internet Advertising (IA2011)](http://www.iis.sinica.edu.tw/page/jise/2012/201201.html)」（219 字）
- 「1. T.-K. Fan and C.-H. Chang: Learning to Predict Ads Click Based on Boosted Collaborative Filtering. [The 2nd IEEE International Conference on Social Computing (SocialCom2010)](http://www.iisocialcom.org/conference/socialcom2010/), Aug. 20-22, 2010, Minneapolis, Minnesota, USA.」（279 字）
- 「1. C.-H. Chang and S.-Y. Lee. MapMarker: Extraction of Postal Addresses And Associated Information for General Web Pages, [IEEE/WIC/ACM International Joint Conferences on Web Intelligence and Intelligent Agent Technologies (WI-IAT 2010)](http://www.yorku.ca/wiiat10/), Toronto, Canada. Sep. 1-3, 2010.」（301 字）
- 「1. T.-K. Fan and C.-H. Chang: [Blogger-Centric Contextual Advertising](http://www.csie.ncu.edu.tw/%7Echia/pub/sp1323-fan.pdf). Proceedings of the 18th ACM Conference on Information and Knowledge Management, CIKM 2009 (Short paper), Hong Kong. Nov. 2-6, 2009. pp. 1803-1806.」（273 字）
- 「1. C.-H. Chang and J.-H. Lin: [Decision Support and Profit Prediction for Online Auction Sellers](http://www.csie.ncu.edu.tw/%7Echia/pub/p1-chang.pdf). The First ACM SIGKDD Workshop on Knowledge Discovery from Uncertain Data (U'09)」（231 字）
- 「1. T.-K. Fan and C.-H. Chang: [Exploring Evolutionary Technical Trends From Research Papers](http://www.csie.ncu.edu.tw/%7Echia/pub/stanley.pdf). [The Eighth IAPR Workshop on Document Analysis Systems](http://www.u-pat.org/das08/), DAS2008 (poster session). Nara, Japan. Sep 16-19, 2008.」（287 字）
- 「1. C.-H. Chang, S.-F. Yang, C.-M. Liou, M. Kayed: [Gadget Creation for Personal Information Integration on Web Portals](http://www.csie.ncu.edu.tw/%7Echia/pub/IRI08_41.pdf), [IEEE International Conference on Information Reuse and Integration](http://iri2008.cpsc.ucalgary.ca/program-papers-per-session.pdf) (short paper), Las Vegas, USA, 2008.」（343 字）
- 「1. M. Kayed, C.-H. Chang, K. Shaalan, and M. Ramzy Girgis: [FiVaTech: Page-Level Web Data Extraction from Template Pages](http://www.csie.ncu.edu.tw/%7Echia/pub/Chang_FiVaTech.pdf), ICDM 2007, [Workshop on Web2.0 Environment](https://www.kde.cs.uni-kassel.de/ws/Web2DM), Omaha, NE, USA. Oct. 28-31, 2007.」（304 字）
- 「1. C.-H. Chang and K.-C. Tsai: [Aspect Summarization from Blogsphere for Social Study](http://www.csie.ncu.edu.tw/%7Echia/pub/Chang-Aspectsum.pdf), ICDM 2007, [Workshop on Web2.0 Environment](https://www.kde.cs.uni-kassel.de/ws/Web2DM), Omaha, NE, Oct. 28-31, 2007.」（265 字）
- 「1. K.-Y. Huang, C.-H. Chang, Jiun-Hung Tung, Cheng-Tao Ho: [COBRA: Closed Sequential Pattern Mining Using Bi-phase Reduction Approanch](http://www.csie.ncu.edu.tw/%7Echia/pub/cobralncs.pdf), Accepted by [DaWak 2006](http://www.dexa.org/drupal/?q=papers/accepted/2), Krakow, Poland.」（281 字）
- 「1. Y.-C. Wu, C.-H. Chang, Y.-S. Lee: [A General and Multi-lingual Phrase Chunking Model Based on Masking Method](http://www.csie.ncu.edu.tw/%7Echia/pub/cicling2006.pdf). Proceedings of the 7th International Conference on Computational Linguistics and Intelligent Text Processing ([CICLING 2006](http://www.gelbukh.com/cicling/2006/)), Mexico City, Mexico, February 19-25, 2006. LNCS 3878, pp. 144--155.」（402 字）
- 「1. K.-Y. Huang and C.-H. Chang: [Efficient Mining Strategy for Frequent Serial Episodes in Temporal Database](http://www.csie.ncu.edu.tw/%7Echia/pub/emmaApWeb06.pdf), [The 8th Asia Pacific Web Conference](http://www.itee.uq.edu.au/%7Eapweb06/) (short paper), Harbin, China, Jan. 16-18, 2006. LNCS 3841, pp. 824--829.」（316 字）
- 「1. K.-Y. Huang, C.-H. Chang, and Kuo-Zui Lin: [ClosedPROWL: Efficient Mining of Closed Frequent Continuities by Projected Window List Technology](http://www.csie.ncu.edu.tw/%7Echia/pub/sdm05.pdf), [SIAM International Conference on Data Mining](http://www.siam.org/meetings/sdm05/index.htm) (short paper), CA, USA, Apr. 21-23, 2005.」（331 字）
- 「1. K.-Y. Huang, C.-H. Chang, and Kuo-Zui Lin: [COCOA: An Efficient Algorithm for Mining Inter-transaction Associations for Temporal Database](http://www.csie.ncu.edu.tw/%7Echia/pub/PKDD3pages.pdf), In the [Proceedings](http://www.springer.de/comp/llncs/index.html) of the 8th European Conference on Principles and Practice of Knowledge Discovery in Databases ([PKDD04](http://ecmlpkdd.isti.cnr.it/) (poster), Pisa, Italy, 2004. LNAI 3202 (SCI expanded), pp. 509--511.」（467 字）
- 「1. C.-H. Chang and Z.-K. Ding: [Categorical Data Visualization and Clustering using Subjective Factors](http://www.csie.ncu.edu.tw/%7Echia/pub/dawak135.pdf), In the [Proceedings](http://www.springerlink.com/index/FVD0GN18WUV3VPWW) of the 6th International Conference on Data Warehousing and Knowledge Discovery ([DaWaK04](http://www.dexa.org/dexa2004/index.php?include=main.php)), Zaragoza, Spain, 2004. LNCS 3181 (SCI expanded), pp. 229-238.」（442 字）
- 「1. K.-Y. Huang and C.-H. Chang: [Mining Periodic Patterns in Sequence Data](http://www.csie.ncu.edu.tw/%7Echia/pub/dawak80.pdf), In the [Proceedings](http://www.springerlink.com/index/40BA5M7CL3QXGVA1) of the 6th International Conference on Data Warehousing and Knowledge Discovery ([DaWaK04](http://www.dexa.org/dexa2004/index.php?include=main.php)), Zaragoza, Spain, 2004. LNCS 3181 (SCI expanded), pp. 401-410.」（413 字）
- 「1. K.-Y. Huang, C.-H. Chang, and Kuo-Zui Lin: [PROWL: An Efficient Frequent Continuity Mining Algorithm on Event Sequences](http://www.csie.ncu.edu.tw/%7Echia/pub/dawak81.pdf), In the [Proceedings](http://www.springerlink.com/index/7827507EMUW7KEL4) of the 6th International Conference on Data Warehousing and Knowledge Discovery ([DaWaK04](http://www.dexa.org/dexa2004/index.php?include=main.php)), Zaragoza, Spain, 2004. LNCS 3181 (SCI expanded), pp. 351-360.」（461 字）
- 「1. C.-H. Chang and S.-C. Kuo: [OLERA: On-Line Extraction Rule Analysis for Semi-structured Documents](http://www.csie.ncu.edu.tw/%7Echia/pub/411-043.pdf), The IASTED International Conference on ARTIFICIAL INTELLIGENCE AND APPLICATIONS ([AIA 2004](http://www.iasted.org/conferences/2004/Innsbruck/aia.htm)). Feb. 16-18, 2004, Austria.」（333 字）
- 「1. K.-Y. Huang and C.-H. Chang: [Asynchronous Periodic Pattern Mining from Multi-event Time Series Databases](http://www.csie.ncu.edu.tw/%7Echia/pub/419-094.pdf), The IASTED International Conference on DATABASES AND APPLICATIONS ([DBA 2004](http://www.iasted.org/conferences/2004/Innsbruck/dba.htm)), Feb. 17-19, 2004, Austria.」（327 字）
- 「1. C.-N. Hsu, C.-H. Chang, H. Siek, J.-J. Lu, J.-J. Chiou: [Reconfigurable Web Wrapper Agents for Web Information Integration](http://www.csie.ncu.edu.tw/%7Echia/pub/wndl2003.pdf), IJCAI 2003 Workshop on Information Integration on the Web, [IIWeb-03](http://www.isi.edu/info-agents/workshops/ijcai03/proceedings.htm), Aug. 2003, pp. 15-20.」（339 字）
- 「1. C.-H. Chang and Shi-Hsan Yang: [Enhancing SWF for Incremental Association Mining by Itemset Maintenance](http://www.csie.ncu.edu.tw/%7Echia/pub/pakdd03.pdf), In the [Proceedings](http://www.springeronline.com/sgw/cda/frontpage/0,10735,5-147-22-2323333-0,00.html?changeHeader=true) of the seventh Pacific-Asia Conference on Knowledge Discovery and Data Mining ([PAKDD03](http://aitrc.kaist.ac.kr/%7Epakdd03/index.htm)), Korea, 2003. LNAI 2637 (SCI expanded), pp. 301-312.」（473 字）
- 「1. C.-H. Chang: [Sequential Pattern Mining for Web Extraction Rule Generalization](http://www.csie.ncu.edu.tw/%7Echia/pub/215SF.pdf), [The 6th World multiconference on Systemics, Cybernetics and Informatics](http://www.iiis.org/sci2002/), July 14-18, 2002, Orlando, Florida」（273 字）
- 「1. C.-H. Chang, S.-C. Kuo, K.-Y. Hwang, T.-H. Ho and C.-L. Lin: [Automatic Information Extraction for Multiple Singular Web Pages](http://www.csie.ncu.edu.tw/%7Echia/pub/0265.pdf), In the [Proceedings](http://www.springer.de/comp/llncs/index.html) of the sixth Pacific-Asia Conference on Knowledge Discovery and Data Mining ([PAKDD02](http://arbor.ee.ntu.edu.tw/pakdd02/)), Taiwan, 2002. LNAI 2336 (SCI expanded), pp. 297-303.」（426 字）
- 「1. C.-H. Chang. and S.-C. Lui: [IEPAD: Information Extraction based on Pattern Discovery](http://www.csie.ncu.edu.tw/%7Echia/pub/www10.pdf), In the Proceedings of the tenth International Conference on World Wide Web ([WWW10](http://www10.org/)), pp. 681-688, May 2-6, 2001, Hong Kong.」（284 字）
- 「1. C.-H. Chang., S.-C. Lui, and Y.-C. Wu: [Applying Pattern Mining to Web Information Extraction](http://www.csie.ncu.edu.tw/%7Echia/pub/pakdd.pdf), In the [Proceedings](http://www.springer.de/comp/llncs/index.html) of the fifth Pacific-Asia Conference on Knowledge Discovery and Data Mining ([PAKDD01](http://www.csis.hku.hk/pakdd01/)), Hong Kong, 2001. LNAI 2035 (SCI expanded), pp. 4-15.」（390 字）
- 「1. C.-H. Chang, S.-C. Lui, and Y.-C. Wu: [Semi-structured Information Extraction Applying Automatic Pattern Discovery](http://www.csie.ncu.edu.tw/%7Echia/pub/B121.pdf) , In Proc. of the fourteenth International Computer Symposium (ICS2000), Chia-Yi, Taiwan, Dec. 6-8. 2000.」（273 字）
- 「1. C.-H. Chang and C.-N. Hsu: Automatic Extraction of Information Blocks Using PAT Trees , In Proc. of the National Computer Symposium, Dec. 20-21, 1999, Taipei, Taiwan」（168 字）
- 「1. C.-H. Chang, C.-C. Hsu and C.-L. Hou: [Exploiting Hyperlinks for Automatic Information Discovery on the WWW ](http://www.csie.ncu.edu.tw/%7Echia/pub/ictai.ps.gz), In Proc. of the tenth IEEE International Conference on Tools with Artificial Intelligence, (ICTAI98), Nov. 1998, Chien Tan Youth Activity Center, Taipei, Taiwan.」（327 字）
- 「1. C.-H. Chang and C.-C. Hsu: [Hypertext Information Retrieval for Short Queries](http://www.csie.ncu.edu.tw/%7Echia/pub/kdex98.ps.gz) , In Proc. of the IEEE Knowledge and Data Engineering Exchange Workshop, Nov. 1998, Chien Tan Youth Activity Center, Taipei, Taiwan.」（267 字）
- 「1. C.-H. Chang and C.-C. Hsu: [Enabling Web Information Retrieval through Query Expansion via Contrast Analysis](http://www.csie.ncu.edu.tw/%7Echia/pub/www7/353.html) , In Proc. of the seventh International Conference on World Wide Web ([WWW7](http://www7.scu.edu.au/)), Apr. 14-18, 1998, Brisbane, Queensland, Australia」（320 字）
- 「1. C.-H. Chang and C.-C. Hsu: [Constructing Personal Information Search Agents](http://www.csie.ncu.edu.tw/%7Echia/pub/pakdd.ps.gz) , In Proc. of the second Pacific Asia Conference on Knowledge Discovery and Data Mining (PAKDD98), Melbourne, Australia, 1998. LNAI 1394 (SCI expanded), pp. 374-375.」（297 字）
- 「1. C.-H. Chang and C.-C. Hsu: [A Multi-Engine Search Tool based on Clustering](http://www.csie.ncu.edu.tw/%7Echia/pub/www6/PAPER53.html) , In Proc. of the sixth international conference on World Wide Web, (WWW6), Apr.7-11, 1997, Santa Clara, CA」（244 字）
- 「### Book Chapters」（17 字）
- 「### Patents」（11 字）
- 「### Domestic Conference Papers (In Chinese)」（43 字）
- 「1. 黃懷萱、張嘉惠、陳冠蓉: [DREAM: 結合領域知識檢索與多代理推理的結構化論文評估方法](https://openreview.net/forum?id=vxtNegzSMo&referrer=%5BAuthor%20Console%5D%28%2Fgroup%3Fid%3DTAAI.org%2F2025%2FConference%2FAuthors%23your-submissions%29), [TAAI 2025](https://taai2025.org/), Dec. 13-14, NTNU, Taipei, Taiwan」（274 字）
- 「1. 葉季儒、張嘉惠、施冠宏: [PagePilot : 基於多代理架構之多模態自動化網頁助理](https://openreview.net/forum?id=pvqmyV41Y8&referrer=%5BAuthor%20Console%5D%28%2Fgroup%3Fid%3DTAAI.org%2F2025%2FConference%2FAuthors%23your-submissions%29), [TAAI 2025](https://taai2025.org/), Dec. 13-14, NTNU, Taipei, Taiwan」（273 字）
- 「1. 丁仕杰、張嘉惠、簡資烜: 基於語音指令的中文ASR錯誤校正系統設計與實現, [ROCLING 2025](http://rocling2025.github.io), Nov. 20th-22th, NTU, Taipei City, Taiwan」（127 字）
- 「1. 龔若齊、張嘉惠: 基於微調開源大型語言模型的交通事故資訊蒐集代理人系統研究, [ROCLING 2025](http://rocling2025.github.io), Nov. 20th-22th, NTU, Taipei City, Taiwan」（128 字）
- 「1. 李倬安、葉展維、張嘉惠: 基於深度學習的跨多輸入法編輯器整合系統 (#81), [TAAI 2024](https://taai2024.org/program-of-domestic-track/) (Appier Award).」（119 字）
- 「1. 黃懷萱、張嘉惠、龔若齊、簡國峻: 大型語言模型對判決理解的探討：以交通事故資訊擷取為例 (#33), [ROCLING 2024](https://rocling2024.github.io/) (Best Paper Award)」（119 字）
- 「1. 龔若齊、黃懷萱、簡國峻、張嘉惠: 基于LLM的交通事故諮詢助理 (#32), [ROCLING 2024](https://rocling2024.github.io/)」（88 字）
- 「1. 黃冠傑、黃淯銘、張嘉惠、黃覺修、鍾曉芳、鄭芳祥: 通過實體和事件關係標記改進問題答案對生成的 控制 , NCS2023.」（63 字）
- 「1. 許志仲、朱翊瑄、劉晨鐘、張嘉惠、温采婷: 基於生成式語言模型之科學探究教學代理之提示詞框架與系統設計, NCS2023.」（63 字）
- 「1. 李聿鎧、張嘉惠: 應用強化學習與知識圖譜於故事共述生成之研究, ROCLING 2023」（47 字）
- 「1. 葉丞鴻、張嘉惠: 中文訊息傳遞服務對話系統之建構, ROCLING 2023.」（42 字）
- 「1. 葉丞鴻, 李聿鎧, 張嘉惠: [多領域任務導向用戶語音助理對話收集系統](https://drive.google.com/file/d/1OYBOAUCFr20Yzs7jnbLD6VjfH8CQnakT/view?usp=sharing), TAAI 2022.」（135 字）
- 「1. 洪裕翔, 張嘉惠: [通過生成式文本摘要改進口語法律案件預測效能之研究](https://drive.google.com/file/d/18G28TCeFlcemN0e72EDKRcWQ48DRSNoA/view?usp=sharing), TAAI 2022.」（135 字）
- 「1. 李逸軒, 張嘉惠: [基於強化式學習結合自編碼器壓縮特徵之資產配置方法](https://drive.google.com/file/d/1QRxSMqHiOpDreZtbPqSS4kpTaJJ5mbrI/view?usp=sharing), TAAI 2022.」（135 字）
- 「1. 黃紫嫺, 張嘉惠:[基於常識知識的移情對話回覆生成](https://aclanthology.org/2022.rocling-1.37/).[ROCLING 2022](https://dblp.org/db/conf/rocling/rocling2022.html#HuangC22): 299-306」（158 字）
- 「1. 高愷言, 張嘉惠:[應用自動資訊擷取於故事書問答生成之研究](https://aclanthology.org/2022.rocling-1.36/).[ROCLING 2022](https://dblp.org/db/conf/rocling/rocling2022.html#KaoC22): 289-298」（160 字）
- 「1. 廖于晴, 張嘉惠. [應用強化式學習探勘活動來源網頁](http://search.taai.org.tw/paper/2021/0/%E6%87%89%E7%94%A8%E5%BC%B7%E5%8C%96%E5%BC%8F%E5%AD%B8%E7%BF%92%E6%8E%A2%E5%8B%98%E6%B4%BB%E5%8B%95%E4%BE%86%E6%BA%90%E7%B6%B2%E9%A0%81.pdf), TAAI 2021.」（222 字）
- 「1. 吳昱豪, 張嘉惠. [應用多任務序列標記模型於零樣本跨語言網頁模板移除之研究](http://search.taai.org.tw/paper/2021/0/%E6%87%89%E7%94%A8%E5%A4%9A%E4%BB%BB%E5%8B%99%E5%BA%8F%E5%88%97%E6%A8%99%E8%A8%98%E6%A8%A1%E5%9E%8B%E6%96%BC%E9%9B%B6%E6%A8%A3%E6%9C%AC%E8%B7%A8%E8%AA%9E%E8%A8%80%E7%B6%B2%E9%A0%81%E6%A8%A1%E6%9D%BF%E7%A7%BB%E9%99%A4%E4%B9%8B%E7%A0%94%E7%A9%B6.pdf), TAAI 2021.」（342 字）
- 「1. 吳承儒, 張嘉惠. [基於自動分頁預測之大規模資料應用程式介面建置 - 以活動擷取為例](http://search.taai.org.tw/paper/2021/0/%E5%9F%BA%E6%96%BC%E8%87%AA%E5%8B%95%E5%88%86%E9%A0%81%E9%A0%90%E6%B8%AC%E4%B9%8B%E5%A4%A7%E8%A6%8F%E6%A8%A1%E8%B3%87%E6%96%99%E6%87%89%E7%94%A8%E7%A8%8B%E5%BC%8F%E4%BB%8B%E9%9D%A2%E5%BB%BA%E7%BD%AE%20-%20%E4%BB%A5%E6%B4%BB%E5%8B%95%E6%93%B7%E5%8F%96%E7%82%BA%E4%BE%8B.pdf), TAAI 2021.」（372 字）
- 「1. [曾筱雯](https://aclanthology.org/people/h/hsiao-wen-tseng/), [張嘉惠](https://aclanthology.org/people/c/chia-hui-chang/), [莊秀敏](https://aclanthology.org/people/h/hsiu-min-chuang/), [基於參數生成網路的遷移學習進行情感分析和歌手命名識別](https://aclanthology.org/2021.rocling-1.26/), ROCLING 2021.」（267 字）
- 「1. [甘岱融](https://aclanthology.org/people/t/tai-jung-kan/), [張嘉惠](https://aclanthology.org/people/c/chia-hui-chang/), [莊秀敏](https://aclanthology.org/people/h/hsiu-min-chuang/), [應用對抗式 Reptile 於家電產品網路評論之研究](https://aclanthology.org/2021.rocling-1.24/), ROCLING 2021.」（264 字）
- 「1. 林政憲, 張嘉惠. [情緒及技術指標於股票漲跌幅排名預測及動態投資組合最佳化之研究](http://search.taai.org.tw/paper/2020/0/%E6%83%85%E7%B7%92%E5%8F%8A%E6%8A%80%E8%A1%93%E6%8C%87%E6%A8%99%E6%96%BC%E8%82%A1%E7%A5%A8%E6%BC%B2%E8%B7%8C%E5%B9%85%E6%8E%92%E5%90%8D%E9%A0%90%E6%B8%AC%E5%8F%8A%E5%8B%95%E6%85%8B%E6%8A%95%E8%B3%87%E7%B5%84%E5%90%88%E6%9C%80%E4%BD%B3%E5%8C%96%E4%B9%8B%E7%A0%94%E7%A9%B6.pdf), [TAAI 2020](https://taai2020.github.io/dprogram.html).」（416 字）
- 「1. 陳震瑜, 張嘉惠, 邱裕民. [應用網路聲量及情緒分析於熱門歌曲點播量預測](http://search.taai.org.tw/paper/2020/0/%E6%87%89%E7%94%A8%E7%B6%B2%E8%B7%AF%E8%81%B2%E9%87%8F%E5%8F%8A%E6%83%85%E7%B7%92%E5%88%86%E6%9E%90%E6%96%BC%E7%86%B1%E9%96%80%E6%AD%8C%E6%9B%B2%E9%BB%9E%E6%92%AD%E9%87%8F%E9%A0%90%E6%B8%AC.pdf), [TAAI 2020](https://taai2020.github.io/dprogram.html).」（331 字）
- 「1. 邱威誠, 張嘉惠. [應用AutoNER於社群網路中文歌手名稱辨識之研究](http://search.taai.org.tw/paper/2020/0/%E6%87%89%E7%94%A8AutoNER%E6%96%BC%E7%A4%BE%E7%BE%A4%E7%B6%B2%E8%B7%AF%E4%B8%AD%E6%96%87%E6%AD%8C%E6%89%8B%E5%90%8D%E7%A8%B1%E8%BE%A8%E8%AD%98%E4%B9%8B%E7%A0%94%E7%A9%B6.pdf), [TAAI 2020 (poster)](https://taai2020.github.io/pdprogram.html).」（320 字）
- 「1. 王育任, 張嘉惠: [利用Attentive來改善端對端中文語篇剖析遞迴類神經網路系統](https://aclanthology.org/2019.rocling-1.36/), ROCLING 2019.」（107 字）
- 「1. 劉至咸, 張嘉惠:[基於訊息配對相似度估計的聊天記錄解構](https://aclanthology.org/2019.rocling-1.39/), ROCLING 2019.」（92 字）
- 「1. 陳震瑜, 邱威誠, 張嘉惠, 邱裕民, 莊秀敏: 運用多領域資料結合深度學習技術於音樂論壇評論之情感分析, TAAI 2019.」（67 字）
- 「1. 簡國峻, 張嘉惠, [利用記憶增強條件隨機場域之深度學習及自動化詞彙特徵於中文命名實體辨識之研究](http://search.taai.org.tw/paper/2018/0/%E5%88%A9%E7%94%A8%E8%A8%98%E6%86%B6%E5%A2%9E%E5%BC%B7%E6%A2%9D%E4%BB%B6%E9%9A%A8%E6%A9%9F%E5%A0%B4%E5%9F%9F%E4%B9%8B%E6%B7%B1%E5%BA%A6%E5%AD%B8%E7%BF%92%E5%8F%8A%E8%87%AA%E5%8B%95%E5%8C%96%E8%A9%9E%E5%BD%99%E7%89%B9%E5%BE%B5%E6%96%BC%E4%B8%AD%E6%96%87%E5%91%BD%E5%90%8D%E5%AF%A6%E9%AB%94%E8%BE%A8%E8%AD%98%E4%B9%8B%E7%A0%94%E7%A9%B6.pdfhttp://search.taai.org.tw/paper/2018/0/%E5%88%A9%E7%94%A8%E8%A8%98%E6%86%B6%E5%A2%9E%E5%BC%B7%E6%A2%9D%E4%BB%B6%E9%9A%A8%E6%A9%9F%E5%A0%B4%E5%9F%9F%E4%B9%8B%E6%B7%B1%E5%BA%A6%E5%AD%B8%E7%BF%92%E5%8F%8A%E8%87%AA%E5%8B%95%E5%8C%96%E8%A9%9E%E5%BD%99%E7%89%B9%E5%BE%B5%E6%96%BC%E4%B8%AD%E6%96%87%E5%91%BD%E5%90%8D%E5%AF%A6%E9%AB%94%E8%BE%A8%E8%AD%98%E4%B9%8B%E7%A0%94%E7%A9%B6.pdf), TAAI 2018.」（818 字）
- 「1. 許國信, 張嘉惠, 莊秀敏, 周建龍: “[應用興趣點辨識技術從Web中挖掘新商家資訊](http://aclweb.org/anthology/O17-1006)”, ROCLING 2017.」（101 字）
- 「1. 鐘智宇, 周建龍, 張嘉惠: “[PTT網站餐廳美食類別擷取之研究](http://www.aclweb.org/anthology/O17-1019)”, ROCLING 2017.」（95 字）
- 「1. 蔣佳峰, 張嘉惠, 劉志灝: “[PTT災害事件擷取系統](http://search.taai.org.tw/paper/2017/0/PTT%E7%81%BD%E5%AE%B3%E4%BA%8B%E4%BB%B6%E6%93%B7%E5%8F%96%E7%B3%BB%E7%B5%B1.pdf)”, TAAI 2017.」（165 字）
- 「1. 楊鎧謙, 張嘉惠, 劉胥影: “[On Large-Scale Multi-Label Classification for POI Tagging](http://search.taai.org.tw/paper/2017/0/On%20Large-Scale%20Multi-Label%20Classification%20for%20POI%20Tagging.pdf)”, TAAI 2017.」（205 字）
- 「1. 張國斌, 張嘉惠: “[透過 POI 的過期驗證以持續維護POI資料庫](http://search.taai.org.tw/paper/2017/0/%E9%80%8F%E9%81%8E%20POI%20%E7%9A%84%E9%81%8E%E6%9C%9F%E9%A9%97%E8%AD%89%E4%BB%A5%E6%8C%81%E7%BA%8C%E7%B6%AD%E8%AD%B7%20POI%20%E8%B3%87%E6%96%99%E5%BA%AB.pdf)”, TAAI 2017.」（250 字）
- 「1. 楊佳靜, 張嘉惠: “[結構化學習應用於消費型商品推薦](http://search.taai.org.tw/paper/2017/0/%E7%B5%90%E6%A7%8B%E5%8C%96%E5%AD%B8%E7%BF%92%E6%87%89%E7%94%A8%E6%96%BC%E6%B6%88%E8%B2%BB%E5%9E%8B%E5%95%86%E5%93%81%E6%8E%A8%E8%96%A6.pdf)”, TAAI 2017.」（224 字）
- 「1. 凌杰甫, 張嘉惠: [商家與圖片配對研究](http://search.taai.org.tw/paper/2016/0/%E5%95%86%E5%AE%B6%E8%88%87%E5%9C%96%E7%89%87%E9%85%8D%E5%B0%8D%E7%A0%94%E7%A9%B6.pdf). TAAI 2016.」（162 字）
- 「1. 許國信, 莊秀敏, 張嘉惠. [基於查詢結果與特徵推導之廠商及產品關聯推斷技術](http://search.taai.org.tw/paper/2016/0/%E5%9F%BA%E6%96%BC%E6%9F%A5%E8%A9%A2%E7%B5%90%E6%9E%9C%E8%88%87%E7%89%B9%E5%BE%B5%E6%8E%A8%E5%B0%8E%E4%B9%8B%E5%BB%A0%E5%95%86%E5%8F%8A%E7%94%A2%E5%93%81%E9%97%9C%E8%81%AF%E6%8E%A8%E6%96%B7%E6%8A%80%E8%A1%93.pdf). TAAI 2016.」（307 字）
- 「1. 陳昱瑾, 楊佳靜, 廖彥鈞, 張嘉惠, 陳品良, 楊秉哲, 谷圳: [使用者行為分析與商品推薦應用於集點APP](http://search.taai.org.tw/paper/2016/0/%E4%BD%BF%E7%94%A8%E8%80%85%E8%A1%8C%E7%82%BA%E5%88%86%E6%9E%90%E8%88%87%E5%95%86%E5%93%81%E6%8E%A8%E8%96%A6%E6%87%89%E7%94%A8%E6%96%BC%E9%9B%86%E9%BB%9EAPP.pdf). TAAI 2016.」（272 字）
- 「1. 林圓皓, 張嘉惠: [Facebook 活動事件擷取系統(Facebook Activity Event Extraction System)](https://aclanthology.coli.uni-saarland.de/papers/O16-1022/o16-1022), ROCLING 2016.」（158 字）
- 「1. 鄭仲庭, 莊秀敏: 張嘉惠, [整合多種搜尋結果以提高POI搜尋的準確性](http://search.taai.org.tw/paper/2015/0/%E6%95%B4%E5%90%88%E5%A4%9A%E7%A8%AE%E6%90%9C%E5%B0%8B%E7%B5%90%E6%9E%9C%E4%BB%A5%E6%8F%90%E9%AB%98POI%E6%90%9C%E5%B0%8B%E7%9A%84%E6%BA%96%E7%A2%BA%E6%80%A7.pdf), TAAI 2015.」（253 字）
- 「1. 丁中立, 張嘉惠: [完整綱要推導之改進](http://search.taai.org.tw/paper/2015/0/%E5%AE%8C%E6%95%B4%E7%B6%B1%E8%A6%81%E6%8E%A8%E5%B0%8E%E4%B9%8B%E6%94%B9%E9%80%B2.pdf), TAAI 2015.」（162 字）
- 「1. 黃雅筠, 張嘉惠, 周建龍: [基於已知名稱搜尋結果的網路實體辨識模型建立工具](https://aclanthology.coli.uni-saarland.de/papers/O15-1015/o15-1015) (A Tool for Web NER Model Generation Using Search Snippets of Known Entities, ROCLING 2015.」（203 字）
- 「1. 高霆耀, 莊秀敏, 張嘉惠: [基於Web之商家景點擷取與資料庫建置](https://aclanthology.org/O15-1018/) (Points of Interest Extraction from Unstructured Web), ROCLING 2015.」（143 字）
- 「1. 林育暘, 張嘉惠: [網頁商家名稱擷取與地址配對之研究 (Store Name Extraction and Name-Address Matching on the Web)](http://aclanthology.info/papers/store-name-extraction-and-name-address-matching-on-the-web-in-chinese). [ROCLING 2014, [In Chinese]](http://aclanthology.info/papers/store-name-extraction-and-name-address-matching-on-the-web-in-chinese)」（328 字）
- 「1. 吳宗庭, 張嘉惠: [利用核依賴估計來進行多軌自動混音 (Automatic Multi-track Mixing by Kernel Dependency Estimation)](http://aclanthology.info/papers/automatic-multi-track-mixing-by-kernel-dependency-estimation-in-chinese). ROCLING 2014」（213 字）
- 「1. 陳天盛, 陳明權, 張嘉惠: 基於頁面層級之快速網頁資料擷取與綱要驗證.[The 19th Conference on Artificial Intelligence (TAAI 2013)](http://taai2014.ntust.edu.tw/best-paper-award/), Nov. 21-23, 2014.」（166 字）
- 「1. 陳明權, 陳天盛 與 張嘉惠: 應用路徑資訊輔助樣板探勘於網頁層級之資料擷取研究, [The 18th Conference on Artificial Intelligence (TAAI 2013)](http://taai2013.nccu.edu.tw/), Dec. 6-8, 2013.」（152 字）
- 「1. 吳宗庭, 林育暘 與 張嘉惠: 探索式線上分析處理在網路附加儲存系統之應用, [The 18th Conference on Artificial Intelligence (TAAI 2013)](http://taai2013.nccu.edu.tw/), Dec. 6-8, 2013.」（149 字）
- 「1. 陳宜勤, 賴郁婷, 莊秀敏 與 張嘉惠: 加入 Google Snippets 改善網頁商家多標籤分類, [The 18th Conference on Artificial Intelligence (TAAI 2013)](http://taai2013.nccu.edu.tw/), Dec. 6-8, 2013.」（163 字）
- 「1. 張嘉惠, 吳文斌: [以聲符部件為主之漢字學習系統設計研究](https://aclanthology.coli.uni-saarland.de/papers/O12-1011/o12-1011) (The Design of Chinese Character Learning System Based on Phonetic Components), the 24th conference on Computational Linguistics and Speech Processing ([ROCLING 2012](https://sites.google.com/site/rocling12/)), Sep. 21-22, 2012.」（330 字）
- 「1. 張嘉惠, 林書彥: [聲符部件排序與形聲字發音規則探勘 ](https://aclanthology.coli.uni-saarland.de/papers/O12-1011/o12-1011)(Phonetic Component Ranking and Pronunciation Rule Mining for Chinese Picto-phonetic Compounds). Computational Linguistics and Speech Processing ([ROCLING 2011](http://sites.google.com/site/rocling2011/)), Sep. 8-9, 2011.」（321 字）
- 「1. 張嘉惠, 李淑瑩, 林書彥, 黃嘉毅, 陳志銘: [以最佳化及機率分佈判斷漢字聲符之研究](https://www.aclweb.org/anthology/O10-1014) (Prediction of Phonetic Component for Picto-phonetic Compounds), ROCLING, Sep. 1-2, 2010.」（181 字）

### 頁面: `publication_publication-by-year`

**差異**: Baseline 327 行 → Experiment 289 行（移除 212 行）

**短文本雜訊（預期移除）**:

- 「### 2026」（8 字）
- 「### 2025」（8 字）
- 「### 2024」（8 字）
- 「### 2023」（8 字）
- 「### 2022」（8 字）
- 「### 2021」（8 字）
- 「### 2020」（8 字）
- 「### 2019」（8 字）
- 「### 2018」（8 字）
- 「### 2017」（8 字）
- 「### 2016」（8 字）
- 「### 2015」（8 字）
- 「### 2014」（8 字）
- 「### 2013」（8 字）
- 「### 2012」（8 字）
- 「### 2011」（8 字）
- 「### 2010」（8 字）
- 「### 2009」（8 字）
- 「### 2008」（8 字）
- 「### 2007」（8 字）
- 「### 2006」（8 字）
- 「### 2005」（8 字）
- 「### 2004」（8 字）
- 「### 2003」（8 字）
- 「### 2002」（8 字）
- 「### 2001」（8 字）
- 「2000」（4 字）
- 「1999」（4 字）
- 「1998」（4 字）
- 「1997」（4 字）

**其他被移除行（需人工審核）**:

- 「# Publication by Year」（21 字）
- 「1. Chi-Ru Yeh, Chia-Hui Chang: PagePilot: web assistant based on natural language, International AAAI Conference on Web and Social Media, Accepted by ICWSM 2026.」（161 字）
- 「1. Sji-Jie Ding, Chia-Hui Chang: Voice-Controlled Text Correction System for Chinese ASR Errors, Accepted by ICASSP 2026 ([https://2026.ieeeicassp.org](https://2026.ieeeicassp.org/)), Barcelona, Spain」（200 字）
- 「1. Cissi LIN, Chung-yu SHIH, Hsiang-wen CHENG, Shu-Chih YANG, Chia-Hui CHANG, Feng-Nan HWANG: Superrefraction Detection with FORMOSAT-7/COSMIC-2 GNSS-RO Observations, 23rd Annual Meeting of the Asia Oceania Geosciences Society (AOGS2026), Aug. 2-7, 2026」（253 字）
- 「1. Hsiang-Wen CHENG,Shu-Chih YANG, Chia-Hui CHANG, Yingtsen LIN, Chung-yu SHIH, Kai-Hsun CHEN, Wen-Chien CHANG, Cheng-Yung HUANG, Yi-Hsiu CHEN, Feng-Nan HWANG: Deep Learning for Detecting Super-refraction in GNSS RO Data, 23rd Annual Meeting of the Asia Oceania Geosciences Society (AOGS2026), Aug. 2-7, 2026」（308 字）
- 「1. Chung-Yu Shih, Shi-Jie Ding, Cissi Ying-tsen Lin, Chia-Hui Chang, Feng-Nan Hwang: Near real-time high-accuracy GPS orbit correction with deep learning, submitted to ION NAVIGATION, 2026 (submitted).」（201 字）
- 「1. Huai Hsuan Huang, Chia-Hui Chang, Kuan-Jung Chen: [DREAM: 結合領域知識檢索與多代理推理的結構化論文評估方法](https://openreview.net/forum?id=vxtNegzSMo&referrer=%5BAuthor%20Console%5D%28%2Fgroup%3Fid%3DTAAI.org%2F2025%2FConference%2FAuthors%23your-submissions%29), [TAAI 2025](https://taai2025.org/), Dec. 13-14, NTNU, Taipei, Taiwan」（311 字）
- 「1. Chi-Ju Yeh, Chia-Hui Chang, Guan-Hong Shi: [PagePilot : 基於多代理架構之多模態自動化網頁助理](https://openreview.net/forum?id=pvqmyV41Y8&referrer=%5BAuthor%20Console%5D%28%2Fgroup%3Fid%3DTAAI.org%2F2025%2FConference%2FAuthors%23your-submissions%29), [TAAI 2025](https://taai2025.org/), Dec. 13-14, NTNU, Taipei, Taiwan」（303 字）
- 「1. Jo-Chi Kung and Chia-Hui Chang: 基於微調開源大型語言模型的交通事故資訊蒐集代理人系統研究, [ROCLING 2025](http://rocling2025.github.io), November 20th-22th, NTU, Taipei City, Taiwan」（155 字）
- 「1. Sji-Jie Ding, Chia-Hui Chang and Zi-Xuan Jian: 基於語音指令的中文 ASR 錯誤校正系統設計與實現, [ROCLING 2025](http://rocling2025.github.io), November 20th-22th, NTU, Taipei City, Taiwan」（167 字）
- 「1. Cheng Wei Xie, Kuan-Jung Chen, Kai-Hsun Chen, Chia-Hui Chang, Siaw-Fong Chung, Fang-Hsiang Cheng, Hui-Chun Hung, and Chen-Chung Liu: Understanding Students Through Dialogue: A Dialogue Knowledge Tracing System for Learning Analytics, CIKM 2025 Workshop on ProActLLM: Conversational Information Seeking with Large Language Models, Nov. 14, Coex, Seoul, South Korea.」（367 字）
- 「1. C.-C. Liu, Y. Y. Lin, F. Y. Lo, C. H. Chang, H. M. Lin (2025).[From readers to players: Exploring student engagement in a gamified metaverse and its effect on reading interest](https://link.springer.com/article/10.1007/s10639-024-13068-1). Education and Information Technologies. Volume 30, pages 421–447」（307 字）
- 「1. Jo-Chi Kung, Huai-Hsuan Huang, Kuo-Chun Chien and Chia-Hui Chang: A Narrative Assistant for Traffic Accidents Based on Large Language Models (LLM) (Long) Brno, Czech Republic. 11-13 December 2024.」（199 字）
- 「1. Kuo-Chun Chien, Chia-Hui Chang, Huai-Hsuan Huang and Jo-Chi Kung: Prosecutorial Outcome Predication with LoRA and QLoRA (Short)Brno, Czech Republic. 11-13 December 2024.」（172 字）
- 「1. Jhuoan Li\* (李倬安), Jason Yeh (葉展維), Chia-Hui Chang: 基於深度學習的跨多輸入法編輯器整合系統 (#81), [TAAI 2024](https://taai2024.org/program-of-domestic-track/) (Appier Award).」（158 字）
- 「1. Yuan-Hao Lin; Chia-Hui Chang; Hsiu-Min Chuang: [Fine-Grained Meetup Events Extraction Through Context-Aware Event Argument Positioning and Recognition](https://link.springer.com/article/10.1007/s44196-024-00697-0), International Journal of Computational Intelligence Systems 17, 296 2024. [https://doi.org/10.1007/s44196-024-00697-0](https://doi.org/10.1007/s44196-024-00697-0)」（380 字）
- 「1. C. C. Liu, C. W. Chiu, C. H. Chang. Analysis of a chatbot as a dialogic reading facilitator: its influence on learning interest and learner interactions. Education Tech Research Dev 72, 2103–2131 (2024). [https://doi.org/10.1007/s11423-024-10370-0](https://doi.org/10.1007/s11423-024-10370-0)」（295 字）
- 「1. C. C. Liu, W. J. Chen, F. Y. Lo, C. H. Chang & H. M. Lin (2024). [Teachable Q&A Agent: The Effect of Chatbot Training by Students on Reading Interest and Engagement](https://journals.sagepub.com/doi/10.1177/07356331241236467). Journal of Educational Computing Research. 62, 4, p. 1122-1154 33」（295 字）
- 「1. Yuan-Hao Lin; Chia-Hui Chang; Hsiu-Min Chuang; Xiang-Shun Lin; Ting Yeh; Min-Jhao Hong: [Cost-Effective Event Mining on the Web via Event Source Page Discovery and Data API Construction](https://ieeexplore.ieee.org/document/10638638), IEEE ACCESS, vol. 12, pp. 115981-115993, 2024,DOI: [10.1109/ACCESS.2024.3445448](https://doi.org/10.1109/ACCESS.2024.3445448)」（363 字）
- 「1. Shih, C. Y., Chang, C. M., Wu, B. F., [Chang, C. H.](https://scholars.ncu.edu.tw/zh/persons/chia-hui-chang) & [Hwang, F. N.](https://scholars.ncu.edu.tw/zh/persons/feng-nan-hwang): [Data-driven numerical simulation with extended Kalman filtering and long short-term memory networks for highway traffic flow prediction](https://academic.oup.com/jom/article/doi/10.1093/jom/ufad046/7480256), [Journal of Mechanics](https://academic.oup.com/jom/). Vol. 40, p. 31-43. 2024.」（472 字）
- 「1. Huai-Hsuan Huang, Chia-Hui Chang, Jo-Chi Kung and Kuo-Chun Chien: To What Extent Do LLMs Understand A VerdictA Case Study on Traffic Accident Information Extraction 大型語言模型對判決理解的探討：以交通事故資訊擷取為例 (#33), [ROCLING 2024](https://rocling2024.github.io/) (Best Paper Award)」（267 字）
- 「1. Jo-Chi Kung, Huai-Hsuan Huang, Kuo-Chun Chien and Chia-Hui Chang: Collision Care Guide based on Large Language Models 基于LLM的交通事故諮詢助理 (#32), [ROCLING 2024](https://rocling2024.github.io/)」（189 字）
- 「1. Min-Chao Hung, Chia-Hui Chang and Chi-Ju Yeh: 中文文章級別人物關係擷取之研究 (#34), [ROCLING 2024](https://rocling2024.github.io/)」（118 字）
- 「1. [Chung-Yu Shih](https://agupubs.onlinelibrary.wiley.com/authored-by/Shih/Chung%E2%80%90Yu), [Cissi Ying-tsen Lin](https://agupubs.onlinelibrary.wiley.com/authored-by/Lin/Cissi+Ying%E2%80%90tsen), [Shu-Yu Lin](https://agupubs.onlinelibrary.wiley.com/authored-by/Lin/Shu%E2%80%90Yu), [Cheng-Hung Yeh](https://agupubs.onlinelibrary.wiley.com/authored-by/Yeh/Cheng%E2%80%90Hung), [Yu-Ming Huang](https://agupubs.onlinelibrary.wiley.com/authored-by/Huang/Yu%E2%80%90Ming), [Feng-Nan Hwang](https://agupubs.onlinelibrary.wiley.com/authored-by/Hwang/Feng%E2%80%90Nan), [Chia-Hui Chang](https://agupubs.onlinelibrary.wiley.com/authored-by/Chang/Chia%E2%80%90Hui): Forecasting of Global Ionosphere Maps With Multi-Day Lead Time Using Transformer-Based Neural Networks, Space Weather. Jan. 2024.[https://doi.org/10.1029/2023SW003579](https://doi.org/10.1029/2023SW003579)」（864 字）
- 「1. Kuo-Chun Chien, Chia-Hui Chang, R. D. Sun, [Legal Knowledge Management for Prosecutors based on Judgement Prediction and Error Analysis from Indictments](https://www.sciencedirect.com/science/article/abs/pii/S0267364923001127), Computer Law & Security Review. Apr. 2024. [https://doi.org/10.1016/j.clsr.2023.105902](https://doi.org/10.1016/j.clsr.2023.105902)」（362 字）
- 「1. Ren-Der Sun, Chia-Hui Chang, and Kuo-Chun Chien: [New Horizons of Legal Judgement Predication via Multi-Task Learning and LoRA](https://ebooks.iospress.nl/doi/10.3233/FAIA230966), 36th International Conference on Legal Knowledge and Information Systems ([Jurix 2023](https://jurix23.maastrichtlawtech.eu/)). Maastricht, the Netherlands, 18-20 December 2023.[https://doi.org/10.3233/FAIA230966](https://doi.org/10.3233/FAIA230966)」（432 字）
- 「1. Yu-Kai Lee and Chia-Hui Chang: [Story Co-Telling Dialogue Generation via Reinforcement Learning and Knowledge Graph](https://alta2023.alta.asn.au/files/6.pdf), The 21st Annual Workshop of the Australasian Language Technology Association ([ALTA 2023](https://alta2023.alta.asn.au/)), Melbourne, Australia, Nov. 29-Dec. 1, 2023. [https://aclanthology.org/2023.rocling-1.2/](https://aclanthology.org/2023.rocling-1.2/)」（418 字）
- 「1. Yu-Yen Ting and Chia-Hui Chang: [Improving Chinese Fact Checking via Prompt Based Learning and Low Rank Adaptation](https://dl.acm.org/doi/10.1145/3625007.3629126), The 2023 IEEE/ACM International Conference on Advances in Social Networks Analysis and Mining ([ASONAM 2023](https://asonam.cpsc.ucalgary.ca/2023/)).Kusadasi, Turkey, 6-9 November 2023. [https://doi.org/10.1145/3625007.3629126](https://doi.org/10.1145/3625007.3629126)」（436 字）
- 「1. Yuan-Hao Lin, Chia-Hui Chang, Hsiu-Min Chuang: [EventGo! Mining Events through Semi-Supervised Event Title Recognition and Pattern-based Venue/Date Coupling](https://doi.org/10.6688/JISE.202305_39%283%29.0013), Journal of Information Science and Engineering, Vol. 39, No. 3, pp.655 - 670, 2023. [10.6688/JISE.202305_39(3).0013](https://doi.org/10.6688/JISE.202305_39%283%29.0013)」（382 字）
- 「1. Yu-Xiang Hong, Chia-Hui Chang: [Improving Colloquial Case Legal Judgment Prediction via Abstractive Text Summarization](https://www.sciencedirect.com/science/article/abs/pii/S0267364923000730), Computer Law & Security Review. Nov. 2023. [https://doi.org/10.1016/j.clsr.2023.105863](https://doi.org/10.1016/j.clsr.2023.105863)」（328 字）
- 「1. [Yong Ting Feng](https://dblp.org/pid/358/1480.html), Chen-Chung Liu, [Chia-Hui Chang](https://dblp.org/pid/84/3307.html): The Design and Analysis of a Storytelling Chatbot with Natural Language Processing Techniques for Enhancing EFL Reading.[ICALT 2023](https://dblp.org/db/conf/icalt/icalt2023.html#FengLC23): 250-251」（323 字）
- 「1. 黃冠傑、黃淯銘、張嘉惠、黃覺修、鍾曉芳、鄭芳祥: 通過實體和事件關係標記改進問題答案對生成的 控制 , NCS2023.」（63 字）
- 「1. 許志仲、朱翊瑄、劉晨鐘、張嘉惠、温采婷: 基於生成式語言模型之科學探究教學代理之提示詞框架與系統設計, NCS2023.」（63 字）
- 「1. 李聿鎧、張嘉惠: 應用強化學習與知識圖譜於故事共述生成之研究, ROCLING 2023」（47 字）
- 「1. 葉丞鴻、張嘉惠: 中文訊息傳遞服務對話系統之建構, ROCLING 2023.」（42 字）
- 「1. 林子平、張嘉惠、劉晨鐘: 基於大型語言模型應用指示詞打造無程式碼對話系統平台 - 以聊故事機器人為例, TAAI 2023」（64 字）
- 「1. 葉丞鴻, 李聿鎧, 張嘉惠: 多領域任務導向一對一用戶對話收集系統, International Journal of Computational Linguistics & Chinese Language Processing (IJCLCLP), 2023 (Accepted)」（145 字）
- 「1. 張嘉惠,陳臆玄,劉晨鐘,鄭芳祥:聊故事機器人對話回應模組選擇之研究, Submitted to International Journal of Computational Linguistics & Chinese Language Processing (1st Revision)」（146 字）
- 「1. 葉丞鴻, 李聿鎧, 張嘉惠: [多領域任務導向用戶語音助理對話收集系統](https://drive.google.com/file/d/1OYBOAUCFr20Yzs7jnbLD6VjfH8CQnakT/view?usp=sharing), TAAI 2022」（134 字）
- 「1. 洪裕翔, 張嘉惠: [通過生成式文本摘要改進口語法律案件預測效能之研究](https://drive.google.com/file/d/18G28TCeFlcemN0e72EDKRcWQ48DRSNoA/view?usp=sharing), TAAI 2022」（134 字）
- 「1. 李逸軒, 張嘉惠: [基於強化式學習結合自編碼器壓縮特徵之資產配置方法](https://drive.google.com/file/d/1QRxSMqHiOpDreZtbPqSS4kpTaJJ5mbrI/view?usp=sharing), TAAI 2022」（134 字）
- 「1. [Tzu-Hsien Huang](https://dblp.org/pid/279/3759.html), Chia-Hui Chang: [Improving Response Diversity through Commonsense-Aware Empathetic Response Generation](https://aclanthology.org/2022.rocling-1.37/).[ROCLING 2022](https://dblp.org/db/conf/rocling/rocling2022.html#HuangC22): 299-306」（290 字）
- 「1. [Kai-Yen Kao](https://dblp.org/pid/333/8168.html), Chia-Hui Chang: [Applying Information Extraction to Storybook Question and Answer Generation](https://aclanthology.org/2022.rocling-1.36/).[ROCLING 2022](https://dblp.org/db/conf/rocling/rocling2022.html#KaoC22): 289-298」（274 字）
- 「1. [Chen-Chung Liu](https://dblp.org/pid/76/122.html), [Mo-Gang Liao](https://dblp.org/pid/328/8100.html), Chia-Hui Chang, [Hung-Ming Lin](https://dblp.org/pid/38/7288.html): [An analysis of children' interaction with an AI chatbot and its impact on their interest in reading](https://www.sciencedirect.com/science/article/abs/pii/S0360131522001476#:~:text=It%20was%20found%20that%20students,with%20the%20chatbot%20faded%20significantly.).[Comput. Educ. 189](https://dblp.org/db/journals/ce/ce189.html#LiuLCL22): 104576 (2022)」（526 字）
- 「1. Chen-Chung Liu, [Tsun-Wei Lin](https://dblp.org/pid/316/5127.html), [Chia-Hui Cheng](https://dblp.org/pid/23/11310.html), [Cai-Ting Wen](https://dblp.org/pid/205/6234.html), [Ming-Hua Chang](https://dblp.org/pid/17/4802.html), [Shih-Hsun Fan Chiang](https://dblp.org/pid/98/8648.html), [Meng-Jung Tsai](https://dblp.org/pid/63/379.html), [Hung-Ming Lin](https://dblp.org/pid/38/7288.html), [Fu-Kwun Hwang](https://dblp.org/pid/93/7708.html): The impact of functional interdependencies of computer simulations on collaborative learning: Evidence from multiple sources.[J. Comput. Assist. Learn. 38(2)](https://dblp.org/db/journals/jcal/jcal38.html#LiuLCWCCTLH22): 455-469 (2022)」（680 字）
- 「1. Thamolwan Poopradubsil andChia-Hui Chang:[Question-answer pairing from IM conversations via message merging and reply-to prediction](https://aclanthology.org/2022.paclic-1.2/), accepted by [PACLIC 2022](https://www.paclic2022.net/papers.html).」（246 字）
- 「1. Chia-Hui Chang, Zhi-Xian Liu, Yu-Ching Liao, Yu-Hao Wu , Thamolwan Poopradubsil: [Chat-log Disentanglement via Same-Thread Classification and Direct-Reply Prediction](https://aclanthology.org/2022.paclic-1.11/), accepted by [PACLIC 2022](https://www.paclic2022.net/papers.html).」（281 字）
- 「1. Chia-Hui Chang, Yu-Ching Liao and Ting Yeh:[Event Source Page Discovery via Policy-based RL with Multi-Task Neural Sequence Model](https://drive.google.com/file/d/1zalwnKtxsF7bpJceB7Tsw-uxH0c1noNh/view?usp=sharing), accepted by[WISE 2022](https://wise2022.sigappfr.org/). \[[pdf](https://drive.google.com/file/d/1h2NxZqgz7xdizQ4BPnSCtQxRovnqiewv/view?usp=drive_link)\]」（371 字）
- 「1. [Chia-Hui Chang](https://sites.google.com/site/jahuichang/), Cheng-Ju Wu and Tzu-Ping Lin:[Automatic Web Data API Creation via Cross-Lingual Neural Pagination Recognition](https://drive.google.com/file/d/1h2NxZqgz7xdizQ4BPnSCtQxRovnqiewv/view?usp=sharing),[ICWE 2022](https://icwe2022.webengineering.org/programandsessions/) (accept rate: 22%).」（347 字）
- 「1. Tai-Jung Kan and Chia-Hui Chang: [Home Appliance Review Analysis Via Adversarial Reptile](https://dl.acm.org/doi/abs/10.1145/3486622.3493958). Web Intelligence 2021.」（168 字）
- 「1. Yu-Hao Wu and Chia-Hui Chang: [Multi-Task Neural Sequence Labeling for Zero-Shot Cross-Language Boilerplate Removal](https://dl.acm.org/doi/10.1145/3486622.3493938). Web Intelligence 2021.」（191 字）
- 「1. [Hsiao-Wen Tseng](https://aclanthology.org/people/h/hsiao-wen-tseng/), [Chia-Hui Chang](https://aclanthology.org/people/c/chia-hui-chang/), [Hsiu-Min Chuang](https://aclanthology.org/people/h/hsiu-min-chuang/), [Aspect-Based Sentiment Analysis and Singer Name Entity Recognition using Parameter Generation Network Based Transfer Learning](https://aclanthology.org/2021.rocling-1.26/), ROCLING 2021.」（401 字）
- 「1. [Tai-Jung Kan](https://aclanthology.org/people/t/tai-jung-kan/), [Chia-Hui Chang](https://aclanthology.org/people/c/chia-hui-chang/), [Hsiu-Min Chuang](https://aclanthology.org/people/h/hsiu-min-chuang/), [Home Appliance Review Research Via Adversarial Reptile](https://aclanthology.org/2021.rocling-1.24/), ROCLING 2021.」（324 字）
- 「1. [Chun-Nan Hsu](https://www.prophy.science/author/6665029/Chun-Nan-Hsu),[Chia-Hui Chang](https://www.prophy.science/author/7880155/Chia-Hui-Chang),[Thamolwan Poopradubsil](https://www.prophy.science/author/56085830/Thamolwan-Poopradubsil),[Amanda Lo](https://www.prophy.science/author/4631575/Amanda-Lo),[Karen A. William](https://www.prophy.science/author/37384906/Karen-A-William),[Ko-Wei Lin](https://www.prophy.science/author/4494245/Ko-Wei-Lin),[Anita Bandrowski](https://www.prophy.science/author/759591/Anita-Bandrowski),[Ibrahim Burak Ozyurt](https://www.prophy.science/author/591672/Ibrahim-Burak-Ozyurt),[Jeffrey S. Grethe](https://www.prophy.science/author/1040933/Jeffrey-S-Grethe),[Maryann E. Martone](https://www.prophy.science/author/834956/Maryann-E-Martone):[Antibody Watch: Text Mining Antibody Specificity from the Literature](https://europepmc.org/article/med/34043624https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8189493/),[arXiv:2008.01937v1](https://arxiv.org/abs/2008.01937v1). Plos Computational Biology, 17(5):e1008967 (2021)」（1052 字）
- 「1. 廖于晴, 張嘉惠. [應用強化式學習探勘活動來源網頁](http://search.taai.org.tw/paper/2021/0/%E6%87%89%E7%94%A8%E5%BC%B7%E5%8C%96%E5%BC%8F%E5%AD%B8%E7%BF%92%E6%8E%A2%E5%8B%98%E6%B4%BB%E5%8B%95%E4%BE%86%E6%BA%90%E7%B6%B2%E9%A0%81.pdf), TAAI 2021.」（222 字）
- 「1. 吳昱豪, 張嘉惠. [應用多任務序列標記模型於零樣本跨語言網頁模板移除之研究](http://search.taai.org.tw/paper/2021/0/%E6%87%89%E7%94%A8%E5%A4%9A%E4%BB%BB%E5%8B%99%E5%BA%8F%E5%88%97%E6%A8%99%E8%A8%98%E6%A8%A1%E5%9E%8B%E6%96%BC%E9%9B%B6%E6%A8%A3%E6%9C%AC%E8%B7%A8%E8%AA%9E%E8%A8%80%E7%B6%B2%E9%A0%81%E6%A8%A1%E6%9D%BF%E7%A7%BB%E9%99%A4%E4%B9%8B%E7%A0%94%E7%A9%B6.pdf), TAAI 2021.」（342 字）
- 「1. 吳承儒, 張嘉惠. [基於自動分頁預測之大規模資料應用程式介面建置](http://search.taai.org.tw/paper/2021/0/%E5%9F%BA%E6%96%BC%E8%87%AA%E5%8B%95%E5%88%86%E9%A0%81%E9%A0%90%E6%B8%AC%E4%B9%8B%E5%A4%A7%E8%A6%8F%E6%A8%A1%E8%B3%87%E6%96%99%E6%87%89%E7%94%A8%E7%A8%8B%E5%BC%8F%E4%BB%8B%E9%9D%A2%E5%BB%BA%E7%BD%AE%20-%20%E4%BB%A5%E6%B4%BB%E5%8B%95%E6%93%B7%E5%8F%96%E7%82%BA%E4%BE%8B.pdf) - 以活動擷取為例, TAAI 2021.」（372 字）
- 「1. Chien-Lung Chou, Chia-Hui Chang, Yuan-Hao Lin, Kuo-Chun Chien: [On the Construction of Web NER Model Training Tool based on Distant Supervision](https://dl.acm.org/doi/abs/10.1145/3422817), Transactions on Asian and Low-Resource Language Information Processing, Transactions on Asian and Low-Resource Language Information Processing, 2020.」（342 字）
- 「1. Oviliani Yenty Yuliana and Chia-Hui Chang: [DCADE: divide and conquer alignment with dynamic encoding for full page data extraction](http://link.springer.com/article/10.1007/s10489-019-01499-0), Applied Intelligence, 50, 271–295 (2020)」（238 字）
- 「1. Chia-Hui Chang, [Yuan-Hao Lin](https://dblp.org/pid/193/3553.html), [Hsiu-Min Chuang](https://dblp.org/pid/150/5799.html): [EventGo! Exploring Event Dynamics from Social-Media Posts](https://ieeexplore.ieee.org/document/9231457).[ICS 2020](https://dblp.org/db/conf/intcompsymp/ics2020.html#ChangLC20): 548-552」（312 字）
- 「1. [Yu-Chieh Chao](https://dblp.org/pid/277/4976.html), Chia-Hui Chang: [Automatic Spelling Correction for ASR Corpus in Traditional Chinese Language using Seq2Seq Models](https://ieeexplore.ieee.org/document/9359053).[ICS 2020](https://dblp.org/db/conf/intcompsymp/ics2020.html#ChaoC20a): 553-558」（297 字）
- 「1. [Yu-Chieh Chao](https://dblp.org/pid/277/4976.html), Chia-Hui Chang: [Automatic Punctuation Restoration for corpus in Traditional Chinese Language using Deep Learning](https://ieeexplore.ieee.org/document/9382482).[TAAI 2020](https://dblp.org/db/conf/taai/taai2020.html#ChaoC20): 91-96」（288 字）
- 「1. [Yuan-Hao Lin](https://dblp.org/pid/193/3553.html), Chia-Hui Chang, [Hsiu-Min Chuang](https://dblp.org/pid/150/5799.html): [Mining Events through Activity Title Extraction and Venue Coupling](https://ieeexplore.ieee.org/document/9382472).[TAAI 2020](https://dblp.org/db/conf/taai/taai2020.html#LinCC20): 136-141」（314 字）
- 「1. [Chun-Nan Hsu](https://dblp.org/pid/h/ChunNanHsu.html), Chia-Hui Chang, [Thamolwan Poopradubsil](https://dblp.org/pid/271/8241.html), [Amanda Lo](https://dblp.org/pid/39/4332.html), [Karen A. William](https://dblp.org/pid/271/8219.html), [Ko-Wei Lin](https://dblp.org/pid/122/5666.html), [Anita E. Bandrowski](https://dblp.org/pid/157/5182.html), [Ibrahim Burak Özyurt](https://dblp.org/pid/75/2171.html), [Jeffrey S. Grethe](https://dblp.org/pid/08/3152.html), [Maryann E. Martone](https://dblp.org/pid/62/2221.html): Antibody Watch: Text Mining Antibody Specificity from the Literature.[CoRR abs/2008.01937](https://dblp.org/db/journals/corr/corr2008.html#abs-2008-01937) (2020)」（683 字）
- 「1. 林政憲, 張嘉惠. [情緒及技術指標於股票漲跌幅排名預測及動態投資組合最佳化之研究](http://search.taai.org.tw/paper/2020/0/%E6%83%85%E7%B7%92%E5%8F%8A%E6%8A%80%E8%A1%93%E6%8C%87%E6%A8%99%E6%96%BC%E8%82%A1%E7%A5%A8%E6%BC%B2%E8%B7%8C%E5%B9%85%E6%8E%92%E5%90%8D%E9%A0%90%E6%B8%AC%E5%8F%8A%E5%8B%95%E6%85%8B%E6%8A%95%E8%B3%87%E7%B5%84%E5%90%88%E6%9C%80%E4%BD%B3%E5%8C%96%E4%B9%8B%E7%A0%94%E7%A9%B6.pdf), [TAAI 2020](https://taai2020.github.io/dprogram.html).」（416 字）
- 「1. 陳震瑜, 張嘉惠, 邱裕民. [應用網路聲量及情緒分析於熱門歌曲點播量預測](http://search.taai.org.tw/paper/2020/0/%E6%87%89%E7%94%A8%E7%B6%B2%E8%B7%AF%E8%81%B2%E9%87%8F%E5%8F%8A%E6%83%85%E7%B7%92%E5%88%86%E6%9E%90%E6%96%BC%E7%86%B1%E9%96%80%E6%AD%8C%E6%9B%B2%E9%BB%9E%E6%92%AD%E9%87%8F%E9%A0%90%E6%B8%AC.pdf), [TAAI 2020](https://taai2020.github.io/dprogram.html).」（331 字）
- 「1. 邱威誠, 張嘉惠. [應用AutoNER於社群網路中文歌手名稱辨識之研究](http://search.taai.org.tw/paper/2020/0/%E6%87%89%E7%94%A8AutoNER%E6%96%BC%E7%A4%BE%E7%BE%A4%E7%B6%B2%E8%B7%AF%E4%B8%AD%E6%96%87%E6%AD%8C%E6%89%8B%E5%90%8D%E7%A8%B1%E8%BE%A8%E8%AD%98%E4%B9%8B%E7%A0%94%E7%A9%B6.pdf), [TAAI 2020 (poster)](https://taai2020.github.io/pdprogram.html).」（320 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_cnm3iP4hxo7T)」（89 字）
- 「1. [Gui-Ru Li](https://dblp.uni-trier.de/pers/hd/l/Li:Gui=Ru), Chia-Hui Chang: Semantic role labeling for opinion target extraction from chinese social network. [ASONAM 2019](https://dblp.uni-trier.de/db/conf/asunam/asonam2019.html#LiC19): 1042-1047」（249 字）
- 「1. [Hsiang-En Cherng](https://dblp.uni-trier.de/pers/hd/c/Cherng:Hsiang=En), Chia-Hui Chang: Short Text Conversation Based on Deep Neural Network and Analysis on Evaluation Measures. [CoRR abs/1907.03070](https://dblp.uni-trier.de/db/journals/corr/corr1907.html#abs-1907-03070) (2019)」（284 字）
- 「1. 陳震瑜, 邱威誠, 張嘉惠, 邱裕民, 莊秀敏: 運用多領域資料結合深度學習技術於音樂論壇評論之情感分析, TAAI 2019.」（67 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_no6XtoV1xo7t)」（89 字）
- 「1. 簡國峻, 張嘉惠, [利用記憶增強條件隨機場域之深度學習及自動化詞彙特徵於中文命名實體辨識之研究](http://search.taai.org.tw/paper/2018/0/%E5%88%A9%E7%94%A8%E8%A8%98%E6%86%B6%E5%A2%9E%E5%BC%B7%E6%A2%9D%E4%BB%B6%E9%9A%A8%E6%A9%9F%E5%A0%B4%E5%9F%9F%E4%B9%8B%E6%B7%B1%E5%BA%A6%E5%AD%B8%E7%BF%92%E5%8F%8A%E8%87%AA%E5%8B%95%E5%8C%96%E8%A9%9E%E5%BD%99%E7%89%B9%E5%BE%B5%E6%96%BC%E4%B8%AD%E6%96%87%E5%91%BD%E5%90%8D%E5%AF%A6%E9%AB%94%E8%BE%A8%E8%AD%98%E4%B9%8B%E7%A0%94%E7%A9%B6.pdfhttp://search.taai.org.tw/paper/2018/0/%E5%88%A9%E7%94%A8%E8%A8%98%E6%86%B6%E5%A2%9E%E5%BC%B7%E6%A2%9D%E4%BB%B6%E9%9A%A8%E6%A9%9F%E5%A0%B4%E5%9F%9F%E4%B9%8B%E6%B7%B1%E5%BA%A6%E5%AD%B8%E7%BF%92%E5%8F%8A%E8%87%AA%E5%8B%95%E5%8C%96%E8%A9%9E%E5%BD%99%E7%89%B9%E5%BE%B5%E6%96%BC%E4%B8%AD%E6%96%87%E5%91%BD%E5%90%8D%E5%AF%A6%E9%AB%94%E8%BE%A8%E8%AD%98%E4%B9%8B%E7%A0%94%E7%A9%B6.pdf), TAAI 2018.」（818 字）
- 「1. [Jen-Tzung Chien](https://aclanthology.org/people/j/jen-tzung-chien/) | [Chia-Hui Chang](https://aclanthology.org/people/c/chia-hui-chang/): [International Journal of Computational Linguistics & {C}hinese Language Processing, Volume 23, Number 1, June 2018](https://aclanthology.org/volumes/2018.ijclclp-1/)」（310 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_nTxUlKoSxfQp)」（89 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_RKM-DSqcxfQx)」（89 字）
- 「1. Chien-Lung Chou, Chia-Hui Chang, Ya-Yun Huang, [Boosted Named Entities Recognition via Tri-Training](http://dl.acm.org/citation.cfm?id=2963100), Transactions on Asian and Low-Resource Language Information Processing, 16(2): Article No. 10 (2016) DOI: 10.1145/2963100」（269 字）
- 「1. C.-H. Chang, H.-M. Chuang, C.-Y. Huang, Y.-S. Su, S.-Y. Li. [Enhancing POI Search on Maps via Online Address Extraction and Associated Information Extraction](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MzIxMjllNmM2ZWNmNDE3ZQ), [Appl. Intell. 44(3)](http://dblp.uni-trier.de/db/journals/apin/apin44.html#ChangCHSL16): 539-556 (2016)」（389 字）
- 「1. C.-H. Chang, Tian-Shen Chen, Ming-Chun Chen, Jhong-Li Ding, [Efficient Page-Level Data Extraction Via Schema Verification](http://download.springer.com/static/pdf/251/chp%253A10.1007%252F978-3-319-31750-2_38.pdf?originUrl=http%3A%2F%2Flink.springer.com%2Fchapter%2F10.1007%2F978-3-319-31750-2_38&token2=exp=1487993774~acl=%2Fstatic%2Fpdf%2F251%2Fchp%25253A10.1007%25252F978-3-319-31750-2_38.pdf%3ForiginUrl%3Dhttp%253A%252F%252Flink.springer.com%252Fchapter%252F10.1007%252F978-3-319-31750-2_38*~hmac=a6a8441745d6d2c668a8627b86b4d4ce4bbe4200ac0f8b77f2031a4db090e79d), PAKDD 2016. DOI: 10.1007/978-3-319-31750-2_38」（616 字）
- 「1. 林圓皓, 張嘉惠: [Facebook 活動事件擷取系統(Facebook Activity Event Extraction System)](https://aclanthology.coli.uni-saarland.de/papers/O16-1022/o16-1022), ROCLING 2016.」（158 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_NV_pFDrtxfQz)」（89 字）
- 「1. Ya-Yun Huang, Chia-Hui Chang, Chien-Lung Chou, [A Tool for Web NER Model Generation Using Search Snippets of Known Entities (基於已知名稱搜尋結果的網路實體辨識模型建立工具](https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6NGM4YzZlMTYzY2VmZTYwMw)), ROCLING 2015.」（275 字）
- 「1. Ting-Yao Kao, Hsiu-Ming Chuang, Chia-Hui Chang, [Points of Interest Extraction from Unstructured Web (基於Web之商家景點擷取與資料庫建置)](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MjA2OGEwZWVhOWFhNDE2NA), ROCLING 2015.」（262 字）
- 「1. [H.-M. Chuang](http://dblp.uni-trier.de/pers/hd/c/Chuang:Hsiu=Min), C.-H. Chang: Verification of POI and Location Pairs via Weakly Labeled Web Data. [Workshop on LocWeb 2015, WWW (Companion Volume)](http://dblp.uni-trier.de/db/conf/www/www2015c.html#ChuangC15): 743-748」（272 字）
- 「1. J.-C. Chen, I.-C. Wu, W.-J. Tseng, B.-H. Lin, C.-H. Chang, [Job-Level Alpha-Beta ](http://goog_1524985009)[Search](http://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=6785996), [IEEE Transactions on Computational Intelligence and AI in Game](http://cis.ieee.org/ieee-transactions-on-computational-intelligence-and-ai-in-games.html) (2014). 10.1109/TCIAIG.2014.2316314」（370 字）
- 「1. 鄭仲庭, 莊秀敏, 張嘉惠, [整合多種搜尋結果以提高POI搜尋的準確性](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6NTk5NzM0YWJmOTM1ODkwMw), TAAI 2015, 國內議程論文佳作.」（184 字）
- 「1. 丁中立, 張嘉惠, [完整綱要推導之改進](https://docs.google.com/a/g.ncu.edu.tw/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6NmIwYmZkN2E5NjI2M2NhNw), TAAI 2015.」（158 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_RSY3TP0NxfQ-)」（89 字）
- 「1. [Chien-Lung Chou](http://www.informatik.uni-trier.de/%7Eley/pers/hd/c/Chou:Chien=Lung.html), Chia-Hui Chang: [Named Entity Extraction via Automatic Labeling and Tri-training: Comparison of Selection Methods](https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MmRmYTM4NWY0YzFiOTE0Zg). [AIRS 2014](http://www.informatik.uni-trier.de/%7Eley/db/conf/airs/airs2014.html#ChouC14): 244-25」（416 字）
- 「1. H.-M. Chuang, C.-H. Chang, and T.-Y. Kao, [Effective Web Crawling for Chinese Addresses and Associated Information](https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MTY4YmQyNTNjNWVmZDlhMA), The 15th International Conference on Electronic Commerce and Web Technologies (ECWeb 2014), Munich, Germany, Sep. 1-5, 2014. (Acceptance rate: 24%).」（375 字）
- 「1. M.-L. Wu, C.-H. Chang, [Parallel co-clustering with augmented matrices algorithm with Map-Reduce](https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6MjE2NzQwMTM1Y2Q3ZjY4NQ), The 16th International Conference on Data Warehousing and Knowledge Discovery (DaWaK 2014), Munich, Germany, Sep. 1-5, 2014.」（333 字）
- 「1. Yu-Yang Lin, Chia-Hui Chang: [網頁商家名稱擷取與地址配對之研究 (Store Name Extraction and Name-Address Matching on the Web)](http://aclanthology.info/papers/store-name-extraction-and-name-address-matching-on-the-web-in-chinese). [ROCLING 2014, [In Chinese]](http://aclanthology.info/papers/store-name-extraction-and-name-address-matching-on-the-web-in-chinese)」（347 字）
- 「1. Tsung-Ting Wu, Chia-Hui Chang: [利用核依賴估計來進行多軌自動混音 (Automatic Multi-track Mixing by Kernel Dependency Estimation)](http://aclanthology.info/papers/automatic-multi-track-mixing-by-kernel-dependency-estimation-in-chinese). ROCLING 2014, [In Chinese]」（248 字）
- 「1. Q. Chen and C.-H. Chang, [Enhancement of Kernel Dependency Estimation with Information Generalization and Case Study on Skewed Data](http://download.springer.com/static/pdf/386/art%253A10.1007%252Fs10489-014-0539-8.pdf?originUrl=http%3A%2F%2Flink.springer.com%2Farticle%2F10.1007%2Fs10489-014-0539-8&token2=exp=1460475855~acl=%2Fstatic%2Fpdf%2F386%2Fart%25253A10.1007%25252Fs10489-014-0539-8.pdf%3ForiginUrl%3Dhttp%253A%252F%252Flink.springer.com%252Farticle%252F10.1007%252Fs10489-014-0539-8*~hmac=ac758da9cde4c1a252f2716e074debbf30617437fee58916fd825f3c7124fa9d), Applied Intelligence, Vol. 41, Issue 2, pp. 582-593. (2014). 10.1007/s10489-014-0539-8」（655 字）
- 「1. 陳天盛, 陳明權, 張嘉惠. 基於頁面層級之快速網頁資料擷取與綱要驗證. [The 19th Conference on Artificial Intelligence (TAAI 2014)](http://taai2014.ntust.edu.tw/best-paper-award/), 國內議程最佳論文奬, Nov. 21-23, 2014.」（178 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_rWOhRED6xfRC)」（89 字）
- 「1. C.-L. Chen and C.-H. Chang, [Evaluation of Session-Based Recommendation Systems for Social Networks](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?tp=&arnumber=6753997&searchWithin%3Dp_Authors%3A.QT.Chang%2C+Chia-Hui.QT.%26sortType%3Ddesc_p_Publication_Year), [Data Mining Workshops (ICDMW)](http://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=6732242), 2013, pp. 758-765. [10.1109/ICDMW.2013.86](http://dx.doi.org/10.1109/ICDMW.2013.77)」（452 字）
- 「1. N.-H. Chen and C.-H. Chang, [Evaluation of Social, Geography, Location Effects for Point-of-Interest Recommendation](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?tp=&arnumber=6753998&searchWithin%3Dp_Authors%3A.QT.Chang%2C+Chia-Hui.QT.%26sortType%3Ddesc_p_Publication_Year), [Data Mining Workshops (ICDMW)](http://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=6732242), 2013, pp. 766-772. [10.1109/ICDMW.2013.77](http://dx.doi.org/10.1109/ICDMW.2013.77)」（468 字）
- 「1. M.-L. Wu and C.-H. Chang, [Integrating Content-Based Filtering with Collaborative Filtering using Co-Clustering with Augmented Matrices](http://dl.acm.org/citation.cfm?id=2565453), Expert Systems With Applications,[10.1016/j.eswa.2013.10.008](http://www.sciencedirect.com/science/article/pii/S0957417413008130)」（313 字）
- 「1. C.-L. Chen and C.-H. Chang: Session-Based Recommendation System for Social Network – Case Study on Tencent Weibo, [The 18th Conference on Artificial Intelligence (TAAI 2013)](http://taai2013.nccu.edu.tw/), Dec. 6-8, 2013.」（224 字）
- 「1. C.-H. Chang, [Y.-L. Lin](http://www.informatik.uni-trier.de/~ley/pers/hd/l/Lin:Yen=Ling.html), [K.-C. Lin](http://www.informatik.uni-trier.de/~ley/pers/hd/l/Lin:Kuan=Chen.html), [M. Kayed](http://www.informatik.uni-trier.de/~ley/pers/hd/k/Kayed:Mohammed.html): Page-Level Wrapper Verification for Unsupervised Web Data Extraction. [WISE (1) 2013](http://www.informatik.uni-trier.de/~ley/db/conf/wise/wise2013-1.html#ChangLLK13): 454-467」（439 字）
- 「1. M.-F. Tsai, C.-H. Hsu, C.-H. Chang, H.-M. Liao, S.-P. Li, D. H. Wu, Primary Chinese Semantic-Phonetic Compounds Pronunciation Rules Mining and Visualization, the 25th conference on Computational Linguistics and Speech Processing ([ROCLING 2013](https://sites.google.com/site/rocling2013/)), Oct. 4-5, 2013.」（309 字）
- 「1. M.-L. Wu, C.-H. Chang, R.-Z. Liu: [Co-clustering with augmented matrix](http://link.springer.com/content/pdf/10.1007%2Fs10489-012-0401-9.pdf). [Appl. Intell. 39](http://www.informatik.uni-trier.de/~ley/db/journals/apin/apin39.html#WuCL13)(1): 153-164 (2013). [10.1007/s10489-012-0401-9](http://dx.doi.org/10.1007/s10489-012-0401-9)」（334 字）
- 「1. 陳明權, 陳天盛 與 張嘉惠: 應用路徑資訊輔助樣板探勘於網頁層級之資料擷取研究, [The 18th Conference on Artificial Intelligence (TAAI 2013)](http://taai2013.nccu.edu.tw/), Dec. 6-8, 2013.」（152 字）
- 「1. 吳宗庭, 林育暘 與 張嘉惠: 探索式線上分析處理在網路附加儲存系統之應用, [The 18th Conference on Artificial Intelligence (TAAI 2013)](http://taai2013.nccu.edu.tw/), Dec. 6-8, 2013.」（149 字）
- 「1. 陳宜勤, 賴郁婷, 莊秀敏 與 張嘉惠: 加入 Google Snippets 改善網頁商家多標籤分類, [The 18th Conference on Artificial Intelligence (TAAI 2013)](http://taai2013.nccu.edu.tw/), Dec. 6-8, 2013.」（163 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_QILR5Ek9xfRH)」（89 字）
- 「1. C.-H. Chang, J.-M. Chen: Automatic Extraction of Blog Post from Diverse Blog Pages, [IEEE/WIC/ACM International Joint Conferences on Web Intelligence and Intelligent Agent Technologies (WI-IAT 2012)](http://www.fst.umac.mo/wic2012/WI/?category=program&node=1), Macau, Dec. 4-7, 2012.」（286 字）
- 「1. C.-H. Wu, C.-H. Chang: Recognition of Invitation E-mails and Extraction of Irregular Time Expressions for Intelligent E-mail Systems (行程邀約郵件的辨識與不規則時間擷取之研究), [The 17th Conference on Artificial Intelligence (TAAI 2012)](http://idb.csie.ncku.edu.tw/taai2012conference/index.php/program/session-paper)」（300 字）
- 「1. Y.-S. Su, C.-H. Chang: Associated Information Extraction from Multiple Addresses Web Page (多筆地址網頁中相關資訊擷取之研究), [The 17th Conference on Artificial Intelligence (TAAI 2012)](http://idb.csie.ncku.edu.tw/taai2012conference/index.php/program/session-paper)」（253 字）
- 「1. C.-H. Chang and W.-P. Wu: [The Design of Chinese Character Learning System Based on Phonetic Components](http://aclweb.org/anthology/O/O12/O12-1011.pdf), the 24th conference on Computational Linguistics and Speech Processing ([ROCLING 2012](https://sites.google.com/site/rocling12/)), Sep. 21-22, 2012.」（305 字）
- 「1. M.-L. Wu, C.-H. Chang, R.-Z. Liu, T.-K. Fan: Aggregate Two-way Co-Clustering of Ads and User Data for Online Advertisements, [Journal of Information Science and Engineering, ](http://goog_1256182943)[ Vol. 28 No. 1. Pages 83-97 (January 2012)](http://www.iis.sinica.edu.tw/page/jise/2012/201201.html)」（303 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_4UBIBDcixfRO)」（89 字）
- 「1. C.-H. Chang, K.-H. Huo: Increasing Broadband Subscriptions for Telecom Carriers through Mobile Advertising. [AIRS 2011](http://www.informatik.uni-trier.de/%7Eley/db/conf/airs/airs2011.html#ChangH11): 127-136」（210 字）
- 「1. C.-H. Chang, K.-H. Huo: [Mobile Advertising: Triple-win for Consumers, Advertisers and Telecom Carriers](http://research.microsoft.com/en-us/um/beijing/events/ia2011/n6.pdf), [SIGIR 2011 Workshop: Internet Advertising (IA2011)](http://research.microsoft.com/en-us/um/beijing/events/ia2011/)」（293 字）
- 「1. M.-L. Wu, C.-H. Chang, R.-Z. Liu: [Co-clustering with Augmented Data Matrix](http://www.springerlink.com/content/d061981wn8217037/). [DaWaK 2011](http://www.informatik.uni-trier.de/%7Eley/db/conf/dawak/dawak2011.html#WuCL11): 289-300」（236 字）
- 「1. C.-H. Chang and S.-Y. Lin: [Phonetic Component Ranking and Pronunciation Rule Mining for Chinese Picto-phonetic Compounds](https://docs.google.com/viewer?a=v&pid=sites&srcid=ZGVmYXVsdGRvbWFpbnxuY3VsYWJ8Z3g6NmU2MDQxZDllMzU3ZDcwNA). the 23th conference on Computational Linguistics and Speech Processing ([ROCLING 2011](http://sites.google.com/site/rocling2011/)), Sep. 8-9, 2011.」（381 字）
- 「1. T.-K. Fan and C.-H. Chang: [Blogger-Centric Contextual Advertising](http://www.sciencedirect.com/science?_ob=ArticleURL&_udi=B6V03-50PVFX4-C&_user=2489623&_coverDate=03%2F31%2F2011&_rdoc=56&_fmt=high&_orig=browse&_origin=browse&_zone=rslt_list_item&_srch=doc-info%28%23toc%235635%232011%23999619996%232568736%23FLA%23display%23Volume%29&_cdi=5635&_sort=d&_docanchor=&_ct=178&_acct=C000057545&_version=1&_urlVersion=0&_userid=2489623&md5=33221c946d28a0e2b86ab69fe812ebf3&searchtype=a). Journal of Expert Systems With Applications (SCI), Vol. 38, Issue 3, Pages 1777-1788, (Mar. 2011). (IF:2.908)」（597 字）
- 「1. C.-Y. Huang, C.-H. Chang: 中文地址及相關資訊擷取的研究, [The 16th Conference on Artificial Intelligence (TAAI 2011)](http://taai2011.cse.yzu.edu.tw/index.php/domestic-session-papers).」（172 字）
- 「1. C.-I. Kuan, C.-H. Chang: 非監督式包覆程式維護中的綱要對映, [The 16th Conference on Artificial Intelligence (TAAI 2011)](http://taai2011.cse.yzu.edu.tw/index.php/domestic-session-papers).」（173 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_pOBjrEccxfRT)」（89 字）
- 「1. T.-K. Fan and C.-H. Chang: [Sentiment Oriented Contexture Advertising](http://www.csie.ncu.edu.tw/%7Echia/pub/SOCA.pdf). [Journal of Knowledge and Information System](http://www.cs.uvm.edu/%7Ekais/).Vol. 23, No. 3, pp. 321-344, 2010.」（236 字）
- 「1. Q.-X. Lin, C.-H. Chang, and J.-L. Chen: A Simple and Effective Closed Test for Chinese Word Segmentation Based on Sequence Labeling.[](http://goog_1406578896)[International Journal of Computational Linguistics & Chinese Language Processing, Vol. 15, No. 3-4, pages 161-180, (Sep. 2010](http://www.aclclp.org.tw/clclp/v15n34.htm)).」（333 字）
- 「1. C.-H. Chang, S.-Y. Lin, S.-Y. Li, M.-F. Tsai, S.-P. Li, H.-M. Liao, C.-W. Sun, and N. E. Huang, Annotating Phonetic Component of Chinese Characters Using Constrained Optimization and Pronunciation Distribution, [International Journal of Computational Linguistics & Chinese Language Processing, Vol. 15, No. 2, Pages 145-159 (June 2010)](http://www.aclclp.org.tw/clclp/v15n2.htm).」（382 字）
- 「1. T.-K. Fan and C.-H. Chang. Learning to Predict Ads Click Based on Boosted Collaborative Filtering. [The 2nd IEEE International Conference on Social Computing (SocialCom2010)](http://www.iisocialcom.org/conference/socialcom2010/), Aug. 20-22, 2010, Minneapolis, Minnesota, USA.」（279 字）
- 「1. C.-H. Chang and S.-Y. Lee. MapMarker: Extraction of Postal Addresses And Associated Information for General Web Pages, [IEEE/WIC/ACM International Joint Conferences on Web Intelligence and Intelligent Agent Technologies (WI-IAT 2010)](http://www.yorku.ca/wiiat10/), Toronto, Canada. Sep. 1-3, 2010.」（301 字）
- 「1. C.-H. Chang, S.-Y. Li, S. Lin, J.-Y. Huang and C.-M. Chen: Prediction of Phonetic Component for Chinese Picto-phonetic Compounds, the 22th conference on Computational Linguistics and Speech Processing ([ROCLING 2010](http://www.aclweb.org/anthology/O/O10/)), Sep. 1-2, 2010.」（277 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_xCFZEVK_xfRZ)」（89 字）
- 「1. T.-K. Fan and C.-H. Chang. [Blogger-Centric Contextual Advertising](http://www.csie.ncu.edu.tw/%7Echia/pub/sp1323-fan.pdf). Proceedings of the 18th ACM Conference on Information and Knowledge Management, CIKM 2009 (Short paper), Hong Kong. Nov. 2-6, 2009. pp. 1803-1806.」（273 字）
- 「1. C.-H. Chang and J.-H. Lin: [Decision Support and Profit Prediction for Online Auction Sellers](http://www.csie.ncu.edu.tw/%7Echia/pub/p1-chang.pdf). The First ACM SIGKDD Workshop on Knowledge Discovery from Uncertain Data (U'09)」（231 字）
- 「1. T.-K. Fan and C.-H. Chang: [Sentiment Oriented Contextual Advertising](http://www.csie.ncu.edu.tw/%7Echia/pub/ECIR09.pdf). ECIR 2009. LNCS series.」（149 字）
- 「1. S.-Y. Li and C.-H. Chang: Application and Extraction of Postal Addresses and Related Information. The 14th Conference on Artificial Intelligence (TAAI 2009).」（160 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_dhW-KkGuxfRd)」（89 字）
- 「1. K.-Y. Huang and C.-H. Chang: [Efficient Mining of Frequent Episodes from Complex Sequences](http://www.csie.ncu.edu.tw/%7Echia/pub/IS2008.pdf), Information Systems, Vol. 33. No. 1, pp. 96-114 (2008).[doi:10.1016/j.is.2007.07.003](http://dx.doi.org/10.1016/j.is.2007.07.003)」（276 字）
- 「1. K.-Y. Huang, C.-H. Chang, and K.-Z. Lin: [Efficient Discovery of Frequent Continuities by Projected Window List Technology](http://www.iis.sinica.edu.tw/page/jise/2008/200807_03.pdf), Journal of Information Science, Vol. 24, No. 4, pp. 1041-1064, 2008.」（255 字）
- 「1. T.-K. Fan and C.-H. Chang: [Exploring Evolutionary Technical Trends From Research Papers](http://www.csie.ncu.edu.tw/%7Echia/pub/stanley.pdf). [The Eighth IAPR Workshop on Document Analysis Systems](http://www.u-pat.org/das08/), DAS2008 (poster session). Nara, Japan. Sep 16-19, 2008.」（287 字）
- 「1. C.-H. Chang, S.-F. Yang, C.-M. Liou, M. Kayed: [Gadget Creation for Personal Information Integration on Web Portals](http://www.csie.ncu.edu.tw/%7Echia/pub/IRI08_41.pdf), [IEEE International Conference on Information Reuse and Integration](http://iri2008.cpsc.ucalgary.ca/program-papers-per-session.pdf) (short paper), Las Vegas, USA, 2008.」（343 字）
- 「1. S.-F. Yang and C.-H. Chang: Multiple Source Data Management for Gadget Creation on Web Portals. The 13th conference on Artiticial Intelligence and and Application (TAAI 2008).」（178 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_hwvl5ZNtxfRh)」（89 字）
- 「1. Y.-C. Wu and C.-H. Chang: [Efficient Text Chunking using Linear Kernel with Mask Method](http://www.csie.ncu.edu.tw/%7Echia/pub/KNOSYS1593.pdf), Knowledge Based Systems, Vol. 20, Issue 3, pp. 209-219, 2007.[doi:10.1016/j.knosys.2006.04.016](http://dx.doi.org/10.1016/j.knosys.2006.04.016)」（291 字）
- 「1. M. Kayed, C.-H. Chang, K. Shaalan, and M. Ramzy Girgis. [FiVaTech: Page-Level Web Data Extraction from Template Pages](http://www.csie.ncu.edu.tw/%7Echia/pub/Chang_FiVaTech.pdf), ICDM 2007, [Workshop on Web2.0 Environment](https://www.kde.cs.uni-kassel.de/ws/Web2DM), Omaha, NE, USA. Oct. 28-31, 2007.」（304 字）
- 「1. C.-H. Chang and K.-C. Tsai. [Aspect Summarization from Blogsphere for Social Study](http://www.csie.ncu.edu.tw/%7Echia/pub/Chang-Aspectsum.pdf), ICDM 2007, [Workshop on Web2.0 Environment](https://www.kde.cs.uni-kassel.de/ws/Web2DM), Omaha, NE, Oct. 28-31, 2007.」（265 字）
- 「1. S.-G. Han and C.-H. Chang. Cleaning of Auction Data for Bidding Decision, 2007 National Computer Symposium (NCS 2007), Asia University, Taiwan.」（146 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_SK38BIfJxfRk)」（89 字）
- 「1. C.-H. Chang, M. Kayed, M. R. Girgis, K. Shaalan: [A Survey of Web Information Extraction Systems](http://www.csie.ncu.edu.tw/%7Echia/pub/iesurvey2006.pdf), IEEE TKDE (SCI, EI), Vol. 18, No. 10, pp. 1411-1428, Oct. 2006.」（222 字）
- 「1. K.-Y. Huang, C.-H. Chang, J.-H. Tung, C.-T. Ho: [COBRA: Closed Sequential Pattern Mining Using Bi-phase Reduction Approanch](http://www.csie.ncu.edu.tw/%7Echia/pub/cobralncs.pdf), Accepted by [DaWak 2006](http://www.dexa.org/drupal/?q=papers/accepted/2), Krakow, Poland.」（273 字）
- 「1. Y.-C. Wu, C.-H. Chang, Y.-S. Lee: [A General and Multi-lingual Phrase Chunking Model Based on Masking Method](http://www.csie.ncu.edu.tw/%7Echia/pub/cicling2006.pdf). Proceedings of the 7th International Conference on Computational Linguistics and Intelligent Text Processing ([CICLING 2006](http://www.gelbukh.com/cicling/2006/)), Mexico City, Mexico, February 19-25, 2006. LNCS 3878, pp. 144--155.」（402 字）
- 「1. K.-Y. Huang and C.-H. Chang: [Efficient Mining Strategy for Frequent Serial Episodes in Temporal Database](http://www.csie.ncu.edu.tw/%7Echia/pub/emmaApWeb06.pdf), [The 8th Asia Pacific Web Conference](http://www.itee.uq.edu.au/%7Eapweb06/) (short paper), Harbin, China, Jan. 16-18, 2006. LNCS 3841, pp. 824--829.」（316 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_mlmaGX-wxfRs)」（89 字）
- 「1. K.-Y. Huang and C.-H. Chang: [SMCA: A General Model for Mining Asynchronous Periodic Patterns in Temporal Databases](http://www.csie.ncu.edu.tw/%7Echia/pub/TKDE-0147-0504-2.pdf), IEEE Transactions on Knowledge and Data Engineering (SCI, EI), Vol. 17, No. 6, pp. 774-785, June 2005.」（284 字）
- 「1. C.-H. Chang and Z.-K. Ding: [Categorical Data Visualization and Clustering Using Subjective Factors](http://www.csie.ncu.edu.tw/%7Echia/pub/article_proof.pdf), Data and Knowledge Engineering (SCI expanded), Vol. 53, Issue 3, pp. 243-262, June 2005. [doi:10.1016/datak.2004.09.001](http://dx.doi.org/10.1016/j.datak.2004.09.001)」（330 字）
- 「1. C.-N. Hsu, C.-H. Chang, C.-H. Hsieh, J.-J. Lu, and C.-C. Chang: [Reconfigurable Web Wrapper Agents for Biological Information Integration](http://www3.interscience.wiley.com/cgi-bin/fulltext/109865531/PDFSTART), [JASIST](http://www3.interscience.wiley.com/cgi-bin/jtoc?ID=76501873) (SCI expanded), [Special Issue on Bioinformatics](http://ils.unc.edu/bmh/JASIST-CFP.doc), Vol. 56, No. 5, pp. 505--517, March 2005.」（416 字）
- 「1. K.-Y. Huang, C.-H. Chang, and K.-Z. Lin: [ClosedPROWL: Efficient Mining of Closed Frequent Continuities by Projected Window List Technology](http://www.csie.ncu.edu.tw/%7Echia/pub/sdm05.pdf), [SIAM International Conference on Data Mining](http://www.siam.org/meetings/sdm05/index.htm) (short paper), CA, USA, Apr. 21-23, 2005.」（329 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_EdDFJQ7NxfRx)」（89 字）
- 「1. C.-H. Chang and S.-C. Kuo: [OLERA: A semi-supervised approach for Web data extraction with visual support](http://www.csie.ncu.edu.tw/%7Echia/pub/56-65.pdf), IEEE Intelligent Systems (SCI, EI), Vol. 19, No. 6, pp. 56--64, Dec. 2004.」（235 字）
- 「1. K.-Y. Huang, C.-H. Chang, and K.-Z. Lin, [COCOA: An Efficient Algorithm for Mining Inter-transaction Associations for Temporal Database](http://www.csie.ncu.edu.tw/%7Echia/pub/PKDD3pages.pdf), In the [Proceedings](http://www.springer.de/comp/llncs/index.html)of the 8th European Conference on Principles and Practice of Knowledge Discovery in Databases ([PKDD04](http://ecmlpkdd.isti.cnr.it/) (poster), Pisa, Italy, 2004. LNAI 3202 (SCI expanded), pp. 509--511.」（464 字）
- 「1. C.-H. Chang and Z.-K. Ding: [Categorical Data Visualization and Clustering using Subjective Factors](http://www.csie.ncu.edu.tw/%7Echia/pub/dawak135.pdf), In the [Proceedings](http://www.springerlink.com/index/FVD0GN18WUV3VPWW) of the 6th International Conference on Data Warehousing and Knowledge Discovery ([DaWaK04](http://www.dexa.org/dexa2004/index.php?include=main.php)), Zaragoza, Spain, 2004. LNCS 3181 (SCI expanded), pp. 229-238.」（442 字）
- 「1. K.-Y. Huang and C.-H. Chang: [Mining Periodic Patterns in Sequence Data](http://www.csie.ncu.edu.tw/%7Echia/pub/dawak80.pdf), In the [Proceedings](http://www.springerlink.com/index/40BA5M7CL3QXGVA1) of the 6th International Conference on Data Warehousing and Knowledge Discovery ([DaWaK04](http://www.dexa.org/dexa2004/index.php?include=main.php)), Zaragoza, Spain, 2004. LNCS 3181 (SCI expanded), pp. 401-410.」（413 字）
- 「1. K.-Y. Huang, C.-H. Chang, and Kuo-Zui Lin: [PROWL: An Efficient Frequent Continuity Mining Algorithm on Event Sequences](http://www.csie.ncu.edu.tw/%7Echia/pub/dawak81.pdf), In the [Proceedings](http://www.springerlink.com/index/7827507EMUW7KEL4) of the 6th International Conference on Data Warehousing and Knowledge Discovery ([DaWaK04](http://www.dexa.org/dexa2004/index.php?include=main.php)), Zaragoza, Spain, 2004. LNCS 3181 (SCI expanded), pp. 351-360.」（461 字）
- 「1. C.-H. Chang and S.-C. Kuo: [OLERA: On-Line Extraction Rule Analysis for Semi-structured Documents](http://www.csie.ncu.edu.tw/%7Echia/pub/411-043.pdf), The IASTED International Conference on ARTIFICIAL INTELLIGENCE AND APPLICATIONS ([AIA 2004](http://www.iasted.org/conferences/2004/Innsbruck/aia.htm)). Feb. 16-18, 2004, Austria.」（333 字）
- 「1. K.-Y. Huang and C.-H. Chang: [Asynchronous Periodic Pattern Mining from Multi-event Time Series Databases](http://www.csie.ncu.edu.tw/%7Echia/pub/419-094.pdf), The IASTED International Conference on DATABASES AND APPLICATIONS ([DBA 2004](http://www.iasted.org/conferences/2004/Innsbruck/dba.htm)), Feb. 17-19, 2004, Austria.」（327 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_t8bv2g59xfR5)」（89 字）
- 「1. C.-H. Chang, J.-J. Chiou, H. Siek, J.-J. Lu, and C.-N. Hsu: [Reconfigurable Web Wrapper Agents](http://www.csie.ncu.edu.tw/%7Echia/pub/ieeeis.pdf), IEEE Intelligent Systems (SCI, EI), Vol. 18, No. 5, pp. 34--40, Oct. 2003.」（225 字）
- 「1. C.-H. Chang, C.-N. Hsu, and S.-C. Lui: [Automatic Information Extraction From Semi-Structured Web Pages By Pattern Discovery](http://www.csie.ncu.edu.tw/%7Echia/pub/IEPAD.pdf), Decision Support Systems Journal (SCI expanded), Vol. 35, Issue 1, pp. 129--147, Apr. 2003. [doi:10.1016/S0167-9236(02)00100-8](http://dx.doi.org/10.1016/S0167-9236%2802%2900100-8)」（360 字）
- 「1. C.-N. Hsu, C.-H. Chang, H. Siek, J.-J. Lu, J.-J. Chiou: [Reconfigurable Web Wrapper Agents for Web Information Integration](http://www.csie.ncu.edu.tw/%7Echia/pub/wndl2003.pdf), IJCAI 2003 Workshop on Information Integration on the Web, [IIWeb-03](http://www.isi.edu/info-agents/workshops/ijcai03/proceedings.htm), Aug. 2003, pp. 15-20.」（339 字）
- 「1. C.-H. Chang and S.-H. Yang: [Enhancing SWF for Incremental Association Mining by Itemset Maintenance](http://www.csie.ncu.edu.tw/%7Echia/pub/pakdd03.pdf), In the [Proceedings](http://www.springeronline.com/sgw/cda/frontpage/0,10735,5-147-22-2323333-0,00.html?changeHeader=true) of the seventh Pacific-Asia Conference on Knowledge Discovery and Data Mining ([PAKDD03](http://aitrc.kaist.ac.kr/%7Epakdd03/index.htm)), Korea, 2003. LNAI 2637 (SCI expanded), pp. 301-312.」（470 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_1TaYg1AMxfR-)」（89 字）
- 「1. C.-H. Chang: [Sequential Pattern Mining for Web Extraction Rule Generalization](http://www.csie.ncu.edu.tw/%7Echia/pub/215SF.pdf), [The 6th World multiconference on Systemics, Cybernetics and Informatics](http://www.iiis.org/sci2002/), July 14-18, 2002, Orlando, Florida.」（274 字）
- 「1. C.-H. Chang, S.-C. Kuo, K.-Y. Hwang, T.-H. Ho and C.-L. Lin: [Automatic Information Extraction for Multiple Singular Web Pages](http://www.csie.ncu.edu.tw/%7Echia/pub/0265.pdf), In the [Proceedings](http://www.springer.de/comp/llncs/index.html) of the sixth Pacific-Asia Conference on Knowledge Discovery and Data Mining ([PAKDD02](http://arbor.ee.ntu.edu.tw/pakdd02/)), Taiwan, 2002. LNAI 2336 (SCI expanded), pp. 297-303.」（426 字）
- 「[](https://sites.google.com/site/nculab/publication/publication-by-year#h.p_d1ztX03dxfR_)」（89 字）
- 「1. C.-H. Chang. and S.-C. Lui: [IEPAD: Information Extraction based on Pattern Discovery](http://www.csie.ncu.edu.tw/%7Echia/pub/www10.pdf), In the Proceedings of the tenth International Conference on World Wide Web ([WWW10](http://www10.org/)), pp. 681-688, May 2-6, 2001, Hong Kong.」（284 字）
- 「1. C.-H. Chang., S.-C. Lui, and Y.-C. Wu: [Applying Pattern Mining to Web Information Extraction](http://www.csie.ncu.edu.tw/%7Echia/pub/pakdd.pdf), In the [Proceedings](http://www.springer.de/comp/llncs/index.html) of the fifth Pacific-Asia Conference on Knowledge Discovery and Data Mining ([PAKDD01](http://www.csis.hku.hk/pakdd01/)), Hong Kong, 2001. LNAI 2035 (SCI expanded), pp. 4-15.」（390 字）
- 「1. C.-C. Hsu and C.-H. Chang: [WebYacht: A Concept-based Search Tool for WWW](http://www.csie.ncu.edu.tw/%7Echia/pub/ijait.zip), International Journal on Artificial Intelligence Tools, 2000.」（190 字）
- 「1. C.-H. Chang, S.-C. Lui, and Y.-C. Wu: [Semi-structured Information Extraction Applying Automatic Pattern Discovery](http://www.csie.ncu.edu.tw/%7Echia/pub/B121.pdf) , In Proc. of the fourteenth International Computer Symposium (ICS2000), Chia-Yi, Taiwan, Dec. 6-8. 2000.」（273 字）
- 「1. C.-H. Chang and C.-C. Hsu: Enabling concept-based relevance feedback on World Wide Web, In IEEE Transactions on Knowledge and Data Engineering (SCI), Special Issue on Web Technologies, Vol.11, No.4, pp. 595-609, July/August 1999.」（232 字）
- 「1. C.-H. Chang and C.-C. Hsu: Enabling Web Information Retrieval through Query Expansion via Contrast Analysis , Computer Networks and ISDN Systems, Vol. 30, pp.621-623, 1998.」（175 字）
- 「1. C.-H. Chang, C.-C. Hsu and C.-L. Hou: [Exploiting Hyperlinks for Automatic Information Discovery on the WWW](http://www.csie.ncu.edu.tw/%7Echia/pub/ictai.ps.gz), In Proc. of the tenth IEEE International Conference on Tools with Artificial Intelligence, (ICTAI98), Nov. 1998, Chien Tan Youth Activity Center, Taipei, Taiwan.」（326 字）
- 「1. C.-H. Chang and C.-C. Hsu: [Hypertext Information Retrieval for Short Queries](http://www.csie.ncu.edu.tw/%7Echia/pub/kdex98.ps.gz), In Proc. of the IEEE Knowledge and Data Engineering Exchange Workshop, Nov. 1998, Chien Tan Youth Activity Center, Taipei, Taiwan.」（266 字）
- 「1. C.-H. Chang and C.-C. Hsu: [Enabling Web Information Retrieval through Query Expansion via Contrast Analysis](http://www.csie.ncu.edu.tw/%7Echia/pub/www7/353.html) , In Proc. of the seventh International Conference on World Wide Web ([WWW7](http://www7.scu.edu.au/)), Apr. 14-18, 1998, Brisbane, Queensland, Australia.」（321 字）
- 「1. C.-H. Chang and C.-C. Hsu: [Constructing Personal Information Search Agents](http://www.csie.ncu.edu.tw/%7Echia/pub/pakdd.ps.gz), In Proc. of the second Pacific Asia Conference on Knowledge Discovery and Data Mining (PAKDD98), Melbourne, Australia, 1998. LNAI 1394 (SCI expanded), pp. 374-375.」（296 字）
- 「1. C.-H. Chang and C.-C. Hsu: Customizable Multi-Engine Search Tool based on Clustering , In Computer Networks and ISDN Systems, Vol. 29, pp.1217-1224, 1997.」（157 字）
- 「1. C.-H. Chang and C.-C. Hsu: [A Multi-Engine Search Tool based on Clustering](http://www.csie.ncu.edu.tw/%7Echia/pub/www6/PAPER53.html), In Proc. of the sixth international conference on World Wide Web, (WWW6), Apr.7-11, 1997, Santa Clara, CA.」（244 字）

### 頁面: `publication_thesisadvised`

**差異**: Baseline 61 行 → Experiment 1 行（移除 32 行）

**其他被移除行（需人工審核）**:

- 「# Thesis Advised」（16 字）
- 「### PhD Thesis」（14 字）
- 「[](https://sites.google.com/site/nculab/publication/thesisadvised#h.p_x2HHxZYPVoso) 2025 林圓皓(Yuan-Hao Lin),[Chinese Meetup Event Extraction via Event Source Page Discovery and Context-Aware Information Extraction](https://hdl.handle.net/11296/2j9wa8) (中文聚會活動來源探索暨上下文感知式精細資訊擷取之研究) 2019 陳燕琴 (Oviliani Yuliana), [Annotation-Free Induction of Full Schema from Template Web Pages with Dynamic Encoding](https://hdl.handle.net/11296/e4zscf)(應用動態編碼及分治對齊算法之免標記樣版網頁完整綱要推導研究) 2018 周建龍 (Chien-Lung Chou), [A Framework for Web NER Model Training based on Semi-supervised Learning](https://hdl.handle.net/11296/7s3a53)(基於半監督式學習的網路命名實體辨識模型訓練框架) 2016 莊秀敏 (Hsiu-Min Chuang), [POI Extraction and Relation Verification from the Web](https://hdl.handle.net/11296/32m9y6)(從Web擷取興趣點及驗證關係) 2014 巫孟倫 (Meng-Lun Wu), [A scalable framework for integrating content-based filtering with collaborative filtering using co-clustering with augmented matrices](https://hdl.handle.net/11296/pqwu8x)(基於共分群模型整合內容式與協同式之即時推薦系統) 2010 范登凱(Teng-Kai Fan), [Allocation of Personalized Ads on the Web](https://hdl.handle.net/11296/ecfq86)(網路個人化廣告配置之研究) 2006 黃國瑜 (Kuo-Yu Huang), [Mining Inter-Transaction Association Rules in Transactional Databases](https://hdl.handle.net/11296/skp85p)(交易型資料庫之跨交易關聯規則探勘之研究)」（1263 字）
- 「### Master Thesis」（17 字）
- 「[](https://sites.google.com/site/nculab/publication/thesisadvised#h.p_E78e_GunVMag) 2025 謝程偉 (Cheng-Wei Xie), [Understanding Students Through Dialogue: A Dialogue Knowledge Tracing System for Learning Analytics](https://hdl.handle.net/11296/hnpang)(從對話中看懂學生：對話式知識追蹤學習分析系統設計與應用) 2025 龔若齊(Jo-Chi Kung), [CCG: A Conversational Agent for Traffic Accidents Information Collection Based on Large Language Models](https://hdl.handle.net/11296/r3nvuhhttps://hdl.handle.net/11296/dvt36q)(CCG: 交通事故對話式筆錄蒐集代理人) 2025 黃懷萱 (Huai-Hsuan Huang), [DREAM: Domain-Retrieved Evidence and Multi-Agent Reasoning for Structured Paper Evaluation](https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd=v1U99z/record?r1=4&h1=1https://hdl.handle.net/11296/h95hbd)(DREAM：結合領域知識檢索與多代理推理的結構化論文評估方法) 2025 葉季儒 (Chi-Ju Yeh), [PagePilot: A Multimodal Automated Web Assistant Based on Multi-Agent Architecture](https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd=v1U99z/record?r1=6&h1=1https://hdl.handle.net/11296/vv7t39)(PagePilot: 基於多代理架構之多模態自動化網頁助理) 2025 丁仕杰 (Shi-Jie Ding), [Toward Conversational User Interface via Voice Command Correction](https://hdl.handle.net/11296/75z37b)(通過語音命令修正實現對話式用戶界面) 2025 洪閔昭 (Min-Chao Hung), [Research on Document-Level Person Relation Extraction in Chinese](https://hdl.handle.net/11296/s75wd4)(中文文章級別人物關係擷取之研究) 2024 黃冠傑 (Guan-Jie Huang), [Effortlessly Creating Teachers’ Agents: Chatbot Creation and System Module Enhancement Based on EduACT](https://hdl.handle.net/11296/vj7ptrhttps://hdl.handle.net/11296/q53w88)(輕鬆打造教師的代理人：基於 EduACT 的聊天機器人創建與系統模組改善) 2024 黃淯銘 (Yu-Ming Huang), [Controlling Question Generation Through Events and Relation Extraction](https://hdl.handle.net/11296/dcyvms)(透過事件和關係擷取控制問題生成) 2023 孫潤德 (Ren-Der Sun), [On the practical legal judgement prediction from prosecutor indictments and court verdicts](https://hdl.handle.net/11296/9ny24a) ([刑事實務預判輔助之研究](https://etd.lib.nctu.edu.tw/cgi-bin/gs32/ncugsweb.cgi/ccd=1Hf8nl/record?r1=5&h1=5)) 2023 李聿鎧 (Yu-Kai Lee), [Story Co-telling Dialogue Generation via Reinforcement Learning and Knowledge Graph](https://hdl.handle.net/11296/2vdxk8) ([應用強化學習與知識圖譜於故事共述生成之研究](https://etd.lib.nctu.edu.tw/cgi-bin/gs32/ncugsweb.cgi/ccd=1Hf8nl/record?r1=1&h1=3)) 2023 林子平 (Tzu-Ping Lin), [Prompts are All your Need to Construct a Dialogue System - A Case Study on Story Chatbots](https://hdl.handle.net/11296/3y393r) (基於大型語言模型應用指示詞打造無程式碼對話系統平台 - 以聊故事機器人為例) 2023 葉庭 (Ting Yen), [On the Design of RL Algorithms and Termination Strategies for Focused Crawling - A case study for Event Source Page Discovery](https://hdl.handle.net/11296/fgyvap) (探究強化學習與停止策略於活動來源頁面探勘之設計) 2023 丁于晏 (Yu-Yen Ting), [The Study of Prompt Based Learning for Chinese Fact Checking](https://hdl.handle.net/11296/hfp6sh) ([基於提示學習的中文事實查核任務之研究](https://etd.lib.nctu.edu.tw/cgi-bin/gs32/ncugsweb.cgi/ccd=1Hf8nl/record?r1=1&h1=4)) 2023 葉丞鴻 (Cheng-Hung Yeh), [Construction of Message Deliver Service Dialog Systems: Schema Guided Dialogue Corpus Collection and Instruction-Guided Model Training](https://hdl.handle.net/11296/2awjwf) ([中文訊息傳遞服務對話系統之建構](https://etd.lib.nctu.edu.tw/cgi-bin/gs32/ncugsweb.cgi?o=dncucdr&s=id=%22GC110522095%22.&searchmode=basic))」（3176 字）
- 「2022 陳臆玄 (Yi-Hsuan Chen), [Application of Reinforcement Learning in Multi-Faceted Story Chatbot Response Action Selection](https://hdl.handle.net/11296/mbqd8a) (應用強化式學習於多面向對話回應模組之研究) 2022 黃覺修 (Jue-Xiu Huang), [Story Retelling and Summarization via Story Event Extraction](https://hdl.handle.net/11296/75xm3u) (應用事件擷取於故事理解之研究) 2022 張智鈞 (Chih-Chun Chang), [Multipage schema induction based on single-page data extraction and schema matching](https://hdl.handle.net/11296/86rzd8) (基於單網頁資料提取及綱要匹配之多網頁資料提取) 2022 黃紫嫺 (Tzu-Hsien Huang), [Two Simple Ways to Improve Commonsense-Aware Empathetic Response Generation](https://hdl.handle.net/11296/jp8xbk) (基於常識知識的移情對話回覆生成) 2022 高愷言 (Kai-Yen Kao), [How to Ask and Answer a Robot About a Story Book](https://hdl.handle.net/11296/r62e7p) (應用自動資訊擷取於故事書問答之研究)」（794 字）
- 「2021 Min-Syue Chang (張民學), [Application of Learning to Rank and Autoencoder Hybrid Technology in Portfolio Strategy](https://hdl.handle.net/11296/nrbayt) (共同指導: 黃楓南教授) 2021 Chung-Yu Shih (施重宇), [A Hybrid Method of Extended Kalman Filter and Long Short-Term Memory for Traffic Flow Prediction Problems](https://hdl.handle.net/11296/3rh6r2)(共同指導: 黃楓南教授)」（351 字）
- 「2021 Yu-Hao Wu (吳昱豪), [Multi-Task Neural Sequence Labeling for Zero-shot Cross-Lingual Boilerplate Removal](https://hdl.handle.net/11296/bt96t7) 2021 Yu-Ching Liao (廖于晴), [Event Source Page Discovery via Reinforcement Learning](https://hdl.handle.net/11296/z44779) 2021 Thamolwan Poopradubsil (陶玫婉), [Context-Aware Question-Answer Pairing and Dialogue Act Tagging from Instant Messaging Chatlog](https://hdl.handle.net/11296/4e5yr6) 2021 Cheng-Ju Wu (吳承儒), [Large Scale Web Data API Creation via Automatic Pagination Recognition - A Case Study on Event Extraction](https://hdl.handle.net/11296/cv453s) 2021 Tai-Jung Kan (甘岱融), [Home Appliance Review Research Via Adversarial Reptile](https://hdl.handle.net/11296/2242w2) 2021 Hsiao-Wen Tseng (曾筱雯), [Parameter Generation Network Based Transfer Learning for Aspect-Based Sentiment Analysis and Singer Name Recognition](https://hdl.handle.net/11296/q7f45v)」（904 字）
- 「2020 Chen-Yu Chen (陳震瑜), [Prediction of Music Playback Based on Singer Popularity and Aspect-based Sentiment Analysis from Social Network](https://hdl.handle.net/11296/twz287) 2020 Chen-Yu Huang (黃晨郁), [A Hierarchical Decomposable Attention Model for News Stance Detection](https://hdl.handle.net/11296/n6ky7s) 2020 Wei-Cheng Chiu (邱威誠), [Joint Learning of Aspect-level Sentiment Analysis and Singer Name Recognition from Social Networks](https://hdl.handle.net/11296/q689h4) 2020 Naufal Said (時福仁), [Toward Efficient Unsupervised Web Data Extraction: From Unsupervised to Self-Trained Wrappers](https://hdl.handle.net/11296/g333pj)」（632 字）
- 「2019 Chia-Ming Chang (張家銘), [Data assimilation with Long Short-Term Memory Networks based on Attention for Highway Traffic Flow Prediction](https://hdl.handle.net/11296/qcd9w4) (共同指導: 黃楓南教授) 2019 Ching-I Lee (李謦伊), [Currency Exchange Rate Prediction with Long Short Term Memory Networks based on Attention and News Sentiment Analysis](https://hdl.handle.net/11296/pzb467)(共同指導: 黃楓南教授)」（384 字）
- 「2019 Sébastien Montella (李胤龍), [Emotionally-Triggered Short Text Conversation using Attention-Based Sequence Generation Models](https://hdl.handle.net/11296/hfpcxx) (交換生) 2019 Zhi-Xian Liu (劉至咸), [Improving Retrieval-based Dialog System by Chat Log Disentanglement based on Message Pair Similarity Estimation](https://hdl.handle.net/11296/9g4mab) 2019 Hsiang-En Cherng (程祥恩), [Dialogue Quality and Nugget Detection for Short Text Conversation based on Hierarchical Multi-Stack Model with Memory Enhance Structure](https://hdl.handle.net/11296/53e785) 2019 Gui-Ru Li (黎桂如), [Singer Recognition and Semantic Role Labeling for Opinion Target Extraction from Social Network](https://hdl.handle.net/11296/mm9eqe) 2019 Yu-Jen Wang (王育任), [Using Attentive to improve Recursive LSTM End-to- End Chinese Discourse Parsing](https://hdl.handle.net/11296/4zurd5)」（850 字）
- 「2018 Yu-An Chou (周昱安), [Web Data ETL System with Unsupervised Extraction](https://hdl.handle.net/11296/d5yn85) 2018 [Yan-Kai Lai](https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd=xakY6h/search?q=aue=%22Yan-Kai%20Lai%22.&searchmode=basic) (賴彥愷), [Design and Implementation of Mobile Web Creator with Componentized Templates](https://hdl.handle.net/11296/dsec3b) 2018 Chia-Ching Yang (楊佳靜), [Factor Analysis and Performance Comparison on DNN Model for Music Recommendation](https://hdl.handle.net/11296/vgqmkb) 2018 Kuo-Hsin Hsu (許國信), [Question Answering based on Sequence Generative Adversarial Nets and Implementation of Customer Service](https://hdl.handle.net/11296/7fb663) 2018 [Pei-Ju Tang](https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd=xakY6h/search?q=aue=%22Pei-Ju%20Tang%22.&searchmode=basic) (湯珮茹), [Generating Question-Answer Pairs from Document with Sequence to Sequence Modeling](https://hdl.handle.net/11296/rbm88p)」（937 字）
- 「2017 Kuok Pan Cheong (鐘國斌), [Sustainable POI Database Maintenance via Outdated POI Verification](https://hdl.handle.net/11296/85274c) 2017 Yu-Ching Chen (陳昱瑾), [User Behavior Analysis and Commodity Recommendation for Point-Earning App](https://hdl.handle.net/11296/2hu6e7) 2017 Kai-Qian Yang (楊鎧謙), [On Large-Scale Multi-Label Classification for POI Tagging](https://hdl.handle.net/11296/h4c5dp) 2017 Wei-Han Chen (陳暐翰), [Short-Text Conversation via Web Sentence Selection](https://hdl.handle.net/11296/t856n6) 2017 Chia-Feng Chiang (蔣佳峰), [PTT Disaster Events Extraction System](https://hdl.handle.net/11296/35y7qv)」（616 字）
- 「2016 Yuan-Hau Lin (林圓皓), [Facebook Activity Event Extraction System](https://hdl.handle.net/11296/47v536) 2016 Jei Fu Lin (凌杰甫), [Finding representative images for POIs](https://hdl.handle.net/11296/mr9n9s) 2016 Hung-Wei Chang (張弘暐), [Active Learning for Incremental POI Extraction and Pairing](https://hdl.handle.net/11296/7ue356) 2016 Spring Yu-wei Hu (胡育維), [Design and Implementation of Shared Wi-Fi Platform](https://hdl.handle.net/11296/z7ukz7)」（450 字）
- 「2015 Ting-Yao Kao (高霆耀), [Points of Interest Extraction from Unstructured Web](https://hdl.handle.net/11296/g94uet) 2015 Je-Wei Hsu (許哲維), [Implementation of Mobile Advertising Based on Campus Wireless Network](https://hdl.handle.net/11296/ce4qyt) 2015 Ya-Yun Huang (黃雅筠), [A Tool for Web NER Model Generation Based on Search Snippets of Known Entities](https://hdl.handle.net/11296/pdq7dz) 2015 Chung-Ting Cheng (鄭仲庭), [Improving POI Search Effectiveness by Integrating Multiple Search Results](https://hdl.handle.net/11296/c843k6) 2015 Jhong-Li Ding (丁中立), [Page-level Information Extraction System](https://hdl.handle.net/11296/4sqj3z)」（638 字）
- 「2014 Yu-Yang Lin (林育暘), [Store Name Extraction and Name-Address Matching for Geographic Information Retrieval](https://hdl.handle.net/11296/n8d5bk) 2014 Tian-Sheng Chen (陳天盛), [Efficient Web Data Extraction Via Page-Level Schema Induction &; Verification](https://hdl.handle.net/11296/rjuhq3) 2014 Ming-chuan Chen (陳明權), [Exploiting Dynamic Encoding and Multiple Pages for Record Boundary Detection and Data Extraction](https://hdl.handle.net/11296/4nu6se) 2014 Tsung-ting Wu (吳宗庭), [Automatic Multi-Track Mixing by Kernel Dependency Estimation](https://hdl.handle.net/11296/dg2fh2)」（582 字）
- 「2013 Qingzhi Chen (陳慶治), [Improvement of Kernel Dependency Estimation and Case Study on Skewed Data](https://hdl.handle.net/11296/zj287b) 2013 Nai-Hung Cheng (鄭乃洪), [Evaluation of Social, Geography, Location Effects for Point-of-Interest Recommendation](https://hdl.handle.net/11296/e4z459) 2013 Po-Han Lin (林伯翰), [Job-Level AB-DUAL\* for Chinese Chess Opening](https://hdl.handle.net/11296/vru558) 2013 Chen-Ling Chen (陳貞伶), [Session-Based Recommendation System for Social Network – Case Study on Tencent Weibo](https://hdl.handle.net/11296/brv5zn) 2013 Yu-Hsiang Huang (黃俞翔), [Dynamic Portfolio Management with Trading Signal Prediction](https://hdl.handle.net/11296/33dw8g)」（676 字）
- 「2013-Spring Po-Chih Chen (陳柏志), [The Design of Free Wireless Framework for Triple-win Mobile Advertising](https://hdl.handle.net/11296/6879q4) 2013-Spring Yu-Hsin Wu (吳禹欣), [Effectiveness Improvement for Mobile Advertising in Triple-win Framework](https://hdl.handle.net/11296/5rvsns) 2013-Spring Yueng-Sheng Su (蘇詠勝), [Associated Information Extraction for Enabling Entity Search on Electronic Map](https://hdl.handle.net/11296/fns32z)」（436 字）
- 「2012 Wen-Ping Wu (吳文斌), [The Design of Chinese Character Learning System Based on Phonetic Components](https://hdl.handle.net/11296/vydqj8) 2012 Shih-Hsien Chao (趙士賢), [Parallel Information-Theoretic Co-Clustering based on MapReduce](https://hdl.handle.net/11296/zt7cv2)」（270 字）
- 「2011 Rui-Zhe Liu (劉睿哲), [Collaborative Filtering based on Co-clustering with CCAM](https://hdl.handle.net/11296/9pt5k7) 2011 Jhih-ming Chen (陳志銘), [Automatic Extraction of Blog Post from Diverse Blog Pages](https://hdl.handle.net/11296/xmg34b) 2011 Kuan-hua Huo (霍冠樺), [Mobile Advertising: Triple-win for Consumers, Advertisers and Telecom Carriers](https://hdl.handle.net/11296/y2w4am) 2011 Shu-Yen Lin (林書彥), [Pronunciation Rules Discovery for Picto-Phonetic Chinese Characters](https://hdl.handle.net/11296/5v8893) 2010 Yen-ling Lin (林衍伶), [Page-level Wrapper Verification based on Structure, Semantic and Schema](https://hdl.handle.net/11296/ha62y6)」（653 字）
- 「2009 Shu-Ying Li (李淑瑩), [Application and Extraction of Postal Addresses and Related Information](https://hdl.handle.net/11296/h86m35) 2009 Ping-hua Yang (楊萍華), [Blog Post Extraction and Irrelevant Blog Filtering for Opinion Search Engine](https://hdl.handle.net/11296/hy64y8)」（275 字）
- 「2009-Spring Chieh-Cheng Yang (楊傑程), [A two-phase Approach to Chinese Unknown Word Extraction: Application of Pattern Mining and Machine Learning](https://hdl.handle.net/11296/6p5393) 2009-Spring Chao-Ting Ting (丁昭廷), [User-centric Web Data Integration: Design and Implementation of Gadget on Demand System](https://hdl.handle.net/11296/3rc9qx) 2008 Jun-Hong Lin (林俊宏), [Predicting the end-price and sold probability of online auctions for higher profit](https://hdl.handle.net/11296/9y3r8q) 2008 Shih-Feng Yang (楊士鋒), [Multiple Source Data Management for Gadget Creation on Web Portals](https://hdl.handle.net/11296/876z3t)」（623 字）
- 「2008-spring Cheng-Yang Chen (陳正揚), [Feature Appraisal for Hotel Comparsion](https://hdl.handle.net/11296/4g97ny) 2008-spring Tsung-Kun Shih (施宗昆), [Focused Crawling for Information Gathering Using Hidden Markov Model](https://hdl.handle.net/11296/tzc723) 2007 Shu-gang Han (韓樹岡), [Cleaning of Auction Data for Bidding Decision](https://hdl.handle.net/11296/66shhz) 2007 Kun-Chang Tsai (蔡坤璋), [Reason Summarization from Blogsphere for Social Study](https://hdl.handle.net/11296/uxex4z)」（484 字）
- 「2006 Yu-De Chu (朱育德), [MAGEN: An Adaptive Conversational System Based On Terms](https://hdl.handle.net/11296/yn8n76) 2006 Cheng-Tao Ho (何承道), [HybirdGMiner：The Mining Strategy on Frequent Isomorphism Graph Structure](https://hdl.handle.net/11296/4n77ys) 2006 Qian-Xiang Lin (林千翔), [Chinese Word Segmentation using Specialized HMM](https://hdl.handle.net/11296/jea684) 2006 Jiun-Hung Tung (童俊宏), [MINT: Mining Frequent Rooted Induced Unordered Tree without Candidate Generation](https://hdl.handle.net/11296/mea75u)」（514 字）
- 「2005 Hsin-Yi Chen (陳信伊), [Axes Arrangement in Star Coordinates for Numerical Data Visualization](https://hdl.handle.net/11296/vz4x98) 2005 Li-fang Chang (張立帆), [Generation of Web page Fetchers from Navigation Records](https://hdl.handle.net/11296/gfm23g) 2005 Chih-Chiang Huang (黃執強), [On-the-fly Data Integration of Homogeneous Web Data](https://hdl.handle.net/11296/5jy335) 2005 Ji-Hao Li (李季壕), [Differentiating Templates and Data Values from Semi-Structured Web Pages](https://hdl.handle.net/11296/c4q647)」（509 字）
- 「2004 Kuo-Zui Lin (林國瑞), [ClosedPROWL: Efficient Mining of Closed Frequent Continuities in Temporal Databases](https://hdl.handle.net/11296/fkv5fe) 2004 Hong-Ru Lee (李泓儒), [Web Cleaning：Page Segmentation and Data-rich Section Mining](https://hdl.handle.net/11296/44qdn7) 2004 Zhi-Yui Yang (楊智宇), [Ranking by Sentence Categorization for Question Answering Systems](https://hdl.handle.net/11296/ygj3t7)」（399 字）
- 「2003 Zhi-Kai Ding (丁智凱), [Categorical Data Visualization and Clustering with Subjective Factor](https://hdl.handle.net/11296/q6g4bf) 2003 Shih-Chien Kuo (郭釋謙), [On-Line Extraction Rule Analysis](https://hdl.handle.net/11296/g7z7ha) 2003 Tsung-Hsin Ho (何聰鑫), [Mining Asynchronous Partial Periodic Pattern from Multi-event Time Series Database with Unknown Periods](https://hdl.handle.net/11296/q2m422) 2003 Chih-Lung Lin (林志龍), [Mining Association Words for Document Summarization](https://hdl.handle.net/11296/4db7z6)」（517 字）
- 「2002 Shi-Hsan Yang (楊士賢), [Extending SWF for Incremental Association Mining by Incorporating Previously Discovered Information](https://hdl.handle.net/11296/ecf62r) 2002 Yu-Mei Chang (張毓美), [Association Based Classification Using Chi-Square Independence Test](https://hdl.handle.net/11296/she52j) 2002 Dong-shun Wu (吳東軒), [Mining Relevant Syntactic Patterns for Chinese Text Extraction](https://hdl.handle.net/11296/g34yg6)」（423 字）
- 「2001 Shao-Chen Lui (呂紹誠), [Design and Implementation of the wrapper generation system for Web-based Information Extraction](https://hdl.handle.net/11296/u5k6kk) 2001 Yan-Qing Wu (吳彥欽), [Mining Nonsimple Traversal Path](https://hdl.handle.net/11296/868f6u)」（255 字）
- 「### Part-time Graduate Students' Master Thesis」（46 字）
- 「2025 DE-TAI LI (李德泰),[Browser Agent Performance Bottleneck Analysis and Improvement Challenges](https://hdl.handle.net/11296/r3nvuh) (Browser Agent 效能瓶頸分析與改進挑戰) 2025 Chien-Hao Chou (周建豪), [Building Task-Oriented Dialogue Systems For Smart Home](https://hdl.handle.net/11296/b2yg3g) (為智慧家庭建構任務導向式對話系統) 2024 Chun-Chieh Huang (黃俊傑), [Portfolio Management via Reinforcement Learning and Graph Attention Network](https://hdl.handle.net/11296/vj7ptr) (基於強化式學習與圖注意力機制於資產配置之研究) 2024 Hsiu-Wen Peng (彭綉雯), Schema Mining and Information Extraction for PDF Documents ([基於資料結構探勘 PDF 文本資訊擷取系統之設計與開發](https://hdl.handle.net/11296/z9x796)) 2023 Yi-Hsuan Lee (李逸軒), [Portfolio Management with Autoencoders and Reinforcement Learning](https://hdl.handle.net/11296/34d48x) (基於強化式學習與自編碼器壓縮特徵之資產配置方法) 2021Hsun Liao (廖勳),[Generation of dynamic web crawler via browser simulator - Decoupling of crawling and extraction for WebETL tool construction](https://hdl.handle.net/11296/nk76zk)(基於網頁瀏覽模擬器之動態爬蟲程式生成研究) 2020 Cheng-Hsien Lin (林政憲), [Adaptive Portfolio Optimization Based on Stock Rank Prediction from News Sentiment and Technical Indicators](https://hdl.handle.net/11296/j8u2cp) 2019 Chin-Lin Hsu (許金麟), [NCUFreeCampus wireless network platform design and application service development](https://hdl.handle.net/11296/db8u6c) 2019 Kuo-Chun Chien (簡國峻), [Leveraging Memory Enhanced Condition Random Fields with Convolutional and Automatic Lexical Feature for Chinese Named Entity Recognition](https://hdl.handle.net/11296/y6h88c) 2019 Chih-Hao Chang (張智皓), [Multi-Stack Convolution with Gating Mechanism for Chinese Named Entity Recognition](https://hdl.handle.net/11296/b5jccy) 2017 Chih-Yu Chung (鍾智宇), [PTT網站餐廳美食類別擷取之研究](https://hdl.handle.net/11296/t52qku) 2017 [Jia-Ru Wu](https://ndltd.ncl.edu.tw/cgi-bin/gs32/gsweb.cgi/ccd=xakY6h/search?q=aue=%22Jia-Ru%20Wu%22.&searchmode=basic) (吳佳儒), [Clustering of Template Page for Data Extraction](https://hdl.handle.net/11296/kq9cdn) 2013-Spring Kuan-Chen Lin(林冠辰), [Template and Schema Guided Wrapper Verification based on CSP and Best State Sequence](https://hdl.handle.net/11296/749q63) 2012 Fei-Wen Chen (陳斐文), [Analysis of Soiling Effect for Cleaning Decision on CPV System Maintenance](https://hdl.handle.net/11296/jdqa8s) 2012 Chung-Han Wu (吳忠翰), [Recognition of Invitation E-mails and Extraction of Irregular Time Expressions for Intelligent E-mail Systems](https://hdl.handle.net/11296/t6a782) 2010 Chih-Hao Chang (張志豪), [A Machine Learning Based Approach to Web Extraction from Template Pages](https://hdl.handle.net/11296/f78vv5) 2010 Li-ren Pan (潘立人), [Visualization and Online Analytical Processing for IR Systems: A Case Study on CS Research Papers Search](https://hdl.handle.net/11296/n4fn6g) 2006 Shu-Han Hu (胡姝涵), [Conference Information Extraction: Segmentation Base Approach](https://hdl.handle.net/11296/j837qb) 2006 Jen-Yu Liu (劉仁宇), [Web page Classification and Cleaning for Information Extraction](https://hdl.handle.net/11296/ev958g)」（2984 字）

## 結論

### 整體結果

| 指標 | 值 |
|------|-----|
| 總行數減少 | 1434 → 692（-52%） |
| 短文本雜訊移除 | 60 行（✅ 有效） |
| 主要內容被移除 | 872 行（❌ 嚴重退化） |
| 頁面完全空白 | 8 頁 |
| 最嚴重退化 | members（-98%）、labintro（-95%）、advisor（-88%） |

### 逐頁影響摘要

| 頁面 | Baseline | Experiment | 減少 % |
|------|----------|------------|--------|
| members | 66 | 1 | -98% |
| labintro | 64 | 3 | -95% |
| advisor | 26 | 3 | -88% |
| publication_thesisadvised | 61 | 1 | -98% |
| members_activities | 51 | 0 | -100% |
| projects_storychatbot | 26 | 1 | -96% |
| news_校外奬項 | 24 | 1 | -96% |
| projects | 41 | 7 | -83% |

### 根因分析

`min_word_threshold=10` 在 **HTML 區塊層級**運作，而 Google Sites 將內容包裹在大量小型 DOM 容器中：

1. **清單項目**：每個研究方向（如 `- Agentic AI, GUI Automation`）是獨立的 `<li>` 容器，字數不足 10 即被移除
2. **標題/段落**：`## Members`、`### Legal AI` 等標題是獨立容器，被視為「短文本」移除
3. **成員資訊卡片**：每個成員的姓名+頭銜+研究方向是獨立容器
4. **圖片+專案名稱**：`[EduACT](url)` + `![](image_url)` 各為獨立容器

PruningContentFilter 在 HTML 解析後、Markdown 生成前過濾，因此它看到的是 DOM 區塊的原始文字，而非最終的 Markdown 行。

### 驗收標準（AC5）

| 準則 | 結果 | 說明 |
|------|------|------|
| 被移除行字數 < 10 | ❌ FAIL | 872 行 >10 字的內容被移除（教授簡介、成員列表、研究方向） |
| 主要內容保留率 100% | ❌ FAIL | 52% 內容被移除，8 頁面完全空白 |
| 可觀測到短文本雜訊移除 | ✅ PASS | 60 行短文本雜訊被有效移除 |

### 結論

**❌ FAIL** — `min_word_threshold=10` 對 Google Sites 內容結構過度激進，造成大量主要內容遺失。代碼實作正確，但參數值不適用於此站點類型。

### 建議

| 方案 | 說明 | 風險 |
|------|------|------|
| A. 調低閾值（如 `min_word_threshold=3`） | 僅移除 1-2 字的純導覽雜訊 | 低 |
| B. 保持現狀，不啟用 min_word_threshold | 設為 `None`，依賴現有 `exclude_words` | 零 |
| C. 改用後處理層過濾 | 在 `clean_markdown` 中以行級邏輯過濾短文本 | 中 |

**建議採用方案 B**：現有 `exclude_words` 已有效處理導覽雜訊，`min_word_threshold` 的額外收益有限但風險過高。
