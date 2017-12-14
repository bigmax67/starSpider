import re
import string
import xlwt
import datetime
import urllib.request
from urllib.parse import quote

# - 类定义 与 模型转化

class Idols(object):

    def __init__(self,name,constellation,nickname,age,achievement):
        self.name = name
        self.constellation=constellation
        self.nickname = nickname
        self.age = age
        self.achievement = achievement
class Singer(Idols):

    def __init__(self,music,concertNumber):
        self.music = music
        self.concertNumber = concertNumber
class Performer(Idols):

    def __init__(self,movie,movieNumber):
        self.movie = movie
        self.movieNumber = movieNumber

# 字典转模型
def getIdolBasicModel(dict):

    idol = Idols(0,0,0,0,0)

    idol.name = dict["name"]
    idol.nickname = dict["nickname"]
    idol.constellation = dict["constellation"]
    idol.achievement = dict["achievement"]
    idol.age = dict["age"]

    return idol

# - 流程方法

# 获取 所有的列表信息 ex:index1.html index2.html
def getIndexUrlLists(url):

    source = getHTMLText(url);

    result = getPatterText('<div id="page">\n      [\s\S*]+\n<div class="clear"></div>\n      </ul>\n    </div>\n<div class="footer_bg">',source);

    urlList = []

    for item in result:
        itemResult = getPatterText('<a.*?href="(.*?)">.*?</a>',item)
        urlList.extend(itemResult)

    sortlist = list(set(urlList))
    sortlist.sort(key=itemResult.index)

    combineList = []

    for indexN in sortlist:
        combineUrl = url + indexN
        combineList.append(combineUrl)

    return combineList

# 获取 根据列表去获取明星名字
def getStarList(url):

    source = getHTMLText(url)
    result = getPatterText('<div class="ulbox">[\s\S*]+<div id="page">',source)
    startList = []

    for item in result:
        itemResult = getPatterText('alt="(.*?)"',item)
        startList.append(itemResult)

    return startList

# 拼装 获取所有的明星名字
def getAllStarNameList(urlList):

    allStarList = []

    for url in urlList:
        list = getStarList(url)
        allStarList.extend(list)

    return allStarList

# 拼装 单个明星的搜索url 成数组 ex:www.baidu.com/杨幂
def getStarInfoUrlList(list,url):

    starInfoUrlList = []

    for item in list:
        for o in item:
          singleInfoUrl = url + o
          starInfoUrlList.append(singleInfoUrl)

    return starInfoUrlList

# 获取 明星基本信息
def getStarBasicInfo(source):
    basicStarInfo = {}
    name = getStarName(source)
    nickname = getStarNickName(source)
    constellation = getStarConstellation(source)
    achievement = getStarAchievemnt(source)
    age = getStarAge(source)

    basicStarInfo["name"] = name
    basicStarInfo["nickname"] = nickname
    basicStarInfo["constellation"] = constellation
    basicStarInfo["achievement"] = achievement
    basicStarInfo["age"] = age

    return basicStarInfo

# 获取 单个明星列表中 所有明星的信息
def getStarInfo(url):

    source = getHTMLText(url)

    type = getStarType(source)

    basicStarInfo = {}

    result = getPatterText('<dt class="basicInfo-item name">[\s\S*]+<div class="anchor-list',source)

    idol = Idols(0,0,0,0,0)

    for item in result:
        dict = getStarBasicInfo(item)
        idol = getIdolBasicModel(dict)

    type = getStarType(source)

    starList = []

    print(idol.name)

    if type == 'singer':

        singer = Singer(0,0)
        singer.music = getTypicWorks(source)
        singer.concertNumber = getSingerConcertNumber(source)

        singer.name = idol.name
        singer.nickname = idol.nickname
        singer.achievement=idol.achievement
        singer.constellation=idol.constellation
        singer.age = idol.age

        starList.append(singer)

    elif type == 'actor':
        performer = Performer(0,0)
        performer.movie = getTypicWorks(source)
        performer.movieNumber = getPerformerMovieNumber(source)

        performer.name = idol.name
        performer.nickname = idol.nickname
        performer.achievement=idol.achievement
        performer.constellation=idol.constellation
        performer.age = idol.age

        starList.append(performer)

    else:
        return

    return starList

