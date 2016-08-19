# coding: UTF-8
from django.shortcuts import render
from bs4 import BeautifulSoup
import bs4
import re
import urllib2
from django.http import HttpResponse
from public_class import Tool
import string
import time
import datetime
from spider.models import Product
from spider.models import User
from spider.models import ProductNew
from spider.models import CommentNew
from spider.models import UserNew
from spider.models import CommentSentiment
import threading, thread

import os
import  glob
import json
import codecs
import random

from QcloudApi.modules.base import Base

class Wenzhi(Base):
    requestHost = 'wenzhi.api.qcloud.com'


readList = []
soupList = []
soupList2 = []

getOnePageNewMsg = ""
getOnePageUserNewMsg = ""
getOnePageUserNewSimpleMsg = ""

def index(request):
    return render(request, 'index.html')

def getSoup(url,page):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
    headers = {'User-Agent': user_agent}
    url += '&pageNumber='+str(page)

    req = urllib2.Request(url, headers=headers)
    res = urllib2.urlopen(req)
    html = res.read().decode('utf-8')
    # 创建BeautifulSoup对象
    soup = BeautifulSoup(html)
    soupList.append(soup)

def getOnePage(request, soup):

    # 分析页面标签，得到产品名称、认为有用数量、每条评论中的打星、每条评论的留言者、每条评论的评论内容、评论时间

    total_info = []
    single_info = []

    section = soup.find_all('div', class_='a-section review')  #各个评论块的所有数据
    for item in section:
        hasImage = False
        if len(item) >= 7:
            hasImage = True

        c_item = item.contents   # 将item的所有直接子节点以list的形式列出
        index = -1
        have_official_comment = False   #有些有官方评论，有些没有
        official_list = [u'a-size-small', u'a-color-state', u'official-comment-banner-outer']
        if c_item[0]['class'] == official_list:
            have_official_comment = True
        if have_official_comment:
            index += 1

        # 认为有用的数量  有些评论块中，竟然没有此项，，， 如果没有，将其跳过
        helpful = unicode(c_item[index + 1].string)
        if helpful != 'None':
            helpful = helpful.replace(',', '')
            pattern = re.compile('(\d+).*?(\d+)')
            helpres = re.findall(pattern, helpful)
            helpres = helpres[0]
            helpful = helpres[0] + '/' + helpres[1]

        # 打星
        star = ''
        star_t = c_item[index + 2].children.next()
        star_t = unicode(star_t.string)  #NavigatbleString -> String
        pattern = re.compile(r'(\d.\d)')
        star_t = re.search(pattern, star_t)
        if star_t:
            star = star_t.group(1)
            star = star.split('.')[0]
            star = int(star)  # 取整

        print str(hasImage) + "--" + str(helpful)

        # 留言者 留言者链接 和 留言时间
        author_href = ''
        author = c_item[index + 3].contents[0].contents[2]
        author_href = 'www.amazon.cn'+author['href']
        author = author.string
        comment_time_str = unicode(c_item[index + 3].contents[3].string)
        comment_time = ''
        pattern = re.compile('(\d+.*?)$')
        comment_time = re.search(pattern, comment_time_str)
        if comment_time:
            comment_time = comment_time.group(1)
            pattern = re.compile('(\d+).*?(\d+).*?(\d+)')
            ctres = re.findall(pattern, comment_time)
            ctres = ctres[0]
            tool = Tool()
            comment_time = tool.time2stamp(int(ctres[0]),int(ctres[1]),int(ctres[2]))

        # 留言内容
        comment = ''
        comments_list = c_item[index + 5].contents[0].children
        for item in comments_list:
            try:
                comment += unicode(item)
            except Exception, e:
                pass
        tool = Tool()
        comment = tool.replace(comment)

        #将以上6部分组装在一个字典中
        single_info = {"helpful":helpful, "star":star, "author":author, "author_href":author_href,
                       "comment_time":comment_time, "comment":comment, "hasImage":hasImage}
        total_info.append(single_info)
    return total_info


def multiThread(url, totalNum, startNum, endNum):
    # 每十个为放在一个线程池中
    soupList = []
    count = 1
    start = startNum
    end = endNum
    if end == 1:
        end = totalNum
    leaveNum = totalNum
    while start<=end:
        cc = 1
        capacity = 10
        if capacity > leaveNum:
            capacity = leaveNum
        threadPool = []
        while cc <= capacity:
            th = threading.Thread(target=getSoup, args=(url, start))
            threadPool.append(th)

            cc += 1
            start += 1
        leaveNum -= capacity

        for th in threadPool:
            th.setDaemon(True)
            th.start()

        for th in threadPool:
            th.join()
def getSoup2(url):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
    headers = {'User-Agent': user_agent}
    req = urllib2.Request(url, headers=headers)
    res = urllib2.urlopen(req)
    html = res.read().decode('utf-8')
    soup = BeautifulSoup(html)
    soupList2.append(soup)
    print "Add %d soup" % len(soupList2)


def multiThread2(res_list):
    soupList2 = []
    count = 0
    length = len(res_list)
    print "res_list length:"+str(length)
    leaveNum = length
    while count < length:
        cc = 1
        capacity = 10
        if capacity > leaveNum:
            capacity = leaveNum
        threadPool = []
        while cc <= capacity:
            t = threading.Thread(target=getSoup2, args=("http://"+res_list[count]['author_href'],))
            threadPool.append(t)
            cc += 1
            count += 1
        leaveNum -= capacity

        for th in threadPool:
            th.setDaemon(True)
            th.start()

        for th in threadPool:
            th.join()

        if count % 60 == 0:
            print "I'll sleep 10 seconds..."
            time.sleep(10)


