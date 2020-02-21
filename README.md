## ptt-crawler

1. clone or download the project  
`git clone https://github.com/nunuku951753/ptt-crawler.git `

2. 建置image  
`$ docker build -t ptt-image . ` 

3. 啟用並進入container  
`$ docker run -p 80:80 -it [image id] /bin/bash `

4. 於container內執行程式  
主程式： PTTMain.py  
參數：  
    * 建立DB：  
      
       `# python PTTMain.py --newDB `  
         
       _ps. 若目錄下無 ptt.db會建立新的資料庫，已存在則不會覆蓋_  
    * 指定看板：  
      
        * 抓取所有看板  
        `# python PTTMain.py --boards all `  
          
        * 抓取指定看板  
        `# python PTTMain.py --boards Gossiping `  
          
        * 抓取多個指定看板(空白間隔)  
        `# python PTTMain.py --boards Gossiping Stock `  
          
        _ps. 以上指令接預設 **page=last**_  
    * 指定頁數  
      
        * 抓取最新頁面  
        `# python PTTMain.py --boards Gossiping --page last `  
          
          _ps. 以上指令等同於`# python PTTMain.py --boards Gossiping `_
        
        * 指定頁數區間  
        `# python PTTMain.py --boards Gossiping --page 1 10 `  
          
5. 將檔案複製到本機          
  `$ docker cp [container id]:/docker_api/ptt.db "D:/Docker Toolbox/PTT/" `  
  
6. 查看DB  
請使用此執行檔開啟ptt.db  
.\sqlitebrowser_200_b1_win\SQLite Database Browser 2.0 b1.exe
