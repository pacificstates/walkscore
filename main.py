import pandas
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

# Read the CSV(s), create data frames.

populationdata = pandas.read_csv("venv/csv-files/city-population.csv")
pop_df = pandas.DataFrame(populationdata)

accidents = pandas.read_csv("venv/csv-files/crash-fatalities2.csv")
a_df = pandas.DataFrame(accidents)

# Create lists

cities = []
city_pop = []
state = []
fatality_stat = []
walkscore = []

for index, name in pop_df.iterrows():
    cities.append(name[8].upper())
    city_pop.append(name[2])
    state.append(name[5])

# For each city, obtain the number of fatal crashes per 10,000 residents
# Here I had to get the count for each city, if the city was not found,
# 'city' was returned to pinpoint problems.

cityindex = 0

for city in cities:
    count = a_df['CITYNAME'].value_counts().get(city, city)
    hundred = int(city_pop[cityindex]) / 100000
    stat = round((int(count) / hundred), 2)
    fatality_stat.append(stat)
    cityindex += 1

# Make changes to the cities list to make it compatible with walkscore.com

cities.pop(0)
cities.insert(0, "New York")
selenium_cities = [city.replace(" ", "_") for city in cities]

# Use Selenium web scraping to obtain WalkScores for each city

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

for index in range(0, 50):
    driver.get(f"https://www.walkscore.com/{state[index]}/{selenium_cities[index]}")
    wait = WebDriverWait(driver, 3)

    try:
        score_div = wait.until(EC.visibility_of_element_located((By.ID, "walkscore")))
        score_img = score_div.find_element(By.TAG_NAME, "img")
    except TimeoutException:
        score_img = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="address-header"]/div[4]/div['
                                                                           '1]/div[1]/div/img')))
    img_alt = score_img.get_attribute("alt")
    success = re.search(r'\b\d+\b', img_alt)
    if success:
        score = int(success.group())
        walkscore.append(score)
    else:
        walkscore.append(0)
    print(walkscore)

driver.quit()

# Compile all data into a pandas DataFrame then write to CSV

fifty_cities = cities[:50]
fifty_stats = fatality_stat[:50]
fifty_scores = [88, 69, 77, 47, 41, 75, 37, 53, 46, 42, 26, 35, 51, 41, 26, 31, 74, 89, 61, 34, 40, 29, 42, 98, 35,
                34, 51, 67, 83, 64, 43, 62, 47, 43, 49, 38, 35, 36, 48, 48, 31, 33, 73, 77, 75, 71, 37, 39, 43, 50]

finished_data = {
    "City": fifty_cities,
    "Fatal Crashes": fifty_stats,
    "Walkscore": fifty_scores  # Change to 'walkscore' to run selenium instead of pre-run hardcoded numbers;
    # comment out the selenium code block to run as-is with hard-coded scores
}

df = pd.DataFrame(finished_data)

df.to_csv('walkscore_vs_crashes.csv', index=False)

# calculate correlation coefficient using numpy

coefficient = np.corrcoef(fifty_scores, fifty_stats)[0, 1]

print("Correlation Coefficient:", coefficient)