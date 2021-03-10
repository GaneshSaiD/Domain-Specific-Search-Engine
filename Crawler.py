import os
import sys
import urllib3
from bs4 import BeautifulSoup
import queuelib
from threading import Thread
from time import sleep
import bs4
import logging
import requests
import time
import gc
import mysql.connector
import configparser
from config import DatabaseConfig
from config import FilesConfig
from config import UnwatedUrlsConfig
from config import PoliteConfig
import re
import json
import socket
from tldextract import tldextract
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import gensim
from gensim.models import KeyedVectors
from w2vec import *

index = 0
mem = str(os.popen("free -t -m").readlines())
visited = []
depth = 0
queue = []
seed_url_PID = 0

w2v_model_300 = KeyedVectors.load_word2vec_format("model300.bin", binary=True)

engine = create_engine(
    "mysql+pymysql://{user}:{pw}@10.20.20.8/{db}".format(
        user=DatabaseConfig.user, pw=DatabaseConfig.passwd, db=DatabaseConfig.database, pool_recycle=3600
    )
)

Session = sessionmaker(bind=engine)
session = Session()
cur = engine.connect()
f = open(FilesConfig.sub_urls, "a")


# Inserting into database
def inst(pid, url, IP):
    check_url_exhist = (
        "select URLs from " + DatabaseConfig.Table_Name + " where URLs = '" + url + "'"
    )
    result = cur.execute(check_url_exhist)
    session.commit()
    check_url_exhist_result = result.rowcount
    if check_url_exhist_result < 1:
        sql = (
            "INSERT INTO "
            + DatabaseConfig.Table_Name
            + "\
              (PID, URLs, IPADD) VALUES (%s, %s, %s)"
        )
        cur.execute(sql, (pid, url, IP))
        session.commit()
    else:
        pass


# Getting PID for URLs
def getPID(url, cur):
    x = url
    sql = "SELECT SNO FROM " + DatabaseConfig.Table_Name + " WHERE URLs = %s"
    myresult = cur.execute(sql, (x,))
    session.commit()
    myresult = myresult.fetchone()
    if myresult is None:
        myresult = 0
        result = myresult
        return result
    else:
        result = myresult[0]
        return result


# Updating visited url in database to 1
def upd(IP_Query_result):
    if IP_Query_result is not None:
        flag_update_sql = ""
        try:
            flag_update_sql = (
                """UPDATE '"""
                + DatabaseConfig.Table_Name
                + """' SET Flag = '1' where
                           URLs = '{IP_Query_result}' """.format(
                    IP_Query_result=IP_Query_result.decode()
                )
            )
        except Exception as e:
            flag_update_sql = (
                """UPDATE """
                + DatabaseConfig.Table_Name
                + """ SET Flag = '1' where
                           URLs = '{IP_Query_result}' """.format(
                    IP_Query_result=IP_Query_result
                )
            )
        try:
            cur.execute(flag_update_sql)
            session.commit()            
        except Exception as e:
            print("$$$$$$$$$$$$$$")
            print(e)
            # pass


def upd_url_type(url):
    sql = (
        "UPDATE "
        + DatabaseConfig.Table_Name
        + " set Url_type = '0' where Urls = '"
        + url
        + "';"
    )
    cur.execute(sql)
    session.commit()


# Process for extraction of data and URLs
def get_url(url):
    global seed_url_PID
    cur2 = engine.connect()
    PID = getPID(url, cur2)
    if PID == 0:
        ip = IP_add(url)
        PID = seed_url_PID - 1
        seed_url_PID = seed_url_PID - 1
        inst(PID, url, ip)
        upd_url_type(url)
        PID = getPID(url, cur2)
    else:
        PID = getPID(url, cur2)
    global index
    index = index + 1
    polite_flag = PoliteConfig.POLITE_FLAG
    polite = PoliteConfig().is_polite(url)
    if polite_flag is False:  # Force crawling of URL if needed.
        polite = True
    if polite is True:
        crawling(url, PID)
    else:
        pass
    cur2.close()


