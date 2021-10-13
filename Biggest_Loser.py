import json
import time
import config as cfg
import datetime as dt
from urllib.request import urlopen
import robin_stocks.robinhood as r

MONEY_PER_STOCK = 100


# class Stock_obj:
#     def __init__(self, name, buy_price = 0.0):
#         self.name = name
#         self.buy_price = buy_price

#     def getBuyPrice(self):
#         return self.buy_price

#     def setBuyPrice(self, buy_price):
#         self.buy_price = buy_price

#     def getName(self):  
#         return self.name

#     def setName(self, name):  
#         self.name = name


def get_latest(STOCK_NAME):
    stock_upper = STOCK_NAME.upper()
    x = r.get_latest_price(stock_upper)
    return(float(x[0]))

def get_jsonparsed_data(url): #returns a dictionry containing the parsed data from endpoint
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def get_loser_list(data): #This executes at 4:00 p.m., and makes sure the stock moves in the 5 minutes so that we buy a stock that is actually changing during after
    loser_list = [] 
    final_loser_list = []
    for index in range(len(data)): #Since dict is ordered by percent loss, as soon as one drops below 26, we can stop the loop
        loser_ticker = data[index]["symbol"]
        if(get_latest(loser_ticker) < MONEY_PER_STOCK):
            loser_list.append(loser_ticker)

    return loser_list



def buy_losers(losers): 
    ticker_list = losers
    #This is where the biggest loser tickers wil be stored
    quantity_list = []
    #This is where the biggest loser prices at market close wil be stored
    for i in range(len(ticker_list)):
        quantity = int(MONEY_PER_STOCK / get_latest(ticker_list[i]))
        buy_data = r.orders.order_buy_limit(ticker_list[i], quantity, get_latest(ticker_list[i]) + get_latest(ticker_list[i]) * .0013 ,timeInForce="gtc",extendedHours=True)
        quantity_list.append(quantity)
        statement = "JUST PLACED A BUY LIMIT ORDER FOR " + ticker_list[i] + " at: " + buy_data["price"]
        #This is the part where we put the line to actually purchase the stock
        print(statement)
    return quantity_list

def sell_losers(losers, quantity_list): 
    ticker_list = losers
    #This is where the biggest loser tickers wil be stored
    #This is where the biggest loser prices at market close wil be stored
    for i in range(len(ticker_list)):
        sell_data = r.orders.order_sell_limit(ticker_list[i], quantity_list[i], get_latest(ticker_list[i]) - get_latest(ticker_list[i]) * .0013 , timeInForce="gtc", extendedHours=True)
        statement = "JUST PLACED A SELL LIMIT ORDER FOR " + ticker_list[i] + " AT: " + sell_data["price"]  
        #This is the part where we put the line to actually sell the stock
        print(statement)
    

def should_sleep():
    current_time = dt.datetime.now()
    if(current_time.hour == 16):
        return
    hr = 16 - current_time.hour
    if(hr > 0):
        val = (3600 * hr) - (60 * current_time.minute) - (current_time.second)
        print("ASLEEP FOR: " + str(val) + " SECONDS, STARTED AT " + str(current_time.hour) + ":" + str(current_time.minute) + ":" + str(current_time.second))
        time.sleep(val)
    else:
        hr = 24 + hr 
        val = (3600 * hr) - (60 * current_time.minute) - (current_time.second)
        print("ASLEEP FOR: " + str(val) + " SECONDS, STARTED AT " + str(current_time.hour) + ":" + str(current_time.minute) + ":" + str(current_time.second))
        time.sleep(val)


flag = False
login = r.login(cfg.vars["ROBINHOOD_USERNAME"], cfg.vars["ROBINHOOD_PASSWORD"])
loser_url = "https://cloud.iexapis.com/stable/stock/market/list/losers?token=" + cfg.vars["IEX_API_KEY"]
#This is the url we call for the data
should_sleep() #Checks if we should sleep until 4:00 p.m.
while(True):
    current_time = dt.datetime.now()
    data = get_jsonparsed_data(loser_url)
    losers = get_loser_list(data)
    if(current_time.hour == 16 and current_time.minute == 0 and flag == False):
        quantity_list = buy_losers(losers)
        flag = True
        min = 54 - current_time.minute 
        sec = current_time.second
        val = 3600 + (60 * min) - sec
        print("ASLEEP FOR: " + str(val) + " SECONDS, STARTED AT " + str(current_time.hour) + ":" + str(current_time.minute) + ":" + str(current_time.second))
        time.sleep(val) #Sleeps until 5:54 p.m. so we can sell the losers
    
    current_time = dt.datetime.now()
    if(current_time.hour == 19 and current_time.minute == 54 and flag):
        sell_losers(losers, quantity_list)
        flag = False
        min = 60 - current_time.minute 
        sec = current_time.second
        val = 72000 + (60 * min) - sec
        print("ASLEEP FOR: " + str(val) + " SECONDS, STARTED AT " + str(current_time.hour) + ":" + str(current_time.minute) + ":" + str(current_time.second))
        time.sleep(val) #Sleeps until 4:00 p.m. the next day so we can buy the next set of losers

