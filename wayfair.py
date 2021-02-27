import requests
import lxml.html
from urllib.parse import urljoin
import pymongo
from pymongo import MongoClient


db = MongoClient().wayfair_2021_02_08
db.products.create_index("product_url", unique=True)

category_url = "https://www.wayfair.com/furniture/sb0/sofas-c413892.html" 
headers = {
        'authority': 'www.wayfair.com', 
        'method': 'GET', 
        'path': '/furniture/sb0/sofas-c413892.html', 
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3; =0.9', 
        'accept-encoding': 'gzip, deflate, br', 
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8', 
        'upgrade-insecure-requests': '1' ,
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        }
                  ####pagerequest####
def start_request(url):
    html = requests.get(url,headers=headers)
    response = lxml.html.fromstring(html.content)
    product_urls = response.xpath(
    	'//div[contains(@class,"ProductCard-container")]/a/@href')
    parse_product_listing(product_urls)
    next_page = response.xpath(
    	'//nav[contains(@class,"pl-Pagination")]//a/@href')
    if next_page:
    	start_request(next_page[0])

                 ####parsing_productlink####
def parse_product_listing(product_urls):
	for url in product_urls: 
		parse_product(url) 

        
                  ####data_extraction####

def parse_product(url):
        html = requests.get(url,headers=headers) 
        response = lxml.html.fromstring(html.content)
        #product_urls = response.xpath(
        #	'//div[contains(@class,"ProductCard-container")]//a/@href') 
        name = response.xpath(
        	'//h1[contains(@class,"pl-Heading pl-Heading--pageTitle")]//text()')
        if name:
        	name=name[0]
        brand = response.xpath(
        	'//p[contains(@class,"ProductDetailInfoBlock-header-manu")]/a/text()')
        if brand:
        	brand=brand[0]
        price = response.xpath(
        	'//div[contains(@class,"BasePriceBlock")]//text()')
        description = response.xpath(
        	'//div[contains(@class,"ProductOverviewInformation-description")]/text()')
        images_url = response.xpath(
        	'//div[contains(@class,"pl-MultiCarousel-innerWrap")]/ul/li//div/img/@src')
                   ######cleaning####
        description = " ".join(description)
        price = " ".join(sel.strip() for sel in price)
        data = {"product_url":url,
                "name":name,
                "brand":brand,
                "price":price,
                "description":description,
                "images_url":images_url,} 
        try:
        	db.products.insert_one(data)
        except pymongo.errors.DuplicateKeyError:pass

start_request(category_url)



