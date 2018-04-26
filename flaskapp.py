from flask import Flask, render_template, redirect, url_for
import pymongo
#from flask_pymongo import PyMongo

# Initialize PyMongo to work with MongoDBs
#conn = 'mongodb://localhost:27017'
#client = pymongo.MongoClient(conn)

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
    records = doc['records']
    return render_template("index.html", records=records)

#  route called `/scrape` that will import
#  your `scrape_mars.py`
#  script and call your `scrape` function.

@app.route("/scrape")
def scrape():
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.mars_scrape
    #delete previous data
    db.mars_web.delete_one()  
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
