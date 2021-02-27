import json                                                                                                                              
import pymongo                                                                                                                           
import lxml.html                                                                                                                         
import requests   
from urllib.parse import urljoin 
url="https://www.qatarliving.com/properties/residential/sale"                                                                            
h={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}    
html=requests.get(url,headers=h)                                                                                                         
response=lxml.html.fromstring(html.content)
client=pymongo.MongoClient()                                                                                                             
db=client['mydb1']                                                                                                                       
coll=db['collection1']
coll.create_index("url",unique=True) 
links=response.xpath('//a[@class="classified-detail-link"]/@href')

try:
  for link in links: 
         key="url"  
         url =urljoin('https://www.qatarliving.com/',link) 
         coll.insert({key:url}) 
except pymongo.errors.DuplicateKeyError:
     pass
     
coll2=db['collection2']     
coll2.create_index("property_id",unique=True)  
x=coll.find()     
try:
    for i in x:  
         #print(i) 
         link=i["url"] 
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
         coll2.insert_one({"property_id" : property_id,  
                            "urls" : urls,  
                            "category" : category,  
                             "title" : title,  
                           "description" : description ,  
                           "location" : location,  
                             "price" : price,          
                         "currency" :currency,                                                                                           
                          "bedrooms" : bedrooms,  
                          "bathrooms" : bathrooms,      
                             "broker": broker,                   
                            "furnished" : furnished}) 
except pymongo.errors.DuplicateKeyError:
              pass
