#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sqlite3

class SQLiteBase():
        
    # 建立資料表
    def createTable(self):
        conn = sqlite3.connect("ptt.db") # 建立資料庫連線
        cursor = conn.cursor() # 建立 cursor 物件

        # 建立 article 資料表
        articleSQL = "CREATE TABLE IF NOT EXISTS article('canonicalUrl' TEXT, 'authorId' TEXT, 'authorName' TEXT, 'title' TEXT, 'publishedTime' TEXT, 'content' TEXT, 'createdTime' DATETIME, 'updateTime' DATETIME, PRIMARY KEY (canonicalUrl))"
        cursor.execute(articleSQL)
        conn.commit() 

        # 建立 comment 資料表
        commentSQL = "CREATE TABLE IF NOT EXISTS comment('canonicalUrl' TEXT, 'commentId' TEXT, 'commentContent' TEXT, 'commentTime' TEXT, 'createdTime' DATETIME, 'updateTime' DATETIME, PRIMARY KEY (canonicalUrl, commentId, commentTime))"
        cursor.execute(commentSQL)
        conn.commit() 

        # 建立 board_class 資料表
        commentSQL = "CREATE TABLE IF NOT EXISTS board_class('board_id' TEXT, 'board_class' TEXT, 'board_link' TEXT, 'createdTime' DATETIME, PRIMARY KEY (board_id))"
        cursor.execute(commentSQL)
        conn.commit() 

        # 建立 caught 資料表
        commentSQL = "CREATE TABLE IF NOT EXISTS caught('board_id' TEXT, 'page' INTEGER, 'publishedDate' TEXT, 'link' TEXT, 'createdTime' DATETIME, PRIMARY KEY (board_id, page))"
        cursor.execute(commentSQL)
        conn.commit() 
        conn.close()  # 關閉資料庫連線
        print("Create Tables Successed!")

    # 匯入資料庫
    def insertData(self, sql):
        conn = sqlite3.connect("ptt.db") # 建立資料庫連線
        cursor = conn.cursor() # 建立 cursor 物件
        cursor.execute(sql)
        conn.commit() 
        conn.close()  # 關閉資料庫連線

    # 查詢資料庫
    def selectData(self, sql):
        conn = sqlite3.connect("ptt.db") # 建立資料庫連線
        cursor = conn.execute(sql)
        objs = []
        for obj in cursor:
            objs.append(obj)
        conn.close()  # 關閉資料庫連線
        return objs
