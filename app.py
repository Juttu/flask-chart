from flask import Flask
from flask import make_response, render_template

from flask_pymongo import pymongo

from py5paisa import FivePaisaClient

import pandas as pd

from py5paisa.order import Order, OrderType, Exchange

from py5paisa.order import Order, OrderType, AHPlaced


import math
from datetime import datetime, timedelta
import json
import plotly
import plotly.express as px


from pytz import timezone

# import mido
from threading import Thread
import multiprocessing

import urllib.request
import json
import os

from flask_cors import CORS


app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = "11b5ca1077aabd6db5a41af3e90cacf4d9cd7f17"
app.config["MONGO_URI"] = "mongodb+srv://Anurag:Anurag@cluster0.toske.mongodb.net/?retryWrites=true&w=majority"

CONNECTION_STRING = "mongodb+srv://Anurag:Anurag@cluster0.toske.mongodb.net/?retryWrites=true&w=majority"
# MONGODB CONNECT
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('opdata')
user_collection = pymongo.collection.Collection(db, 'user_collection')


# BROKER CONNECT

today_date = datetime.now()


@app.route("/data")
def data():
    # url = "https://chart-backend.onrender.com/data".format(
    #     os.environ.get("TMDB_API_KEY"))
    # response = urllib.request.urlopen(url)
    # data = response.read()
    # dict = json.loads(data)
    # print(dict)

    all_items_db = db.opdata.find()

    all_items = []

    for i in all_items_db:
        all_items.append(i)

    for i in all_items:
        del i['_id']
    XAxis = []
    YAxis = []
    for e in all_items:
        XAxis.append(e['x_coordinate'])
    for e1 in all_items:
        YAxis.append(e1['y_coordinate'])

    df = pd.DataFrame({
        'Time': XAxis,
        'OP': YAxis,
    })

    fig = px.line(df, x='Time', y='OP', width=1200, height=600)
    fig.update_layout(legend=dict(
        orientation="v",
        yanchor="auto",
        y=1,
        xanchor="right",  # changed
        x=-0.3
    ))
    dat = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    resp = make_response(dat)
    resp.mimetype = 'application/json'
    return resp


@app.route('/')
def bar_with_plotly():
    return render_template('index.html')


@app.route("/dataapi")
def dataapi():
    all_items_db = db.opdata.find()

    all_items = []

    for i in all_items_db:
        all_items.append(i)

    for i in all_items:
        del i['_id']
    XAxis = []
    YAxis = []
    for e in all_items:
        XAxis.append(e['x_coordinate'])
    for e1 in all_items:
        YAxis.append(e1['y_coordinate'])

    print(datetime.timestamp(all_items[0]["x_coordinate"])*1000)

    for i in all_items:
        i["x_coordinate"] = round(datetime.timestamp(i["x_coordinate"])*1000)
    for i in all_items:
        i['time'] = i.pop('x_coordinate')
    for j in all_items:
        j['value'] = j.pop('y_coordinate')
    return all_items




@app.route("/bndataapi")
def bndataapi():
    all_items_db = db.bnopdata.find()

    all_items = []

    for i in all_items_db:
        all_items.append(i)

    for i in all_items:
        del i['_id']
    XAxis = []
    YAxis = []
    for e in all_items:
        XAxis.append(e['x_coordinate'])
    for e1 in all_items:
        YAxis.append(e1['y_coordinate'])

    print(datetime.timestamp(all_items[0]["x_coordinate"])*1000)

    for i in all_items:
        i["x_coordinate"] = round(datetime.timestamp(i["x_coordinate"])*1000)
    for i in all_items:
        i['time'] = i.pop('x_coordinate')
    for j in all_items:
        j['value'] = j.pop('y_coordinate')
    return all_items





if __name__ == "__main__":

    app.run(debug=False, host='0.0.0.0', threaded=True)
