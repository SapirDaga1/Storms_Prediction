import time
import numpy as np
import bs4
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import itertools

# required years
LAST_YEAR = 2021
FIRST_YEAR = 1950
# required oceans
oceansURL = {
    'Atlantic Ocean': "https://www.wunderground.com/hurricane/archive/AL",
    'East Pacific': "https://www.wunderground.com/hurricane/archive/EP",
    'Western Pacific': "https://www.wunderground.com/hurricane/archive/WP",
    'Indian Ocean': "https://www.wunderground.com/hurricane/archive/IO",
    'Central Pacific': "https://www.wunderground.com/hurricane/archive/CP",
    'Southern Hemisphere': "https://www.wunderground.com/hurricane/archive/SH"
}

# required fields
yearOfStorm = []
oceans = []
dates = []
hours = []
stormsName = []
stormType = []
latCorr = []
longCorr = []
windPower = []
airPressure = []
deaths = []
damagedUsd = []
# Enter in chromeDriverPath your chrome driver path
chromeDriverPath = ""
s = Service(chromeDriverPath)
driver = webdriver.Chrome(service=s)


# get bs4 obj of current URL using driver and bs4
def getSoupObj(url):
    driver.get(url)
    c = driver.page_source
    return bs4.BeautifulSoup(c, "html.parser")


def sendToCSV(dataFrame, fileName):
    dataFrame.to_csv(fileName, index=False)


def getDataFrame(stormsName, yearOfStorm, oceans, dates, hours, windPower, airPressure, stormType, latCorr, longCorr):
    return pd.DataFrame(
        pd.DataFrame({'storm_name': stormsName, 'year': yearOfStorm, 'Ocean': oceans, 'date': dates, 'time': hours,
                      'wind_power': windPower,
                      'air_pressure': airPressure, 'storm_type': stormType, 'lat': latCorr, 'long': longCorr}))


def scrapData():
    for ocean, url in oceansURL.items():
        for i in range(LAST_YEAR, FIRST_YEAR, -1):
            scrapDataFromCurrYear(i, ocean, yearOfStorm, oceans, dates, hours, windPower, airPressure,
                                  stormType, stormsName, latCorr, longCorr, url)

    driver.quit()


def getStormRecords(soup, year, ocean, years, oceans, dates, hours, windPower, airPressure,
                    stormType, stormNames, latCorr, longCorr):
    # Sleep for wait for the dynamic page will be loaded.
    time.sleep(2)
    stormName = driver.find_element(By.CLASS_NAME, 'sub-header').text
    stormName = stormName.split(' ')[1]
    stormName = 'NOT_NAMED' if stormName == 'NOT' else stormName
    try:
        rows = soup.find('tbody').find_all('tr')
    except:
        rows = []
    for row in rows:
        columns = row.find_all('td')
        years.append(year)
        oceans.append(ocean)
        stormNames.append(stormName)
        dates.append(columns[0].text)
        hours.append(columns[1].text)
        latCorr.append(columns[2].text)
        longCorr.append(columns[3].text)
        windPower.append(columns[4].text)
        airPressure.append(columns[5].text)
        stormType.append(columns[6].text)


def xpath_soup(element):
    """
    Generate xpath of soup element
    :param element: bs4 text or node
    :return: xpath as string
    """
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        """
        @type parent: bs4.element.Tag
        """
        previous = itertools.islice(parent.children, 0, parent.contents.index(child))
        xpath_tag = child.name
        xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
        components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)


def getInfoOfRow(row, year, ocean, years, oceans, dates, hours, windPower, airPressure,
                 stormType, stormNames, latCorr, longCorr):
    columns = row.find_all('td')
    startDate = str(columns[1].text).split(' - ')[1] + '/' + str(year)
    years.append(year)
    oceans.append(ocean)
    stormNames.append(columns[0].text)
    dates.append(startDate)
    hours.append('12:00:00 PM')
    latCorr.append(np.nan)
    longCorr.append(np.nan)
    windPower.append(columns[2].text)
    airPressure.append(columns[3].text)
    stormType.append(columns[4].text)


