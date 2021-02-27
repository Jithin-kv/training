import requests
import lxml.html
from urllib.parse import urljoin
import pymongo
from pymongo import MongoClient
import logging
import json
import sys


db = MongoClient().josbank_2021_02_11
db.josbank_products.create_index("product_url", unique=True)

logger = logging.getLogger()

                              
#category_url = "https://www.josbank.com/c/dress-shirts"
argument_category_url = sys.argv[1]

headers ={'authority': 'www.josbank.com',
          'method': 'GET',
          'path': '/p/1905-collection-slim-fit-plaid-nativa-trade-suit-with-brrr-deg-comfort-3UGC',
          'scheme': 'https',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'accept-encoding': 'gzip, deflate, br',
          'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
          'upgrade-insecure-requests': '1',
          'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
          }
                         
                         ####pagerequest####

def start_request(url):
    try:
        html = requests.get(url,headers=headers)
        html.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(e)
    response = lxml.html.fromstring(html.content)
    product_urls = response.xpath('//div[contains(@class,"product_image quick-view-wrapper")]//@href')
    parse_product_listing(product_urls)
    next_page = response.xpath(
    	'//link[contains(@rel,"next")]//@href')
    #if next_page:
       	#start_request(next_page[0])
 
                       ####parsing_producturls####

def parse_product_listing(product_urls):
	for url in product_urls: 
		parse_product(url) 
		break
		
		

		

              
                #####dataextraction######

def parse_product(url):
        try:
            html = requests.get(url,headers=headers)
            html.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(e)
        response = lxml.html.fromstring(html.content)
        product_name = response.xpath(
        	'//h1[contains(@class,"product-name")]/span/text()')
        price=response.xpath(
        	'//span[contains(@id,"offerPrice_")]//text()')
        product_description=response.xpath(
        	'//div[contains(@id,"product_longdescription_")]//text()')
        breadcrumbs = response.xpath(
        	'//li[contains(@class,"categoryBreadCrumb")]//span[contains(@itemprop,"name")]/text()') 
        variants_xpath = response.xpath(
        	'//div[contains(@id,"entitledItem")]//text()')
        

        

                          ######datacleaning#######
       
        product_name = product_name[0] if product_name else ''
        price ="".join(price[0].strip('\n')) if price else ''
        
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
            
               


        data = {"product_url":url,
                "product_name":product_name,
                "price":price,
                "breadcrumbs":breadcrumbs,
                "product_description":product_description,
                "variants":variants_list,
                } 
        try:
        	db.josbank_products.insert_one(data)
        except pymongo.errors.DuplicateKeyError:pass

start_request(argument_category_url )