def userInfo(soup):
   # try:
    tool = Tool()
    # 该产品的个人信息字典
    personal_info = {}
    # 历史评价产品列表,但里边的每一项都是字典
    history_list = []

    # 依次取出评论人的 姓名、该产品评论的排名、该产品评论的有用度(有用条数/总条数)、
    #         历史上评论的产品（包括产品名称、打星、建议、评论时间、评论）
    # 首先： 个人信息
    profile_info_items = soup.find('div', class_='profile-info').contents

    name = 'None'

    if len(profile_info_items) == 5:
        name = profile_info_items[1].string
    elif len(profile_info_items) == 6:
        name = profile_info_items[1].contents[0].contents[0].string

    personal_info = {'name': name}

    # 历史评论消息
    section = soup.find_all('div', class_='a-row columnizer-block profile-item-card profile-item-container')

    for item in section:
        # 产品名
        title = item.contents[2].contents[0].contents[0].contents[1].contents[4].contents[0].contents[0]
        title = unicode(title)


        item_card_data = item.contents[2].contents[0].contents[1]
        if len(item_card_data) == 4:
            # 打星
            star_tag = item_card_data.contents[1].contents[0]
            star = string.split(star_tag.attrs['class'][2], '-')[-1]
            # 建议
            suggestion = star_tag.next_sibling.next_sibling.contents[0].string
            # 评论时间
            comment_time = item_card_data.contents[2].contents[0].string
            # 评论
            comment_list = item_card_data.contents[3].contents[0].contents[0].stripped_strings
            comment = ''
            for v in comment_list:
                comment += v
            # 多少人认为有用， 一共多少人
            item_useful_total = 0
            item_useful_ok = 0

        elif len(item_card_data) == 6:
            # 打星
            star_tag = item_card_data.contents[3].contents[0]
            star = string.split(star_tag.attrs['class'][2], '-')[-1]
            # 建议
            suggestion = star_tag.next_sibling.next_sibling.contents[0].string
             # 评论时间
            comment_time = item_card_data.contents[4].contents[0].string
             # 评论
            comment_list = item_card_data.contents[5].contents[0].contents[0].stripped_strings
            comment = ''
            for v in comment_list:
                comment += v
            # 多少人认为有用， 一共多少人
            item_useful = unicode(item_card_data.contents[1].string)
            pattern = re.compile('(\d+).*?(\d+)')
            resset = re.findall(pattern, item_useful)
            # print resset
            item_useful_total = resset[0][0]
            item_useful_ok = resset[0][1]



        single_section = {"author":personal_info['name'],"title": title, "star": star,
                          "suggestion": suggestion,"item_useful_total": item_useful_total,
                          "item_useful_ok": item_useful_ok,
                          "comment_time": tool.engMon2stamp(comment_time), "comment": comment}

        history_list.append(single_section)
    # except Exception, e:
    #     if hasattr(e, 'reason'):
    #         return HttpResponse(e.reason)
    #     return HttpResponse(e)

    return history_list



def handle1(request):
    if request.method == 'POST':
        url = request.POST['url']
        quantity = request.POST['num']
        needDb = request.POST['needDb']

        totalNum = 0
        startNum = 1
        endNum = 1
        res_list = []   # 返回结果是一个列表， 列表中每个元素是字典，字典中存放各个属性

        # 从url中得到网页数据，结果为html
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
        headers = {'User-Agent': user_agent}
        req = urllib2.Request(url, headers=headers)
        res = urllib2.urlopen(req)
        html = res.read().decode('utf-8')

        # 创建BeautifulSoup对象
        soup = BeautifulSoup(html)
        print "first page soup is generated"
        # 产品名称
        title = soup.find('a', {'class':'a-size-large a-link-normal'}).string
        # 找到总页码
        pagination = soup.find('ul', class_='a-pagination')
        end_page_index =  len(pagination.contents) - 2
        allPageNum_str = pagination.contents[end_page_index].string
        tool = Tool()
        allPageNum = tool.englishNum2intNum(allPageNum_str)

        if quantity == 'one':
            totalNum = 1
        elif quantity == 'two':
            totalNum = 2
        elif quantity == 'quarter':
            totalNum = allPageNum/4
        elif quantity == 'half':
            totalNum = allPageNum/2
        elif quantity == 'all':
            totalNum = allPageNum
        elif quantity == 'option':
            startNum = int(request.POST['num1'])
            endNum = int(request.POST['num2'])
            totalNum = endNum - startNum + 1


        multiThread(url, totalNum, startNum, endNum)
        print "All page_soup are generated..."
        c = 0
        for item_soup in soupList:
            c += 1
            print "Start analyze soup "+ str(c)
            res_dict_list = getOnePage(request, item_soup)
            res_list.extend(res_dict_list)
        # count = 1
        # while count <= totalNum:
        #     url += '&pageNumber'+str(count)
        #     # 通过多线程方法， 获取soup分页的列表
        #     res_dict_list = getOnePage(request, soup)
        #     res_list.extend(res_dict_list)
        #     count += 1
        totalCommentNum = len(res_list)   # 总条数

        userInfo_list = []
        # 写数据库
        if needDb == '1':
            userInfo_list = []
            print "Start to get userInfo..."
            multiThread2(res_list)
            for soup in soupList2:
                # 通过author_href来获取用户历史评论数据
                userInformation = userInfo(soup)
                for item_item in userInformation:
                    ttt = {'author':item_item['author'], 'title':item_item['title'],
                           'star':item_item['star'], 'suggestion':item_item['suggestion'],
                           'help':str(item_item['item_useful_ok']) + '/' + str(item_item['item_useful_total']),
                           'comment_time':item_item['comment_time'], 'comment':item_item['comment']}
                    userInfo_list.append(ttt)
            print "UserInfo got successfully..."

            print "start to write database..."

            datacount = 0
            for item in res_list:
                # 保存product
                Product.objects.create(title=title, p_url=url, commenter=item['author'], c_url=item['author_href'],
                                     c_time=item['comment_time'], star=item['star'], help=item['helpful'],
                                     comment=item['comment'], hasImage=item['hasImage'])
                datacount += 1
                if datacount % 200 == 0:
                    print "I'll sleep 5 second..."
                    time.sleep(5)
            print "product wrote over..."

            print "Now, start to save users..."
            datacount2 = 0
            print "userCount is : ---->  "+ str(len(userInfo_list))
            for item_item in userInfo_list:
                if item_item['author'] != None:
                    User.objects.create(username=item_item['author'], p_name=item_item['title'],
                                            star=item_item['star'], suggestion=item_item['suggestion'],
                                            help=item_item['help'], time=item_item['comment_time'], content=item_item['comment'])
                    datacount2 += 1
                    if datacount2 % 200 == 0:
                        print "I'll sleep 5 second..."
                        time.sleep(5)
                    print str(datacount2)

            print "user wrote over..."


        return render(request, 'handle1.html', {'res_list': res_list, 'title': title,
                                                'totalCommentNum': totalCommentNum, 'userInfo_list': userInfo_list})

    return HttpResponse("NOT POST")


