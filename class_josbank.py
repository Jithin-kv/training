import requests
import lxml.html
from urllib.parse import urljoin
import pymongo
from pymongo import MongoClient
import logging
import json
import sys
import base64
db = MongoClient().josbank_2021_02_11
db.josbank_products.create_index("product_url", unique=True)
db.finishline_products.create_index("product_url",unique=True)
#category_url = "https://www.josbank.com/c/dress-shirts"
class Start():
    def __init__(self):
        self.logger = logging.getLogger()
        self.headers ={'authority': 'www.josbank.com',
          'method': 'GET',
          'path': '/p/1905-collection-slim-fit-plaid-nativa-trade-suit-with-brrr-deg-comfort-3UGC',
          'scheme': 'https',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'accept-encoding': 'gzip, deflate, br',
          'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
          'upgrade-insecure-requests': '1',
          'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
          }
        
    def start_request(self,url,product_urlxpath,next_urlxpath):
        try:
            html = requests.get(url,headers=self.headers)
            html.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.error(e)
        response = lxml.html.fromstring(html.content)
        product_urls = response.xpath(product_urlxpath)
        self.parse_product_listing(product_urls)
        next_page = response.xpath(next_urlxpath)
        if next_page:
            next_page=''.join(next_page)
            
            if next_page.startswith('https'):
               next_page=next_page
            else:
                next_page=urljoin('https://www.finishline.com',next_page)
        else:
            next_page=''
        if next_page:
            self.start_request(next_page,product_urlxpath,next_urlxpath)
                       ####parsing_producturls####
    def parse_product_listing(self,product_urls):
        for url in product_urls:
            if url.startswith('https'):
                self.parse_product(url)
            else:
                url=urljoin('https://www.finishline.com',url)
                self.parse_product(url)




                #####dataextraction######

class JosBank(Start):
    def __init__(self):
        super().__init__()
        self.product_urlxpath='//div[contains(@class,"product_image quick-view-wrapper")]//@href'
        self.next_urlxpath='//link[contains(@rel,"next")]//@href'
        self.start_request(argument_category_url,self.product_urlxpath,self.next_urlxpath)
    def parse_product(self,url):

        try:
            html = requests.get(url,headers=self.headers)
            html.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(e)
        response = lxml.html.fromstring(html.content)
        product_name = response.xpath(
            '//h1[contains(@class,"product-name")]/span/text()')
        brand=response.xpath(
            '//span[contains(@class,"visuallyhidden")]//text()')
        price=response.xpath(
            '//span[contains(@id,"offerPrice_")]//text()')
        product_description=response.xpath(
            '//div[contains(@id,"product_longdescription_")]//text()')
        breadcrumbs = response.xpath(
            '//li[contains(@class,"categoryBreadCrumb")]//span[contains(@itemprop,"name")]/text()')
        variants_xpath = response.xpath(
            '//div[contains(@id,"entitledItem")]//text()')
        image = response.xpath(
            '//div[@class="product-color-wrapper"]/img/@data-scene7set')
        list_s = response.xpath(
            '//ul[contains(@class,"facetSelect")]/li[contains(@class,"singleFacet leftNav0")]')
        filters=response.xpath('//form[@id="productsFacets"]/fieldset')  
                          ######datacleaning#######
        product_name = product_name[0] if product_name else ''
        brand="".join(brand[0]) if brand else''
        price ="".join(price[0].strip('\n')) if price else ''
        if price.startswith('$'):
            currency="USD"
        else: ''
        product_description = "".join(product_description[0]) if product_description else''
        variants_xpath = " ".join(variants_xpath)
        variants_json = json.loads(variants_xpath)
        variants_list=[]
        for i in variants_json:
            attributes = i["Attributes"].keys()
            variants_dict = {}
            for i in attributes:
                variants_key = i.split('_')
                key = variants_key[0]
                value = variants_key[1]
                variants_dict.update({key:value})
            variants_list.append(variants_dict)
        image= image[0].split(',') if image else ''
        image_url=[]
        for i in image :
            image_= i.split(';')
            for i in image_:
                image_s = i.split(',')[0]
                image_s = urljoin("https://image.josbank.com/is/image/",image_s)
            image_url.append(image_s)


        
        try:
            html = requests.get(argument_category_url,headers=self.headers)
            html.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.error(e)
        response = lxml.html.fromstring(html.content)
        listing_dict = {}
        for i in list_s:
           key = i.xpath('a//text()') 
           key = [x.strip() for x in key if x.strip()] 
           value = i.xpath('ul/li//text()') 
           value = [x.strip() for x in value if x.strip()] 
           key="".join(key) 
           print(listing_dict.update({key:value})) 
        filter_dict = {}
        for ele in filters:
            key=i.xpath('legend/text()')
            value=i.xpath('div//span[@class="outline"]/span[contains(@id,"facetLabel")]/text()')
            key="".join(key) 
            print(filter_dict.update({key:value}))



        data = {"product_url":url,
                "product_name":product_name,
                "brand":brand,
                "price":price,
                "currency":currency,
                "breadcrumbs":breadcrumbs,
                "product_description":product_description,
                "variants":variants_list,
                "imageurl":image_url,
                
                }
        try:
            db.josbank_products.insert_one(data)
        except pymongo.errors.DuplicateKeyError:pass

