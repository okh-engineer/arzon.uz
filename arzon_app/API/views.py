from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from urllib.parse import quote
from data.data import zoodmall_api_link, sello_api_link, olcha_api_link, texnomart_api_link, korrektor_token

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--incognito")

browser = webdriver.Chrome(options=chrome_options)



def uzum(encoded_query):


    browser.get(f"https://uzum.uz/uz/search?query={encoded_query}")
    wait = WebDriverWait(browser, 30)

    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "card-info-block")))

    uzum_page = browser.page_source
    uzum_soup = BeautifulSoup(uzum_page, "lxml")
    
    
    product_check = uzum_soup.find("div", attrs={"id":"category-header"})
    
    if product_check:

        uzum_products_data = uzum_soup.find("div", attrs={"id":"category-content"})

        uzum_products = uzum_products_data.find_all("div", attrs={"class":"ui-card"})

        uzum_products = uzum_products[0:5]
        
        products = []
        
        for product in uzum_products:
            uzum_pr_block = product.find("a", attrs={"class":"subtitle-item"})
            uzum_pr_image = product.find("img", attrs={"class":"main-card-icon-and-classname-collision-made-to-minimum"}).get('src')
            uzum_pr_name = uzum_pr_block.text.strip()
            uzum_pr_link = uzum_pr_block.get('href')

            uzum_pr_price = product.find("span",attrs={"class":"currency product-card-price slightly medium"}).text.strip().replace('\xa0', ' ').replace(' ', '').replace(',', ' ').replace("so'm", "")
            products.append(
                {
                    'name': uzum_pr_name,
                    'price': int(uzum_pr_price),
                    'link': "https://uzum.uz"+uzum_pr_link,
                    'image_link': uzum_pr_image
                }
            )
        
        
        def get_price(products):
            price_str = products.get('price', '0')
            
            return float(price_str)
        
        products.sort(key=get_price, reverse=False)
        
        return products

    else:
        return ("Uzumda bunday mahsulot topilmadi,", status.HTTP_204_NO_CONTENT )
     
def zoodmall(encoded_query, zoodmall_api_link):
    
    url = f"{zoodmall_api_link}{encoded_query}&page=1&sort=1"
    headers = {
        "x-lang": "uz",
        "x-marketcode": "UZ" 
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        
    
        data = response.json()
        products = data['marketList'][0:5]
        API = []
        
        if products:
        
            for product in products:
                API.append(
                    {
                        'name': product['name'],
                        'price': product['localPrice'],
                        'link': f"https://www.zoodmall.uz/product/{product['productId']}/",
                        'image_link': product['imgUrl']
                    }
                )
            
            def get_price(API):
                price = API.get('price', '0')
                return float(price)
            
            API.sort(key=get_price, reverse=False)
            return API
        else:
            return ("Zoodmallda bunday mahsulot topilmadi,", status.HTTP_204_NO_CONTENT )   
    else:
        print("Status code", response.status_code)
               
def asaxiy(encoded_query):



    browser.get(f"https://asaxiy.uz/uz/product/sort=rate-high?key={encoded_query}")
    wait = WebDriverWait(browser, 30)

    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "container")))

    asaxiy_page = browser.page_source
    asaxiy_soup = BeautifulSoup(asaxiy_page, "lxml")
    
    product_check = asaxiy_soup.find("div", attrs={"class":"row custom-gutter mb-40"})
    if product_check:
        
    
        asaxiy_products = asaxiy_soup.find_all("div", attrs={"class":"product__item d-flex flex-column justify-content-between"})
        asaxiy_products = asaxiy_products[0:5]
        
        products = []
        
        
        for product in asaxiy_products:

            asaxiy_pr_name = product.find("span", attrs={"class":"product__item__info-title"}).text.strip()
            asaxiy_pr_link = product.find("a").get('href')
            asaxiy_pr_image = product.find("img", attrs={"class":"img-fluid lazyload"}).get('src')
            asaxiy_pr_price = product.find("span",attrs={"class":"product__item-price"}).text.strip()[0:-4].replace(' ', '')
               
            products.append(
                {
                    'name': asaxiy_pr_name,
                    'price': int(asaxiy_pr_price),
                    'link': "https://www.asaxiy.uz"+asaxiy_pr_link,
                    'image_link': asaxiy_pr_image
                }
            )
        
        def get_price(products):
            price_str = products.get('price', '0')
            return float(price_str)
        
        products.sort(key=get_price, reverse=False)
        
        return products

    else:
        return ("Asaxiy mahsulot topilmadi,", status.HTTP_204_NO_CONTENT )
 
