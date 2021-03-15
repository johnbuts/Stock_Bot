
#This is my basic Robinhood Stock Bot, Buy/Sell based off of MACD
import robin_stocks
import robin_stocks.robinhood as r
import pyotp
from pyrh import Robinhood
import tulipy as tp
import numpy as np
import sched
import time
import datetime


price_list = []
two_factor = pyotp.TOTP("TWO FACTOR CODE").now()
login = r.login("USERNAME", "PASSWORD")
scheduler = sched.scheduler(time.time, time.sleep)
trade = False 
trade_counter = 0
first_candle_buy = -999
second_candle_buy = -999
third_candle_buy = -999
fourth_candle_buy = -999
first_bool_buy = True
second_bool_buy = False
third_bool_buy = False
fourth_bool_buy = False
fifth_bool_buy = False
first_candle_sell = 999
second_candle_sell = 999
third_candle_sell = 999
fourth_candle_sell = 999
first_bool_sell = True
second_bool_sell = False
third_bool_sell = False
fourth_bool_sell = False
fifth_bool_sell = False
current_candle_sell = 0
current_candle_sell = 0
current_time = datetime.datetime.now()
#prints the latest stock price as a float
def print_latest(STOCK_NAME):
    stock_upper = STOCK_NAME.upper()
    x = r.get_latest_price(stock_upper)
    print(str(x[0]))

#returnss the latest stock price as a float
def get_latest(STOCK_NAME):
    stock_upper = STOCK_NAME.upper()
    x = r.get_latest_price(stock_upper)
    return(float(x[0]))

def get_vol(STOCK_NAME):
    stock_upper = STOCK_NAME.upper()
    x = robin_stocks.robinhood.stocks.get_fundamentals(stock_upper, info=None)
    return float(x[0]["volume"])

def should_trade(STOCK_NAME):
    if(current_time.hour > 15 or current_time.hour <= 8): #sleeps until 9:31, and resumes sleep at 4:01
        hr = current_time.hour - 9
        mn = current_time.minute - 30
        if(hr < 0): hr = abs(hr)
        else: hr = 24 - hr
        if(mn < 0): mn = abs(mn)
        else: mn = 60 - mn
        val = 3600 * hr + 60 * mn
        print("ASLEEP FOR: " + str(val) + " SECONDS, STARTED AT " + str(current_time.hour) + ":" + str(current_time.minute) + ":" + str(current_time.second))
        time.sleep(val)
    
    latest_price = get_latest(STOCK_NAME)
    global trade
    global trade_counter
    global price_list
    if len(price_list) < 15: 
    #add to the list until we can do the calculation
        price_list.append(latest_price)
        print(str(price_list) + str(len(price_list)))
        #counter += 1
        #print(counter)
    elif len(price_list) > 15 and trade_counter < 4:
        print("*--------------*")
        numpy_price_list = np.array(price_list)
        (macd, macd_signal, macd_histogram) = tp.macd(numpy_price_list, 5, 13, 1)
        print("MACD IS: " + str(macd[len(macd_signal) - 1]))
        print("SIGNAL MACD IS: " + str(macd_signal[len(macd_signal) - 1]))
        if macd[len(macd) - 1] < macd_signal[len(macd_signal) - 1] and trade == False: # just checking if tan is over blue
            #tan over blue, you buy
            should_buy = buy_streak(macd_signal[len(macd_signal) - 1]) 
            if (should_buy):
                print("JUST BOUGHT AT" + str(latest_price))
                trade = True
                trade_counter += 1
        
        elif macd_signal[len(macd_signal) - 1] < macd[len(macd) - 1] and trade == True: #checking if blue is over tan
        #tan over blue, and if you have the stock already, you sell
            should_sell = sell_streak(macd[len(macd) -1]) 
            if (should_sell):
                print("JUST SOLD AT" + str(latest_price))
                trade = True
                trade_counter += 1
        price_list.append(latest_price)
    

    scheduler.enter(180, 1, should_trade, ("F"))