class Finishline(Start):
    def __init__(self):
        super().__init__()
        self.product_urlxpath='//div[contains(@class,"product-card")]/@data-baseurl'
        self.next_urlxpath='//a[contains(@class,"button pag-button next ")]/@href'
        self.start_request(argument_category_url,self.product_urlxpath,self.next_urlxpath)
    
    def parse_product(self,url):                                                                        
        try:
            html = requests.get(url,headers = self.headers)
            html.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.error(e)
        response = lxml.html.fromstring(html.content)
        self.product_base_url = url.split('?')[0]
        #xpath
        xpath_name = '//div[@class="row column mt-1"]/h1[contains(@class,"titleDesk")]/text()'
        xpath_brand = '//div[@class="row column mt-1"]/h1[contains(@class,"titleDesk")]/@data-vendor'
        xpath_breadcrum = '//ul[@class="breadcrumbs"]/li/a//text()'
        xpath_currency = '//div[contains(@class,"productPrices")]//span/text()'
        xpath_description = '//div[@id="productDescription"]//text()'
        #extract
        name = response.xpath(xpath_name)
        brand = response.xpath(xpath_brand)
        breadcrumbs = response.xpath(xpath_breadcrum)
        currency = response.xpath(xpath_currency)
        description = response.xpath(xpath_description)
        price_color_list,variants_list=self.variance(url)

        #cleaning
        name = ' '.join(name).strip()
        brand = ' '.join(brand)
        breadcrumbs = [i.strip() for i in breadcrumbs]
        breadcrumbs = list(filter(None,breadcrumbs))
        currency = currency[0] if currency else ''
        currency = currency[0]

        description = ' '.join([i.strip() for i in description])
        finishline ={"product_url": url,
                    "name": name,
                    "brand": brand,
                    "breadcrumbs": breadcrumbs,
                    "price and color":price_color_list,
                    "image_list": image_url_list,
                    "variants":variants_list,
                    "currency": currency,
                    "description":description
                    }
        try:
            db.finishline_products.insert_one(finishline)
        except pymongo.errors.DuplicateKeyError:
            pass
        
        ###  extract variance data ######
    def variance(self,url):
        try:
            html = requests.get(url,headers = self.headers)
            html.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.logger.error(e)
        response = lxml.html.fromstring(html.content)
        pro_id = url.split('/')[-1].split('?')[0]
        base_url = 'https://www.finishline.com/store/browse/json/productSizesJson.jsp?productId='
        variants_url = base_url+pro_id
        data = requests.get(variants_url, headers = self.headers)   
        response = lxml.html.fromstring(data.content)
        variants_data = response.xpath('//text()')
        variants_data = ' '.join(variants_data)
        variants_json = {}
        variants_list = []
        id_list = []
        try:
            variants_json = json.loads(variants_data)
        except json.decoder.JSONDecodeError as errors:
            self.logger.error(errors)
        if variants_json:   
            variants_dict = variants_json["productSizes"]
            del variants_dict[-1]
            for i in variants_dict: 
                sku = base64.b64decode(i["sku"])
                Sku = sku[3: ]
                stockLevel = base64.b64decode(i["stockLevel"])
                product_id = i["productId"]   
                if product_id not in id_list:
                    id_list.append(product_id)
                json_dict = {"size" : i["sizeValue"],
                        "Sku" :int(Sku),
                        "stocklevel" : int(stockLevel) }
                variants_list.append(json_dict)


        ### extract price and color  ####
        price_color_list = []
        image_url_list = []
        for i in id_list:    
            styleId = i.split('_')[0]
            colorId = i.split('_')[1]   
            pro_url = self.product_base_url+'?'+'styleId='+styleId+'&colorId='+colorId
            data = requests.get(pro_url, headers = self.headers)
            response = lxml.html.fromstring(data.content)
            ##xpath and extract
            price = response.xpath('//div[contains(@class,"productPrices")]//span[@class="fullPrice"]/text() | //div[contains(@class,"productPrices")]//span[@class="nowPrice"]/text()')
            price = price[0] if price else ''
            color = response.xpath('//div[@id="styleColors"]//text()')
            image = response.xpath('//div[contains(@class,"thumbSlide")]//img/@data-thumbsrc')
            #cleaning
            color = ' '.join(color).strip()
            image_url = {"image_url":image}
            image_url_list.append(image_url)
            price_color = {"price":price,
                        "color":color}
            price_color_list.append(price_color) 

        return(variants_list,price_color_list,image_url_list)
        

argument_category_url= sys.argv[1]
if (argument_category_url.startswith('https://www.josbank.com')):
    obj = JosBank()
else:
 (argument_category_url.startswith('https://www.finishline.com'))
 obj=Finishline()