def handle2(request):
    if request.method == 'POST':
        # try:
        tool = Tool()
        url = request.POST['user_url']
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
        headers = {'User-Agent': user_agent}
        req = urllib2.Request(url, headers=headers)
        res = urllib2.urlopen(req)
        html = res.read().decode('utf-8')

        # 该产品的个人信息字典
        personal_info = {}
        # 历史评价产品列表,但里边的每一项都是字典
        history_list = []

        soup = BeautifulSoup(html)

        # 依次取出评论人的 姓名、该产品评论的排名、该产品评论的有用度(有用条数/总条数)、
        #         历史上评论的产品（包括产品名称、打星、建议、评论时间、评论）
        # 首先： 个人信息
        profile_info_items = soup.find('div', class_='profile-info').contents

        if len(profile_info_items) == 5:
            name = profile_info_items[1].string
            #  有两种情况！！！！
            tag1 = profile_info_items[2]
            # 第一次做的东西，即排名是一个链接
            if len(tag1) == 1:
                ranking = profile_info_items[2].contents[0].contents[0].contents[0].string
                useful_percent = profile_info_items[3].contents[0].contents[0].string
                useful_num_str = profile_info_items[3].contents[3].contents[0].string
                useful_num_str = unicode(useful_num_str)
                useful_num_str = useful_num_str.replace(',', '')
                pattern = re.compile('(\d+).*?(\d+)')
                resset = re.findall(pattern, useful_num_str)
                # print resset
                useful_total = tool.englishNum2intNum(resset[0][0])
                useful_ok = tool.englishNum2intNum(resset[0][1])
            elif len(tag1) == 2:
                ranking = profile_info_items[2].contents[0].string
                useful_percent = profile_info_items[3].contents[0].contents[0].string
                useful_num_str = profile_info_items[3].contents[3].contents[0].string
                useful_num_str = unicode(useful_num_str)
                useful_num_str = useful_num_str.replace(',', '')
                pattern = re.compile('(\d+).*?(\d+)')
                resset = re.findall(pattern, useful_num_str)

                # print resset
                useful_total = tool.englishNum2intNum(resset[0][0])
                useful_ok = tool.englishNum2intNum(resset[0][1])

        elif len(profile_info_items) == 6:
            name = profile_info_items[1].contents[0].contents[0].string
            ranking = profile_info_items[3].contents[0].contents[0].contents[0].string
            useful_percent = profile_info_items[4].contents[0].contents[0].string
            useful_num_str = profile_info_items[4].contents[3].contents[0].string
            useful_num_str = unicode(useful_num_str)
            pattern = re.compile('(\d+.*?\d+).*?(\d+.*?\d+)')
            resset = re.findall(pattern, useful_num_str)
            useful_total = tool.englishNum2intNum(resset[0][0])
            useful_ok = tool.englishNum2intNum(resset[0][1])

        personal_info = {'name': name, "ranking": ranking, "useful_percent": useful_percent,
                         "useful_total": useful_total, "useful_ok": useful_ok}

        # 历史评论消息
        section = soup.find_all('div', class_='a-row columnizer-block profile-item-card profile-item-container')

        for item in section:
            # 产品名
            title = item.contents[2].contents[0].contents[0].contents[1].contents[4].contents[0].contents[0]
            title = unicode(title)


            item_card_data = item.contents[2].contents[0].contents[1]
            if len(item_card_data) == 4:
                # 打星
                star_tag = item_card_data.contents[1].contents[0]
                star = string.split(star_tag.attrs['class'][2], '-')[-1]
                # 建议
                suggestion = star_tag.next_sibling.next_sibling.contents[0].string
                # 评论时间
                comment_time = item_card_data.contents[2].contents[0].string
                # 评论
                comment_list = item_card_data.contents[3].contents[0].contents[0].stripped_strings
                comment = ''
                for v in comment_list:
                    comment += v
                # 多少人认为有用， 一共多少人
                item_useful_total = 0
                item_useful_ok = 0

            elif len(item_card_data) == 6:
                # 打星
                star_tag = item_card_data.contents[3].contents[0]
                star = string.split(star_tag.attrs['class'][2], '-')[-1]
                # 建议
                suggestion = star_tag.next_sibling.next_sibling.contents[0].string
                 # 评论时间
                comment_time = item_card_data.contents[4].contents[0].string
                 # 评论
                comment_list = item_card_data.contents[5].contents[0].contents[0].stripped_strings
                comment = ''
                for v in comment_list:
                    comment += v
                # 多少人认为有用， 一共多少人
                item_useful = unicode(item_card_data.contents[1].string)
                pattern = re.compile('(\d+).*?(\d+)')
                resset = re.findall(pattern, item_useful)
                # print resset
                item_useful_total = resset[0][0]
                item_useful_ok = resset[0][1]



            single_section = {"title": title, "star": star, "suggestion": suggestion,
                              "item_useful_total": item_useful_total, "item_useful_ok": item_useful_ok,
                              "comment_time": tool.engMon2stamp(comment_time), "comment": comment}
            # print comment_time
            history_list.append(single_section)
        # except Exception, e:
        #     if hasattr(e, 'reason'):
        #         return HttpResponse(e.reason)
        #     return HttpResponse(e)

        return render(request, "handle2.html", {"personnal_info": personal_info, "history_list": history_list,
                                                "totalHistory": len(history_list)})

    return HttpResponse("NOT POST")