def sello(encoded_query, sello_api_link):
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Fingerprint": "10b4ad6ce60f51511b502f34c14f8966",
        "Language": "uz" 
    }
    response = requests.get(f"{sello_api_link}{encoded_query}&page=1&perPage=30&sortBy=price_asc", headers=headers)
    
    
    if response.status_code == 200:
        
    
        data = response.json()

        products = data['hits'][0:5]
        API = []
        
        if products:
            for product in products:
                
                if product['discounted_price']:
                    price = product['discounted_price']
                else:
                    price = product['price']
                API.append(
                    {
                        'name': product['name'],
                        'price': price,
                        'link': f"https://sello.uz/uz/product/{product['slug']}/",
                        'image_link': f"https://static.sello.uz/unsafe/x500/https://static.sello.uz{product['imageURL']}"
                    }
                )
            
            def get_price(API):
                price = API.get('price', '0')
                return float(price)
            
            API.sort(key=get_price, reverse=False)
            return API
        else:
            return ("Selloda mahsulot topilmadi,", status.HTTP_204_NO_CONTENT )
    else:
        return ("Status code:", response.status_code)
        
def olcha(encoded_query, olcha_api_link):
    
    headers = {
        "Accept-Language": "oz"
    }
    response = requests.get(f"{olcha_api_link}{encoded_query}", headers=headers)
    
    if response.status_code == 200:    
        data = response.json()
        products = data['data']['products'][0:5]
        API = []
        
        if products:
            for product in products:
                
                if product['discount_price']:
                    price = product['discount_price']
                else:
                    price = product['total_price']
                API.append(
                    {
                        'name': product['name_oz'],
                        'price': price,
                        'link': f"https://olcha.uz/oz/product/view/{product['alias']}/",
                        'image_link': product['main_image']
                    }
                )
            
            def get_price(API):
                price = API.get('price', '0')
                return float(price)
            
            API.sort(key=get_price, reverse=False)
            return API
        else:
            return ("Olchada mahsulot topilmadi,", status.HTTP_204_NO_CONTENT )
    else:
        return ("Status code:", response.status_code)

def texnomart(encoded_query, texnomart_api_link):
    
    headers = {
        "Accept-Language": "uz"
    }
    response = requests.get(f"{texnomart_api_link}{encoded_query}&sort=&page=1", headers=headers)
    
    if response.status_code == 200:  
        data = response.json() 
        products = data['data']['products'][0:5]
        API = []
        
        if products:
            for product in products:
                
                if product['sale_price']:
                    price = product['sale_price']
                else:
                    price = product['loan_price']
                API.append(
                    {
                        'name': product['name'],
                        'price': price,
                        'link': f"https://texnomart.uz/product/detail/{product['id']}",
                        'image_link': product['image']
                    }
                )
            
            def get_price(API):
                price = API.get('price', '0')
                return float(price)
            
            API.sort(key=get_price, reverse=False)
            return API
        else:
            return ("Mahsulot topilmadi,", status.HTTP_204_NO_CONTENT )
    else:
        return ("Status code:", response.status_code)

class SearchProductView(APIView):
    def get(self, request):
        product_name = request.GET.get('query')
        encoded_query = quote(product_name)
        if encoded_query:

            result_uzum = uzum(encoded_query=encoded_query)
            result_asaxiy = asaxiy(encoded_query=encoded_query)
            result_zoodmall = zoodmall(encoded_query, zoodmall_api_link=zoodmall_api_link)
            result_sello = sello(encoded_query, sello_api_link=sello_api_link)
            result_olcha = olcha(encoded_query, olcha_api_link=olcha_api_link)
            result_texnomart = texnomart(encoded_query, texnomart_api_link=texnomart_api_link)
            
            try:
                return Response({"products": {
                    "uzum": result_uzum,
                    "asaxiy": result_asaxiy,
                    "zoodmall": result_zoodmall,
                    "sello": result_sello,
                    "olcha": result_olcha,
                    "texnomart": result_texnomart
                } })
            except Exception as e:
                return Response(f"Error message: {e}")
        else:
            return Response({"message": "Product name not provided."})