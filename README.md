# RERA Project Scraper

A Python-based web scraper that extracts project details from the Odisha RERA (Real Estate Regulatory Authority) website using Playwright.

## Features

- Automated scraping of RERA project details
- Extracts information such as RERA registration numbers, project names, promoter details, and GST numbers
- Saves data to CSV format
- Built-in error handling and recovery mechanisms
- Progress tracking and detailed logging

## Requirements

- Python 3.7+
- Playwright
- pandas

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Rohand19/web-scraper.git
cd web-scraper
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

## Usage

Run the scraper using:

```bash
python playwright_scraper.py
```

By default, the scraper will extract details for 6 projects. You can modify this by changing the `num_projects` parameter in the script.

## Output

The scraper generates a CSV file (`rera_projects.csv`) containing the following information for each project:
- RERA Registration Number
- Project Name
- Promoter Name
- Promoter's Address
- GST Number

## Error Handling

The scraper includes robust error handling:
- Automatic recovery from page load failures
- Timeout handling
- Multiple selector attempts for reliable data extraction
- Detailed logging of any issues encountered
