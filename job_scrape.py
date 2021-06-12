import requests
import re
import csv
import datetime

from bs4 import BeautifulSoup
from job_ids import ids


class IndeedScrape:

    def __init__(self):
        pass

    def run(self):

        job_search = "software engineer"
        location = "New York, NY"
        url = f"https://www.indeed.com/jobs?q={job_search}&l={location}&jt=fulltime&explvl=mid_level&taxo1=8GQeqOBVSO2eVhu55t0BMg"

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # cards = soup.find_all('a', 'result')

        records = []

        while True:
            try:
                url = f"https://www.indeed.com{soup.find('a', {'aria-label': 'Next'}).get('href')}"
            except AttributeError:
                break

            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('a', 'result')

            for card in cards:
                job_id = card.get('id')

                if job_id in ids:
                    continue

                ids.append(job_id)
                record = self.get_job_record(card)
                records.append(record)

        with open('jobs.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['JobTitle', 'URL', 'Company', 'Location', 'Description', 'Date', 'Salary', 'DateScraped'])
            writer.writerows(records)

        print(ids)

    def get_job_record(self, card):
        job_title = card.h2.span.get('title')
        url = f"https://indeed.com{card.get('href')}"
        company = card.find('span', 'companyName').text
        all_location = card.find('div', 'companyLocation').text
        location = ''.join(re.findall('([a-zA-Z ]*)\d*,*', all_location)[:2])
        job_snippet = card.find('div', 'job-snippet').text.strip()
        date_posted = card.find('span', 'date').text
        date_scraped = datetime.datetime.now()

        try:
            salary = card.find('span', 'salary-snippet').text
        except AttributeError:
            salary = "Unknown"

        return job_title, url, company, location, job_snippet, date_posted, salary, date_scraped


IndeedScrape().run()
