import requests,re
import os
import operator
import googlemaps
import geocoder
import csv
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
"""==================Crawler=================="""
g = []#product list
p = []#price list
for i in range(10):#Get product&price lists
    res = requests.get('https://p-bandai.com/tw/search?text=&sort=newArrival&sellDate=0&sellDate=1&page='+str(i))
    sp = BeautifulSoup(res.text, 'lxml')
    goods = str(sp.select('.m-card__name'))
    good = re.findall("m-card__name\">.+?<",goods)#取品名
    for i in good:
            d1 = i.find(">")+1
            d2 = i.find("<")
            string = i[d1:d2]
            g.append(string)
    prices = str(sp.select('.m-card__price'))
    price = re.findall("span>.+?<",prices)#取價格
    for i in price:
            d1 = i.find(">")+1
            d2 = i.find("<")
            string = i[d1:d2]
            p.append(string)
p = [w.replace(',', '') for w in p]
p = list(map(int, p))#原先爬下的價格為字串且中間包含','，這邊將它轉為可用來比大小的數值
catg = dict(zip(g, p))
catg = {k: v for k, v in sorted(catg.items(), #依價格排序商品總覽
                                key=lambda item: item[1],reverse = True)}
while True:
    try:
        print('品項總覽：')
        for keys,values in catg.items():
            print(keys,': NT$',values)

        i = 0
        new = dict()#經品名篩選後
        nnew = dict()#經價格篩選後
        r1 = []
        r2 = []
        req = input('輸入想找的品項，若無則直接enter：')
        for result1 in list(key for key, value in catg.items() if req in key.lower()):
            r1.append(result1)
            for result2 in list(value for key, value in catg.items() if req in key.lower()):
                r2.append(result2)
        r2 = list(map(int, r2))
        catgo = dict(zip(r1,r2))#符合輸入關鍵字的品項與價格生成另一個value可比大小的dictionary
        for keys,values in catgo.items():#生成符合要求品名的所有商品與對應價錢列表
            print(keys,': NT$',values)
        maximum = max(catgo, key=catgo.get)
        exp = catgo[maximum]
        minimum = min(catgo, key=catgo.get)
        chp = catgo[minimum]
        #得商品中的最高與最低價
        print("最高價格：",exp,"最低價格：",chp)
        break
    except:
        print('沒有該品項喔')   

while True:
    try:
        a = int(input('--------輸入價格上限，若無則輸入"99999"-------'))
        break
    except:
        print('價格定義錯誤')
while True:
    try:
        b = int(input('--------輸入價格下限，若無則輸入"0"-------'))
        break
    except:
        print('價格定義錯誤')        
if a <= exp:#上界成功定義
    new = dict((k, v) for k, v in catgo.items() if v <= a)
    if b >= chp :#成功定義下界
        nnew = dict((k, v) for k, v in new.items() if v >= b)
    elif b == 0 :#不定義下屆
        nnew = dict((k, v) for k, v in new.items() if v >= chp)
    else:#下界定太小
        nnew = dict((k, v) for k, v in new.items() if v >= chp)
elif a == 99999 :#不定義上界
    new = dict((k, v) for k, v in catgo.items() if v <= exp)
    if b >= chp:
        nnew = dict((k, v) for k, v in new.items() if v >= b)
    elif b == 0 :
        nnew = dict((k, v) for k, v in new.items() if v >= chp)
    else:
        nnew = dict((k, v) for k, v in new.items() if v >= chp)
else:#上界定太大
    new = dict((k, v) for k, v in catgo.items() if v <= exp)
    if b >= chp:
        nnew = dict((k, v) for k, v in new.items() if v >= b)
    elif b == 0 :
        nnew = dict((k, v) for k, v in new.items() if v >= chp)
    else:
        nnew = dict((k, v) for k, v in new.items() if v >= chp)
for keys,values in nnew.items():
    print(keys,': NT$',values)#列出經過品項與價格篩選後的商品
    