def getGeneralRecord(year, ocean, years, oceans, dates, hours, windPower, airPressure,
                     stormType, stormNames, latCorr, longCorr):
    soup = getSoupObj(driver.current_url)
    try:
        rows = soup.find('tbody').find_all('tr')
    except:
        rows = []
    for row in rows:
        getInfoOfRow(row, year, ocean, years, oceans, dates, hours, windPower, airPressure,
                     stormType, stormNames, latCorr, longCorr)


def scrapDataFromCurrYear(year, ocean, years, oceans, dates, hours, windPower, airPressure,
                          stormType, stormNames, latCorr, longCorr, url):
    try:
        url = url + '/' + str(year)
        driver.get(url)
        time.sleep(4)
        storm = driver.find_element(By.XPATH, '//*[@id="inner-content"]/div[2]/div/div/div[2]/div/div[3]'
                                              '/lib-storms-list/div/div/div[2]/div/div/table/tbody/tr[1]/td[1]/a')

        if storm.text != 'NOT_NAMED' and storm.text != ' NOT_NAMED ':
            storm.click()
            soup = getSoupObj(driver.current_url)
            if soup.find('table') is not None:
                while True:
                    soup = getSoupObj(driver.current_url)
                    getStormRecords(soup, year, ocean, years, oceans, dates, hours, windPower, airPressure,
                                    stormType, stormNames, latCorr, longCorr)
                    try:
                        nextStorm = driver.find_element(By.XPATH,
                                                        '//*[@id="inner-content"]/div[2]/div/div/div[2]/div/div['
                                                        '2]/lib-storm/div/div/div[1]/ul/li[3]/a')
                        if nextStorm.text != 'All Storms »':
                            nextStorm.click()
                        else:
                            break
                    except:
                        break
            else:
                soup = getSoupObj(url)
                rows = soup.find('tbody').find_all('tr')
                getInfoOfRow(rows[0], year, ocean, years, oceans, dates, hours, windPower, airPressure,
                             stormType, stormNames, latCorr, longCorr)
                tdOfStorm = soup.find_all('td', {
                    'class': 'mat-cell cdk-cell cdk-column-summaryStormName mat-column-summaryStormName ng-star-inserted'})
                stormsLink = [s.find('a') for s in tdOfStorm]
                for i in range(1, len(stormsLink)):
                    driver.get(url)
                    time.sleep(4)
                    xpath = xpath_soup(stormsLink[i])
                    nextStorm = stormsLink[i]
                    if nextStorm.text == ' NOT_NAMED ' or nextStorm.text == 'NOT_NAMED':
                        getInfoOfRow(rows[i], year, ocean, years, oceans, dates, hours, windPower, airPressure,
                                     stormType, stormNames, latCorr, longCorr)
                        continue

                    # moving to next page by clicking on link text (with selenium)
                    element = driver.find_element(By.XPATH, xpath)
                    element.click()
                    soup = getSoupObj(driver.current_url)
                    haveTable = soup.find('table')
                    if haveTable is not None:
                        getStormRecords(soup, year, ocean, years, oceans, dates, hours, windPower, airPressure,
                                        stormType, stormNames, latCorr, longCorr)
                    else:
                        soup = getSoupObj(url)
                        time.sleep(5)
                        rows = soup.find('tbody').find_all('tr')
                        getInfoOfRow(rows[i], year, ocean, years, oceans, dates, hours, windPower, airPressure,
                                     stormType, stormNames, latCorr, longCorr)
        else:
            soup = getSoupObj(driver.current_url)
            try:
                rows = soup.find('tbody').find_all('tr')
            except:
                rows = []
            for row in rows:
                getInfoOfRow(row, year, ocean, years, oceans, dates, hours, windPower, airPressure,
                             stormType, stormNames, latCorr, longCorr)
    except:
        print(driver.current_url)
