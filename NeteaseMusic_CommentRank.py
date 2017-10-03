#Author1:   Zayne   1120161983
#Author2:   Daisy   1120162011

import requests
import urllib
import warnings
from Crypto.Cipher import AES
import base64
import json
import time
from bs4 import BeautifulSoup
from prettytable import PrettyTable

warnings.filterwarnings("ignore")
COMMENT_LIMIT = 10000
FILE_NAME = "SongRankList.txt"
_session = requests.session()
headers = {
    "User-Agent":"Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36"
}

first_param = "{rid:\"\", offset:\"0\", total:\"true\", limit:\"20\", csrf_token:\"\"}"
second_param = "010001"
third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
forth_param = "0CoJUm6Qyw8W8jud"

#密钥
def get_params():
    iv = "0102030405060708"
    first_key = forth_param
    second_key = 16 * 'F'
    h_encText = AES_encrypt(first_param, first_key, iv)
    #将b64encode结果强制转换为utf-8
    h_encText = h_encText.decode('utf-8')
    h_encText = AES_encrypt(h_encText, second_key, iv)
    h_encText = h_encText.decode('utf-8')
    return h_encText

def get_encSecKey():
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    return encSecKey

def AES_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text

#获取json的结果
def get_json(url, params, encSecKey):
    data = {
         "params": params,
         "encSecKey": encSecKey
    }
    response = requests.post(url, headers=headers, data=data)
    return response.content

def GetSongInfo():
    print("#####正在获取歌曲信息列表#####")
    MAX_PAGE_LIMIT = 1
    SongList = []
    for p in range(MAX_PAGE_LIMIT):
        time.sleep(0.05)
        dic = {}
        url = 'http://grri94kmi4.app.tianmaying.com/songs?page=' + str(p)
        url.encode('utf-8')
        soup = BeautifulSoup(_session.get(url,headers = headers).content, 'lxml')
        ReList = soup.findAll('a', attrs={'target': '_blank'})
        for a in ReList:
            SongId = a['href'].split('=')[1]
            SongName = a.get_text()
            dic = {"id":SongId, "name":SongName, "num":0}
            SongList.append(dic)
        print("\r#####正在获取第{}页的歌曲信息#####".format(p + 1), end="")
    return SongList
    
def GetCommentNum(id):
    url = "https://music.163.com/weapi/v1/resource/comments/R_SO_4_"+str(id)+"?csrf_token="
    params = get_params()
    encSecKey = get_encSecKey()
    json_text = get_json(url, params, encSecKey)
    json_dict = json.loads(json_text.decode('utf-8'))
    return json_dict['total']

def GetSongList(SongList):
    print("#####正在获取歌曲评论数#####")
    for idx, song in enumerate(SongList):
        n = song["id"]
        CommentNum = GetCommentNum(n)
        SongList[idx]["num"] = CommentNum
        time.sleep(1)
        print("\r#####已经获取{}首歌的评论数#####".format(idx + 1), end="")
    return SongList

def SortList(NumList):
    ReList = sorted(NumList, key = lambda x: x['num'], reverse = True)
    return ReList

def SaveToFile(table, FileName):
    print("#####正在写入文件#####")
    data = table.get_string()
    with open(FileName, 'w+') as fw:
        fw.write(data)
    print("#####文件写入成功#####")

def PrintTable(PList):
    table = PrettyTable(['排名','评论数', '歌曲名称', '网址'])
    for idx, song in enumerate(PList):
        url = "https://music.163.com/#/song?id=" + str(song["id"])
        if song["num"] > COMMENT_LIMIT:
            table.add_row([idx + 1, song["num"], song["name"], url])
    print(table)
    return table

def main():
    start_time = time.time()

    #获取info列表
    SongList = GetSongInfo()
    print("\n#####歌曲信息列表获取完成#####")
    n = len(SongList)
    print("#####获取到{}首歌曲#####".format(n))

    #获取歌曲评论数
    NumList = GetSongList(SongList)
    print("\n#####获取评论数成功#####")

    #歌曲评论数排序
    SortedList = SortList(NumList)
    print("#####排序完成#####")

    table = PrintTable(SortedList)

    #存入文件
    SaveToFile(table, FILE_NAME)

    end_time = time.time()
    print("任务完成，耗时{:.2f}s".format(end_time - start_time))

if __name__ == '__main__':
    main()
