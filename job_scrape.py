import requests
import re
import csv
from datetime import datetime
import json
import time

from bs4 import BeautifulSoup
import smtplib
import schedule
from email.mime.text import MIMEText


class IndeedScrape:

    def __init__(self):
        pass

    def run(self):

        job_search = "python engineer"
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

            # store only new job ids found
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

            # setup display format for emailed jobs
            emailed_jobs = []
            for job_title, url, company, location, job_snippet, date_posted, salary, date_today in records:
                job_details = f"Job Title: {job_title} \nCompany: {company}\nLocation: {location}\n" \
                              f"Salary: {salary if salary else 'unknown'}\n" \
                              f"Date Posted: {f'{date_posted}'}\n" \
                              f"Job Snippet: {job_snippet}\nURL: {url}\n\n"
                emailed_jobs.append(job_details)

            # send formatted email of new stored jobs
            sender = 'email@gmail.com'
            receivers = ["email@gmail.com"]
            email_body = f"{len(emailed_jobs)} New Jobs found for '{job_search}' on {datetime.today().strftime('%m/%d/%Y')}\n\n{''.join(emailed_jobs)}"

            msg = MIMEText(email_body)
            msg['Subject'] = 'Daily Indeed Job Alerts'
            msg['From'] = sender
            msg['To'] = ','.join(receivers)

            s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
            s.login(user=sender, password=eamil_password')
            s.sendmail(sender, receivers, msg.as_string())
            s.quit()

    def get_job_record(self, card):
        job_title = card.h2.span.get('title') or card.h2.find_all('span')[1].get('title')
        url = f"https://indeed.com{card.get('href')}"
        company = card.find('span', 'companyName').text
        all_location = card.find('div', 'companyLocation').text
        location = ', '.join(re.findall('([a-zA-Z ]*)\d*,*', all_location)[:2])
        job_snippet = card.find('div', 'job-snippet').text.strip()
        date_posted = card.find('span', 'date').text
        today = datetime.today()
        try:
            salary = card.find('span', 'salary-snippet').text
        except AttributeError:
            salary = "Unknown"

        return job_title, url, company, location, job_snippet, date_posted, salary, today


# Schedule program execution time
schedule.every().day.at("23:15").do(IndeedScrape().run)

while True:
    schedule.run_pending()
    time.sleep(60)