def crawling(url, PID):  # crawling plain text, and sub urls
    print(url)
    try:
        sno_sql = (
            "select SNO from "
            + DatabaseConfig.Table_Name
            + " where URLs = '"
            + url
            + "'"
        )
        result = cur.execute(sno_sql)
        result = result.fetchone()
        sno = result[0]
        sno = str(sno)
        print(sno)
        f.write(url + "\n*************************\n")
        f.close
        req = requests.get(url)
        visited.append(url)
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        hash_x = hash(text)
        hash_update_sql = (
            "UPDATE " + DatabaseConfig.Table_Name + " SET H1 = %s  where URLs = %s"
        )
        val = ((hash_x), str(url))
        cur.execute(hash_update_sql, val)
        session.commit()
        fn = open(FilesConfig.text_storing + sno + ".txt", "w")
        fn.write(url + "\n")
        fn.write(text)
        f1 = open(FilesConfig.hash_value + sno + ".txt", "w")
        f1.write("%d" % hash_x)
        f1.close()
        w2v_sim(url, text)
        n = 0
        for link in soup.find_all("a"):
            sub_link = link.get(
                "href"
            )  # sub_link is the one by one sub links from link
            if sub_link is not None and "https" in sub_link:
                for x in UnwatedUrlsConfig.web_sites:
                    x = UnwatedUrlsConfig.web_sites.encode("ascii")
                    web_sites = json.loads(x)
                    res = any(ele in sub_link for ele in web_sites)
                    if res is True:
                        pass
                    else:
                        if sub_link not in visited:
                            # appending data into visited list
                            visited.append(sub_link)
                            n = n + 1
                            f.write(str(n) + " ) " + sub_link + "\n")
                            print(sub_link)
                            IP = IP_add(sub_link)
                            inst(PID, sub_link, IP)  # insert func() for sub-urls
    except Exception as e:
        pass
    gc.collect()
    sleep(5)

    sorting_ip(PID, url)


def sorting_ip(PID, url):  # Sorting IP in form of ascending order
    queue.remove(url)
    sql = (
        "select distinct substring_index(IPADD,'.',1) as a,"
        "substring_index(substring_index(IPADD,'.',2),'.',-1) as b,"
        "substring_index(substring_index(substring_index\
          (IPADD,'.',3),'.',-1),'.',-1) as c,"
        "substring_index(IPADD,'.',-1) as d, IPADD  from "
        + DatabaseConfig.Table_Name
        + "\
          where PID = '"
        + (str(PID))
        + "' and Url_type = 0 order by a+0,b+0,c+0,d+0;"
    )
    try:
        sql_results = cur.execute(sql)
        session.commit()
        sql_results = sql_results.fetchall()
        for element in sql_results:
            ip = element[4]
            result = getUrlsIPBased(ip)
            for url in result:
                P_url = url[0]
                if P_url not in queue:
                    queue.append(P_url)

    except Exception as e:
        print(e)
        print("############")
    thread_initializer(queue)


def getUrlsIPBased(ip):  # fetching all the IP address already in DB
    sql = (
        "select distinct URLs,IPADD  from "
        + DatabaseConfig.Table_Name
        + " \
    where IPADD='"
        + ip
        + "' and Flag !=1;"
    )
    try:
        sql_results = cur.execute(sql)
        session.commit()
        sql_results = sql_results.fetchall()
        return sql_results
    except Exception as e:
        print(e)
        print("***********")


def IP_add(l):  # extraction of IP address
    ext = tldextract.extract(l)
    URL = ext.subdomain + "." + ext.domain + "." + ext.suffix
    ip = socket.gethostbyname(URL)
    return ip


def thread_initializer(queue):
    # print("thread_initializer")
    thrs = []
    # Checking free memory
    #T_ind = mem.index("T")
    #mem_G = mem[T_ind + 14 : -4]
    #S1_ind = mem_G.index(" ")
    #mem_T = mem_G[0:S1_ind]
    #mem_G1 = mem_G[S1_ind + 8 :]
    #S2_ind = mem_G1.index(" ")
    #mem_U = mem_G1[0:S2_ind]
    #mem_F = mem_G1[S2_ind + 8 :]
#    print(mem_F)
    #mem_F = int(mem_F)
    
    for u1 in queue:
        if u1 is not None:
            # initialising of threads
            thr = Thread(target=get_url, args=(u1,))
            thr.start()
            thrs.append((u1, thr))
    for thr in thrs:
        upd(thr[0])
        thr[1].join()


if __name__ == "__main__":

    # Checking if there is already some URL's in DB.
    sql = (
        "select distinct substring_index(IPADD,'.',1) as a,\
          substring_index(substring_index(IPADD,'.',2),'.',-1) as b,"
        "substring_index(substring_index\
          (substring_index(IPADD,'.',3),'.',-1),'.',-1) as c,"
        "substring_index(IPADD,'.',-1) as d, IPADD,pid,urls  from "
        + DatabaseConfig.Table_Name
        + " \
          where  flag<>1 and Url_type = 0 order by a+0,b+0,c+0,d+0 limit 1;"
    )
    result = cur.execute(sql)
    session.commit()
    result = result.fetchone()
    if (
        result is not None
    ):  # if there are URL's in DB, add those to the queue and start thread.
        seed_url = result[6]
        queue.append(seed_url)
        thread_initializer(queue)
    else:  # if no URL's in DB, taking from the set of seed URL's
        with open("wiki_urls.txt", "r") as seed_url_file:
            content = seed_url_file.read()
            content = content.split("\n")
            for url in content:
                seed_url = url
                queue.append(seed_url)  # Adding seed-url into queue
                thread_initializer(queue)
