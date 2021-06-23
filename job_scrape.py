import requests
import re
import csv
import datetime
import json
import smtplib
from email.mime.text import MIMEText

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

        # stores records of new jobs scraped
        records = []

        while True:
            # exit loop if Next button not displayed
            try:
                url = f"https://www.indeed.com{soup.find('a', {'aria-label': 'Next'}).get('href')}"
            except AttributeError:
                break

            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = soup.find_all('a', 'result')

            # store only new job ids
            with open('data.json', 'r+') as f:
                data = json.load(f)
                saved_job_ids = data['ids']

                for job in jobs:
                    job_id = job.get('id')

                    if job_id in saved_job_ids:
                        continue

                    f.seek(0)
                    saved_job_ids.append(job_id)
                    record = self.get_job_record(job)
                    records.append(record)
                    json.dump(data, f, indent=4)
                    f.truncate()

        if len(records) > 0:
            # store added job details in csv file
            with open('jobs.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['JobTitle', 'URL', 'Company', 'Location', 'Description', 'Date', 'Salary', 'DateScraped'])
                writer.writerows(records)

            emailed_jobs = []
            for job_title, url, company, location, job_snippet, date_posted, salary, date_scraped in records:
                date_scraped = date_scraped.strftime('%m/%d/%Y')
                job_details = f"Job Title: {job_title} \nCompany: {company}\nLocation: {location}\n" \
                              f"Salary: {salary if salary else 'unknown'}\n" \
                              f"Date Posted: {f'{date_posted} from {date_scraped}'}\n" \
                              f"Job Snippet: {job_snippet}\nURL: {url}\n\n"
                emailed_jobs.append(job_details)

            # send email of new stored jobs
            sender = 'sender email here'
            receivers = ["receiver email here"]
            email_body = "".join(emailed_jobs)

            msg = MIMEText(email_body)
            msg['Subject'] = 'Daily Indeed Job Alerts'
            msg['From'] = sender
            msg['To'] = ','.join(receivers)

            s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
            s.login(user=sender, password='sender passsword')
            s.sendmail(sender, receivers, msg.as_string())
            s.quit()

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
