#!/usr/bin/env python3
'''
class for CAS authorization
'''
from urllib.parse import urlparse, parse_qs, urlencode
import logging
from lxml import etree
import requests
import urllib3


class CASSession(object):
    '''
    CAS login
    '''

    def __init__(self):
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0)
        # Gecko/20100101 Firefox/24.0'}
        headers = urllib3.make_headers(keep_alive=True, \
            accept_encoding='gzip, deflate, br', user_agent="Mozilla/5.0 \
            (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/58.0.3029.96 Safari/537.36")
        self.host = 'https://cas.sustc.edu.cn'
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.url = ""
        self.uid = None
        self.passwd = None

    def loginService(self, serviceURL):
        params = urlencode({"service": serviceURL})
        self.url = 'https://cas.sustc.edu.cn/cas/login?%s' % params
        logging.debug(self.url)
        r = self.session.get(self.url)
        # if not login CAS
        self.__loginCAS(r.text)

    def setAuthInfo(self, uid, passwd):
        self.uid = uid
        self.passwd = passwd

    def __loginCAS(self, pagetext):
        page = etree.HTML(pagetext)
        inputs = page.xpath("/html//form[@id='fm1']//input")
        fields = {'username': self.uid, "password": self.passwd}
        logging.debug(inputs)
        for input_ in inputs:
            name = input_.xpath("@name")[0]
            value = input_.xpath("@value")
            if value:
                value = value[0]
            if value != '':
                fields[name] = value
        logging.debug(fields)
        postURL = self.url
        # actionURL = self.host + page.xpath("/html//form[@id='fm1']/@action")[0]
        logging.debug(postURL)
        r = self.session.post(url=postURL, data=fields)
        logging.debug(r)

    def getSession(self):
        return self.session


def getxklist(session):
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
    xklist = list()
    if row_count > 1:
        for row in range(row_count - 1):
            item_time = page.xpath(
                "/html/body//table[@id='tbKxkc']/tr[%d]/td[3]/text()[1]" % (row + 2))[0]
            item_url = page.xpath(
                "/html/body//table[@id='tbKxkc']/tr[%d]/td[4]/a/@href[1]" % (row + 2))[0]
            # parsed = urlparse(
            #     "/jsxsd/xsxk/xklc_view?jx0502zbid=2A018810EA3C4DCFAD5A971752AD1A0D")
            parsed = urlparse(
                "/jsxsd/xsxk/xklc_view?jx0502zbid=334A7F7E4AB340C7913B2AB0A8FBE871")
            query = parse_qs(qs=parsed.query)
            print(item_time, query['jx0502zbid'][0])
            xklist.append((item_time, query['jx0502zbid'][0]))
    return xklist


def main():
    logging.basicConfig(level=logging.DEBUG)
    uid = "11510493"
    passwd = "***REMOVED***"
    c = CASSession()
    c.setAuthInfo(uid, passwd)
    c.loginService("http://jwxt.sustc.edu.cn/jsxsd/")
    s = c.getSession()
    xklist = getxklist(s)
    logging.debug(xklist)
    r = s.get(
        url="http://jwxt.sustc.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid=" + xklist[0][1])
    r = s.get(
        url="http://jwxt.sustc.edu.cn/jsxsd/xsxkkc/fawxkOper?jx0404id=201720182001072&xkzy=&trjf=")
    print(r.text)


if __name__ == "__main__":
    main()
