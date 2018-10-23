#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 21:54:44 2018

@author: gaadi
"""

import nsepy
import pandas as pd
from datetime import date
import numpy as np
from bokeh.models import ColumnDataSource, LinearColorMapper
from bokeh.plotting import figure, show, output_file

nse_infy = nsepy.get_history(symbol='INFY',
                             start=date(2015,1,1),
                             end=date(2016,12,31))
nse_infy.index = pd.to_datetime(nse_infy.index)

nse_tcs = nsepy.get_history(symbol='TCS',
                             start=date(2015,1,1),
                             end=date(2016,12,31))
nse_infy.index = pd.to_datetime(nse_infy.index)

nifty_it_index = nsepy.get_history(symbol='NIFTY IT',
                             start=date(2015,1,1),
                             end=date(2016,12,31),
                             index=True)
nifty_it_index.index = pd.to_datetime(nifty_it_index.index)

def moving_avg_closing_price(data,weeks):
    data.index = pd.to_datetime(data.index) #convert to datetime for safety
    window_days = weeks*7
    closing_price = data[['Close']].copy()
    closing_price_avg = closing_price.rolling(window=(str(window_days)+'D')).mean()
    #min_periods is left to default value of 1
    return closing_price_avg

nse_infy_4w = moving_avg_closing_price(nse_infy,4)
nse_infy_16w = moving_avg_closing_price(nse_infy,16)
nse_infy_52w = moving_avg_closing_price(nse_infy,52)
nse_tcs_4w = moving_avg_closing_price(nse_tcs,4)
nse_tcs_16w = moving_avg_closing_price(nse_tcs,16)
nse_tcs_52w = moving_avg_closing_price(nse_tcs,52)
nifty_it_index_4w = moving_avg_closing_price(nifty_it_index,4)
nifty_it_index_16w = moving_avg_closing_price(nifty_it_index,16)
nifty_it_index_52w = moving_avg_closing_price(nifty_it_index,52)

# Volumn shock
def volume_shock(data):
    data.index = pd.to_datetime(data.index) #convert to datetime for safety
    data_volume = data[['Volume']].pct_change()
    volume_shock = data_volume.Volume.apply(lambda x: 1 if abs(x*100) > 10 else 0)
    # 1 if change greater than 10%
    volume_shock = volume_shock.rename('volume_shock')
    volume_direction = data_volume.Volume.apply(lambda x: 1 if x >= 0 else 0)
    # 1 if change is +ve or no change
    volume_direction = volume_direction.rename('volume_direction')
    
    return volume_shock,volume_direction

nse_infy_volume_shock,nse_infy_volume_direction = volume_shock(nse_infy)
nse_tcs_volume_shock,nse_tcs_volume_direction = volume_shock(nse_tcs)
nifty_it_volume_shock,nifty_it_volume_direction = volume_shock(nifty_it_index)

# Price Shock
def price_shock(data):
    data.index = pd.to_datetime(data.index) #convert to datetime for safety
    data_price = data[['Close']].pct_change()
    price_shock = data_price.Close.apply(lambda x: 1 if abs(x*100) > 2 else 0)
    # 1 if change greater than 2%
    price_shock = price_shock.rename('price_shock')
    price_direction = data_price.Close.apply(lambda x: 1 if x >= 0 else 0)
    # 1 if change is +ve or no change
    price_direction = price_direction.rename('price_direction')
    
    return price_shock,price_direction

nse_infy_price_shock,nse_infy_price_direction = price_shock(nse_infy)
nse_tcs_price_shock,nse_tcs_price_direction = price_shock(nse_tcs)
nifty_it_price_shock,nifty_it_price_direction = price_shock(nifty_it_index)

# Couldn't clearly understand black swan, so leaving it for now

# Pricing shock without volume shock
def price_shock_no_volume_shock(price_shock,volume_shock):
    condition = ((price_shock == 1) & (volume_shock == 0))
    price_shock_no_volume_shock = price_shock
    price_shock_no_volume_shock[:] = 0
    price_shock_no_volume_shock[condition] = 1
    return price_shock_no_volume_shock

nse_infy_price_vol_shock = price_shock_no_volume_shock(nse_infy_price_shock,nse_infy_volume_shock)
nse_tcs_price_vol_shock = price_shock_no_volume_shock(nse_tcs_price_shock,nse_tcs_volume_shock)
nifty_it_price_vol_shock = price_shock_no_volume_shock(nifty_it_price_shock,nifty_it_volume_shock)

# data visualization
## NSE INFY
source1 = ColumnDataSource(nse_infy)
nse_infy_plot = figure(x_axis_type="datetime", plot_width=800, plot_height=350,
                       title="INFY closing price timeseries")
nse_infy_plot.line('Date', 'Close', color='blue', source=source1)
output_file("nse_infy_plot.html")
show(nse_infy_plot)

nse_infy_volume_shock_subset = pd.Series(np.where(nse_infy_volume_shock == 1, nse_infy['Close'], np.nan))
nse_infy_volume_shock_subset = nse_infy_volume_shock_subset.rename('Close').to_frame()
nse_infy_volume_shock_subset.index = nse_infy.index
source2 = ColumnDataSource(nse_infy_volume_shock_subset)
nse_infy_plot.line('Date', 'Close', color='red', source=source2)
output_file("nse_infy_plot_volume_shock.html")
show(nse_infy_plot)

nse_infy['Close_diff_52'] = nse_infy[['Close']].sub(nse_infy_52w)
source3 = ColumnDataSource(nse_infy)
nse_infy_plot_52diff = figure(x_axis_type="datetime", plot_width=800, plot_height=350,
                       title="INFY closing price timeseries diff 52W")
color_mapper = LinearColorMapper(palette='Blues8', low=min(nse_infy.Close_diff_52), high=max(nse_infy.Close_diff_52))
nse_infy_plot_52diff.scatter('Date', 'Close_diff_52', color={'field': 'Close_diff_52', 'transform': color_mapper}, source=source3)
output_file("nse_infy_plot_52diff.html")
show(nse_infy_plot_52diff)

## NSE TCS
source1 = ColumnDataSource(nse_tcs)
nse_tcs_plot = figure(x_axis_type="datetime", plot_width=800, plot_height=350,
                       title="TCS closing price timeseries")
nse_tcs_plot.line('Date', 'Close', color='blue', source=source1)
output_file("nse_tcs_plot.html")
show(nse_tcs_plot)

nse_tcs_volume_shock_subset = pd.Series(np.where(nse_tcs_volume_shock == 1, nse_tcs['Close'], np.nan))
nse_tcs_volume_shock_subset = nse_tcs_volume_shock_subset.rename('Close').to_frame()
nse_tcs_volume_shock_subset.index = nse_tcs.index
source2 = ColumnDataSource(nse_tcs_volume_shock_subset)
nse_infy_plot.line('Date', 'Close', color='red', source=source2)
output_file("nse_tcs_plot_volume_shock.html")
show(nse_tcs_plot)

nse_tcs['Close_diff_52'] = nse_tcs[['Close']].sub(nse_tcs_52w)
source3 = ColumnDataSource(nse_tcs)
nse_tcs_plot_52diff = figure(x_axis_type="datetime", plot_width=800, plot_height=350,
                       title="TCS closing price timeseries diff 52W")
color_mapper = LinearColorMapper(palette='Blues8', low=min(nse_tcs.Close_diff_52), high=max(nse_tcs.Close_diff_52))
nse_tcs_plot_52diff.scatter('Date', 'Close_diff_52', color={'field': 'Close_diff_52', 'transform': color_mapper}, source=source3)
output_file("nse_tcs_plot_52diff.html")
show(nse_tcs_plot_52diff)

## NIFTY IT INDEX
source1 = ColumnDataSource(nifty_it_index)
nifty_it_plot = figure(x_axis_type="datetime", plot_width=800, plot_height=350,
                       title="NIFTY IT INDEX closing price timeseries")
nifty_it_plot.line('Date', 'Close', color='blue', source=source1)
output_file("nifty_it_plot.html")
show(nifty_it_plot)

nifty_it_volume_shock_subset = pd.Series(np.where(nifty_it_volume_shock == 1, nifty_it_index['Close'], np.nan))
nifty_it_volume_shock_subset = nifty_it_volume_shock_subset.rename('Close').to_frame()
nifty_it_volume_shock_subset.index = nifty_it_index.index
source2 = ColumnDataSource(nifty_it_volume_shock_subset)
nifty_it_plot.line('Date', 'Close', color='red', source=source2)
output_file("nifty_it_plot_volume_shock.html")
show(nifty_it_plot)

nifty_it_index['Close_diff_52'] = nifty_it_index[['Close']].sub(nifty_it_index_52w)
source3 = ColumnDataSource(nifty_it_index)
nifty_it_plot_52diff = figure(x_axis_type="datetime", plot_width=800, plot_height=350,
                       title="NIFTY IT INDEX closing price timeseries diff 52W")
color_mapper = LinearColorMapper(palette='Blues8', low=min(nse_tcs.Close_diff_52), high=max(nifty_it_index.Close_diff_52))
nifty_it_plot_52diff.scatter('Date', 'Close_diff_52', color={'field': 'Close_diff_52', 'transform': color_mapper}, source=source3)
output_file("nifty_it_plot_52diff.html")
show(nifty_it_plot_52diff)