# 获取 所有明星的信息
def getAllStarList(allStarInfoUrlList):

    allstarList = []

    for item in allStarInfoUrlList:
        list = getStarInfo(item)
        for single in list:
            allstarList.append(single)

    return allstarList

# 写入 明星信息
def writeExcel(localUrl,list):

    workbook = xlwt.Workbook()
    sheet1 = workbook.add_sheet('starInfo',cell_overwrite_ok=True)

    sheet1.write(0,0,"姓名")
    sheet1.write(0, 1, "星座")
    sheet1.write(0, 2, "别名")
    sheet1.write(0, 3, "年龄")
    sheet1.write(0, 4, "成就")
    sheet1.write(0, 5, "代表作")
    sheet1.write(0, 6, "代表作数目")

    index = 0

    for star in list:

        index = index + 1

        sheet1.write(index, 0, star.name)
        sheet1.write(index, 1, star.constellation)
        sheet1.write(index, 2, star.nickname)
        sheet1.write(index, 3, star.age)
        sheet1.write(index, 4, star.achievement)

        if isinstance(star,Singer):

            sheet1.write(index, 5,star.music)
            sheet1.write(index, 6, star.concertNumber)

        elif isinstance(star,Performer):

            sheet1.write(index, 5,star.movie)
            sheet1.write(index, 6, star.movieNumber)

        else:
            return

    workbook.save(localUrl)

# - 获取明星信息方法

# 获取 明星年龄
def getStarAge(source):

    result = getPatterText('<dt class="basicInfo-item name">出生日期</dt>\n<dd class="basicInfo-item value">\n(.*?)\n</dd>??',
                          source)
    str = ""
    for item in result:
        str = str + item

    cleanResult = stripTagSimple(str)

    if cleanResult.find("年") != -1 :
        cleanResult = cleanResult[0:4]
        age = datetime.datetime.now().year - int(cleanResult)
        return  age
    else:
        return "未知"

# 获取 明星昵称
def getStarNickName(source):

    result = getPatterText('<dt class="basicInfo-item name">别&nbsp;&nbsp;&nbsp;&nbsp;名</dt>\n<dd class="basicInfo-item value">\n(.*?)\n</dd>??',
                          source)
    str = getCombineStr(result)
    tempStr = stripTagSimple(str)
    return  tempStr

# 获取 明星星座
def getStarConstellation(source):

    result =  getPatterText('<dt class="basicInfo-item name">星&nbsp;&nbsp;&nbsp;&nbsp;座</dt>\n<dd class="basicInfo-item value">\n(.*?)\n</dd>??',
                          source)
    str = getCombineStr(result)
    tempStr = stripTagSimple(str)
    return tempStr

# 获取 明星名字
def getStarName(source):

    result = getPatterText('<dt class="basicInfo-item name">中文名</dt>\n<dd class="basicInfo-item value">\n(.*?)\n</dd>??',
                         source)
    str = getCombineStr(result)
    tempStr = stripTagSimple(str)
    return  tempStr

# 获取 明星成就
def getStarAchievemnt(source):

    achievement = getPatterText('<dt class="basicInfo-item name">主要成就</dt>\n<dd class="basicInfo-item value">\n(.*?)</dd>??',
                         source)

    list = []
    for item in achievement:
        result = stripTagSimple(item)
        list.append(result)

    str = ",".join(list)
    clearStr = clearAchievement(str)

    return str

# 获取 明星的类型(演员或歌手)
def getStarType(source):

    result = getPatterText('drama-actor',source)

    if len(result) == 0:
        return 'singer'
    else:
        return 'actor'

