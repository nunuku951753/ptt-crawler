#!/usr/bin/env python
# coding: utf-8

# In[10]:


import calendar
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from SQLiteBase import SQLiteBase as sql

class PTTCrawler():
    
    def __init__(self):
        self.home_url = "https://www.ptt.cc"
        # 通過18禁警告
        self.header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36",
            "cookie":"over18=1"
        }
        
        self.sqlBase = sql()
    
    # 擷取文章內文並過濾空白行
    def contentProcess(self, content):
        lines = content.replace("'", "''").split("\n")

        head = ["作者", "標題", "時間"]
        end = ["※ 發信站:", "※ 編輯:"]
        end_not = [": ※ 發信站:", ": ※ 編輯:"]
        content_p=""
        for line in lines:
            if all( h in line for h in head) or            line.replace("\n", "").strip() == "":
                continue
            elif any( e in line for e in end) and              all( n not in line for n in end_not):
                break
            else:
                content_p += line + "\n"
        return content_p

    # 擷取文章相關欄位資訊
    def getArticleData(self, article_page):
        data = {}

        tags = article_page.findAll("span", class_="article-meta-tag")
        values = article_page.findAll("span", class_="article-meta-value")
        for i in range(0, len(tags)):
            value = values[i].text
            tag = tags[i].text

            if tag=="作者":
                author_sp = value.replace("'", "''").split("(")
                data["authorId"] = author_sp[0].strip()
                data["authorName"] = author_sp[1].replace(")", "").strip()
            if tag=="標題":
                if "]" in value:
                    data["title"] = value.split("]")[1].replace("'", "''").strip()
                else:
                    data["title"] = value.replace("'", "''").strip()
            if tag=="時間":
                data["publishedTime"] = self.getTime(value.strip(), "%a %b %d %H:%M:%S %Y", "time")
                data["publishedDate"] = self.getTime(value.strip(), "%a %b %d %H:%M:%S %Y")
        return data

    # 擷取文章推文資訊，判斷斷句，將依同時間同推文者合併推文
    def getCommentData(self, article_page, publishedDate):
        comment_dict={}
        zyear = int(datetime.strftime(publishedDate, '%Y'))  # 貼文年度
        zmonth = int(datetime.strftime(publishedDate, '%m')) # 貼文月份

        pushs = article_page.findAll("div", class_="push")
        for push in pushs:
            if "push-userid" not in str(push):
                continue # 跳過非正常推文

            comment_data={}
            comment_data["commentId"] = push.find("span", class_="f3 hl push-userid").text.replace("'", "''").strip()
            comment_data["commentContent"] = push.find("span", class_="f3 push-content").text                                        .replace(":", "").replace("'", "''").strip()
            ipdatetime = push.find("span", class_="push-ipdatetime").text.strip()
            date_str = ipdatetime[ipdatetime.index("/")-2 : ipdatetime.index("/")+3]
            time_str=""
            if ":" in ipdatetime: # 判斷有沒有時間
                time_str = ipdatetime[ipdatetime.index(":")-2 : ipdatetime.index(":")+3]
            else:
                time_str = "00:00" # 無時間預設 00:00
            
            # 因推文沒提供年度，需推算年度
            mon = int(date_str.split("/")[0]) # 這則推文的月份
            if zmonth > mon: # 若本文月份 > 推文月份，則年度加一
                zyear += 1
            zmonth = mon # 更新月份基準
            
            commentTime_str = str(zyear)+"/"+date_str+" "+time_str
            comment_data["commentTime"] = self.getTime(commentTime_str, "%Y/%m/%d %H:%M", "time")

            key = comment_data["commentId"]+comment_data["commentTime"]
            if key in comment_dict.keys():
                comment_dict[key]["commentContent"] = comment_dict[key]["commentContent"] +                                                   comment_data["commentContent"]
            else:
                comment_dict[key] = comment_data
        return comment_dict
    
    def getPageList(self, board, page):
        pageList=[]
        if page=="last":
            url = "https://www.ptt.cc/bbs/{}/index.html".format(board)
            last_page = BeautifulSoup(requests.get(url, headers=self.header).text, 'html.parser')
            if "Connection timed out" in str(last_page):
                print("※ 目前網頁無法連線，請確認!")
                return pageList
            group = last_page.find("div", class_="btn-group btn-group-paging")
            hrefs = group.findAll("a", class_="btn wide")
            for h in hrefs:
                if "上頁" in h.text:
                    href = h["href"].split(".")[0]
                    p = int(href[href.index("index")+5:])+1
                    pageList.append(p)
        else:
            ps = list(map(int, page))
            for p in range(ps[0], ps[1]+1):
                pageList.append(p)
        return pageList

    # 日期轉timestamp
    def getTime(self, zdate, date_format, ztype=""):
        try:
            time_format = datetime.strptime(zdate, date_format)
            if ztype=="time":
                ztime = calendar.timegm(time_format.timetuple())
                time_format = "{:0<13d}".format(ztime) # 不滿13位後面補0
        except:
            time_format = ""
            ztime = ""
            print("日期轉換錯誤：", zdate)
        return time_format

    def pageSleep(self, s):
        print("※ 避免資安問題，休息%d秒後繼續" % s)
        i = 0
        while i != s:
            i += 1
            time.sleep(1) # 休眠1秒
            print(".")

    # 看板資訊匯入
    def insertBoardClass(self):
        boardSQL="insert or ignore into board_class (board_id, board_class, board_link, createdTime)               values('{}','{}','{}',CURRENT_TIMESTAMP)" 
        appendSQL_board=", ('{}','{}','{}',CURRENT_TIMESTAMP)"

        url = "https://www.ptt.cc/bbs/index.html"
        response = requests.get(url)
        source = BeautifulSoup(response.text, 'html.parser')
        boards = source.findAll("div", class_="b-ent")

        i=0
        boardSQL2=""
        for board in boards:
            board_class = board.find("div", class_="board-class").text.replace("'", "''").strip()
            board_href = board.find("a", class_="board")["href"].replace("'", "''").strip()
            board_id = board_href.split("/")[2].replace("'", "''").strip()
            board_link = self.home_url + board_href

            nextSQL=""
            if i==0:
                nextSQL = boardSQL
                i += 1
            else:
                nextSQL = appendSQL_board

            boardSQL2 += nextSQL.format(board_id, board_class, board_link)

        sql.insertData(self.sqlBase, boardSQL2)

    def insertArticleInfo(self, boards, pages):
        # 文章及推文匯入
        articleSQL="insert into article (canonicalUrl, authorId, authorName, title, publishedTime, content,            createdTime, updateTime)values('{}','{}','{}','{}','{}','{}',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)" 
        commentSQL="insert into comment (canonicalUrl, commentId, commentContent, commentTime,            createdTime, updateTime)values('{}','{}','{}','{}',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)" 
        appendSQL_comment=", ('{}','{}','{}','{}',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)"
        caughtSQL="insert or ignore into caught (board_id, page, publishedDate, link,            createdTime)values('{}','{}','{}','{}',CURRENT_TIMESTAMP)"

        # 資料庫已抓過的canonicalUrl
        canonicalUrl_old = str(sql.selectData(self.sqlBase, " select distinct canonicalUrl from article "))

        url_tmp = "https://www.ptt.cc/bbs/{}/index{}.html"
        for board in boards: # 看板迴圈
            caughtSQL2=""
            first_date=""
            pageList = self.getPageList(board, pages)
            for page in pageList: # 頁面迴圈
                link = url_tmp.format(board, page)
                print("看板頁面: ", link)

                article_page = BeautifulSoup(requests.get(link, headers=self.header).text, 'html.parser')
                if "Connection timed out" in str(article_page):
                    print("※ 目前網頁無法連線，請確認!")
                    break
                articles = article_page.findAll("div", class_="r-ent")
                j=0
                for article in articles:
                    title_div = article.find("div", class_="title").find("a")
                    if title_div==None:
                        print("※ 該版面已被刪除，跳過不處理!")
                        continue
                    
                    canonicalUrl = self.home_url + title_div["href"]
                    print("目前頁面: ", canonicalUrl)

                    if canonicalUrl in canonicalUrl_old:
                        continue # 該頁面已抓過不重抓

                    article_page = BeautifulSoup(requests.get(canonicalUrl, headers=self.header).text, 'html.parser')

        # ----------------------------------- article info ---------------------------------------------
                    content = article_page.find("div", class_="bbs-screen bbs-content").text
                    content_p = self.contentProcess(content) # 擷取文章內文並過濾空白行
                    article_dict = self.getArticleData(article_page) # 擷取文章相關欄位資訊
                    if article_dict=={}:
                        print("※ 非一般版面，跳過不處理! 網址:", canonicalUrl)
                        continue

                    articleSQL2 = articleSQL.format(canonicalUrl, 
                                                    article_dict["authorId"], 
                                                    article_dict["authorName"], 
                                                    article_dict["title"], 
                                                    article_dict["publishedTime"], content_p)
                    if j==0:
                        first_date = article_dict['publishedDate']
                        j += 1

        # ----------------------------------- comment info ---------------------------------------------
                    comment_dict = self.getCommentData(article_page, article_dict["publishedDate"]) # 擷取文章推文資訊，將依同時間同推文者合併推文

                    i=0
                    commentSQL2=""
                    for key in comment_dict:
                        comment = comment_dict[key]
                        nextSQL=""
                        if i==0:
                            nextSQL = commentSQL             
                            i += 1
                        else:
                            nextSQL = appendSQL_comment

                        commentSQL2 += nextSQL.format(canonicalUrl, 
                                                      comment["commentId"], 
                                                      comment["commentContent"], 
                                                      comment["commentTime"])
                    # 匯入資料庫
                    sql.insertData(self.sqlBase, articleSQL2)
                    sql.insertData(self.sqlBase, commentSQL2)
                    # articles loop end

        # ----------------------------------- caught info ---------------------------------------------
                if first_date != "":
                    publishedDate = datetime.strftime(first_date, '%Y-%m-%d')
                    caughtSQL2 = caughtSQL.format(board, page, publishedDate, link)
                    sql.insertData(self.sqlBase, caughtSQL2)

                self.pageSleep(5) # sleep
                # page loop end

    
    