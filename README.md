# ptt-crawler

### PTT 網頁爬蟲，使用環境 python3.7.3, SQLite

### 資料表介紹
Table: article - 文章相關資訊  
![GITHUB](https://imgur.com/WFstI4B.png "article")  
  
Table: comment - 推文相關資訊  
![GITHUB](https://imgur.com/JXRPKW8.png "comment")  

Table: board_class - 看板資訊  
![GITHUB](https://imgur.com/JoMI9CH.png "board class")

Table: caught - 已擷取過的網址紀錄
![GITHUB](https://imgur.com/fzv5L7L.png "caught")  
  
* 資料擷取前檢查 article資料表是否已含有該文章之網址(canonicalUrl)，若已存在則跳過不重複抓取
  
* 假設機器因不可預期狀況停機,可藉由 caught資料表查詢未擷取成功之資料頁數，以利後續補抓缺漏
  
* 為避免快速擷取頁面而造成的網路資安問題，目前設計為看板每頁擷取後皆會間隔5秒再繼續擷取
* 因暫無找到指定發佈日期的方法，目前替代方案為運用 caught資料表紀錄每頁第一筆文章之日期(publishedDate)，  
  藉此查出大概日期區間所對應的頁數  

### 安裝步驟
1. clone or download the project  
`git clone https://github.com/nunuku951753/ptt-crawler.git `

2. 建置image  
`$ docker build -t ptt-image . ` 

3. 啟用並進入container  
`$ docker run -p 80:80 -it [image id] /bin/bash `

4. 於container內執行程式  
主程式： PTTMain.py  
參數：  
![GITHUB](https://imgur.com/idpgrQh.png "article")
    * 建立DB：  
      
       `# python PTTMain.py --newDB `  
         
       _ps. 若目錄下無 ptt.db會建立新的資料庫，已存在則不會覆蓋_  
    * 指定看板：  
      
        * 擷取所有看板  
        `# python PTTMain.py --boards all `  
          
        * 擷取指定看板  
        `# python PTTMain.py --boards Gossiping `  
          
        * 擷取多個指定看板(空白間隔)  
        `# python PTTMain.py --boards Gossiping Stock `  
          
        _ps. 以上指令接預設 **page=last**_  
    * 指定頁數  
      
        * 擷取最新頁面  
        `# python PTTMain.py --boards Gossiping --page last `  
          
          _ps. 以上指令等同於`# python PTTMain.py --boards Gossiping `_
        
        * 指定頁數區間  
        `# python PTTMain.py --boards Gossiping --page 1 10 `  
          
5. 將檔案複製到本機          
  `$ docker cp [container id]:/docker_api/ptt.db "D:/Docker Toolbox/PTT/" `  
  
6. 查看DB  
請使用此執行檔開啟ptt.db  
.\sqlitebrowser_200_b1_win\SQLite Database Browser 2.0 b1.exe
  

### ※ Notice
      1. 因推文未提供年度，將依照文章的年度往下推算
      2. 若推文日期無提供時分秒，將預設 00:00
      3. 若同篇文章內同人同時間推文，判斷為自動斷句，將合併推文