def handle3(request):
    if request.method != 'POST':
        return HttpResponse("NOT POST METHOD")
    radioType = request.POST['radioType']
    url = request.POST['sort_page_url']
    page = 1
    if radioType == '0':
        url += "&page=" + str(page)
    elif radioType == '1':
        url += "&pg=" + str(page)

    # 从url中得到网页数据，结果为html
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
    user_agent1 = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'
    headers = {'User-Agent': user_agent1}
    req = urllib2.Request(url, headers=headers)
    res = urllib2.urlopen(req)
    html = res.read().decode('utf-8')
    dirname = os.path.dirname(__file__)
    fullpath = dirname + '\\tmp_html\\'
    rename = 'firstHtml.html'
    tool = Tool()
    tool.writeFile(fullpath + rename, html, 'w')
    # 根据rename文件建立soup
    soup = BeautifulSoup(open(fullpath + rename))
    section = None
    if radioType == '0':
        section = soup.find_all('a', class_='a-link-normal s-access-detail-page  a-text-normal')
    elif radioType == '1':
        newSection = []
        section = soup.find_all('div', class_='zg_title')
        for item in section:
            newSection.append(item.a)
        section = newSection
    i = 0
    msg = ""
    for item in section:
        msg += item["href"].strip() + "\n"
        i += 1
    tool.writeFile(fullpath + "list.txt", msg, 'w')

    return HttpResponse("Step 1 --- Done")

def getAndSaveHtml(url, name):
    firefox = random.randint(30,45)
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/'+str(firefox)+'.0'
    headers = {'User-Agent': user_agent}
    req = urllib2.Request(url, headers=headers)
    res = urllib2.urlopen(req)
    html = res.read().decode('utf-8')
    tool = Tool()
    fullpath = os.path.dirname(__file__) + "\\tmp_html\\"
    tool.writeFile(fullpath + name, html, 'w')


def multiThreadForHtmlFile(arr, suffix):
    # 多线程
    i = 0  # 控制循环
    j = 0  # 计数
    leaveNum = len(arr)
    while j < len(arr):
        i = 0
        threadPool = []
        poolSize = 10
        if poolSize > leaveNum:
            poolSize = leaveNum
        while i < poolSize:
            name = str(j) + suffix
            thread = threading.Thread(target=getAndSaveHtml, args=(arr[j], name))
            threadPool.append(thread)
            i += 1
            j += 1
        leaveNum -= poolSize
        for th in threadPool:
            th.setDaemon(True)
            th.start()
        for th in threadPool:
            th.join()

