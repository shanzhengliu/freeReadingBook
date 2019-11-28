from flask import Flask,request, Response
import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor
import re
app = Flask(__name__)

executor = ThreadPoolExecutor(2)
@app.route('/get_content')
def content():
    name = request.args.get("bookname")
    page = request.args.get("page")
    url = "http://www.quanben.io/amp/n/"+name+"/"+page+".html"
    rq = requests.get(url)
    soup = BeautifulSoup(rq.text, 'html.parser')
    content = soup.find("div","articlebody")



    result = ''.join(map(str, content.contents))
    resp = Response(result)
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@app.route('/get_item')
def item():
    name = request.args.get("bookname")
    dict = {}

    listNum = []
    url = "http://www.quanben.io/amp/n/"+name+"/list.html"
    rq = requests.get(url)
    soup = BeautifulSoup(rq.text,"html.parser")
    i = 1
    for content in soup.find("ul", attrs={"class":"list3"}).find_all('a'):
        contentTitle = content.get_text()
        url = "http://www.quanben.io/"+content.attrs['href']

        tempDict={};
        tempDict['title']=contentTitle
        tempDict['url']=url

        listNum.append(tempDict)


    dict['item']=listNum
    jsonData = json.dumps(dict, ensure_ascii=False)

    resp = Response(jsonData)
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp


@app.route('/fenlei')
def fenlei():
    leibie = str(request.args.get("leibie"))
    page = str(request.args.get("page"))
    dict = {}
    item = []
    url = "http://www.quanben.io/c/" + leibie + "_" + page+".html"
    print(url)
    print(url)
    rq = requests.get(url)
    soup = BeautifulSoup(rq.text, "html.parser")
    # print(soup.find_all("div", 'box'))
    for details in soup.find_all("div", "box")[1].find_all("div", "row"):
        tempdict = {}
        bookname = details.find("img").attrs['alt']
        imgurl = details.find("img").attrs['src']
        link = details.find('a').attrs['href'].replace("/n/", "")
        link = link[0:len(link) - 1]

        author = details.find_all("span")[1].get_text()
        description = details.find("p", attrs={"itemprop": "description"}).get_text()
        tempdict["bookname"] = bookname
        tempdict["imgurl"] = imgurl
        tempdict["link"] = link
        tempdict["author"] = author
        tempdict["description"] = description
        item.append(tempdict)
    dict["item"] = item
    jsonData = json.dumps(dict, ensure_ascii=False)
    resp = Response(jsonData)
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp
@app.route('/package')
def package():
    bookname = str(request.args.get('bookname'))
    executor.submit(book_generating,bookname )
    return "book is generating"


def book_generating(bookname):

    strlabel = "begin"
    content = ""

    i = 1;
    while (strlabel != "end"):
        page = i
        url = "http://www.quanben.io/amp/n/" + bookname + "/" + str(page) + ".html"
        rq = requests.get(url)
        soup = BeautifulSoup(rq.text, 'html.parser')
        thiscontect = soup.find("div", "articlebody")
        if (str(thiscontect.get_text()).find("此章节已被删除") == -1):
            content = content + soup.find("div", "articlebody").get_text()
            i += 1
            print(i)

        else:
            strlabel = "end"


    f = open(bookname + ".txt")
    f.write(content)
    f.close()









@app.route('/search')
def search():
    bookname = str(request.args.get("keywords"))
    page = str(request.args.get("page"))
    dict={}
    item = []
    url = "http://www.quanben.io/index.php?c=book&a=search&keywords="+bookname+"&page="+page
    print(url)
    rq = requests.get(url)
    soup = BeautifulSoup(rq.text, "html.parser")
  # print(soup.find_all("div", 'box'))
    for details in soup.find_all("div","box")[1].find_all("div","row"):
       tempdict = {}
       bookname = details.find("img").attrs['alt']
       imgurl = details.find("img").attrs['src']
       link = details.find('a').attrs['href'].replace("/n/","")
       link = link[0:len(link)-1]

       author = details.find_all("span")[1].get_text()
       description = details.find("p",attrs={"itemprop":"description"}).get_text()
       tempdict["bookname"]=bookname
       tempdict["imgurl"]=imgurl
       tempdict["link"]=link
       tempdict["author"]=author
       tempdict["description"]=description
       item.append(tempdict)
    dict["item"]=item
    jsonData = json.dumps(dict, ensure_ascii=False)
    resp = Response(jsonData)
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0')
