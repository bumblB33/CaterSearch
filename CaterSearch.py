import requests
import time
import re
import itertools
from bs4 import BeautifulSoup
from googlesearch import search
from typing import List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import logging


logging.basicConfig(level=logging.INFO)


def search_google(query: str, num_results: int = 200) -> List[str]:
    search_results = list(itertools.islice(search(query), num_results))
    return search_results


def extract_name(soup: BeautifulSoup) -> str:
    # Extract name using different methods based on the structure of the webpage
    name = soup.title.text.strip() if soup.title else 'N/A'
    if not name:
        # Additional methods can be added here based on the structure of the webpage
        pass
    return name

def extract_additional_info(soup: BeautifulSoup) -> Dict[str, str]:
    additional_info = {
        'email': 'N/A',
        'category': 'N/A',
        'hours': 'N/A',
    }

    # Extract email from different locations in the HTML structure
    email_tags = soup.find_all('a', {'href': re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')})
    email = next((tag.text.strip() for tag in email_tags), 'N/A')

    additional_info['email'] = email

    # Extract category (modify based on the structure of the webpage)
    category = soup.find('span', {'class': 'category'})  # Replace with actual class or tag
    additional_info['category'] = category.text.strip() if category else 'N/A'

    # Extract hours (modify based on the structure of the webpage)
    hours = soup.find('div', {'class': 'business-hours'})  # Replace with actual class or tag
    additional_info['hours'] = hours.text.strip() if hours else 'N/A'

    return additional_info

def extract_address(soup: BeautifulSoup) -> str:
    # Extract address using different methods based on the structure of the webpage
    address = soup.find('address') or soup.find('span', {'class': 'street-address'})
    address = address.text.strip() if address else 'Street-Address: N/A'
    if not address:
        # Additional methods can be added here based on the structure of the webpage
        pass
    return address

def extract_phone_number(soup: BeautifulSoup) -> str:
    phone_number = soup.find('span', {'class': 'tel'}) or soup.find('div', {'class': 'phone'})
    
    if not phone_number:
        # Check for phone number within an <a> tag with href containing "tel:"
        phone_number = soup.find('a', href=re.compile(r'tel:'))

    phone_number = phone_number.text.strip() if phone_number else 'Phone-Number: N/A'

    # Updated phone number patterns
    phone_number_patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (XXX) XXX-XXXX, XXX-XXX-XXXX, XXX.XXX.XXXX, XXX XXX-XXXX, etc.
        r'\+\d{1,2}\s?\(?\d{2,}\)?[-.\s]?\d{1,}',
        # International formats with or without country code
    ]

    for format_pattern in phone_number_patterns:
        match = re.search(format_pattern, phone_number)
        if match:
            return match.group()

    return 'N/A'


def save_to_csv(data: List[Tuple[str, str, str, str, Dict[str, str]]], filename: str = "potential_businesses.csv") -> None:
    """
    Save the potential businesses' information to a CSV file, avoiding duplicates.

    Args:
    - data (List[Tuple[str, str, str, str, Dict[str, str]]]): List of tuples containing business information.
    - filename (str): Name of the CSV file (default: "potential_businesses.csv").

    Returns:
    - None
    """
    # Read existing data from the CSV file
    existing_data = set()
    try:
        with open(filename, "r", encoding="utf-8") as csv_file:
            for line in csv_file:
                existing_data.add(tuple(line.strip().split(',')))
    except FileNotFoundError:
        pass  # Ignore if the file doesn't exist yet

    # Check for duplicates and add new data to the CSV file
    with open(filename, "a", encoding="utf-8") as csv_file:
        for business in data:
            business_tuple = tuple(business[:-1])  # Exclude the dictionary from the tuple
            if business_tuple not in existing_data:
                csv_file.write(",".join(map(str, business)) + "\n")
                existing_data.add(business_tuple)

def process_result(result: str) -> Tuple[str, str, str, str, Dict[str, str]]:
    try:
        response = requests.get(result)

        if response.status_code == 403:
            print(f"Access denied for {result}")
            return 'N/A', 'N/A', 'N/A', result, {}

        soup = BeautifulSoup(response.text, 'html.parser')

        name = extract_name(soup)
        address = extract_address(soup)
        phone_number = extract_phone_number(soup)
        additional_info = extract_additional_info(soup)

        # Only add to the CSV if a phone number is found
        if phone_number != 'N/A':
            return name, address, phone_number, result, additional_info
        else:
            return 'N/A', 'N/A', 'N/A', result, {}
    except requests.exceptions.RequestException as e:
        print(f"Error while scraping {result}: {e}")
        return 'N/A', 'N/A', 'N/A', result, {}
    except Exception as e:
        print(f"Unexpected error while scraping {result}: {type(e).__name__} - {e}")
        return 'N/A', 'N/A', 'N/A', result, {}

def search_and_save(business_details: Tuple[str, str, float, str]) -> None:
    business_type, location, radius, additional_keywords = business_details
    search_query = f"{business_type} in {location} {additional_keywords}"

    # Log the start of the search
    logging.info(f"Connecting and searching for: {search_query}")

    search_results = search_google(search_query)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_result, result) for result in search_results]

        for future in concurrent.futures.as_completed(futures):
            time.sleep(2)  # Adjust the delay time as needed
            potential_business = future.result()
            save_to_csv([potential_business])

if __name__ == "__main__":
    # List of business details to search for
    business_list = [
        ("Corporate Offices", "Dallas", 50, "Tech, Law, Entertainment"), 
        ("Schools", "Oklahoma City", 50, "ISD, isd, Highschool, homeschool, Co-op, coop, church, private"),
        ("Law Firm", "Seattle", 50, "Defence, Injury, Family"),
        # Add more business types as needed
    ]

    for business_details in business_list:
        search_and_save(business_details)