def handle4(request):
    # 读取list.txt中的链接，分别获取页面，并将得到的html存于本地，按照排名依次命名1,2,3,4....（.txt）
    fullpath = os.path.dirname(__file__) + "\\tmp_html\\"
    listTxt = "list.txt"
    arr = []   # 将url存入arr中
    file = open(fullpath + listTxt, 'r')
    for line in file.readlines():
        line = line.strip()
        if not len(line):
            continue
        arr.append(line)

    multiThreadForHtmlFile(arr, ".htm")
    print "html pages have been fetched!"

    # 现在已经将数据存入tmp_html文件夹中，分别读取文件，建立soup，找到评论页面链接，找完后删掉这些文件
    arr2 = []  # 评论链接存在arr2中
    msg = ""
    for filename in glob.glob(fullpath + "*.htm"):
        # 分别建立soup，最后删除soup
        soup = BeautifulSoup(open(filename))
        try:
            link = soup.find('a', {'id':'acrCustomerReviewLink'})
            tmp = link["href"]
            tmp = urllib2.quote(tmp.encode("utf-8"))
            tmp = "http://www.amazon.cn" + tmp
            arr2.append(tmp)
            msg += tmp + "\n"
        except Exception,e:
            print filename
            pass
        del soup

    # 应该把arr2中的链接存到文件中，第三步会使用
    tool = Tool()
    tool.writeFile(fullpath + "comment_list.txt", msg , 'w')

    # 删掉.htm文件
    for filename in glob.glob(fullpath + "*.htm"):
        os.unlink(filename)


    print "html pages have been deleted!"

    # 然后，通过arr2，获取html，这次建立的文件名后缀为.htm
    multiThreadForHtmlFile(arr2, ".htm")

    print "comment pages have been fetched!"
    print "start to save data in DB..."
    # 然后，分析评论界面，

    # 首先将以前所有的数据is_last_add项置为0
    ProductNew.objects.update(is_last_add=0)
    last = ProductNew.objects.last()
    if last == None:
        rank = 0
    else:
        rank = last.rank
    i = 0
    for filename in glob.glob(fullpath + "*.htm"):
        # 分别建立soup，
        soup = BeautifulSoup(open(filename))
        # 产品排名
        rank += 1
        # ####################产品名称(修改于6月29号， 如果以后不可用可以改回来)
        # title = soup.find('a', {'class':'a-size-large a-link-normal'})
        title = soup.find('a', {'class':'a-link-normal'})
        product_url = title['href']
        title = title.string
        # 产品价格
        try:
            price = soup.find('span', {'class':'a-color-price arp-price'}).string.encode("utf-8")
            tool = Tool()
            price = tool.getPrice(price)
        except:
            continue

        # 综合打星
        total_star = soup.find('div',{'class':'a-row averageStarRatingNumerical'}).string
        pattern = re.compile(r'(\d.\d)')
        total_star = re.search(pattern, total_star)
        if total_star:
            total_star = total_star.group(1)
        # 找到总页码
        pagination = soup.find('ul', class_='a-pagination')
        if pagination != None:
            end_page_index =  len(pagination.contents) - 2
            allPageNum_str = pagination.contents[end_page_index].string
            allPageNum = tool.englishNum2intNum(allPageNum_str)
        else:
            allPageNum = 1

        # 将以上数据写入数据库
        ProductNew.objects.create(title=title, url=product_url, price=price, rank=rank,
                                  star = total_star, commentPageNum=allPageNum,
                                  comment_url = arr2[i], is_last_add=1)
        i += 1

        del soup

    # 删掉htm文件，他们只是评论的一页数据，没有什么用
    for filename in glob.glob(fullpath + "*.htm"):
        os.unlink(filename)

    return HttpResponse("Step 2 --- Done!")


def multiThreadForCommentHtmlFile(url, pageNum, rank):
    j = 1  # 控制外层循环
    leaveNum = pageNum
    while j <= pageNum:
        i = 0  # 控制内层循环
        poolSize = 10
        threadPool = []
        if poolSize > leaveNum:
            poolSize = leaveNum
        while i < poolSize:
            newUrl = url + "&pageNumber=" + str(j)
            filename = str(rank) + "-" + str(j) + ".comment"
            thread = threading.Thread(target=getAndSaveHtml, args=(newUrl, filename))
            threadPool.append(thread)
            i += 1
            j += 1
        leaveNum -= poolSize
        for th in threadPool:
            th.setDaemon(True)
            th.start()

        for th in threadPool:
            th.join()




def handle5(request):
    # 读ProductNew数据表中的comment_url， 然后使用handle1中方法分析
    data = ProductNew.objects.filter(is_last_add=1)
    length = len(data)
    # 循环爬取每个商品的评论， 评论页面用 rank-[page].comment 来存
    for item in data:
        rank = item.rank
        pageNum = item.commentPageNum
        url = item.comment_url
        multiThreadForCommentHtmlFile(url, pageNum, rank)

    return HttpResponse("Step 3 --- Done")


# 得到一个评论页面的信息，存到文件中去
def getOnePageNew(request, soup, pid):

    # 分析页面标签，得到产品名称、认为有用数量、每条评论中的打星、每条评论的留言者、每条评论的评论内容、评论时间
    # total_info = []

    global getOnePageNewMsg
    tool = Tool()
    fullpath = os.path.dirname(__file__) + "\\tmp_html\\"

    # 评论时间集合
    comment_date_arr = []
    comment_date_tmp = soup.find_all('span',class_='a-size-base a-color-secondary review-date')  # 当前页的所有评论时间
    for item in comment_date_tmp:
        str_tmp = item.string
        pattern = re.compile(u"于 (\d+)年(\d+)月(\d+)日")
        res = re.search(pattern, str_tmp)
        if res:
            date_tmp = res.group(1) + "/" + res.group(2) + "/" + res.group(3)
        else:
            date_tmp = ""
        comment_date_arr.append(date_tmp)

    # 回应数集合
    reply_num_arr = []
    reply_num_tmp = soup.find_all('span', class_='review-comment-total aok-hidden')  # 当前页的所有回复数目
    for item in reply_num_tmp:
        reply_num_arr.append(int(item.string))

    # 认为有用数集合
    help_arr = []
    help_tmp = soup.find_all('span', class_='cr-vote-buttons')
    for item in help_tmp:
        help_one = ""
        i_item = item.contents
        if len(i_item[0]) == 3:
            str_tmp = i_item[0].children.next().string
            pattern = re.compile(u"(\d+)")
            res = re.search(pattern, str_tmp)
            if res:
                help_one = res.group(1)
                print help_one
            else:
                help_one = "0"
        else:
            help_one = "0"
        help_arr.append(help_one)

    section = soup.find_all('div', class_='a-section review')  #各个评论块的所有数据
    i = 0
    for item in section:
        hasImage = 0
        if len(item) >= 7:
            hasImage = 1

        c_item = item.contents   # 将item的所有直接子节点以list的形式列出

        # 打星和评论总结
        star = ''
        star_t = c_item[0].children.next().string
        star_t = unicode(star_t.string)  #NavigatbleString -> String
        pattern = re.compile(r'(\d.\d)')
        star_t = re.search(pattern, star_t)
        if star_t:
            star = star_t.group(1)
            star = star.split('.')[0]
        suggestion = ""
        try:
            suggestion = c_item[0].contents[2].string
        except Exception, e:
            print "Hint : no suggestion"
            pass


        # 留言者
        user_url = c_item[1].contents[0].contents[2]["href"]
        user_name = c_item[1].contents[0].contents[2].string

        # 是否确认购买
        isConfirmed = 1
        row2 = c_item[2].contents
        if(len(row2) <= 2):
            isConfirmed = 0

        # 评论具体内容
        comment = ''
        comments_list = c_item[3].contents[0].children
        for item in comments_list:
            try:
                comment += unicode(item)
            except Exception, e:
                pass

        comment = tool.replace(comment)



        single_info = {"pid": int(pid), "star": star, "suggestion":suggestion, "user_url":user_url,"user_name":user_name,
                       "isConfirmed":isConfirmed, "comment":comment,"hasImage":hasImage,
                       "comment_date":comment_date_arr[i], "hasReply":reply_num_arr[i],
                       "help":help_arr[i]}
        # total_info.append(single_info)
        print "writing global variable getOnePageNewMsg..."
        getOnePageNewMsg += json.dumps(single_info) + "\n"

        i += 1


    # tool.writeFile(fullpath + "all_comment_items.txt", msg, 'a')

    del soup   # 释放内存

    # return total_info