# 获取 明星的代表作
def getTypicWorks(source):

    result = getPatterText('<dt class="basicInfo-item name">代表作品</dt>\n<dd class="basicInfo-item value">[\s\S*]+\n</dd>\n<dt class="basicInfo-item name">主要成就</dt>',source)

    list = []

    for item in result:
        itemResult = getPatterText('<a target=_blank .*?">(.*?)</a>',item)
        for single in itemResult:
            list.append(single)

    str = ",".join(list)
    clearStr = stripTagSimple(str)

    return  clearStr

# 获取 演员的电影数量
def getPerformerMovieNumber(source):

    result = getPatterText('<a name="canyandianying2" class="lemma-anchor " ></a>[\s\S*]+<a name="参演电视剧" class="lemma-anchor " ></a>',source)

    count = 0

    for item in result:
        itemResult = getPatterText('<p>\n<b class="title"><a target=_blank href=".*?".*?>(.*?)</a></b><b>.*?</b>\n</p>',item)
        count = count + len(itemResult)

    return  count

# 获取 歌手的演唱会数量
def getSingerConcertNumber(source):

    result = getPatterText('<tr>\s<td class="normal ">\s<b>.*?</b>\s</td>\s<td class="normal ">\s<b>.*?</b>\s</td>\s<td class="normal ">\s<b>.*?</b>\s</td>\s<td class="toggle" width="45">\s<a class="toggle-button collapsed" href="javascript:;" data-id=".*?"></a>\s</td>\s</tr>',source)

    count = 0

    for item in result:

        itemResult = getPatterText('<tr>\n<td class="normal ">\n<b>.*?</b>\n</td>\n<td class="normal ">\n<b>.*?</b>\n</td>\n<td class="normal ">\n<b>(.*?)</b>\n</td>\n<td class="toggle" width="45">\n<a class="toggle-button collapsed" href="javascript:;" data-id=.*?></a>\n</td>\n</tr>',item)

        for item in itemResult:
            count = count + int(item);

    return count

# - 辅助方法

# 获取html
def getHTMLText(url):
    printUrl = quote(url, safe=string.printable)
    return urllib.request.urlopen(printUrl).read().decode()

# 清空多余的HTML标签
def stripTagSimple(htmlStr):

    dr = re.compile(r'</?\w+[^>]*>',re.S)
    htmlStr =re.sub(dr,'',htmlStr)
    removeStrong = re.compile('(<strong>|</strong>|<span>|</span>)')
    content1 = re.sub(removeStrong, "", htmlStr)
    replaceLine = re.compile('(&nbsp)', re.S)
    content = re.sub(replaceLine, " ", content1)

    return  content

# 针对成就一项 清除对应的字段
def clearAchievement(str):
    clearStr = str.replace('&nbsp','')
    clearStr = clearStr.replace('收起','')
    clearStr = clearStr.replace('主要成就','')
    clearStr = clearStr.replace('展开', '')
    rereobj = re.compile('[.*?]')
    clearStr = rereobj.subn("", str)
    return clearStr

# 拼接list中的字符串
def getCombineStr(list):
    str =""
    for item in list:
        str = str + item
    return str

# 获取正则后的信息
def getPatterText(regex,source):
    pattern = re.compile(regex,re.S)
    result = re.findall(pattern, source)
    return result

# - 封装主方法

def cwjMain():

    star_list_url = "http://www.mingxing.com/list/neidi/"
    star_info_url = "https://baike.baidu.com/item/"
    star_excel_address = "/Users/eric/Desktop/CCSecret/webSpider.xls"

    # 获取有哪些明星列表
    urlList = getIndexUrlLists(star_list_url)
    # 获取所有明星的名字
    allStarList = getAllStarNameList(urlList)
    # 拼装搜索单个明星的地址
    allStarInfoUrlList = getStarInfoUrlList(allStarList, star_info_url)
    # 获取明星的信息
    allstarList = getAllStarList(allStarInfoUrlList)
    # 写入明星信息
    writeExcel(star_excel_address, allstarList)

# 开始爬虫

cwjMain()







