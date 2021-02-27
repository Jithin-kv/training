import requests
import json
import lxml.html
url='https://olx.com.bh/en/properties/'
h={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
html=requests.get(url=u,headers=h)
response=lxml.html.fromstring(html.content)
next_url=response.xpath('//span[contains(text(),"Next")]//parent::a/@href')
next_url=" ".join(next_url)
while next_url:
       propert=response.xpath('//div[contains(@class,"ads__item__info")]/a/@href')
       for link in propert: 
                  f=open('property.txt','a') 
                  f.write(link +'\n') 
                  f.close() 
       requests.get(next_url,headers=h) 
       next_urls=response.xpath('//span[contains(text(),"Next")]//parent::a/@href')  
       next_url=next_urls[0].strip()  
       if next_urls: 
             continue 
       else :  
             break 
