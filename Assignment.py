#!/usr/bin/env python
# coding: utf-8

# In[333]:


#Insert libraries


# In[334]:


import pandas as pd
import datetime as dt
import numpy as np
from dateutil.relativedelta import relativedelta
import MySQLdb
import matplotlib.pyplot as plt


# In[335]:


#Necessary Keys for mysql DB access`


# In[336]:


hostname= "sql6.freesqldatabase.com"
username= "sql6492539"
password= "eSsNRpl62A"
database = "sql6492539"
port =3306
myDB = MySQLdb.connect(port=port,host=hostname,user=username,passwd=password,db=database)
cur = myDB.cursor()


# In[337]:


#Read xlsx and file and create csv from it


# In[338]:


df = pd.read_excel('/Users/arpan/Downloads/momentum_500close(2).xlsx')


# In[339]:


df_new = df.to_csv('momentum.csv', encoding='utf-8', index=False)


# In[340]:


newdata = pd.read_csv('momentum.csv')


# In[341]:


#Modifying the input schema


# In[342]:


newdata = newdata.drop(index=0)


# In[343]:


newdata.rename(columns = {'Unnamed: 0':'Date'}, inplace = True)


# In[344]:


monthly_return = newdata


# In[345]:


monthly_return.index = pd.to_datetime(newdata['Date'])


# In[346]:


monthly_return = monthly_return.iloc[:,1:]


# In[347]:


monthly_return = monthly_return.astype(float)


# In[348]:


#Calculating profit from the daily percentage change in prices and then resampling it to a monthly basis


# In[349]:


monthly_return = monthly_return.pct_change().resample('M').agg(lambda x:(x+1).prod()-1)


# In[350]:


#Calculating returns for the past 12 months excluding the last month


# In[351]:


past_months = (monthly_return+1).rolling(11).apply(np.prod)-1


# In[352]:


#Function for creating basket of optimal stocks and the overall return


# In[353]:


def meanbasketreturns(past_months,end_measurement):
    return_for_past_12_months = past_months.loc[end_measurement]
    return_for_past_12_months = return_for_past_12_months.reset_index()
    return_for_past_12_months.rename(columns = {return_for_past_12_months.columns[1]:'Date'}, inplace = True)
    return_for_past_12_months.sort_values(by=['Date'], inplace=True, ascending=False)
    momentum_basket = list(return_for_past_12_months.iloc[:21,0])
    mean_returns = return_for_past_12_months.iloc[:21,1].mean()
    return momentum_basket,mean_returns


# In[354]:


#Function for insertion of momentum stocks for a particular date into MySQL db


# In[355]:


def insertintoDB(date,momentum_basket):
    sql_date = date
    sql_stocks = ",".join(momentum_basket)
    sql_weights = "Same weightage"
    
    insert_query = 'INSERT INTO `momentum_investing` (Date,Stocks,Weights) VALUES ('
    variables = "'" + str(sql_date) + "', '" + str(sql_stocks) + "', '" + sql_weights +"')"
    insert_query+= variables
    
    cur.execute(insert_query)
    myDB.commit()


# In[356]:


#Final dataframe for storing returns


# In[357]:


annualreturns = pd.DataFrame(columns = ['date', 'returns'])
print(annualreturns)


# In[358]:


#Dates for which the portfolio is rebalanced


# In[359]:


formation_dates = [dt.datetime(2008,12,31),dt.datetime(2009,12,31),dt.datetime(2010,12,31),dt.datetime(2011,12,31),
                   dt.datetime(2012,12,31),dt.datetime(2013,12,31),dt.datetime(2014,12,31),dt.datetime(2015,12,31),
                   dt.datetime(2016,12,31),dt.datetime(2017,12,31),dt.datetime(2018,12,31),
                   dt.datetime(2019,12,31), dt.datetime(2020,12,31)]


# In[360]:


#Creating basket for each timeframe


# In[361]:


for date in formation_dates:
    end_date = date - relativedelta(months=1)
    momentum_basket,mean_returns = meanbasketreturns(past_months,end_date)
    insertintoDB(date, momentum_basket)
    annualreturns = annualreturns.append({'date' : date, 'returns' : mean_returns}, 
                ignore_index = True)


# In[362]:


#Rolling Volatility


# In[363]:


annualreturns['volatility'] = annualreturns['returns'].pct_change().rolling(3).std()


# In[364]:


#Drawdown


# In[365]:


annualreturns['cumulative'] = annualreturns.returns.cumsum()


# In[366]:


annualreturns['HighValue'] = annualreturns['cumulative'].cummax()
annualreturns['Drawdown'] = annualreturns['cumulative'] - annualreturns['HighValue']


# In[367]:


#Rolling Sharpe


# In[368]:


def calc_sharpe_ratio(y):
    return np.sqrt(13) * (y.mean() / y.std())


# In[369]:


annualreturns['rs'] = annualreturns['returns'].rolling(3).apply(calc_sharpe_ratio)

fig, ax = plt.subplots(figsize=(10, 3))
annualreturns['rs'].plot(style='-', lw=3, color='indianred', label='Sharpe')\
        .axhline(y = 0, color = "black", lw = 3)

plt.ylabel('Sharpe ratio')
plt.legend(loc='best')
plt.title('Rolling Sharpe ratio (10years)')
fig.tight_layout()
plt.show()


# In[370]:


annualreturns


# In[371]:


plt.ylabel('Standard Deviation')
plt.legend(loc='best')
plt.title('Volatility(10years)')
fig.tight_layout()
plt.plot(annualreturns.date, annualreturns.volatility)


# In[ ]:




