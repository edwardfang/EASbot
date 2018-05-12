#!/usr/bin/env python3
# -*- coding=utf-8 -*-
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
        headers = urllib3.make_headers(keep_alive=True,
                                       accept_encoding='gzip, deflate, br', user_agent="Mozilla/5.0 \
            (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/58.0.3029.96 Safari/537.36")
        self.host = 'https://cas.sustc.edu.cn'
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.url = ""
        self.uid = None
        self.passwd = None

    def loginService(self, serviceURL=None):
        if not serviceURL:
            self.url = 'https://cas.sustc.edu.cn/cas/login'
        else:
            params = urlencode({"service": serviceURL})
            self.url = 'https://cas.sustc.edu.cn/cas/login?%s' % params
        r = self.session.get(self.url)
        result = self.__loginCAS(r.text)
        return result

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
        # logging.debug(postURL)
        r = self.session.post(url=postURL, data=fields)
        if "success" in r.text or "成功" in r.text:
            return True
        else:
            return False
        logging.debug(r)

    def getSession(self):
        return self.session
