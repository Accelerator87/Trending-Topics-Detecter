import time
import jieba
import requests
import math
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from datetime import datetime
import warnings
import tkinter as tk
from tkinter import *
import time

ny = int(time.strftime("%Y",  time.localtime()))
nm = int(time.strftime("%m",  time.localtime()))
ndy = int(time.strftime("%d", time.localtime()))

win = tk.Tk()
win.title("PTT")
win.geometry("500x375")

title = tk.Label(win,text="批踢踢實作坊竄紅話題偵測",bg="#FFFFE0",font=("標楷體",18),width=30,height=2)
title.pack()

stframe = tk.Frame(win)
stText = tk.Label(stframe,text="起始時間: ")  #time_st str(Mth d0 h0:m0:s0 Y000)
yearText1 = tk.Label(stframe,text="年")
monthText1 = tk.Label(stframe,text="月")
dayText1 = tk.Label(stframe,text="日")

etframe = tk.Frame(win)
etText = tk.Label(etframe,text="結束時間: ")  #time_ed
yearText2 = tk.Label(etframe,text="年")
monthText2 = tk.Label(etframe,text="月")
dayText2 = tk.Label(etframe,text="日")

tinframe = tk.Frame(win)
tinText = tk.Label(tinframe,text="時間間隔: ")  #per(s)
dayText3 = tk.Label(tinframe,text="天 ")
hourText = tk.Label(tinframe,text="時 ")

mintframe = tk.Frame(win)
mintText = tk.Label(mintframe,text="最小出現次數: ")
timesText = tk.Label(mintframe,text="次")

rrframe = tk.Frame(win)
rrText1 = tk.Label(rrframe,text="取前")
rrText2 = tk.Label(rrframe,text="筆資料")

skText = tk.Label(win,text="選擇看板:")
skframe1 = tk.Frame(win)
skframe2 = tk.Frame(win)
skframe3 = tk.Frame(win)
skframe4 = tk.Frame(win)

warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()
rs = requests.session()
stock_name, time_st, time_ed, per_start, per, cnt_min, result_range = "","","","",0,0,0

#-------------------------------------------over18-----------------------------------------#

def over18(stock_name):
    res = rs.get("https://www.ptt.cc/bbs/" + stock_name + "/index.html",verify=False)
    if res.url.find('over18') > -1 :
        load = { "from":"/bbs/" + stock_name + "/index.html" ,"yes":"yes" }
        res = rs.post("https://www.ptt.cc/ask/over18",verify=False,data=load)
        return BeautifulSoup(res.text,"html.parser")
    return BeautifulSoup(res.text,"html.parser")

#---------------------------------------get_page_number------------------------------------#

def get_page_number(href):
    return href[href.find("index") + 5: href.find(".html")]

#--------------------------------------time_form_change------------------------------------#

def time_form_change(data):
    
    if data == "no time" :
        return data
    
    dic = { "Jan":"01" ,"Feb":"02" ,"Mar":"03" ,"Apr":"04" ,"May":"05" ,"Jun":"06"  ,
            "Jul":"07" ,"Aug":"08" ,"Sep":"09" ,"Oct":"10" ,"Nov":"11" ,"Dec":"12"  ,
            "?01":"01" ,"?02":"02" ,"?03":"03" ,"?04":"04" ,"?05":"05" ,"?06":"06"  ,
            "?07":"07" ,"?08":"08" ,"?09":"09" ,"?10":"10" ,"?11":"11" ,"?12":"12"  ,
            "?00":"00" ,"??00":"08" ,"?09":"09" ,"?10":"10" ,"?11":"11" ,"?12":"12" }
    try :
        time = data[-4:] + dic[ data[4]+data[5]+data[6] ]
        for i in range(8,19,+1):
            time = time + ( "0" if data[i] == " " or data[i] == ":" else data[i] )
        return time
    
    except :
        return "no time"

#------------------------------------------check_per---------------------------------------#

def check_per(mn,mx):
    
    carry_mn = int(mn[:4])               *12
    carry_mx = int(mx[:4])               *12
    carry_mn = (carry_mn+int(mn[4:6]))   *30
    carry_mx = (carry_mx+int(mx[4:6]))   *30
    carry_mn = (carry_mn+int(mn[6:8]))   *24
    carry_mx = (carry_mx+int(mx[6:8]))   *24
    carry_mn = (carry_mn+int(mn[9:11]))  *60
    carry_mx = (carry_mx+int(mx[9:11]))  *60
    carry_mn = (carry_mn+int(mn[12:14])) *60
    carry_mx = (carry_mx+int(mx[12:14])) *60
    carry_mn = (carry_mn+int(mn[15:]))
    carry_mx = (carry_mx+int(mx[15:]))

    if carry_mx - carry_mn >= per:
        return True
    else:
        return False

#--------------------------------------------count-----------------------------------------#

stopwords = [line.strip() for line in open("stopwords.txt",encoding="utf-8").readlines()]
wordXix,ixXword,word_cnt = {},{},{}

def count(content,now):

    global wordXix,ixXword,word_cnt
    
    for word in word_cnt:
        word_cnt[word].append(0)
    
    words = jieba.lcut(content)
    for word in words:
        if (word not in stopwords) and (len(word) != 1):
            if word not in wordXix:
                ix = len(wordXix)
                wordXix[word] = ix
                ixXword[ix] = word
            ix = wordXix[word]
            word_cnt[ix] = word_cnt.get(ix,[0]*now)
            word_cnt[ix][now-1] += 1

#--------------------------------------------result----------------------------------------#

def cos_sita(x,y):
    x = np.array(x)
    y = np.array(y)
    nx = x/np.sqrt(np.sum(x**2))
    ny = y/np.sqrt(np.sum(y**2))
    return np.dot(nx,ny)

def get_result():
    
    std = 0.8
    topicslist,topics_cnt = [],{}
    topics = {}

    print("getting topicslist...")
    print("quantity of word:",len(word_cnt))

    for word in range(0,len(word_cnt)):
        if sum(word_cnt[word]) <= cnt_min:
            continue
        for topicID in range(0,len(topicslist)):
            check = True
            for topicWORD in topicslist[topicID]:
                if cos_sita(word_cnt[word],word_cnt[topicWORD]) <= std:
                    check = False
                    break
            if check:
                tmp = topicslist[topicID].copy()
                topicslist.append(tmp)
                newID = len(topicslist)-1
                topicslist[newID].append(word)
                tmp = topics_cnt[topicID].copy()
                topics_cnt[newID] = topics_cnt.get(newID,tmp)
                topics_cnt[newID] += np.array(word_cnt[word])
                topics[newID] = topics.get(newID,topicslist[newID])
                newtopic = topics[newID].copy()
                for i in range(newID):
                    try:
                        oldtopic = topics[i].copy()
                    except:
                        continue
                    if oldtopic == newtopic:
                        continue
                    diff = len(set(oldtopic).symmetric_difference(set(newtopic)))
                    if len(oldtopic) < len(newtopic):
                        if diff <= len(newtopic):
                            del topics[i]
                    else:
                        if diff <= len(oldtopic):
                            del topics[newID]
                            break
        topicslist.append([word])
        newID = len(topicslist)-1
        topics_cnt[newID] = topics_cnt.get(newID,np.array(word_cnt[word]))
        
    print("sorting...")

    topic_rk = [[-1,-1,-1,-1]]*result_range
    timerange = len(topics_cnt[0])
    
    for i in topics:
        if len(topics[i]) <= 3:
            continue
        
        m,start,end = -1.0,0,0
        for window in range(1,timerange+1):
            for j in range(0,timerange):
                
                cnt,check = 0,False
                for size in range(0,window):
                    if j+size >= timerange:
                        check = True
                        break
                    else:
                        cnt += topics_cnt[i][j+size]
                if check:
                    break
                
                m_tmp,start_tmp,end_tmp = 0.0,0,0
                for k in range(j+window-1,timerange):
                    if topics_cnt[i][k] < cnt/2:
                        end_tmp = k
                        break
                    if k == timerange-1:
                        end_tmp = -1
                        break
                for k in range(j+window-1,-1,-1):
                    if topics_cnt[i][k] < cnt/2:
                        start_tmp = k
                        break
                    if k == 0:
                        start_tmp = -1
                        break
                    
                m_tmp = float(cnt)/float(window)
                if m == -1.0 or m <= m_tmp:
                    m = m_tmp
                    start = start_tmp
                    end = end_tmp
                    
        for j in range(result_range-1,-1,-1):
            if topic_rk[j][0] >= m:
                topic_rk.insert(j+1,[m,start,end,i])
                topic_rk.pop()
                break
            if j == 0:
                topic_rk.insert(j,[m,start,end,i])
                topic_rk.pop()
                break
    
    print("drawing chart...\n")
    print("--------------")

    rank = 1
    x = [i for i in range(0,timerange)]
    plt.xticks(x)
    color = ["#CC3333","#000000","#FFFF00","#228b22","#6699CC",
             "#336699","#000066","#663366","#009966","#99CC33"]
    data = []
    for topic in topic_rk:
        if topic[3] == -1:
            print("no any more result")
            break
        words = ""
        for word in topics[topic[3]]:
            words += ixXword[word] + " "
        print("rank:",rank)
        print(words)
        if topic[2] == -1 and topic[1] == -1:
            print("### couldn't find starting time and ending time ###")
        elif topic[2] == -1:
            print("from",topic[1],"  ### couldn't find ending time ###")
        elif topic[1] == -1:
            print("### couldn't find starting time ###  ","to",topic[2])
        else:
            print("from",topic[1],"to",topic[2])

        y = topics_cnt[topic[3]]
        a ,= plt.plot(y,"-",color=color[rank-1],label="rank: "+str(rank))
        data.append(a)
        rank += 1

    plt.legend(handles=[i for i in data],bbox_to_anchor=(1.05,1.0,0.3,0.2),loc="upper left")
   
