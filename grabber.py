from cas import CASSession
from urllib.parse import urlparse, parse_qs, urlencode
from lxml import etree
import logging
import time
import json

class Grabber(object):
    operator = {0:'fawxk', 1:'ggxxkxk', 2:'knjxk', 3:'bxqjhxk'}

    def __init__(self):
        self.session = None
        self.uid = None
        self.passwd = None
        self.courselist = list()
        self.delay = 100
        self.threadCount = 1
        self.xklist = list()

    def getCourseList(self):
        showlist = [(courseNo, Grabber.operator[courseType]) for (courseNo, courseType) in self.courselist]
        return showlist

    def setspeed(self, delay, threadCount):
        self.delay = delay
        self.threadCount = threadCount

    def init(self):
        c = CASSession()
        c.setAuthInfo(self.uid,self.passwd)
        c.loginService("http://jwxt.sustc.edu.cn/jsxsd/")
        self.session = c.getSession()
        

    def setloginInfo(self, username, password):
        self.uid = username
        self.passwd = password

    def addcourse(self, courseNo, courseType = 0):
        '''
        coursetype: 0-fawxk, 1-ggxxkxk, 2-knjxk, 3-bxqjhxk
        '''
        self.courselist.append((courseNo,courseType))
    def saveConfig(self,filename = 'grabber-conf.json'):
        from collections import OrderedDict
        configstr = OrderedDict(delay=self.delay, uid=self.uid, password=self.passwd, courseList=self.courselist)
        with open(filename,'w') as file:
            file.write(json.dumps(configstr))

    def loadConfig(self, filename = 'grabber-conf.json'):
        text = None
        with open(filename,'r') as file:
            text = file.read()
        config = json.loads(text)
        self.uid = config['uid']
        self.passwd = config['password']
        self.courselist = config['courseList']
        self.delay = int(config['delay'])
        logging.info(config)

    def start(self):
        if len(self.courselist) < 1:
            return
        while(True):
            if len(self.xklist) < 1:
                self.xklist = self.__getxklist(self.session)
                logging.info("waiting for the entrance")
            else:
                for course in self.courselist:
                    ## Important here! self.xklist[0][1]
                    ## http://jwxt.sustc.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid=2A018810EA3C4DCFAD5A971752AD1A0D
                    self.session.get(url="http://jwxt.sustc.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid="+self.xklist[0][1])
                    r = self.session.get(url="http://jwxt.sustc.edu.cn/jsxsd/xsxkkc/%sOper?jx0404id=%s&xkzy=&trjf=" % (Grabber.operator[course[1]],course[0]))
                    result = json.loads(r.text)
                    if 'success' in result.keys():
                        logging.info("course: %s, response: %s, message: %s" % (course[0], result['success'], result['message']))
                    else:
                        logging.info("no such course")
            time.sleep(self.delay/1000)
        #test = ('201720181000695',0)
        


    def __getxklist(self,session):
        '''
        # r = s.get(url="http://jwxt.sustc.edu.cn/jsxsd/xsxk/xklc_list")
        # first row head | the rest content
        # time page.xpath("/html/body//table[@id='tbKxkc']/tr[2]/td[3]/text()[1]")[0]
        # url page.xpath("/html/body//table[@id='tbKxkc']/tr[2]/td[4]/a/@href[1]")[0]
        '''
        r = session.get(url="http://jwxt.sustc.edu.cn/jsxsd/xsxk/xklc_list")
        page = etree.HTML(r.text)
        # get the list
        row_count = len(page.xpath("/html/body//table[@id='tbKxkc']/tr"))
        row_exist = len(page.xpath("/html/body//table[@id='tbKxkc']/tr[2]/td"))
        xklist = list()
        if row_exist>1:
            for row in range(row_count-1):
                item_time = page.xpath("/html/body//table[@id='tbKxkc']/tr[%d]/td[3]/text()[1]" % (row+2))[0]
                item_url = page.xpath("/html/body//table[@id='tbKxkc']/tr[%d]/td[4]/a/@href[1]" % (row+2))[0]
                parsed = urlparse("/jsxsd/xsxk/xklc_view?jx0502zbid=2A018810EA3C4DCFAD5A971752AD1A0D")
                query = parse_qs(qs = parsed.query)
                print(item_time,query['jx0502zbid'][0])
                xklist.append((item_time,query['jx0502zbid'][0]))
        return xklist

def main():
    logging.basicConfig(level=logging.INFO)
    g = Grabber()
    isloadconfig = input("Load the config file? y or n [y]:")
    if isloadconfig == 'y' or isloadconfig =='':
        g.loadConfig()
    else:
        uid = "11510493"
        passwd = "***REMOVED***"
        g.setloginInfo(uid,passwd)
        total = input("Please input the total number of courses you want to grab:")
        if total == '':
            total = 0
        try:
            total = int(total)
        except ValueError:
            print("That's not an int!")
        for i in range(int(total)):
            courseCode = input("Course code:")
            courseType = input("0-fawxk, 1-ggxxkxk, 2-knjxk, 3-bxqjhxk c-cancel \nCourse Type (default 0):")
            if courseCode == '' or courseType == 'c':
                continue
            if courseType == '':
                courseType = 0
            g.addcourse(courseCode,int(courseType))
        print(g.getCourseList())
        input("Please Check, Press enter to continue")
        input("Press enter to start")
        g.saveConfig()
    g.init()
    g.start()


if __name__== "__main__":
    main()