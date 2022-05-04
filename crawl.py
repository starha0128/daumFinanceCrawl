from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pyperclip

import re

import time

def reportGetDriver(Headless, url):
    chrome_options = webdriver.ChromeOptions()

    if(Headless):
        chrome_options.add_argument('headless')
        
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("disable-gpu")
    # chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('land=ko_KR')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options=chrome_options)

    driver.implicitly_wait(30)

    driver.get(url)

    return driver

def getStockInfo(code):
    stockUrl = f'https://wisefn.finance.daum.net/v1/company/c1020001.aspx?cmp_cd={code}'

    info = {}

    driver = reportGetDriver(False, stockUrl) #기업개요

    print("종목 개요 크롤링")
    
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located)
    time.sleep(1)

    info['compEPS'] = driver.find_element(By.CSS_SELECTOR, "table#comInfo > tbody > tr:last-child > td.m_box > b:nth-child(1)").text
    info['compBPS'] = driver.find_element(By.CSS_SELECTOR, "table#comInfo > tbody > tr:last-child > td.m_box > b:nth-child(3)").text
    info['compPER'] = driver.find_element(By.CSS_SELECTOR, "table#comInfo > tbody > tr:last-child > td.m_box > b:nth-child(5)").text
    info['sectorPER'] = driver.find_element(By.CSS_SELECTOR, "table#comInfo > tbody > tr:last-child > td.m_box > b:nth-child(7)").text
    info['compPBR'] = driver.find_element(By.CSS_SELECTOR, "table#comInfo > tbody > tr:last-child > td.m_box > b:nth-child(9)").text
    print("EPS / BPS / PER / PBR 크롤링 완료")

    info['compOwner'] = driver.find_element(By.CSS_SELECTOR, "#cTB201 > tbody > tr:nth-child(3) > td.c4.txt").text
    print("대표이사 정보 크롤링 완료")

    comInfo = driver.find_element(By.ID, "comInfo").screenshot_as_png
    with open('./img/comInfo.png', 'wb') as file:
        file.write(comInfo)
    print("종목 정보 요약 이미지 저장 완료")

    comHistory = driver.find_elements(By.CSS_SELECTOR, "#cTB202 > tbody > tr")  #최근연혁
    history = []
    # comHistoryFlag = driver.find_elements(By.CSS_SELECTOR, "#cTB202 > tbody > tr:nth-child(2) > td")
    try:
        for i in comHistory:
            date = i.find_element(By.TAG_NAME, "th").text
            cont = i.find_element(By.TAG_NAME, "td").get_attribute("title")
            history.append(f'{date} - {cont}')

        info['compHST'] = history[1:-1]
    except:
        info['compHST'] = "None"
    print("최근연혁 크롤링 완료")
    
    salesRatio = driver.find_elements(By.CSS_SELECTOR, "#cTB203 > tbody > tr")  #주요제품 매출구성(%)
    salesR = []
    salesRatioFlag = driver.find_element(By.CSS_SELECTOR, "#cTB203 > tbody > tr:nth-child(2) > td").text
    if "검색된 데이터가 없습니다." not in salesRatioFlag:
        for i in salesRatio:
            product = i.find_element(By.TAG_NAME, "th").get_attribute("title")
            ratio = i.find_element(By.TAG_NAME, "td").text
            salesR.append(f'{product} - {ratio}')

        info['compSalesRatio'] = salesR[1:-1]
    else:
        info['compSalesRatio'] = "None"
    print("주요제품 매출구성 크롤링 완료")


    marketShare = driver.find_elements(By.CSS_SELECTOR, "#cTB204 > tbody > tr") #주요제품 시장 점유율(%)
    marketSh = []
    marketShareFlag = driver.find_element(By.CSS_SELECTOR, "#cTB204 > tbody > tr:nth-child(2) > td").text
    if "검색된 데이터가 없습니다." not in marketShareFlag:
        for i in marketShare:
            market = i.find_element(By.TAG_NAME, "th").get_attribute("title")
            ratio = i.find_element(By.TAG_NAME, "td").text
            marketSh.append(f'{market} - {ratio}')

        info['compMarketShare'] = marketSh[1:-1]
    else:
        info['compMarketShare'] = "None"
    print("주요제품 시장 점유율 크롤링 완료")


    driver.get(f'https://wisefn.finance.daum.net/v1/company/c1010001.aspx?cmp_cd={code}')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located)
    time.sleep(1)
    
    comRecommend = driver.find_element(By.ID, "cTB15").screenshot_as_png
    with open('./img/comRecommend.png', 'wb') as file:
        file.write(comRecommend)
    print("투자의견 요약 이미지 저장 완료")

    prcInfo = {}
    priceInfo = str(driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(1) > td").text)
    prcInfo['endPrice'] = priceInfo.split(" / ")[0] #종가(원)
    prcInfo['DTD'] = priceInfo.split(" / ")[1]      #전일대비
    prcInfo['yield'] = priceInfo.split(" / ")[2]    #수익률
    print("종가/전일대비/수익률 크롤링 완료")

    prc52 =  str(driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(2) > td").text)
    prcInfo['52High'] = prc52.split(" / ")[0]   #52주 고가
    prcInfo['52Low'] = prc52.split(" / ")[1]    #52주 저가
    print("52주 고/저가 크롤링 완료")

    prcInfo['faceValue'] = driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(3) > td").text   #액면가
    print("액면가 크롤링 완료")

    tradeInfo = str(driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(4) > td").text)
    tradeUnit = re.findall('\(([^)]+)', str(driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(4) > th").text))[0]
    prcInfo['tradeVol'] = f'{tradeInfo.split(" / ")[0]} {tradeUnit}' #거래량
    prcInfo['transactionAmount'] = f'{tradeInfo.split(" / ")[1]} {tradeUnit}'    #거래대금
    print("거래량/거래대금 크롤링 완료")

    marketCap = driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(5) > td").text
    capeUnit = re.findall('\(([^)]+)', str(driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(5) > th").text))[0]
    prcInfo['marketCap'] = f'{marketCap} {capeUnit}'    #시가총액
    print("시가총액 크롤링 완료")

    prcInfo['betaCoefficient'] = driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(6) > td").text     #52주 베타
    print("52주 베타 크롤링 완료")

    compStk = str(driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(7) > td").text)
    prcInfo["totalIssuedStk"] = compStk.split(" / ")[0] #발행주식수
    prcInfo["currRatio"] = compStk.split(" / ")[1]  #유동비율
    print("발행주식/유동비율 크롤링 완료")

    prcInfo['foreOwn'] = driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(8) > td").text #외국인지분율
    print("외국인지분율 크롤링 완료")

    yieldList = {}
    yieldTxt = str(driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(9) > td").text)
    yieldList['yield1M'] = yieldTxt.split(" / ")[0] #1달수익
    yieldList['yield3M'] = yieldTxt.split(" / ")[1] #3달수익
    yieldList['yield6M'] = yieldTxt.split(" / ")[2] #6달수익
    yieldList['yield1Y'] = yieldTxt.split(" / ")[3] #1년수익
    print("1/3/6달, 1년 수익률 크롤링 완료")

    prcInfo['yieldList'] = yieldList

    trendChart = driver.find_element(By.CSS_SELECTOR, "#pArea > div:nth-child(6) > table > tbody").screenshot_as_png
    with open('./img/trend.png', 'wb') as file:
        file.write(trendChart)
    print("주가/상대수익률 추이 이미지 저장 완료")

    info["prcInfo"] = prcInfo

    driver.get(f'https://finance.daum.net/quotes/A{code}#news/disclosure')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located)
    time.sleep(1)
    print("공시정보 크롤링 진행")

    disclosureList = driver.find_element(By.CSS_SELECTOR, "#boxContents > div:nth-child(5) > div:nth-child(3) > div.box_contents > div > ul > li")

    print(info)

    driver.quit()

def test(code):
    stockUrl = f'https://wisefn.finance.daum.net/v1/company/c1010001.aspx?cmp_cd={code}'
    driver = reportGetDriver(False, stockUrl) #기업개요

    priceInfo = driver.find_element(By.CSS_SELECTOR, "#cTB11 > tbody > tr:nth-child(1) > td").text
    print(priceInfo)

    driver.quit()

if __name__ == '__main__':
    # code = "282330"
    # code = "282880"
    code = "005930"
    getStockInfo(code)
    # test(code)
