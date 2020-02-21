#!/usr/bin/env python
# coding: utf-8

import argparse
from SQLiteBase import SQLiteBase as sql
from PTTCrawler import PTTCrawler

# 參數
parser = argparse.ArgumentParser(description='Code for PTTCrawler.')
parser.add_argument('--newDB', help='Please input the page range. ex: --page 1 10', action='store_true')
parser.add_argument('--boards', nargs='+', help='Please input the name of the board. ex: --boards Gossiping', default='')
parser.add_argument('--page', nargs='+', help='Please input the page range. ex: --page 1 10', default='last')
args = parser.parse_args()

crawBase = PTTCrawler() # 建立爬蟲物件

if args.newDB:
    sql.createTable(sql())
    PTTCrawler.insertBoardClass(crawBase)

boards=[]
if args.boards=="all": # 讀取所有看板
    PTTCrawler.insertBoardClass(crawBase)
    boards_per = sql.selectData(sql(), " select distinct board_id from board_class ")
    for board in boards_per:
        boards.append(board[0])
else:
    boards = args.boards

if boards=="":
    print("Please input the board. ex: --boards Gossiping or --boards all")
else:
    print("boards = {}, page = {}".format(boards, args.page))


PTTCrawler.insertArticleInfo(crawBase, boards, args.page)
