"""
    using Beautiful soup and requests module
    searchs the input keyword and prints out top 10 results from Amazon and Ebay
    calculates the time from the request to end printiing results
"""


from bs4 import BeautifulSoup
import requests
import string
import time

def Removewords(tag):
    CleanWord = [letter for letter in tag if letter in string.digits or letter == "."]
    return "".join(CleanWord)

def GetEbayItems(soup):

    final = {}
    result_items = soup.find_all("li",{"class":"s-item s-item__pl-on-bottom"})
    
    
    for item_count,item in enumerate(result_items,1):
        item_name =  item.find("h3",{"class":"s-item__title"}).text
        if(item_name):
            item_price = item.find("span",{"class":"s-item__price"})
            item_price_striped =  item_price.getText()
            final.__setitem__(item_name,item_price_striped)
        if item_count == 10:
            break
    return final



def GetAmazonitems(soup):

    final = {}
    
    try:
        result_items = soup.find_all("div",{"class": "s-include-content-margin s-latency-cf-section s-border-bottom s-border-top"})

        for item_count,item in enumerate(result_items,1):
            item_name =  item.find("a",{"class":"a-link-normal a-text-normal"}).text
            item_price =  item.find("span",{"class":"a-offscreen"})
            item_price = Removewords(str(item_price))
            final.__setitem__(item_name,item_price)
            if item_count == 10: 
                break
    except AttributeError as Ae:
        pass
    return final

def start_scraping(search):
    ebay_link = "http://www.ebay.com/sch/i.html?_from=R40&_trksid=p2050601.m570.l1313.TR10.TRC0.A0.H0.X"+search+".TRS0&_nkw="+search+"&_sacat=0"
    amazon_link = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="+search


    Ebay_Items = None
    start = time.time()
    print("got your search keyword...")
    # creating requesting , soup , getting result
    ebay = requests.get(ebay_link)
    
    ebay_soup = BeautifulSoup(ebay.content,"html.parser")
    print("request succesfull..")
    exception_counter_e = 1
    try:
        Ebay_Items = GetEbayItems(ebay_soup)
    except Exception as e:
        exception_counter_e += 1
        if exception_counter_e == 5 :
            Ebay_Items = GetEbayItems(ebay_soup)
        else: 
            print(e)
            print("can't get results from ebay..")
    print("got your items from ebay...")

    # creating requesting ,soup , getting result
   
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    amazon = requests.get(amazon_link,headers = headers)
    amazon_soup = BeautifulSoup(amazon.content,"html.parser")
    exception_counter = 1
    try:
        Amazon_Items = GetAmazonitems(amazon_soup)
    except:
        exception_counter+=1
        if exception_counter != 5 :
            Amazon_Items = GetAmazonitems(amazon_soup)
        else: 
            print("can't get results from Amazon")
    print("got your items from amazon...")

    final_result = {}


    #printing the acquried results
    # print("----------------EBAY DEALS---------------")
    # ebay_items = {}
    # for key, value in Ebay_Items.items():
    #     print(key ,"--------->","$", value)
    # print("\n")
    final_result['ebay'] = Ebay_Items
    # print("----------------AMAZON DEALS---------------")
    # for key, value in Amazon_Items.items():
    #     print(key ,"--------->","$", value)
    final_result['amazon'] = Amazon_Items

    # end = time.time()
    # print("results in "+str(end-start)+"secs...")
    return final_result

