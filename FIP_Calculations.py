# -*- coding: utf-8 -*-
"""ScreenedPrices.ipynb

This script will return an excel sheet of stocks who meet the FIP (frog in pan) Calculations requirement* Note: Please understand what FIP is before running script.
Script will screen for volume>100k, price>$1.00, List of Industries, and stocks that have a positive 12 month Cumulative Return.
FIP calculations will be performed on the final list of screened stocks, and then be output as a excel document in the folder where your script is located.

# Please Have The Following Packages Installed

# !pip install yfinance
# !pip install yahoofinancials
# !pip install yahoo-finance
# !pip install yahoo_fin
# !pip install yahoo_fin --upgrade
# !pip install requests_html
# !pip install gspread


# Mount the drive if using google colab or juypter notebook
from google.colab import drive
drive.mount('/content/drive')

"""



from yahoofinancials import YahooFinancials
from yahoo_fin.stock_info import get_data
from yahoo_finance import Share
import pandas as pd

"""# Ticker List"""

# List of industries to keep


list_to_keep = ['Agricultural Chemicals','Aluminum','Engineering & Construction','Environmental Services','Home Furnishings','Homebuilding','Major Chemicals','Military/Government/Technical',
                'Mining &amp; Quarrying of Nonmetallic Minerals (No Fuels)','Package Goods/Cosmetics','Paints/Coatings','Precious Metals','Specialty Chemicals','Steel/Iron Ore','Telecommunications Equipment',
                'Aerospace','Auto Manufacturing','Auto Parts:O.E.M.','Automotive Aftermarket','Biotechnology: Laboratory Analytical Instruments','Building Materials','Construction/Ag Equipment/Trucks',
                'Electrical Products','Electronic Components','Engineering &amp; Construction','Fluid Controls','Industrial Machinery/Components','Industrial Specialties','Medical Specialities',
                'Metal Fabrications','Specialty Chemicals','Telecommunications Equipment','Automotive Aftermarket','Building Products','Consumer Electronics/Appliances','Consumer Specialties',
                'Diversified Electronic Products','Electrical Products','Electronic Components','Miscellaneous manufacturing industries','Specialty Chemicals','Apparel','Beverages (Production/Distribution)',
                'Consumer Electronics/Appliances','Consumer Specialties','Packaged Foods','Plastic Products','Recreational Products/Toys','Specialty Foods','Telecommunications Equipment','Advertising','Broadcasting',
                'Building operators','Catalog/Specialty Distribution','Consumer Specialties','Department/Specialty Retail Stores','Diversified Commercial Services','Hotels/Resorts',
                'Other Consumer Services','Other Specialty Stores','Professional Services','Restaurants','Telecommunications Equipment','Transportation Services','Business Services',
                'Finance: Consumer Services','Biotechnology: Biological Products (No Diagnostic Substances)','Biotechnology: Commercial Physical &amp; Biological Research',
                'Biotechnology: Electromedical &amp; Electrotherapeutic Apparatus','Biotechnology: In Vitro &amp; In Vivo Diagnostic Substances','Industrial Specialties','Major Pharmaceuticals',
                'Medical/Dental Instruments','Misc Health and Biotechnology Services','Business Services','Industrial Machinery/Components','Multi-Sector Companies','Advertising','Computer Communications Equipment',
                'Computer Manufacturing','Computer peripheral equipment','Computer Software: Prepackaged Software','Computer Software: Programming Data Processing','Diversified Commercial Services',
                'EDP Services','Electrical Products','Electronic Components','Industrial Machinery/Components','Professional Services','Radio And Television Broadcasting And Communications Equipment',
                'Semiconductors','Air Freight/Delivery Services','Marine Transportation']


#Ensure your stock list has the following columns: Symbol, Industry, Volume, Name, Industry and Market Cap Size


stocks_df = pd.read_excel('/content/drive/MyDrive/StocksToScreen/StockMasterList.xlsx')
stocks_df = stocks_df.loc[stocks_df['Industry'].isin(list_to_keep)]
stocks_df_new = stocks_df.rename(columns={'Market Cap Size':'MarketCapSize'})
#stocks_df

# Define the ticker list
ticker_list = stocks_df['Symbol']
print(ticker_list)

historical_datas = {}
for ticker in ticker_list:
    try:
      historical_datas[ticker] = get_data(ticker)
      print(f"saved {ticker}")
    except:
      print(f"Error with {ticker}")

# Spot test
historical_datas["TSLA"]['volume'].loc["2021-2-10"]

