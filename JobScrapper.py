
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd

def get_driver():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options)
    return driver

def indeed_job_search(what, where):
    driver = get_driver()
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

    base_url = driver.current_url
    soup = get_soup(base_url)

    links = []
    pages = soup.find('ul', {'class':'pagination-list'})
    for page in pages.find_all('li'):
        for p in page.find_all('a', href=True):
            links.append(p['href'])
            
    links_clean = []
    l = 0        
    while l < len(links):
        if l == 0:
            links_clean.append("https://indeed.com" + links[l])
            l += 1
        elif links[l] == links[0]:
            break
        else:
            links_clean.append("https://indeed.com" + links[l])
            l += 1
            
    driver.quit()
    return links_clean

def get_soup(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    link_status = req.status_code
    if link_status != 200:
        print("REQUEST FAILED")
    else:
        return soup

def indeed_soup(link_list):
    big_soup = []
    for link in link_list:
        lsoup = get_soup(link)
        big_soup.append(lsoup)
    return big_soup

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
        post_date.find('span', {'class' : 'visually-hidden'}).extract()
        last_active = post_date.get_text()
    except:
        last_active = "N/A"
    try:
        href = job_meta.find('a', href=True)
        link = "https://indeed.com" + str(href.attrs['href'])
    except:
        link = "N/A"
    return title, name, location, est_salary, last_active, link

def create_table():
    df_columns = ['job_title', 'company_name', 'company_location', 'est_salary', 'last_active', 'job_link']
    jobs_table = pd.DataFrame(columns=df_columns)
    return jobs_table

def get_indeed_dict(job_soup):
    jobs_df = create_table()
    for card in job_soup.find_all('div', {"id":"mosaic-provider-jobcards"}):
        for job_data in card.find_all('div', {'class' : 'job_seen_beacon'}):
            title, name, location, est_salary, last_active, link = scrape_job_card(job_data)
            job_dict = {'job_title' : [title],
                'company_name' : [name],
                'company_location' : [location],
                'est_salary' : [est_salary],
                'last_active' : [last_active],
                'job_link': [link]}
            j_df = pd.DataFrame.from_dict(job_dict)
            jobs_df = jobs_df.append(j_df, ignore_index=True)
            # if len(jobs_df) < 30:
            #     jobs_df.append(j_df, ignore_index=True)
            # else:
            #     break
    return jobs_df

#%%
results = indeed_job_search("QA Automation", "Remote")
big_soup = indeed_soup(results)
for ind in big_soup:
    print(get_indeed_dict(ind))