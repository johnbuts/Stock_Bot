#This is my basic Robinhood Stock Bot, Buy/Sell based off of MACD
#import robin_stocks

import robin_stocks.robinhood as r
import pyotp
import config as cfg
from pyrh import Robinhood
import tulipy as tp
import numpy as np
import time
import datetime as dt
import os
from twilio.rest import Client


def print_latest(STOCK_NAME):
    stock_upper = STOCK_NAME.upper()
    x = r.get_latest_price(stock_upper)
    print(str(x[0]))

#returns the latest stock price as a float
def get_latest(STOCK_NAME):
    stock_upper = STOCK_NAME.upper()
    x = r.get_latest_price(stock_upper)
    return(float(x[0]))

def get_vol(STOCK_NAME):
    stock_upper = STOCK_NAME.upper()
    x = r.stocks.get_fundamentals(stock_upper, info=None)
    return float(x[0]["volume"])

def sendSMS(message):
    account_sid = str(cfg.vars["ACCOUNT_SID"]) #set TWILIO_ACCOUNT_SID="ACTUALSID"
    auth_token = str(cfg.vars["AUTH_TOKEN"])
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
            body=message,
            from_='2407248154',
            to='7035549788'
        )

def should_sleep():
    current_time = dt.datetime.now()
    flag = False
    if(current_time.hour > 15 or current_time.hour < 9): #sleeps until 9:31, and resumes sleep at 4:01
        hr = current_time.hour - 9
        mn = current_time.minute - 30
        if(mn < 0):
            mn = abs(mn)
        else:
            mn = 60 - mn
            flag = True

        if(hr < 0):
            hr = abs(hr)
        else:
            hr = 24 - hr

        if flag:
            hr -= 1
        
        val = 3600 * hr + 60 * mn
        print("ASLEEP FOR: " + str(val) + " SECONDS, STARTED AT " + str(current_time.hour) + ":" + str(current_time.minute) + ":" + str(current_time.second))
        time.sleep(val)

def should_trade(stock_information):
    should_sleep()
    
    ticker = stock_information.getName()
    latest_price = get_latest(ticker)
    price_list = []
    temp_hist_positive = -999
    temp_hist_negative = 999
    histogram_positive = True
    histogram_negative = True
    history = r.get_stock_historicals(ticker, "10minute", "week", "regular")
    for i in history:
        price_list.append(float(i["open_price"])) 
    numpy_price_list = np.array(price_list)
    (macd, macd_signal, macd_histogram) = tp.macd(numpy_price_list, 12, 26, 9)
    #Add RSI Indicator, above 70 rsi sell, below 30 rsi buy
    #12, 26, 3 for BTC
    histogram_arr = macd_histogram[len(macd_histogram) - 6 : len(macd_histogram) - 2 ]
    print(ticker, histogram_arr)
    for i in range(len(histogram_arr)): #checks if it is increasing or decreasing
        if histogram_arr[i] >= temp_hist_positive + .01 and histogram_arr[i] > 0 :
            temp_hist_positive = histogram_arr[i]
        else: 
            histogram_positive = False

        if histogram_arr[i] <= temp_hist_negative - .01 and histogram_arr[i] < 0 :
            temp_hist_negative = histogram_arr[i]
        else: 
            histogram_negative = False

    if stock_information.getBuyPrice() == 0:
        if macd_histogram[len(macd_histogram) - 1] >= histogram_arr[len(histogram_arr) - 1] and histogram_negative and macd_signal[len(macd_signal) - 1] < 0: 
            # if last one is higher than the one before (meaning the bottom of the curve) and len - 6 to len - 2 (macd_histogram indexes) are negative, and signal is negative
            stock_information.setBuyPrice(latest_price)
            print("\nJUST BOUGHT ", ticker, " AT: ", latest_price)
            fo.write("JUST BOUGHT " + ticker + " AT: "+ str(latest_price) + "\n")
            sendSMS("JUST BOUGHT " + ticker + " AT: "+ str(latest_price) + "\n")
            

    elif stock_information.getBuyPrice() != 0:
        if macd_histogram[len(macd_histogram) - 1] <= histogram_arr[len(histogram_arr) - 1] and histogram_positive and macd_signal[len(macd_signal) - 1] > 0: 
            # if last one is lower than the one before (meaning the top of the curve) and len - 6 to len - 2 (macd_histogram indexes) are positive, and signal is positive
            if latest_price > stock_information.getBuyPrice():
                stock_information.setBuyPrice(0)
                print("\nJUST SOLD ", ticker, " AT: ", latest_price)
                fo.write("JUST SOLD " + ticker + " AT: "+ str(latest_price) + "\n")
                sendSMS("JUST SOLD " + ticker + " AT: "+ str(latest_price) + "\n")