#----------------------------------------check_and_get-------------------------------------#

def check_and_get(soup,data,index,link):

    try :
        info = soup.select(".article-meta-value")[index].text
    except :
        info = "no "+ data
    return info

#-------------------------------------------crawler----------------------------------------#

def crawler(url):
    
    res = rs.get(url,verify=False)
    soup = BeautifulSoup(res.text,"html.parser")
    
    if soup.title.text.find("Service Temporarily") > -1 :
        time.sleep(1)
    else:
        for r_ent in soup.find_all(class_="r-ent"):
            link = r_ent.find('a')
            if link :
                op = get_info('https://www.ptt.cc' + link['href'])
                if op == "break" :
                    return -1
                elif op == "continue":
                    continue
    return 1

#------------------------------------------get_info----------------------------------------#

nowtime,push_tmp = 1,""
titleXix,ixXtitle,IDXtitle = {},{},{}

def get_info(link):
    
    global nowtime,push_tmp,time_st,time_ed,per_start
    
    res = rs.get(link,verify=False)
    soup = BeautifulSoup(res.text,"html.parser")
    time = check_and_get(soup,"time",3,link)

    time_tmp = time_form_change(time)
    if time_tmp == "no time" :
        return "continue"
    elif min(time_tmp,time_st,time_ed)==time_st and max(time_tmp,time_st,time_ed)==time_ed:
        pass
    elif max(time_tmp,time_st,time_ed) == time_tmp :
        count(push_tmp,nowtime)
        return "break"
    else:
        return "continue"

    for tag in soup.select("div.push"):
        try :
            push_content = tag.find("span",{"class":"push-content"}).text[1:]
            push_tmp += push_content
        except :
            print("Couldn't find push in",link)

    if check_per(per_start,time_tmp):
        count(push_tmp,nowtime)
        nowtime += 1
        push_tmp = ""
        per_start = time_tmp
    
    print(time_tmp)

#--------------------------------------------send------------------------------------------#

def send():
    global stock_name,file_name,time_st,time_ed,cnt_min,result_range,per,per_start
    
    tv1 = int(ssbm.get())
    tv2 = str(ssbd.get())
    tv3 = str(ssby.get())
    tv4 = int(esbm.get())
    tv5 = str(esbd.get())
    tv6 = str(esby.get())
    if int(tv2) // 10 == 0 :
        tv2 = "0" + str(tv2)
    if int(tv5) // 10 == 0 :
        tv5 = "0" + str(tv5)
    
    time_st = "????" + monList[tv1-1] + " " + tv2 + " 00:00:00 " + tv3
    time_ed = "????" + monList[tv4-1] + " " + tv5 + " 00:00:00 " + tv6
    per = int(insbd.get()) * 86400 + int(insbm.get()) * 3600
    cnt_min = int(mintsb.get())
    result_range = min(int(sbrr.get()),10)
    
    stock_name = vsk.get()
    if stock_name == "others":
        stock_name = vo.get()

    win.destroy()
    
    time_st = time_form_change(time_st)
    time_ed = time_form_change(time_ed)
    per_start = time_st
    soup = over18(stock_name)
    all_href = soup.select(".btn.wide")[1]["href"]
    all_page = int(get_page_number(all_href)) + 2
    
    print("getting comments in PTT...")
    
    for page in range(1,all_page,+1):
        url = "https://www.ptt.cc/bbs/" + stock_name +"/index" + str(page) + ".html"
        if crawler(url) == -1 :
            break
    
    get_result()
    file_name = stock_name + '-' + datetime.now().strftime('%Y%m%d%H%M%S')
    plt.title("topics from top"+str(result_range),fontsize=24)
    plt.xlabel("time("+str(per)+"s)",fontsize=16)
    plt.ylabel("quantity",fontsize=20)
    file_name = stock_name + '-' + datetime.now().strftime("%Y%m%d%H%M%S")
    plt.tight_layout()
    plt.savefig(file_name+".png")
    
    print("--------------\n")


