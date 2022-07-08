
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd

def search_jobs(what, where):
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.indeed.com")
    time.sleep(10)
    job_search = driver.find_element(By.XPATH, '//input[@id="text-input-what"]')
    job_search.send_keys(what)

    location_search = driver.find_element(By.XPATH,'//input[@id="text-input-where"]')
    location_search.click()
    location_search.send_keys(Keys.CONTROL + "a")
    location_search.send_keys(Keys.DELETE)
    location_search.send_keys(where)
    # print("Job Location set to: " + location_search.get_attribute('value'))
    submit = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit.click()
    time.sleep(5)
    url = driver.current_url
    driver.quit()
    return url

def scrape_job_card(job_meta):
    try:
        title = job_meta.find('h2', {"class":"jobTitle"}).get_text().lstrip('new\n')
    except:
        title = "--"
    try:
        name = job_meta.find('span',{"class":"companyName"}).get_text()
    except:
        name = "--"
    try:
        location = job_meta.find('div',{"class":"companyLocation"}).get_text()
    except:
        location = "--"
    try:
        est_salary = job_meta.find('div', {'class':'metadata salary-snippet-container'}).get_text()
    except:
        est_salary = "N/A"
    try:
        post_date = job_meta.find('span', {'class':'date'})
        status = post_date.find('span', {'class' : 'visually-hidden'}).extract()
        last_active = post_date.get_text()
    except:
        last_actve = "N/A"
    return title, name, location, est_salary, last_active

def get_job_dict(page_html):
    req = requests.get(page_html)
    job_soup = BeautifulSoup(req.text, 'lxml')
    df_columns = ['job_title', 'company_name', 'company_location', 'est_salary', 'last_active']
    jobs_df = pd.DataFrame(columns=df_columns)
    for card in job_soup.find_all('div', {"id":"mosaic-provider-jobcards"}):
        for job_data in card.find_all('div', {'class' : 'job_seen_beacon'}):
            title, name, location, est_salary, last_active = scrape_job_card(job_data)
            job_dict = {'job_title' : [title],
                'company_name' : [name],
                'company_location' : [location],
                'est_salary' : [est_salary],
                'last_active' : [last_active]}
            j_df = pd.DataFrame.from_dict(job_dict)
            jobs_df = jobs_df.append(j_df, ignore_index=True)
    return jobs_df
            

url = search_jobs("QA Automation", "Remote")
print(get_job_dict(url))


 