login = r.login(cfg.vars["ROBINHOOD_USERNAME"],
cfg.vars["ROBINHOOD_PASSWORD"]) #Uses environment variable to login
#print(os.getenv('ROBINHOOD_USERNAME'))
#two_factor = pyotp.TOTP("ZG3ZKORQJCKKHJBC").now()
#prints the latest stock price as a float


class Stock_obj:
    def __init__(self, name, buy_price = 0.0):
        self.name = name
        self.buy_price = buy_price

    def getBuyPrice(self):
        return self.buy_price

    def setBuyPrice(self, buy_price):
        self.buy_price = buy_price

    def getName(self):  
        return self.name

    def setName(self, name):  
        self.name = name



ticker_list = [Stock_obj("AAPL", 149.8), Stock_obj("MSFT"), Stock_obj("DIS"), Stock_obj("FB"), 
    Stock_obj("QQQ"), Stock_obj("GS"), Stock_obj("SPY"), Stock_obj("FTNT"), Stock_obj("C"), Stock_obj("WMT"), Stock_obj("JPM"), 
    Stock_obj("GM"), Stock_obj("KO"), Stock_obj("INTC"), Stock_obj("AMD"), Stock_obj("NVDA"), Stock_obj("JNJ", 170.00), Stock_obj("WMT"), 
    Stock_obj("MA"), Stock_obj("BAC"), Stock_obj("HD"), Stock_obj("PG"), Stock_obj("NKE"), Stock_obj("XOM"), Stock_obj("ORCL"),
    Stock_obj("COST"), Stock_obj("CVX"), Stock_obj("SHOP"), Stock_obj("TQQQ"), Stock_obj("SQQQ"),
    Stock_obj("PANW"), Stock_obj("CRWD", 264.18), Stock_obj("SNOW"), Stock_obj("NDAQ"), Stock_obj("PLTR"), Stock_obj("LMT"),
    Stock_obj("WMT"), Stock_obj("TGT"), Stock_obj("LOGI"), Stock_obj("ON"), Stock_obj("NLOK"), Stock_obj("PYPL"), Stock_obj("DKNG"),
    Stock_obj("ULTA"), Stock_obj("LULU"), Stock_obj("PENN", 81.29), Stock_obj("ROKU", 332.85), Stock_obj("TTWO"),Stock_obj("GSAT"), 
    Stock_obj("AFRM"), Stock_obj("KPLT"), Stock_obj("ROOT"), Stock_obj("AMZN"), 
    Stock_obj("ASTR"), Stock_obj("TSLA", 747.37), Stock_obj("ANY"), Stock_obj("BGFV"), Stock_obj("EDU"), 
    Stock_obj("ATIF"), Stock_obj("COF"), Stock_obj("GLBE"), Stock_obj("DQ"), Stock_obj("VALN"), Stock_obj("IRDM"),Stock_obj("HRC"),
    Stock_obj("MTTR"), Stock_obj("UBER"), Stock_obj("IDEX")]

#add stock ticker to ticker_list to run algorithim

fo = open("orders.txt", "a")
while True:
    fo.write("**********************************************" + "\n")
    for i in ticker_list:
        should_trade(i)
    time.sleep(600)
    print("-----------")


