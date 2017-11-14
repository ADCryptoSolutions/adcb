# -*- coding: utf-8 -*-
"""
Created on Thu Nov 02 18:37:54 2017

@author: Daniel
"""

import pandas as pd
from pandas_datareader import data
import datetime
import matplotlib.pyplot as plt
import numpy as np


def rsi(close,w=14):
    
    # Window length for moving average
    window_length = w
    # Get the difference in price from previous step
    delta = close.diff()
    # Get rid of the first row, which is NaN since it did not have a previous 
    # row to calculate the differences
    #delta = delta[1:] 
    
    # Make the positive gains (up) and negative gains (down) Series
    up, down = delta.copy(), delta.copy()
    up[up < 0.0] = 0.0
    down[down > 0.0] = 0.0
    
    # Calculate the EWMA
    roll_up1 = pd.stats.moments.ewma(up, window_length)
    roll_down1 = pd.stats.moments.ewma(down.abs(), window_length)
     
    # Calculate the RSI based on EWMA
    RS1 = roll_up1 / roll_down1
    # Replace inf values with NaN
    #RS1.replace(np.inf, np.nan,inplace=True)
    # fill NaN values  with the next non NaN value
    #RS1.fillna(method='bfill',inplace=True)
    RSI1 = 100.0 - (100.0 / (1.0 + RS1))
    #RSI1.dropna(axis=0,inplace=True)
    
    # Calculate the SMA
    roll_up2 = pd.rolling_mean(up, window_length)
    roll_down2 = pd.rolling_mean(down.abs(), window_length)
    
    # Calculate the RSI based on SMA
    RS2 = roll_up2 / roll_down2
    RSI2 = 100.0 - (100.0 / (1.0 + RS2))
    
    df = pd.DataFrame(data={"RSI1":RSI1,"close":close,"up":up,"down":down,"roll_up1":roll_up1,"roll_down1":roll_down1,"RS1":RS1,"delta":delta})
    
    
    return RSI1,df
		
if __name__ == "__main__":
    # Dates
    start = datetime.datetime(2010, 1, 1)
    end = datetime.datetime(2013, 1, 27)
    # Get data
    data = data.DataReader('AAPL', 'yahoo', start, end)
    # Get just the close
    close = data['Adj Close']
    
    RSI1, RSI2 = rsi(close=close)
    # Compare graphically
    plt.figure()
    RSI1.plot()
    RSI2.plot()
    plt.legend(['RSI via EWMA', 'RSI via SMA'])
    plt.show()
