import requests 
import lxml.html 
from urllib.parse import urljoin 
import sys                                                                                                                               

url=sys.argv[1]                                                                                                    

headers ={'authority': 'www.josbank.com', 
          'method': 'GET', 
          'path': '/store/product/womens-adidas-originals-nmd-r1-casual-shoes/prod3030000?styleId=FV1787&colorId=001', 
          'scheme': 'https', 
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 
           'accept-encoding': 'gzip, deflate, br', 
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8', 
           'upgrade-insecure-requests': '1', 
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36', 
             }                                                                                                                              

html = requests.get(url,headers=headers) 
response = lxml.html.fromstring(html.content)                                                                                            

list_s = response.xpath(
  '//ul[contains(@class,"facetSelect")]/li[contains(@class,"singleFacet leftNav0")]') 
url_dict=[]
for elem in list_s:
  url_sub=elem.xpath('ul[contains(@class,"facetSelect")]/li[contains(@class,"singleFacet leftNav1")]/a/@href') 
  sub_name=elem.xpath('ul[contains(@class,"facetSelect")]/li[contains(@class,"singleFacet leftNav1")]/a//text()')
  sub_name=[x.strip() for x in sub_name if x.strip()]
  url_list=[]  
  for link in url_sub:  
    url_list.append(link)  
    data={} 
    for key in sub_name: 
      for value in url_list: 
        data.update({key:value}) 
  url_dict.append(data) 
print(url_dict) 