def multiThreadForComment(request, arr):
    length = len(arr)

    j = 0
    while j < length:
        i = 0
        poolSize = 10
        leaveNum = length
        threadPool = []
        if poolSize > leaveNum:
            poolSize = leaveNum
        while i < poolSize and j < length:
            pid = arr[j].split("\\")[-1].split("-")[0]
            soup = BeautifulSoup(open(arr[j]))
            thread = threading.Thread(target=getOnePageNew, args=(request, soup, pid))
            threadPool.append(thread)
            i += 1
            j += 1
        leaveNum -= poolSize
        for th in threadPool:
            th.setDaemon(True)
            th.start()
        for th in threadPool:
            th.join()


def handle6(request):
    global getOnePageNewMsg
    fullpath = os.path.dirname(__file__) + "\\tmp_html\\"

    file_arr = []
    for filename in glob.glob(fullpath + "*.comment"):
        file_arr.append(filename)

    multiThreadForComment(request,file_arr)

    tool = Tool()
    tool.writeFile(fullpath + "all_comment_items.txt", getOnePageNewMsg, 'w')


    # 存入数据库
    # 首先将以前所有的数据is_last_add项置为0
    CommentNew.objects.update(is_last_add=0)
    file = codecs.open(fullpath + "all_comment_items.txt")
    i = 0
    total_info = []

    for item in file.readlines():
        i += 1
        item = item.decode("utf-8").encode('gbk')
        dictionary = json.loads(item)
        total_info.append(dictionary)

    file.close()

    for item in total_info:
        CommentNew.objects.create(pid = item["pid"],user_url = item["user_url"],user_name = item["user_name"],
                                  star = item["star"],suggestion = item["suggestion"],
                                  sugg_sen_pos = 0, sugg_sen_neg = 0,
                                  isConfirmed = item["isConfirmed"], comment = item["comment"],
                                  comment_count = len(item["comment"]),hasImage = item["hasImage"],
                                  comment_date = item["comment_date"],
                                  hasReply = item["hasReply"], help = item["help"], is_last_add = 1)

    return HttpResponse("Step 4 --- Done!")


def multiThreadForUserHtmlFile(data):
    length = len(data)
    j = 0  # 控制外层循环
    leaveNum = length
    while j < length:
        i = 0  # 控制内层循环
        poolSize = 10
        threadPool = []
        if poolSize > leaveNum:
            poolSize = leaveNum
        while i < poolSize and j < length:
            filename = str(data[j].pid) + "-" + str(data[j].id) + ".user"
            url = "http://www.amazon.cn" + data[j].user_url
            thread = threading.Thread(target=getAndSaveHtml, args=(url, filename))
            threadPool.append(thread)
            i += 1
            j += 1
        leaveNum -= poolSize
        for th in threadPool:
            th.setDaemon(True)
            th.start()

        for th in threadPool:
            th.join(15)

        time.sleep(10)   # 每执行十个线程，就睡十秒


def handle7(request):

    data = CommentNew.objects.filter(is_last_add=1)
    # 页面用pid-i.user来保存，pid为商品表的id，在CommentNew中为pid，i为序号
    multiThreadForUserHtmlFile(data)

    return HttpResponse("Step 5 --- Done!")


