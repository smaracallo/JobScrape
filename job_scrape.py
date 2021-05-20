from bs4 import BeautifulSoup

from selenium import webdriver
import chromedriver_binary #Adds chromedriver binary to path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class IndeedScrape:

    def __init__(self):
        pass

    def run(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)  # keeps browser open
        url = "https://www.indeed.com/"
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Enter search credential and click search button
        job_title = driver.find_element_by_id('text-input-what')
        location = driver.find_element_by_id('text-input-where')

        location.clear()

        job_title.send_keys("Software Engineer")
        location.send_keys("")

        search_jobs = driver.find_element_by_class_name("icl-WhatWhere-button")
        search_jobs.click()

        # sort by date
        driver.find_element_by_link_text('date').click()

        # close pop-up if displayed
        # WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "popover-foreground")))
        driver.implicitly_wait(10)
        pop_up = driver.find_element_by_id('popover-foreground')

        if pop_up.is_displayed():
            driver.find_element(By.XPATH, '//button[@aria-label="Close"]').click()

        all_jobs = driver.find_elements_by_class_name("result")
        print(all_jobs)


IndeedScrape().run()