def buy_streak(signal):
    global first_candle_buy
    global second_candle_buy
    global third_candle_buy
    global fourth_candle_buy
    global first_bool_buy
    global second_bool_buy
    global third_bool_buy
    global fourth_bool_buy
    global current_candle_buy
    global fifth_bool_buy
    #signal is tan
    #already if tan is over blue
    #WHAT THIS IS DOING:
    #Pretty much, its checking for a streak of when the macd is decreasing, so we can get a good price, so once it goes down 4 times in a row, we buy it
    if(first_candle_buy == -999 and first_bool_buy and signal < 0):
        first_candle_buy = signal
        first_bool_buy = False
        second_bool_buy = True
        print("1st")

    elif(first_candle_buy >= signal and second_bool_buy and signal < 0):
        second_candle_buy = signal
        second_bool_buy = False
        third_bool_buy = True
        print("2nd")

    elif(second_candle_buy >= signal and third_bool_buy and signal < 0):
        third_candle_buy = signal
        third_bool_buy = False
        fourth_bool_buy = True
        print("3rd")

    elif(third_candle_buy >= signal and fourth_bool_buy and signal < 0):
        fourth_candle_buy = signal
        fourth_bool_buy = False
        fifth_bool_buy = True
        print("4th")

    elif(fourth_candle_buy >= signal and fifth_bool_buy and signal < 0):
        reset_globals()
        return True

    else:
        print("FAIL, 5th")
        reset_globals()
        return False

    return False

def sell_streak(mac):
    global first_candle_sell
    global second_candle_sell
    global third_candle_sell
    global fourth_candle_sell
    global first_bool_sell
    global second_bool_sell
    global third_bool_sell
    global fourth_bool_sell
    global fifth_bool_sell
    global current_candle_sell
    #macD is blue
    #WHAT THIS IS DOING:
    #Pretty much, its checking for a streak of when the macd is increasing, so we can get a good price, so once it goes up 4 times in a row, we sell it
    if(first_candle_sell == 999 and first_bool_sell and mac > 0):
        first_candle_sell = mac
        first_bool_sell = False
        second_bool_sell = True
        print("1st BUY")

    elif(first_candle_sell <= mac and second_bool_sell and mac > 0):
        second_candle_sell = mac
        second_bool_sell = False
        third_bool_sell = True
        print("2nd BUY")

    elif(second_candle_sell <= mac and third_bool_sell and mac > 0):
        third_candle_sell = mac
        third_bool_sell = False
        fourth_bool_sell = True
        print("3rd BUY")

    elif(third_candle_sell <= mac and fourth_bool_sell and mac > 0):
        fourth_candle_sell = mac
        fourth_bool_sell = False
        fifth_bool_sell = True
        print("4th BUY")

    elif(fourth_candle_sell <= mac and fifth_bool_sell and mac > 0):
        reset_globals()
        print("SUCCESS BUY")
        return True

    else:
        reset_globals()
        print("FAIL, 5th BUY")
        return False
    return False

def reset_globals():
    global first_candle_sell
    global second_candle_sell
    global third_candle_sell
    global fourth_candle_sell
    global first_bool_sell
    global second_bool_sell
    global third_bool_sell
    global fourth_bool_sell
    global fifth_bool_sell
    global first_candle_buy
    global second_candle_buy
    global third_candle_buy
    global fourth_candle_buy
    global first_bool_buy
    global second_bool_buy
    global third_bool_buy
    global fourth_bool_buy
    global fifth_bool_buy
    first_candle_sell = 999
    second_candle_sell = 999
    third_candle_sell = 999
    fourth_candle_sell = 999
    first_bool_sell = True
    second_bool_sell = False
    third_bool_sell = False
    fourth_bool_sell = False
    fifth_bool_sell = False
    first_candle_buy = -999
    second_candle_buy = -999
    third_candle_buy = -999
    fourth_candle_buy = -999
    first_bool_buy = True
    second_bool_buy = False
    third_bool_buy = False
    fourth_bool_buy = False
    fifth_bool_buy = False
    print("RESET")


scheduler.enter(1, 1, should_trade, ("F"))
scheduler.run() 
#print(get_latest("USDP"))
#-------------------- TIME AND SCHEDULE
# function to print time  
# and name of the event 
#scheduler = sched.scheduler(time.time, time.sleep) 
#def print_event(name): 
#    print('EVENT: ') 
#    scheduler.enter(10, 1, print_event, ('1 st', )) 
# printing starting time 
#print ('START:', time.time()) 
# first event with delay of 
# 1 second 
# executing the events 
#scheduler.enter(10, 1, print_event, ('1 st', ))#seconds, #priority, #function, #parameter in weird format
#scheduler.run() 
#----------------------------- MAC D
#m = np.array([12, 12.01, 12.02, 12.03, 12.04, 12.05, 12.06, 12.07, 12.08, 
#12.09, 12.10, 12.11, 12.12, 12.13, 12.14, 12.15, 12.16, 12.17, 12.18, 12.19, 12.20,
#12.21, 12.22, 12.23, 12.23, 12.4, 12.6])
#(macd, macd_signal, macd_histogram) = tp.macd(m, 12, 26, 9)
#short, #long, signal params
#print(macd) #blue
#print(macd_signal) #tan
#blue over tan you buy
#tan over blue you sell

#print(macd_histogram)