monList = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

vsy=StringVar()
ssby = Spinbox(stframe,from_=1995,to=ny,textvariable=vsy,width=4)
vsy.set(ny)

vsm=StringVar()
ssbm = Spinbox(stframe,from_=1,to=12,textvariable=vsm,width=2)
vsm.set(nm)

vsd=StringVar()
ssbd = Spinbox(stframe,from_=1,to=31,textvariable=vsd,width=2)
vsd.set(ndy)

vey=StringVar()
esby = Spinbox(etframe,from_=1995,to=ny,textvariable=vey,width=4)
vey.set(ny)

vem=StringVar()
esbm = Spinbox(etframe,from_=1,to=12,textvariable=vem,width=2)
vem.set(nm)

ved=StringVar()
esbd = Spinbox(etframe,from_=1,to=31,textvariable=ved,width=2)
ved.set(ndy)

vind=StringVar()
insbd = Spinbox(tinframe,from_=0,to=9,textvariable=vind,width=2)
vind.set(1)

vinm=StringVar()
insbm = Spinbox(tinframe,from_=0,to=23,textvariable=vinm,width=2)
vinm.set(0)

vmint=StringVar()
mintsb = Spinbox(mintframe,from_=1,to=10000000,textvariable=vmint,width=5)
vmint.set(1)

vrr=StringVar()
sbrr = Spinbox(rrframe,from_=1,to=10,textvariable=vrr,width=4)
vrr.set(1)

vsk = tk.StringVar(value=0)
Gossiping = tk.Radiobutton(skframe1, text="Gossiping", variable=vsk, value="Gossiping")
Stock = tk.Radiobutton(skframe1, text="Stock", variable=vsk, value="Stock")
C_chat = tk.Radiobutton(skframe1, text="C_chat", variable=vsk, value="C_chat")
NBA = tk.Radiobutton(skframe2, text="NBA", variable=vsk, value="NBA")
Baseball = tk.Radiobutton(skframe2, text="Baseball", variable=vsk, value="Baseball")
Lifeismoney = tk.Radiobutton(skframe2, text="Lifeismoney", variable=vsk, value="Lifeismoney")
Car = tk.Radiobutton(skframe3, text="Car", variable=vsk, value="Car")
Tech_Job = tk.Radiobutton(skframe3, text="Tech_Job", variable=vsk, value="Tech_Job")
KoreaStar = tk.Radiobutton(skframe3, text="HatePolitics", variable=vsk, value="HatePolitics")
others = tk.Radiobutton(skframe4, text="其他", variable=vsk, value="others")

vo = StringVar()
othersEntry = tk.Entry(skframe4, textvariable=vo, bd=5)

stframe.pack(side=TOP)
stText.pack(side=LEFT)
ssby.pack(side=LEFT)
yearText1.pack(side=LEFT)
ssbm.pack(side=LEFT)
monthText1.pack(side=LEFT)
ssbd.pack(side=LEFT)
dayText1.pack(side=LEFT)

etframe.pack(side=TOP)
etText.pack(side=LEFT)
esby.pack(side=LEFT)
yearText2.pack(side=LEFT)
esbm.pack(side=LEFT)
monthText2.pack(side=LEFT)
esbd.pack(side=LEFT)
dayText2.pack(side=LEFT)

tinframe.pack(side=TOP)
tinText.pack(side=LEFT)
insbd.pack(side=LEFT)
dayText3.pack(side=LEFT)
insbm.pack(side=LEFT)
hourText.pack(side=LEFT)

mintframe.pack(side=TOP)
mintText.pack(side=LEFT)
mintsb.pack(side=LEFT)
timesText.pack(side=LEFT)

rrframe.pack(side=TOP)
rrText1.pack(side=LEFT)
sbrr.pack(side=LEFT)
rrText2.pack(side=LEFT)

skText.pack(side=TOP)
skframe1.pack(side=TOP)
Gossiping.pack(side=LEFT)
Stock.pack(side=LEFT)
C_chat.pack(side=LEFT)
skframe2.pack(side=TOP)
NBA.pack(side=LEFT)
Baseball.pack(side=LEFT)
Lifeismoney.pack(side=LEFT)
skframe3.pack(side=TOP)
Car.pack(side=LEFT)
Tech_Job.pack(side=LEFT)
KoreaStar.pack(side=LEFT)
skframe4.pack(side=TOP)
others.pack(side=LEFT)
othersEntry.pack(side=LEFT)

sendButton = tk.Button(win,text="送出",command=send)
sendButton.pack()

win.mainloop()
