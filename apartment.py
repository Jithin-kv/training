import requests                                                         

import lxml.html                                                        

import json           

h={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               'accept-encoding': 'gzip, deflate',
               'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
               'cache-control': 'no-cache',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36', }


f = open('test.txt') 
for link in f.readlines(): 
    link = link.strip() 
    prop=requests.get(link,headers=h) 
    res=lxml.html.fromstring(prop.content) 
    property_id = res.xpath('//link[@rel="shortlink"]/@href')
    property_id=" ".join(i.rsplit('/')[-1] for i in property_id) 
    urls=" ".join(res.xpath('//body/@data-entity-url')) 
    title=res.xpath('//h1/text()') 
    title=" ".join(sel.strip() for sel in title) 
    description=res.xpath('//div[contains(@class,"b-property-description")]/div/div/p//text()') 
    description=" ".join(sel.strip() for sel in description) 
    category=res.xpath('//span[@itemprop="name"]/text()') 
    category=" ".join(sel.strip() for sel in category) 
    location=" ".join(res.xpath('//div[contains(@class,"col-md-4 fa-location")]//p[2]/text()') )
     
    price=res.xpath('//div[contains(@class,"b-price-conditions--el-header")]/p[1]/text()') 
    price=" ".join(sel.strip() for sel in price) 
    currency=res.xpath('//div[contains(@class,"wrapper-desktop")]/div/div[1]/p[2]/text()') 
    currency=" ".join(sel.strip() for sel in currency) 
    bedrooms=res.xpath('//div[contains(@class,"b-feature Property bedrooms")]/p[last()]/text()') 
    bedrooms=" ".join(sel.strip() for sel in bedrooms) 
    bathrooms=res.xpath('//div[contains(@class,"b-feature Property bathrooms")]/p[last()]/text()') 
    bathrooms=" ".join(sel.strip() for sel in bathrooms) 
    furnished=res.xpath('//div[contains(@class,"b-feature Property furnish")]/p[last()]/text()') 
    furnished=" ".join(sel.strip() for sel in furnished) 
    broker=res.xpath('//div[contains(@class,"b-seller")]/p/a/text()') 
    broker=" ".join(sel.strip() for sel in broker) 
    dict_data = {"property_id" : property_id, 
              "urls" : urls, 
              "category" : category, 
               "title" : title, 
               "description" : description , 
               "location" : location, 
                "price" : price, 
                "currency" : currency, 
               "bedrooms" : bedrooms, 
                "bathrooms" : bathrooms, 
                "broker": broker, 
                "furnished" : furnished} 

    f1=open("data.json",  'a')  
    json.dump(dict_data, f1) 
    f1.write('\n')  
    f1.close()
f.close()   
  
                                                                                            


