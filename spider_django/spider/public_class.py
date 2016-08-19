# coding: UTF-8
import re
import math
import string
import time
import datetime
#处理页面标签类
class Tool:
    #去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        #strip()将前后多余内容删除
        return x.strip()

    # 将英文数字（每三位数字隔一个逗号）转为正常的int型数字
    def englishNum2intNum(self, num):
        allPageNum_list = string.split(num, ',')
        allPageNum_list_len = len(allPageNum_list)
        allPageNum = 0
        k = 1
        for item in allPageNum_list:
            # print item
            t = int(item)
            allPageNum += t * math.pow(10, 3*(allPageNum_list_len-k))
            k += 1
        allPageNum = int(allPageNum)
        return allPageNum

    # 写文件
    def writeFile(self, filename, html, mode):
        # 测试 将html写入文件中
        file = open(filename, mode)
        try:
            file.write(html.encode('utf-8'))
        except UnicodeEncodeError,e:
            if hasattr(e, 'reason'):
                print e.reason
            print 'writing occurs error'
        print 'writing succeed'

    # 时间转为时间戳
    def time2stamp(self, year, month, day, hour=0, minute=0, second=0):
        dateC=datetime.datetime(year, month, day, hour, minute, second)
        timestamp=time.mktime(dateC.timetuple())
        return timestamp

    # 时间戳转时间
    def stamp2time(self, timestamp):
        ltime=time.localtime(timestamp)
        timeStr=time.strftime("%Y-%m-%d %H:%M:%S", ltime)
        return timeStr

    # 将带有英文月份的时间转成时间戳
    def engMon2stamp(self, str):
        eng_dict = {"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,
                    "July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
        arr = string.split(str,' ')
        month = int(eng_dict[arr[0]])
        year = int(arr[2])
        arr2 = string.split(arr[1],',')
        day = int(arr2[0])


        return self.time2stamp(year,month,day)

    def getPrice(self, str):
        i = 0;
        length = len(str)
        while i < length:
            if str[i] >= '0' and  str[i] <= '9':
                break
            i += 1
        return str[i:]


