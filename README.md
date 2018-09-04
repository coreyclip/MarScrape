# MarScrape
<hr>
## Creating a basic web page populated with information scraped from NASA 

### Technology and libraries used
* pandas: for wrangling data
* requests: for getting NASA's data
* beautiful soup: parsing and scraping html
* pymongo: storing the scraped info in a mongo database
* flask: as a webserver to display the information we scraped

# Demoing the app
if you're running this locally, you need to have (Mongo DB)[https://www.mongodb.com/] 
properly installed on your machine

Then start the mongo server with the command ``mongod`` in a terminal. If you encounter any errors, 
make sure you're current directory in the terminal is on the same drive as where you set up your mongo 
local database. 

You'll also need to have a (chrome driver)[http://chromedriver.chromium.org/] which is essentially an 
automated chrome browser

From there you can start up the flask web application by running the command ``Python flaskapp.py``
in a terminal located in this repository. 

# mars_scrape.py
<hr>
This holds the main function that performs the scrapping operation,
comments in the code detail what each block of code is for

some key points bellow

## setting up a pyMongo connection
```python
    print("Initialize PyMongo to work with MongoDBs")
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)


    # Define database and collection
    db = client.mars_scrape
    collection = db.mars_web
    print('Mongo Initialized')
```

## connecting to a Chrome driver
```python

    # make sure you have the Chrome driver
    executable_path = {'executable_path':'D:/Chromedriver/chromedriver.exe'}
    browser = Browser('chrome', **executable_path)
    #browser = Browser(driver_name='chrome')
    browser.visit(news_url)
    soup = bs(browser.html, 'html.parser')
```

## targetting div tags via their class
```python
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
    # pprint(news_records)
```
## Gathering Tweets
```python
    browser.visit(weather_url)
    twitter_soup = bs(browser.html, 'html.parser')
    tweets = twitter_soup.find_all("div", class_="js-tweet-text-container")
    for tweet in tweets:
        print(tweet.p.text)
        print("##" *20)
        martian_weather.append(tweet.p.text)

    for tweet in martian_weather:
        try:
            #if this passes it follows the weather tweeting format like 04/21/2018
            time_string = tweet.split("),")[0].split(" (")[1]
            print("Most recent weather tweet: "+ time_string)
            #get the most recent weather tweet
            mars_weather = tweet
            print(mars_weather)
            break
        except:
            pass
 ```

## reformating a panda dataframe html object
df.to_html creates a string, string can be have .replace methods performed on them. These strings are later parsed into html by flask.
This is on such method to add classes and styling to pandas dataframes that are destined for the web
```python

    #saving dataframe as a new string
    df.columns = ['', '']
    reformated_table_str = df.to_html(index=False).replace('<tr>','<tr style ={"background-color:  rgba(1, 22, 39, 1),' +
                                 ' color: rgba(253, 255, 252, 1)}>').\
                                replace('<table border="1" class="dataframe">','<table class="table table-hover">' )
```
    
## Saving our records to a json string that will go into MongoDB

```python
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
```

# flaskapp.py

Nothing super crazy here but a note for beginners. Notice how we essentially use a seperate route to just call the function for scraping our data. 

```python
app = Flask(__name__)
#mongo = PyMongo(app)



#index page
@app.route('/')
def index():
    # Define database and collection
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.mars_scrape
    doc = db.mars_web.find_one()
    #print('Mongo Initialized')

    #print(f"loading data from {doc['timestamp']}")
    try:
        records = doc['records']
    except TypeError:
        import mars_scrape
        records = mars_scrape.scrape_nasa()['records']
    return render_template("index.html", records=records)

#  route called `/scrape` that will import
#  your `scrape_mars.py` script and call your `scrape` function.

@app.route("/scrape")
def scrape():
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.mars_scrape
    #delete previous data
    db.mars_web.delete_many({})  
    # perform scraping
    print("Scrapping new data") 
    import mars_scrape
    data = mars_scrape.scrape_nasa()
    # Define database and collection  
    db = client.mars_scrape.mars_web
    # by definition find_one gets the most recent doc, if no query logic
    db.update({},data,upsert=True,)

    return redirect("http://localhost:5000/", code=302)


if __name__== "__main__":
    app.run(debug=True)

```

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

```

