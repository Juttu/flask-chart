from flask import Flask
from flask import make_response, render_template

from flask_pymongo import pymongo

from py5paisa import FivePaisaClient

import pandas as pd

from py5paisa.order import Order, OrderType, Exchange

from py5paisa.order import Order, OrderType, AHPlaced

import asyncio

import math
from datetime import datetime, timedelta
import json
import plotly
import plotly.express as px

import random


from pytz import timezone

# import mido
from threading import Thread


app = Flask(__name__)
app.config["SECRET_KEY"] = "11b5ca1077aabd6db5a41af3e90cacf4d9cd7f17"
app.config["MONGO_URI"] = "mongodb+srv://Anurag:Anurag@cluster0.toske.mongodb.net/?retryWrites=true&w=majority"

CONNECTION_STRING = "mongodb+srv://Anurag:Anurag@cluster0.toske.mongodb.net/?retryWrites=true&w=majority"
# MONGODB CONNECT
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('opdata')
user_collection = pymongo.collection.Collection(db, 'user_collection')


# BROKER CONNECT
cred = {
    "APP_NAME": "5P53408370",
    "APP_SOURCE": "9600",
    "USER_ID": "sXXGlk7fWd2",
    "PASSWORD": "AyymZGd8jNd",
    "USER_KEY": "LaEwsZJO1eFxpyr2l41lXsaXdlyDVu0v",
    "ENCRYPTION_KEY": "oMOjFnPWhz0DAZd0yGPTL7lsQVsXufC8"
}

client = FivePaisaClient(email="hrushikesh838@gmail.com",
                         passwd="Itsmyvsh838@", dob="19990530", cred=cred)
client.login()


today_date = datetime.now()
# print(today_date.date)


@app.route("/data")
def data():

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

    fig = px.line(df, x='Time', y='OP', markers=True)
    dat = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    resp = make_response(dat)
    resp.mimetype = 'application/json'
    return resp


@app.route('/')
def bar_with_plotly():
    return render_template('index.html')


def cont_fun(a):
    while True:
        today_date = datetime.now()
        res_del1 = db.opdata.delete_many({"x_coordinate": {"$lt": datetime(
            today_date.year, today_date.month, today_date.day)}})

        niftyspot = [{"Exchange": "N", "ExchangeType": "C", "Symbol": "NIFTY"}]
        niftyltp = client.fetch_market_depth_by_symbol(
            niftyspot)['Data'][0]['LastTradedPrice']
        print(niftyltp)
        atmstrikeup = math.ceil(niftyltp/50)*50
        atmstrikedown = math.floor(niftyltp/50)*50
        if (atmstrikeup-niftyltp) >= (niftyltp-atmstrikedown):
            strikeprice = float(atmstrikedown)
            strikeprice = "{:.2f}".format(strikeprice)
            strikeprice = str(strikeprice)
        else:
            strikeprice = float(atmstrikeup)
            strikeprice = "{:.2f}".format(strikeprice)
            strikeprice = str(strikeprice)

        b1 = float(strikeprice)
        c1 = b1+50
        d1 = "{:.2f}".format(c1)
        strikepriceup = str(d1)

        b2 = float(strikeprice)
        c2 = b2-50
        d2 = "{:.2f}".format(c2)
        strikepricedown = str(d2)

        putscripname = "NIFTY 19 Jan 2023 PE"+" "+strikeprice
        callscripname = "NIFTY 19 Jan 2023 CE"+" "+strikeprice

        putscripnameup = "NIFTY 19 Jan 2023 PE"+" "+strikepriceup
        callscripnameup = "NIFTY 19 Jan 2023 CE"+" "+strikepriceup

        putscripnamedown = "NIFTY 19 Jan 2023 PE"+" "+strikepricedown
        callscripnamedown = "NIFTY 19 Jan 2023 CE"+" "+strikepricedown

        putstrike = [
            {"Exchange": "N", "ExchangeType": "D", "Symbol": putscripname}]
        callstrike = [
            {"Exchange": "N", "ExchangeType": "D", "Symbol": callscripname}]
        put = client.fetch_market_depth_by_symbol(putstrike)['Data'][0]
        # print(put['ScripCode'])
        pp = put['LastTradedPrice']
        call = client.fetch_market_depth_by_symbol(callstrike)['Data'][0]

        cp = call['LastTradedPrice']

        putstrikeup = [
            {"Exchange": "N", "ExchangeType": "D", "Symbol": putscripnameup}]
        callstrikeup = [
            {"Exchange": "N", "ExchangeType": "D", "Symbol": callscripnameup}]
        putup = client.fetch_market_depth_by_symbol(putstrikeup)['Data'][0]
        # print(putup['ScripCode'])
        ppup = putup['LastTradedPrice']
        callup = client.fetch_market_depth_by_symbol(callstrikeup)['Data'][0]

        cpup = callup['LastTradedPrice']

        putstrikedown = [
            {"Exchange": "N", "ExchangeType": "D", "Symbol": putscripnamedown}]
        callstrikedown = [
            {"Exchange": "N", "ExchangeType": "D", "Symbol": callscripnamedown}]
        putdown = client.fetch_market_depth_by_symbol(putstrikedown)['Data'][0]
        # print(putdown['ScripCode'])

        ppdown = putdown['LastTradedPrice']

        calldown = client.fetch_market_depth_by_symbol(callstrikedown)[
            'Data'][0]

        cpdown = calldown['LastTradedPrice']

        final_data = [cp, pp, cpup, ppup, cpdown, ppdown]

        print(final_data)
        x_coordinate = datetime.now()

        past = datetime.now() - timedelta(days=1)

        y_coordinate = (final_data[0]+final_data[1]+final_data[2] +
                        final_data[3]+final_data[4]+final_data[5])/3

        ind_time = datetime.now(timezone("Asia/Kolkata"))
        print(ind_time, "IND_TIME")
        # print(today_date,"TIMEEEEEE")

        today_nine30 = ind_time.replace(
            hour=9, minute=30, second=0, microsecond=0)
        today_three30 = ind_time.replace(
            hour=15, minute=30, second=0, microsecond=0)
        # print(today_nine30,today_three30)
        # if ind_time>=today_nine30 and today_date<=today_three30:
        db.opdata.insert_one({"x_coordinate": x_coordinate,
                              "y_coordinate": y_coordinate})
        print("CONT", a)


if __name__ == "__main__":

    p = Thread(target=cont_fun, args=(1,))
    p.start()
    app.run(debug=False, host='0.0.0.0')
    p.join()
