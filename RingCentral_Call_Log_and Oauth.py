###Automated Oauth and Call Log Retrieval - template to extract call records from RingCentral via Python

import time
import urllib
import requests
import pandas as pd
import base64
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.common.by import By
options = webdriver.ChromeOptions()
import json
from datetime import datetime
import arrow
from urllib import parse
import os
import locale
import sys
import _locale

#JUPYTER SETTINGS
from IPython.core.display import display, HTML
display(HTML("<style>.container { width:80% !important; }</style>"))
pd.set_option('display.max_colwidth',-1) ######Sets the Jupyter Notebook wider to see more of what you are typing (script creation purpose)
pd.set_option('display.expand_frame_repr', False)

cid='XXXCLIENT_IDXXX'
secret='XXXCLIENT_SECRETXXX'
user='XXXUSERNAMEXXX'
passcode='XXXPASSWORDXXX'
state= 'XXANYTHINGXX'
rduri='http://localhost/'
rcurl= 'https://platform.ringcentral.com/restapi/oauth/token?'

phones=(XXXPHONE#1XXX,XXXPHONE#2XXX,XXXPHONE#3XXX)


def authrequest():
    Rbody=('response_type=code&','redirect_uri=http://localhost/',f'client_id={cid}&',f'state={state}&','display=prompt=')

    auth=('https://platform.ringcentral.com/restapi/oauth/authorize?'
        f'client_id={cid}&'
        f'redirect_uri={rduri}&'
        'response_type=code&'
        f'state={state}&'
        'display=&'
        'prompt='
        )

    profile_path= r"C:\XXXPATH_TO_YOUR_CHROME_PROFILEXXX\Profile 2"
    options.add_argument(f'user-data-dir={profile_path}')
    prefs = {"download.default_directory" : r"C:\XXXPATH_TO_DEFAULT_DIRECTORY"}
    driver = webdriver.Chrome(chrome_options=options)
    driver.maximize_window()
    time.sleep(3)
    driver.get(auth)
    time.sleep(2)
    username = driver.find_element_by_xpath('//*[@id="credential"]')
    time.sleep(2)
    username.clear()
    username.send_keys(user)
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="pageContent"]/div/div/div/form/div/div/div/div[2]/div[2]/button').click()
    time.sleep(3)
    password = driver.find_element_by_xpath('//*[@id="password"]')                                        
    password.send_keys(passcode)
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="pageContent"]/div/div/div/form/div/div[1]/div/div/div[3]/div/div/button[2]').click()
    time.sleep(4)
    driver.find_element_by_xpath('//*[@id="pageContent"]/div/div/div/div[2]/div/div/div[3]/div/div/button[2]').click()
    time.sleep(3)
    aclink=driver.current_url

    acode= aclink.partition('&')

    acode = acode[0]
    acode = acode[23:]
    rcurl='https://platform.ringcentral.com/restapi/oauth/token?'
    headers = {
        "Content-Type" : "application/x-www-form-urlencoded"}

    values=(
        'grant_type=authorization_code&'
        f'code={acode}&'
        f'client_id={cid}&'
        f'redirect_uri={rduri}&'
        'access_token_ttl=7200&'
        'refresh_token_ttl=306047999')
    
    params= urllib.parse.parse_qsl(values)
    arequest=requests.post(rcurl,headers=headers, data = params).json() 

    arequest
    global atoken
    atoken=(arequest['access_token']) #Need to keep this
    global rtoken
    rtoken=(arequest['refresh_token']) #Need to keep this, as it refreshes the access token and 
    driver.close()
    return
    
authrequest()

def accessrefresh():
    rturl='https://platform.ringcentral.com/restapi/oauth/token'
    headers={
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        "Authorization": "Basic " + base64.b64encode((cid + ':' + secret).encode()).decode()
        }

    body= (
        f'refresh_token={rtoken}&'
        'grant_type=refresh_token')

    req=requests.post(rturl,headers=headers,data=body).json()
    global at
    at=(req['access_token'])

accessrefresh()


list=[]

def logapi():
    
    for phone in phones:
        curl='https://platform.ringcentral.com/restapi/v1.0/account/~/call-log'
        accountId = '~'
        extensionId = '~'

        dateTo=arrow.utcnow()
        dateTo=dateTo.strftime('%Y-%m-%dT%I:%M:%S.%f')
        dateTo=(dateTo[0:23]+'Z')
        dateFrom='2021-06-01T00:01:01.000Z'

        headers= {'Authorization':'Bearer '+ at,'Accept': 'application/json','Content-Type': 'application/json'}
        params={

            'phoneNumber':f'{phone}',
            'view':'Detailed',
            'perPage':'1000',
            'direction':'Inbound',
             'showBlocked':True,
             'dateTo':dateTo,
             'dateFrom':f'{dateFrom}'}
        global clog
        clog=requests.get(curl,headers=headers,params=params).json()
        list.append(clog)
        
    

logapi()

def cleanjson():
    global list
    list=pd.DataFrame(list)
    list=list.explode('records')
    list=list.dropna()
    list=pd.json_normalize(list['records'])
    list=list.drop(columns='legs')
    list['startTime']=pd.to_datetime(list['startTime'])
    list['startTime']=list['startTime'].dt.tz_localize(None)
    list['to.phoneNumber']=list['to.phoneNumber'].str[2:]
    list['from.phoneNumber']=list['from.phoneNumber'].str[2:]

cleanjson()
