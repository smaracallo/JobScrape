# Job Scraper
Scrapes job data from Indeed.com

## Description
This project searches for a specified job and scrapes data from all jobs returned from the search. All Job data are stored in a CSV and Json file. Program is set to run daily and send formatted email with all new jobs scraped.
	
## Technologies
Project is created with:
* Python 3
	
#### Important modules

```
from bs4 import BeautifulSoup
import smtplib
import schedule
from email.mime.text import MIMEText
```

## setup
To run this project, customize email sender(including email password) and receivers. If neccessary, change scheduled run time.