"""# Start Final Data Frame. Get Volume first and clear volumes <100,000"""

from pandas.tseries.offsets import BMonthEnd, BMonthBegin
from datetime import date

#Get today's date to get yesterdays volume
todayD1 = date.today()



#Create new data frame to hold and start building a complete data frame from all the stocks on the list
full_df = pd.DataFrame()

# Get last weekday's volume and append to df
for volTickers in ticker_list:
  try:
    x = historical_datas[volTickers]['volume'].loc[f"{todayD1.year}-{todayD1.month}-{todayD1.day -1}"]
    if x > 100000:
      full_df = full_df.append({volTickers : x}, ignore_index=True)
      full_df[volTickers] = historical_datas[volTickers]['volume'].loc["2021-2-10"]
  except:
      print(f"error with {volTickers}")

# Drop NaN rows to get a single row of volumes
full_df = full_df.dropna()
print(full_df)

"""# Create list of tickers from volume screened df"""

volScreenList = list(full_df.columns)
print(volScreenList)
print(len(volScreenList))

"""# Create Prices Data frame from volume screened list and remove tickers with avg price <1"""

#Get dates

todayD = date.today()
offset = BMonthEnd(-1)
offsetFirst = BMonthBegin(-13)

# Get first mo. first day, last mo. last day
lastDayLastMonth = todayD+offset
firstDayFirstMonth = todayD+offsetFirst


# Append prices to tickers
prices_df = pd.DataFrame()

for ticker in volScreenList:
  try:
    prices_df[ticker] = historical_datas[ticker]['close'].loc[f"{firstDayFirstMonth.year}-{firstDayFirstMonth.month}-{firstDayFirstMonth.day}" : f"{lastDayLastMonth.year}-{lastDayLastMonth.month}-{lastDayLastMonth.day}"]
    print(f"completed {ticker}")
  except:
    print(f"error with {ticker}")

#prices_df.head()
#historical_datas["AAPL"]['close'].loc["2020-2-1" : "2021-1-30"]
prices_df[:].mean()

pricesLessThan1_df = prices_df.copy()
pricesLessThan1_df.drop([col for col, val in pricesLessThan1_df.mean().iteritems() if val < 1], axis=1, inplace=True)

# Spot test
pricesLessThan1_df.tail()
pricesLessThan1_df['AAPL'].loc["2020-2-5"]

"""# Get Dates"""

# Get previous months dates

# Date Range:
firstDates = []
lastDates = []
d=date.today()

for x in range(1,13):
  offset = BMonthEnd(-x)
  offsetFirst = BMonthBegin(-x-1)
  firstDates.append(d+offsetFirst)
  lastDates.append(d+offset)

d=date.today()
print(lastDates)
print(firstDates)

"""# Get CRs"""

import time 
import datetime 

pricesLessThan1TickerList = list(pricesLessThan1_df.columns)

CR_dict = {}
for CRticker in pricesLessThan1TickerList:
  tempList = []
  for x in range(0,len(firstDates)):
    # Get First Date Value
    try:
      doubleFirst = pricesLessThan1_df[CRticker].loc[f"{firstDates[x].year}-{firstDates[x].month}-{firstDates[x].day}"]
    except:
      try:
        doubleFirst = pricesLessThan1_df[CRticker].loc[f"{firstDates[x].year}-{firstDates[x].month}-{firstDates[x].day+1}"]
      except:
        try:
          doubleFirst = pricesLessThan1_df[CRticker].loc[f"{firstDates[x].year}-{firstDates[x].month}-{firstDates[x].day+2}"]
        except:
          try:
            doubleFirst = pricesLessThan1_df[CRticker].loc[f"{firstDates[x].year}-{firstDates[x].month}-{firstDates[x].day+3}"]
          except:
            print("Failure in First Date Value")
    # Get Last Date Value
    try:
      doubleLast = pricesLessThan1_df[CRticker].loc[f"{lastDates[x].year}-{lastDates[x].month}-{lastDates[x].day}"]
    except:
      try:
        doubleLast = pricesLessThan1_df[CRticker].loc[f"{lastDates[x].year}-{lastDates[x].month}-{lastDates[x].day-1}"]
      except:
        try:
          doubleLast = pricesLessThan1_df[CRticker].loc[f"{lastDates[x].year}-{lastDates[x].month}-{lastDates[x].day-2}"]
        except:
          try:
            doubleLast = pricesLessThan1_df[CRticker].loc[f"{lastDates[x].year}-{lastDates[x].month}-{lastDates[x].day-3}"]
          except:
            print("Failure in Last Date Value")
      ###
    CRValue = ((doubleLast - doubleFirst)/doubleFirst)+1
    tempList.append(CRValue)
  #Append to dict
  CR_dict[CRticker] = tempList