def getOnePageUserNew(request, soup, cid):
    global getOnePageUserNewMsg
    tool = Tool()
    profile = soup.find('div',class_='profile-info').contents
    profile_len = 0
    for item in profile:
        if isinstance(item, bs4.element.Tag):
            profile_len += 1

    # 名字
    name = soup.find('span', {'class':'profile-display-name break-word'}).string.strip()
    # 排名， 评论人数，觉得有用数
    rank = 0
    help_receive = 0
    help_useful = 0
    size_small_tmp = soup.select('.profile-info .a-size-small')
    try:
        if profile_len == 5:
            arr_tmp = soup.find_all('span',class_='a-size-large a-text-bold')
            rank = int(arr_tmp[0].string)

        elif profile_len == 4:
            rank = size_small_tmp[0].string
            r_index = rank.index('#')
            rank = rank[r_index+1:]
            rank = tool.englishNum2intNum(rank)
    except Exception, e:
        pass

    if type(rank) != int:
        rank = 0

    try:
        if len(size_small_tmp) >= 3:
            help_string = size_small_tmp[2].string
            pattern = re.compile('(\d+.*?\d+).*?(\d+.*?\d+)')
            resset = re.findall(pattern, help_string)
            if resset:
                help_receive = tool.englishNum2intNum(resset[0][0])
                help_useful = tool.englishNum2intNum(resset[0][1])
    except Exception, e:
        pass
    # 产品名集合
    pname_arr = []
    pname_arr_tmp = soup.select(".profile-item-container .product-title")
    for i in pname_arr_tmp:
        pname_arr.append(i.children.next())
    # 产品打星集合
    pstar_arr = []
    pstar_arr_tmp = soup.select(".profile-item-container .a-icon-star-medium")
    for i in pstar_arr_tmp:
        cla = i['class'][2]
        cla = cla.split('-')[-1]
        pstar_arr.append(int(cla))
    # 产品建议集合
    psuggestion_arr = []
    psuggestion_arr_tmp = soup.find_all('a',class_='a-size-base a-link-normal a-color-base review-title a-text-bold')
    for i in psuggestion_arr_tmp:
        psuggestion_arr.append(i.children.next().string)
    # 评论内容集合
    pcomment_arr = []
    pcomment_arr_tmp = soup.find_all('span',class_='a-size-base review-text pr-multiline-ellipses-container')
    for i in pcomment_arr_tmp:
        pcomment_arr.append(tool.replace(unicode(i.children.next().string)))

    print "one user page analysed over,start to write gloable variable..."
    # 产品数量
    plen = len(pname_arr)
    plen = 1
    i = 0
    while i < plen:
        single_info = {"cid":cid, "user_name":name,"rank":rank,"help_receive":help_receive,"help_useful":help_useful,
                       "pname":pname_arr[i],"pstar":pstar_arr[i],"psuggestion":psuggestion_arr[i],
                       "pcomment":pcomment_arr[i]}
        single_info_string = json.dumps(single_info)
        getOnePageUserNewMsg += single_info_string + "\n"
        i += 1


def multiThreadForUser(request,arr):
    length = len(arr)
    j = 0
    while j < length:
        i = 0
        poolSize = 10
        leaveNum = length
        threadPool = []
        if poolSize > leaveNum:
            poolSize = leaveNum
        while i < poolSize and j < length:
            a_tmp = arr[j].split("\\")[-1].split("-")
            cid = a_tmp[1].split(".")[0]
            soup = BeautifulSoup(open(arr[j]))
            thread = threading.Thread(target=getOnePageUserNew, args=(request, soup, cid))
            threadPool.append(thread)
            i += 1
            j += 1
        leaveNum -= poolSize
        for th in threadPool:
            th.setDaemon(True)
            th.start()
        for th in threadPool:
            th.join()

def handle8(request):

    global getOnePageUserNewMsg
    fullpath = os.path.dirname(__file__) + "\\tmp_html\\"
    file_arr = []

    for filename in glob.glob(fullpath + "*.user"):
        file_arr.append(filename)


    multiThreadForUser(request,file_arr)

    tool = Tool()
    tool.writeFile(fullpath + "all_user_items.txt", getOnePageUserNewMsg, 'w')

    print "all user page analysed over,start to write DB..."

    file = codecs.open(fullpath + "all_user_items.txt")
    i = 0
    total_info = []

    for item in file.readlines():
        i += 1
        item = item.decode("utf-8").encode('gbk')
        dictionary = json.loads(item)
        total_info.append(dictionary)
    file.close()
    # 写数据库
    for item in total_info:
        UserNew.objects.create(user_name=item["user_name"],rank=item["rank"],help_receive=item["help_receive"],
                               help_useful=item["help_useful"],pname=item["pname"],pstar=item["pstar"],
                               psuggestion=item["psuggestion"],pcomment=item["pcomment"],is_last_add=1)


    return HttpResponse("Step 6 --- Done!")

def getOnePageSimpleUserNew(request, soup, cid):
    global getOnePageUserNewSimpleMsg
    tool = Tool()
    name = soup.find('span',class_='public-name-text').string
    rank = -1
    help_useful = -1
    info = soup.find('div', class_='a-expander-content a-expander-partial-collapse-content')
    usefulinfo = soup.find('div', class_='a-row a-spacing-small a-spacing-top-small')
    if info:
        i_info = info.contents
        rank_str = i_info[1].children.next().string
        rank = tool.englishNum2intNum(rank_str)
    if usefulinfo:
        help_useful_contents = usefulinfo.contents[0].contents
        if len(help_useful_contents) == 3:
            help_useful_str = help_useful_contents[2].contents[0].string
            help_useful_str = help_useful_str[1:]
            help_useful = tool.englishNum2intNum(help_useful_str)


    single_info = {"cid":int(cid),"user_name":name,"rank":rank,"help_receive": -1,"help_useful":help_useful,
                   "pname":"","pstar":"","psuggestion":"",
                   "pcomment":""}
    single_info_string = json.dumps(single_info)
    getOnePageUserNewSimpleMsg += single_info_string + "\n"

    print "global variable getOnePageUserNewSimpleMsg written over..."


def multiThreadForSimpleUser(request,arr):
    length = len(arr)
    j = 0
    while j < length:
        i = 0
        poolSize = 10
        leaveNum = length
        threadPool = []
        if poolSize > leaveNum:
            poolSize = leaveNum
        while i < poolSize and j < length:
            cid = arr[j].split("\\")[-1].split("-")[1].split(".")[0]
            soup = BeautifulSoup(open(arr[j]))
            thread = threading.Thread(target=getOnePageSimpleUserNew, args=(request, soup, cid))
            threadPool.append(thread)
            i += 1
            j += 1
        leaveNum -= poolSize
        for th in threadPool:
            th.setDaemon(True)
            th.start()
        for th in threadPool:
            th.join()