"""==================Youtube Api=================="""
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
youtube_api_key = 'AIzaSyC-YEMllOYm-jgIPJH4zlLCy_7LzzW2i3Q'
youtube = build('youtube', 'v3', developerKey = youtube_api_key)
#引入youtube data api
key_words = []
rating_points = []
while True:
    try:
        key_word = input("輸入前面所得商品影片關鍵字：")
        key_words.append(key_word)
        s_num = int(input("輸入想取的影片數量："))
        
        key_request = youtube.search().list(
            q = key_word, part='snippet', type='video', maxResults = s_num )
        res = key_request.execute()#依據輸入關鍵字取得所要求數量影片的資訊

        vid_ids = []#影片ID
        titles = []#影片標題
        for item in res['items']:#取得影片id和標題
            vid_ids.append(item['id']['videoId'])
            titles.append(item['snippet']['title'])
        
        print("影片有：")
        for item in titles:#列出影片標題
            print(item)
        
        view_ct = []#觀看數
        like_ct = []#讚數
        dslike_ct = []#倒讚數
        comment = []#留言

        for item in vid_ids:
            info_request = youtube.videos().list(
            part="statistics",id = item)
            info_response = info_request.execute()
            for item in info_response['items']:
                view_ct.append(int(item['statistics']['viewCount']))
                like_ct.append(int(item['statistics']['likeCount']))
                dslike_ct.append(int(item['statistics']['dislikeCount']))
        #取觀看數、讚數、倒讚數

        likes = list(map(operator.add, like_ct,dslike_ct))
        likes_rate = list(map(operator.truediv, like_ct,likes))
        likes_point = list(map(operator.mul, view_ct,likes_rate))
        likes_point = [i / (10000 * s_num) for i in likes_point]
        likes_point = [int(i) for i in likes_point]
        public = sum(likes_point)
        #取{觀看數*[讚數/(讚數+倒讚數)]/(10000*}為大眾評分

        i = int(input("輸入想取的留言數量："))
        for item in vid_ids:
            co_request = youtube.commentThreads().list(
                part = "snippet,replies",maxResults = i,order="relevance",videoId = item)
            co_response = co_request.execute()
            for item in co_response['items']:
                comment.append(item['snippet']['topLevelComment']['snippet'][ 'textOriginal'])
        for item in comment:
            print(item)
            print("")
        #取留言  
        personal = int(input("請依據留言評價為商品打0~100的分數："))#取個人評分
        rating_point = round((personal * 0.95) + (public * 0.05) , 2)#總評分為大眾評分*個人評分
        rating_points.append(rating_point)
    
        a = int(input("====是否要找另一項商品的評價？是則輸入'1'，否則輸入'2'===="))
        if a == 1:
            continue
        else:
            break
        #搜尋更多商品的介紹、評測、開箱影片
    except:
        print('有影片不開放留言，請減少取影片的量')
        
"""==================Google Map Api=================="""
g = geocoder.ip('me')
# 取現在位置
places_api_key = 'AIzaSyAvNERcb_LiqxDwm0vGqLs8yATr-tIlZNE'
while True:
    try:
        dt = int(input("請問要尋找方圓幾公尺內的模型店？"))
        break
    except:
        print('輸入的不是距離，請重新輸入')
gmaps = googlemaps.Client(key = places_api_key)#
places_result  = gmaps.places_nearby(location = g.latlng, 
    radius = dt, open_now = True , keyword = '模型店',language = 'zh-TW')
#搜尋以當前位置為核心，符合使用者要求範圍內的模型店位置
name = []
address = []
for place in places_result['results']:#取出店名和地址
    name.append(place['name'])
    address.append(place['vicinity'])

places = dict(zip(name, address))
"""===========Final Output============"""
result = dict(zip(key_words,rating_points))
result = {k: v for k, v in sorted(result.items(), key=lambda item: item[1],reverse = True)}
#依分數高到低排序最後結果
i = 1
k = 1
#輸出商品的推薦購買順序與各自分數，以及所求範圍內至多20間營業中的模型店
with open('推薦清單.csv', 'w', newline='') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(['商品推薦購買順序與分數'])
    writer.writerow(['推薦排名','品名','分數'])
    for name, point in result.items():
       writer.writerow([i,name,point])
       i = i + 1
    writer.writerow(['所求範圍內營業中的模型店'])
    writer.writerow(['關注度排名','店名','地址'])
    for name, address in places.items():
       writer.writerow([k,name,address])
       k = k + 1
print("結果清單已生成")
