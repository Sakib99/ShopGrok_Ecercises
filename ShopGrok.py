# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 00:22:29 2021

@author: user
"""

import requests
from bs4 import BeautifulSoup
import csv


csv_columns = ['Product_title','Product_image','Packsize','Price','Price per unit']
BASE_URL = "https://www.aldi.com.au/"
links=[]
Prod_list=[]
grocery_items=[]



def make_request(url):
   return requests.get(url)
def get_scrapped_content(page):
    return BeautifulSoup(page.content, "html.parser")
def get_submenu_lists(soup):
    results = soup.find_all('ul',class_="main-nav--level megamenu")
    results=results[0].find_all('li',class_="main-nav--item ym-clearfix product-range is-closed is-first-level")
    container=results[0].find('div',class_="main-nav--level-container gm-bg-product-range")
    submenus=container.find('ul').find_all('li')
    return submenus


#function for getting the category name
def get_category_name(link):
    for link_words in link:
        name=link_words.split('/')
        if len(name)==7:
            grocery_items.append(name[len(name)-2])
        if len(name)==8:
            grocery_items.append(name[len(name)-3]+'/'+name[len(name)-2])

#function for getting the category list_URL

def get_submenu_products_list_URL(submenus,links):
    for submenu in submenus:
        ref=submenu.find('div',class_="main-nav--item--inner-wrapper").find('a')['href']
        if(str(ref).find("#main-nav")):
            ref=str(ref).replace("#main-nav",'')
        links.append(ref)
    return links

# Function for getting the product attributes
def get_product_attributes(link):
                img=""
                header=""
                size=""
                value=""
                decimal=""
                price_per_unit=""            
                try:
                    img=link.find("img")['src']
                except:
                    print("no-image")
                try:
                   header=link.find("div",class_="box--description--header").text
                   header=header.replace("\n",'')
                   header=header.replace("\t",'')
                   
                except:
                  print("no-box-header")
                try:
                    size=link.find("div",class_="box--price").find("span",class_="box--amount").text
                except:
                    print('no size available')
                try:
                    value=link.find("div",class_="box--price").find("span",class_="box--value").text
                except:
                    print("no value")
                try:
                    decimal=link.find("div",class_="box--price").find("span",class_="box--decimal").text
                except:
                    print("no decimal value")
                try:
                  price_per_unit=link.find("div",class_="box--price").find("span",class_="box--baseprice").text
                except:
                  print("no price per unit")
                price=value+decimal
                return (img,header,size,price,price_per_unit)

def return_dictionary(img,header,size,price,price_per_unit):
    return {'Product_title':header,'Product_image':img,'Packsize':size,'Price':price,'Price per unit':price_per_unit}

def linked_product_iterator(products):
    
    for product in products:
            products_attributes=product.find_all("a")
            for product_attribute in products_attributes:
                img,header,size,price,price_per_unit = get_product_attributes(product_attribute)
                prod_dict=return_dictionary(img,header,size,price,price_per_unit)
                Prod_list.append(prod_dict)
    
def grocery_link_iterator(links):
    for link in links:
        page = make_request(link)
        soup1= get_scrapped_content(page)
        
        products=soup1.find_all("div",class_="tx-aldi-products")
        linked_product_iterator(products)
        
        
#saving the Products to the Dictionary
def convert_to_CSV(list_dict,name):
    csv_file = name
    try:
      with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in list_dict:
            writer.writerow(data)
    except IOError:
        print("I/O error")
        
   
     
page = make_request(BASE_URL)
soup = get_scrapped_content(page)    
submenus = get_submenu_lists(soup)
links=get_submenu_products_list_URL(submenus,links)
get_category_name(links)
grocery_link_iterator(links)
convert_to_CSV(Prod_list,"Products.csv")



