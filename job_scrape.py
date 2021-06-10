import requests
import re

from bs4 import BeautifulSoup


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
                record = self.get_job_record(card)
                records.append(record)

        print(len(records))

    def get_job_record(self, card):
        job_title = card.h2.span.get('title')
        url = f"https://indeed.com{card.get('href')}"
        company = card.find('span', 'companyName').text
        all_location = card.find('div', 'companyLocation').text
        location = ''.join(re.findall('([a-zA-Z ]*)\d*,*', all_location)[:2])
        job_snippet = card.find('div', 'job-snippet').text.strip()
        date_posted = card.find('span', 'date').text

        try:
            salary = card.find('span', 'salary-snippet').text
        except AttributeError:
            salary = ""

        return job_title, url, company, location, job_snippet, date_posted, salary


IndeedScrape().run()
