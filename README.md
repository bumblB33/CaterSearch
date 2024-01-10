# Business Contact Info Web Scraper

## Description

This Python script performs web scraping to find business contact information based on search queries. It utilizes Google search results and extracts information such as name, address, phone number, email, category, and hours from business websites.



## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/business-contact-scraper.git
Navigate to the project directory:

bash
Copy code
cd business-contact-scraper
Install the required packages:

bash
Copy code
pip install -r requirements.txt
Usage
Open the main.py file and update the business_list with the desired business details.

python
Copy code
business_list = [
    ("Business Type", "Location", Search_Radius, "Additional Keywords"),
    # Add more business details as needed
]





Run the script:

bash
Copy code
python main.py
The script will connect to Google, search for businesses based on the provided details, and save potential business information to a CSV file (potential_businesses.csv). Duplicate entries are avoided.





Notes
Adjust the search radius and additional keywords according to your requirements.
The script includes a delay between requests to avoid being blocked by the web server.
Requirements
Python 3.x
BeautifulSoup
Googlesearch
Requests