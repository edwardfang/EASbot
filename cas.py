
import requests
import urllib3
from lxml import etree
from bs4 import BeautifulSoup
from urllib.parse import urlparse,parse_qs,urlencode

# urllib3.disable_warnings()

headers = urllib3.make_headers(keep_alive=True,accept_encoding='gzip, deflate, br',user_agent="Mozilla/5.0 \
 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36")
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
'''
CAS login
'''
# id = input("Your ID:")
# passwd = input("Password:")
host1 = 'https://cas.sustc.edu.cn'
host2 = 'http://jwxt.sustc.edu.cn'
uid = "11510493"
passwd = "***REMOVED***"
s = requests.Session()
s.headers.update(headers)
# http = urllib3.PoolManager(headers = headers,cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
s.get('http://jwxt.sustc.edu.cn/jsxsd/')
# r = http.request('GET',)
r = s.get('https://cas.sustc.edu.cn/cas/login?service=http%3A%2F%2Fjwxt.sustc.edu.cn%2Fjsxsd%2F')
soup = BeautifulSoup(r.text,"html.parser")
btn_row = soup.find_all("section",{"class":"row btn-row"})[0]
fields = {'username':uid,"password":passwd}
for input_ in btn_row.find_all("input"):
    fields[input_['name']] = input_['value']

actionURL = host1 + soup.find_all("form",{'id':'fm1'})[0]['action']
# print(actionURL)
# print(fields)
r = s.post(url=actionURL, data=fields)
# r = s.post(actionURL,fields=fields)
# Successful Login
#print(r.text)

# r = s.get(url="http://jwxt.sustc.edu.cn/jsxsd/xsxk/xklc_list")
# first row head | the rest content
# time page.xpath("/html/body//table[@id='tbKxkc']/tr[2]/td[3]/text()[1]")[0]
# url page.xpath("/html/body//table[@id='tbKxkc']/tr[2]/td[4]/a/@href[1]")[0]

def getxklist():
    r = s.get(url="http://jwxt.sustc.edu.cn/jsxsd/xsxk/xklc_list")
    page = etree.HTML(r.text)
    # get the list
    row_count = len(page.xpath("/html/body//table[@id='tbKxkc']/tr"))
    xklist = list()
    if row_count>1:
        for row in range(row_count-1):
            item_time = page.xpath("/html/body//table[@id='tbKxkc']/tr[%d]/td[3]/text()[1]" % (row+2))[0]
            item_url = page.xpath("/html/body//table[@id='tbKxkc']/tr[%d]/td[4]/a/@href[1]" % (row+2))[0]
            parsed = urlparse("/jsxsd/xsxk/xklc_view?jx0502zbid=2A018810EA3C4DCFAD5A971752AD1A0D")
            query = parse_qs(qs = parsed.query)
            print(item_time,query['jx0502zbid'][0])
            xklist.append((item_time,query['jx0502zbid'][0]))
    return xklist

xklist = getxklist()
r = s.get(url="http://jwxt.sustc.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid="+xklist[0][1])
r = s.get(url="http://jwxt.sustc.edu.cn/jsxsd/xsxkkc/fawxkOper?jx0404id=201720181000695&xkzy=&trjf=")
print(r.text)
