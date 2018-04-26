import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time
from splinter import Browser
from pprint import pprint
from datetime import datetime
import pymongo
from bson.json_util import loads
import json 
import pytz

def scrape_nasa():
    print("Initialize PyMongo to work with MongoDBs")
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)

    # Define database and collection
    db = client.mars_scrape
    collection = db.mars_web
    print('Mongo Initialized')


    # urls
    news_url = "https://mars.nasa.gov/news/"
    featured_pic_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    weather_url = "https://twitter.com/marswxreport?lang=en"
    facts_url = "http://space-facts.com/mars/"


    #lists to fill
    titles = []
    headlines = []
    news_records = []
    martian_weather = []
    featured_image_url = None
    martian_weather = []
    hemisphere_image_urls = []


    executable_path = {'executable_path':'D:/Chromedriver/chromedriver.exe'}
    browser = Browser('chrome', **executable_path)
    #browser = Browser(driver_name='chrome')
    browser.visit(news_url)
    soup = bs(browser.html, 'html.parser')

    #all the div tags with the class 'content_title'
    for title in soup.find_all("div", class_='content_title'):
        #print("-0-" * 10)
        title_string = title.find('a').string
        #print(title_string)
        titles.append(title_string)

    for text in soup.find_all("div", class_='article_teaser_body'):
        #print("-0-" * 10)
        #print("\n")
        teaser_text = text.text
        #print(teaser_text)
        headlines.append(teaser_text)


    for title, hl in zip(titles, headlines):
        news_records.append({
                'title': title,
                'headline': '"' + hl + '"',
                })

    print('finished gathering news_records')    
    pprint(news_records)


    print('gathering featured images')
    browser.visit(featured_pic_url)
    # navigate browser to target page
    browser.click_link_by_id("full_image")
    time.sleep(2)
    img_soup = bs(browser.html, 'html.parser')
    print("locate the featured image src")
    print(img_soup.find("img"))
    print(f'{" " *10}|\n' *2 )
    print(img_soup.find("img", class_="fancybox-image"))
    print(f'{" " *10}|\n' *2 )

    print(img_soup.find("img", class_="fancybox-image")['src'])
    featured_image_url = "https://www.jpl.nasa.gov/" + img_soup.find("img", class_="fancybox-image")['src']
    print("featured_image_url:" + featured_image_url)

    browser.visit(weather_url)
    twitter_soup = bs(browser.html, 'html.parser')
    tweets = twitter_soup.find_all("div", class_="js-tweet-text-container")
    for tweet in tweets:
        print(tweet.p.text)
        print("##" *20)
        martian_weather.append(tweet.p.text)

    for tweet in martian_weather:
        try:
            #if this passes it follows the weather tweeting format from 04/21/2018
            time_string = tweet.split("),")[0].split(" (")[1]
            print("Most recent weather tweet: "+ time_string)
            #get the most recent weather tweet
            mars_weather = tweet
            print(mars_weather)
            break
        except:
            pass

    browser.visit(facts_url)
    facts_soup = bs(browser.html, features='html.parser')
    table = facts_soup.find('table')
    # print(table)
    raw_table = pd.read_html(str(table), flavor="bs4")

    
    print(raw_table)
    headers = raw_table[0][0]
    data = raw_table[0][1]

    # saving it as a dataframe
    df = pd.DataFrame([headers.values,data.values]).T
    print(df)

    #saving it as a new string
    reformated_table_str = df.to_html()
    print(reformated_table_str)

    hemisphere_image_urls = [
        {"title": "Valles Marineris Hemisphere", "img_url":"https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/valles_marineris_enhanced.tif/full.jpg" },
        {"title": "Cerberus Hemisphere", "img_url": "https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/cerberus_enhanced.tif/full.jpg"},
        {"title": "Schiaparelli Hemisphere", "img_url": "https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/schiaparelli_enhanced.tif/full.jpg"},
        {"title": "Syrtis Major Hemisphere", "img_url": "https://astropedia.astrogeology.usgs.gov/download/Mars/Viking/syrtis_major_enhanced.tif/full.jpg"},
    ]
    
    '''
    try adding a timezone to format 
    '''
    
    timestamp = str(datetime.now())    
    
    final_json = {
        
        'timestamp':timestamp,
        #"timestamp":{
        #   "$date": timestamp,
        #    },
        "records":{
            "nasa_news": news_records,
            "featured_image_url":featured_image_url,
            "martian_weather":mars_weather,
            "fact_table": reformated_table_str,
            "hemisphere_images_urls": hemisphere_image_urls,
            }
        }

    print("record to be inserted to MongoDB")
    print("====" * 20)
    #pprint(final_json)
    try:
        collection.insert_one(final_json)
        #how we would input if we had $date
        #collection.insert_one(loads(json.dumps(final_json)))
    except Exception as e:
        print(e)
    return final_json

#scrape_nasa()
