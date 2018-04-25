from flask import Flask, jsonify, render_template, redirect
import pymongo
import mars_scrape
#from flask_pymongo import PyMongo

# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

app = Flask(__name__)
#mongo = PyMongo(app)

def mongo_pull():
    # Define database and collection
    db = client.mars_scrape
    # by definition find_one gets the most recent doc, if no query logic
    doc = db.mars_web.find_one()
    print('Mongo Initialized')

    print(f"loading data from {doc['timestamp']}")
    records = doc['records']

    return records
    

#index page
@app.route('/')
def index():
    
    records = mongo_pull()

    return render_template("index.html", records=records)

#  route called `/scrape` that will import
#  your `scrape_mars.py`
#  script and call your `scrape` function.

@app.route("/scrape")
def scrape():
    # perform scraping 
    data = mars_scrape.scrape_nasa()
    records.update(
                {},
                data,
                upsert=True,)
    return redirect("http://localhost:5000/", code=302)


if __name__== "__main__":
    app.run(debug=True)