# Create new data frame to hold CR's. Create list of tickers from pricesLessThan1_df

print(CR_dict)

import numpy

final_CR_dict = {}

for finalTickers in pricesLessThan1TickerList:
  tempList = CR_dict[finalTickers]
  final_CR_dict[finalTickers] = numpy.prod(tempList)-1


print(final_CR_dict)

"""# Get Num Up and Down for Year"""

# Use pricesLessThan1_df and get count of num pos days and num neg days
# Create a dictionary to hold the pos and neg number

pricesLessThan1_df.head(15)
posNeg_dict = {}

print(len(pricesLessThan1_df))

# Get counts for pos/neg times in the past year
for posnegTickers in pricesLessThan1_df.columns:
  posNeg_list = []
  # Set entire column values to list
  posNeg_list = pricesLessThan1_df[posnegTickers].tolist()
  results_list = []
  for x in range(0,len(posNeg_list)):
    #calculate (next - current)/current
    try:
      temp = ((posNeg_list[x+1] - posNeg_list[x])/posNeg_list[x])
      results_list.append(temp)
    except:
      #do nothing
      fake = -1
  #Count num pos and num neg
  pos_count, neg_count = 0,0
  for num in results_list:
    if num >= 0:
      pos_count +=1
    else:
      neg_count +=1
  
  #use dict to hold {ticker: [pos,neg]}
  posNeg_dict[posnegTickers] = [pos_count, neg_count]

print(len(posNeg_dict))

"""# FIP Calculation

> sign * [% neg - %pos]

sign = 1 if cr > 0
sign = -1 if cr < 0


"""

# iterate through each ticker and complete the final calculation
fip_dict = {}

temptempList = posNeg_dict['A']
print(temptempList)
for fipTickers in pricesLessThan1_df.columns:
  fipTempList = posNeg_dict[fipTickers]
  negPercent = fipTempList[1]/(fipTempList[0] + fipTempList[1])
  posPercent = fipTempList[0]/(fipTempList[0] + fipTempList[1])
  if final_CR_dict[fipTickers] > 0:
    signPRET = 1
  else:
    signPRET = -1
  fip_dict[fipTickers] = (signPRET * (negPercent - posPercent))

print(fip_dict)

fip_dict

ticktick = "CVAC"
print(final_CR_dict[ticktick])
print(fip_dict[ticktick])

"""# DICT TO DATA FRAMES"""

FIP_df = pd.DataFrame.from_dict(fip_dict, orient='index', columns=["FIP SCORE"])
CR_df = pd.DataFrame.from_dict(final_CR_dict, orient='index', columns=["12M CR Value"])

stocks_df[stocks_df['Symbol'] == "AAPL"]

#information dict
info_dict = {}
info_list = []


for symbs in pricesLessThan1_df.columns:
  for index,rows in stocks_df_new.iterrows():
    if rows.Symbol == symbs:
      info_list = [rows.Name, rows.Industry, rows.MarketCapSize]
      info_dict[symbs] = info_list

info_dict

# info_dict
info_df = pd.DataFrame.from_dict(info_dict, orient='index', columns=["Name","Industry","MarketCapSize"])

result_df = pd.concat([info_df,FIP_df,CR_df], axis=1, join ="inner")

result_df

"""# Print To Excel"""

#Exports to Local Data. Need to download to computer for now
result_df.to_excel('FIP_FEBRUARY.xlsx',index=True)

"""# Testing RSI api's"""

!pip install finnhub-python
from finnhub import client as Finnhub

from finnhub import client as Finnhub
client = Finnhub.Client(api_key="bsu3fpv48v6r5qhbp2ug")

symbol = "BLNK"

temp = client.aggregate_indicator(symbol, resolution='D')

print(temp)

# temp['technicalAnalysis']['signal']
temp['trend']['adx']
temp['trend']['trending']

# pattern recognition analysis
temp = client.pattern_recognition(symbol,resolution='D')
temp

for x in temp['points']:
  print(x['patternname'])
  print(x['patterntype'])
  print("")

print(client.recommendation_trends(symbol))

client.support_resistance(symbol, resolution="D")

# Load Technicals into data frame. Later merge data frame to master df
technicals_df = pd.DataFrame()