def handle9(request):
    global getOnePageUserNewSimpleMsg
    fullpath = os.path.dirname(__file__) + "\\tmp_html\\"
    file_arr = []

    for filename in glob.glob(fullpath + "*.user"):
        file_arr.append(filename)



    multiThreadForSimpleUser(request,file_arr)

    tool = Tool()
    tool.writeFile(fullpath + "all_user_items.txt", getOnePageUserNewSimpleMsg, 'w')

    print "all user page analysed over,start to write DB..."

    file = codecs.open(fullpath + "all_user_items.txt")
    i = 0
    total_info = []

    for item in file.readlines():
        i += 1
        item = item.decode("utf-8").encode('gbk')
        dictionary = json.loads(item)
        total_info.append(dictionary)
    file.close()
    # 写数据库
    for item in total_info:
        UserNew.objects.create(cid=item["cid"],user_name=item["user_name"],rank=item["rank"],help_receive=item["help_receive"],
                               help_useful=item["help_useful"],pname=item["pname"],pstar=item["pstar"],
                               psuggestion=item["psuggestion"],pcomment=item["pcomment"],is_last_add=1)


    return HttpResponse("Step 6 --- Done!")

def sentiment(request):
    action = 'TextSentiment'
    config = {
        'Region': 'bj',
        'secretId': 'AKID0IvaSG3K260IgxG7dcRZITv54y0Wvn8L',
        'secretKey': 'ctzE5bet9iTWGXieMYMijN6yYRfW0vyA',
        'method': 'post'
    }
    total_info = []
    start = 0
    end = 0
    start_t = request.POST["start"]
    end_t = request.POST["end"]
    if start_t.strip():
        start = int(start_t)
    if end_t.strip():
        end = int(end_t)

    comment_arr = CommentNew.objects.all()[start:end]
    # for item in comment_arr:
    #     print str(item.id)
    for item in comment_arr:
        if item.comment == "":
            continue
        try:
            params = {
                "content" : item.comment.encode("utf-8"),
            }
            service = Wenzhi(config)
            result = service.call(action, params)
            res_json = json.loads(result)
            res_json["cid"] = item.id
            res_json["comment"] = item.comment
            total_info.append(res_json)

            CommentSentiment.objects.create(cid=res_json["cid"], comment=res_json["comment"],comment_count=len(res_json["comment"]),
                                            code=res_json["code"],
                                            message=res_json["message"], positive=res_json["positive"],
                                            negative=res_json["negative"])
            print str(item.id) + " : analysed over..."
        except:
            pass
    # print "now start to write DB..."
    # for item in total_info:
    #     CommentSentiment.objects.create(cid=item["cid"], comment=item["comment"],comment_count=len(item["comment"]),
    #                                     code=item["code"],
    #                                     message=item["message"], positive=item["positive"],
    #                                     negative=item["negative"])

    return HttpResponse("Sentiment Done")

def sentiment2(request):
    action = 'TextSentiment'
    config = {
        'Region': 'bj',
        'secretId': 'AKID0IvaSG3K260IgxG7dcRZITv54y0Wvn8L',
        'secretKey': 'ctzE5bet9iTWGXieMYMijN6yYRfW0vyA',
        'method': 'post'
    }
    total_info = []
    start = 0
    end = 0
    start_t = request.POST["start"]
    end_t = request.POST["end"]
    if start_t.strip():
        start = int(start_t)
    if end_t.strip():
        end = int(end_t)

    comment_arr = CommentNew.objects.all()[start:end]
    # for item in comment_arr:
    #     print str(item.id)
    for item in comment_arr:
        if item.suggestion == "":
            continue
        try:
            params = {
                "content" : item.suggestion.encode("utf-8"),
            }
            service = Wenzhi(config)
            result = service.call(action, params)
            res_json = json.loads(result)

            # 修改数据库
            CommentNew.objects.filter(id=item.id).update(sugg_sen_pos=res_json["positive"])
            CommentNew.objects.filter(id=item.id).update(sugg_sen_neg=res_json["negative"])
            print str(item.id) + " : analysed over..."
        except:
            pass


    print "Totally over..."


    return HttpResponse("Sentiment2 Done")



def deleteCommentFile(request):
    fullpath = os.path.dirname(__file__) + "\\tmp_html\\"
    for filename in glob.glob(fullpath + "*.comment"):
        os.unlink(filename)
    return HttpResponse("删除*.comment成功")
def deleteUserFile(request):
    fullpath = os.path.dirname(__file__) + "\\tmp_html\\"
    for filename in glob.glob(fullpath + "*.user"):
        os.unlink(filename)
    return HttpResponse("删除*.user成功")
def deleteGlobalVar(request):
    global getOnePageNewMsg
    global getOnePageUserNewMsg
    global getOnePageUserNewSimpleMsg
    getOnePageNewMsg = ""
    getOnePageUserNewMsg = ""
    getOnePageUserNewSimpleMsg = ""
    return HttpResponse("清空全局变量成功")

def test(request):
    str_tmp = "于 2016年4月20日"
    pattern = re.compile(r"于 (\d+)年(\d+)月(\d+)日")
    res = re.search(pattern, str_tmp)
    if res:
        print res.group(1)
        print res.group(2)
        print res.group(3)
    else :
        print "Nothing"
    return HttpResponse("OK")
