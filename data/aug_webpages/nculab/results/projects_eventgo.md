# EventGo!(2020-2023)

## Team member:

林圓皓、吳昱豪、吳承儒、廖于晴、程祥恩、黃悅文、謝献爵

## Abstract

Finding activities to attend has been the prelude in our leisure time. Meanwhile, people also make use of social network such as Facebook or blogs to post event news. Unfortunately, the search interface of Facebook event pages only covers official events. In this case, WIDM lab developed a better tool for event search, called EventGO! The backend of EventGO! contains a web crawler, two IE (information extraction) models for activity name and location recognition as well as a search engine for event search. The frontend is an android application to present the search result in list or map view. The web crawler collects information from both Facebook and Google search engine. The former make use of Facebook Graph API to monitor 230K fan pages in Taiwan to collect posts, while the later query Google search engine with event relevant keywords such as exhibition, concert, workshop, etc. to gather web pages. Second, the IE models recognize activity name and location with pre-trained model and extract start and end date via regular expression. Note that the performance of location recognition is enhanced with 2.45 million FB places to locate the GPS position. Finally, these structured data would be stored into a Solr database for the IR search module. Note that FB event API also contribute one fourth of the events in Solr database. EventGo! android application provides a conversational search to avoid manual setting of location and temporal constraint, and present the search result from three different views: map, calendar or list. Last but not least, users can add a event as well as its details to their calendar in just a single click. EventGO!, an brilliant way to search for events.

## Demo

[Web Demonstration](https://eventgo.widm.csie.ncu.edu.tw/#/) [Download (Android)](https://play.google.com/store/apps/details?id=com.widmlab.eventgo&hl=zh_TW) [![https://play.google.com/store/apps/details?id=com.widmlab.eventgo&hl=zh_TW](https://sites.google.com/sitesv-images-rt/AMxu72tkpqE4NESV8Sawi6iUGYmlnEL34qD4SEGBLm3NE6SaDh9OxlTIxQ5Dnl4Wtg1V3Pf6BmRszYA5lOCVMt8flOE0is4yjIIRiWR7nlWVW5Th2U3mS-QMnlJdreVkmPNCUkMB3f9E3USqqBfRk5OjzCtPB_wuGT9A0fMKqEBt1oWrsBA51PpsCr0_07-1B8zLfZjwj2Of8ris=w1280)
](https://play.google.com/store/apps/details?id=com.widmlab.eventgo&hl=zh_TW)

## Publication

- Yuan-Hao Lin; Chia-Hui Chang; Hsiu-Min Chuang: [Fine-Grained Meetup Events Extraction Through Context-Aware Event Argument Positioning and Recognition](https://link.springer.com/article/10.1007/s44196-024-00697-0), International Journal of Computational Intelligence Systems 17, 296 2024. [https://doi.org/10.1007/s44196-024-00697-0](https://doi.org/10.1007/s44196-024-00697-0)
- Yuan-Hao Lin; Chia-Hui Chang; Hsiu-Min Chuang; Xiang-Shun Lin; Ting Yeh; Min-Jhao Hong: [Cost-Effective Event Mining on the Web via Event Source Page Discovery and Data API Construction](https://ieeexplore.ieee.org/document/10638638/authors#authors),[IEEE Access 12](https://dblp.org/db/journals/access/access12.html#LinCCLYH24): 115981-115993 (19 August 2024)DOI: [10.1109/ACCESS.2024.3445448](https://doi.org/10.1109/ACCESS.2024.3445448)
- Chia-Hui Chang, Yu-Ching Liao and Ting Yeh:[Event Source Page Discovery via Policy-based RL with Multi-Task Neural Sequence Model](https://link.springer.com/chapter/10.1007/978-3-031-20891-1_42), [WISE 2022](https://wise2022.sigappfr.org/).
- Chia-Hui Chang, Cheng-Ju Wu and Tzu-Ping Lin:[Automatic Web Data API Creation via Cross-Lingual Neural Pagination Recognition](https://link.springer.com/chapter/10.1007/978-3-031-09917-5_8), ICWE 2022.
- Yuan-Hao Lin, Chia-Hui Chang, Hsiu-Min Chuang: [EventGo! Mining Events through Semi-Supervised Event Title Recognition and Pattern-based Venue/Date Couplin](https://www.airitilibrary.com/Publication/alDetailedMesh?DocID=10162364-202305-202212270003-202212270003-655-670)g, Journal of Information Science and Engineering, May 2023 (Accepted).
- Yu-Hao Wu and Chia-Hui Chang: [Multi-Task Neural Sequence Labeling for Zero-Shot Cross-Language Boilerplate Removal](https://dl.acm.org/doi/10.1145/3486622.3493938). Web Intelligence 2021.
- Chia-Hui Chang,[Yuan-Hao Lin](https://dblp.uni-trier.de/pid/193/3553.html),[Hsiu-Min Chuang](https://dblp.uni-trier.de/pid/150/5799.html): [EventGo! Exploring Event Dynamics from Social-Media Posts](https://ieeexplore.ieee.org/document/9359024).[ICS 2020](https://dblp.uni-trier.de/db/conf/intcompsymp/ics2020.html#ChangLC20): 548-552
- [Yuan-Hao Lin](https://dblp.uni-trier.de/pid/193/3553.html), Chia-Hui Chang,[Hsiu-Min Chuang](https://dblp.uni-trier.de/pid/150/5799.html): [Mining Events through Activity Title Extraction and Venue Coupling](https://ieeexplore.ieee.org/document/9382472).[TAAI 2020](https://dblp.uni-trier.de/db/conf/taai/taai2020.html#LinCC20): 136-141
- Y. H. Lin, C.-H. Chang, “[Facebook Activity Event Extraction System](https://aclanthology.org/O16-1022.pdf),” Proceedings of the 28th Conference on Computational Linguistics and Speech Processing, pp. 229–243, 2016.

## Related Technologies

1. Named Entity Recognition: Auto labeling activity name: ([Data](https://goo.gl/X2QLr6))
1. Temporal Tagger Module - Heideltime

- J. Strötgen, M. Gertz, “Heideltime: High quality rule-based extraction and normalization of temporal expressions,” Proceedings of the 5th International Workshop on Semantic Evaluation, 2010.