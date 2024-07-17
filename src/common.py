import requests, re, os, subprocess,sys
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("get_json.log", mode='w')])

# Get the README file of the GitHub repository
def get_readme(url):
    try:
        headers = {"Accept": "application/vnd.github.v3.raw"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.text
        else:
            logging.error(f"Failed to get README.md. Status code: {response.status_code}. URL: {url}")
    except requests.RequestException as e:
        logging.error(f"An error occurred: {e}")

def get_readme_htmlURL(url):
    try:
        headers = {
            "Authorization": ""
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            html_url = data.get("html_url")
            if html_url:
                return html_url
            else:
                logging.error("HTML URL not found in the response")
                return None
        else:
            logging.error(f"Failed to get README.md. Status code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"An error occurred: {e}")

# Get the content of a link
def get_content(url):
    try:
        # Send a GET request to get the page content
        response = requests.get(url)
        
        # Check the response status code
        if response.status_code == 200:
            # Parsing HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove all <footer> tags
            for footer in soup.find_all('footer'):
                footer.decompose()

            # Remove all <nav> tags
            for footer in soup.find_all('nav'):
                footer.decompose()

            # Delete all elements with class='footer'
            for footer_class in soup.find_all(class_='footer'):
                footer_class.decompose()

            # Delete all elements with id='top'
            for footer_class in soup.find_all(id='top'):
                footer_class.decompose()

            # Delete all elements with role='navigation'
            for footer_class in soup.find_all(role='navigation'):
                footer_class.decompose()
            
            # Get the text content displayed on the page
            page_content = soup.get_text()
            return page_content
        else:
            logging.error(f"Failed to retrieve content. Status code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"An error occurred: {e}")

def get_github_readme(url):
    # Convert GitHub file page URLs to raw content URLs
    raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/').replace('/tree/', '/')
    
    response = requests.get(raw_url)
    
    if response.status_code == 200:
        return response.text
    else:
        logging.error(f"Failed to fetch the file. Status code: {response.status_code}. url: {url}")
        return None

# Get the length of a content. If it is too long, split the content into chunks.
def content_chunk(content):
    max = 509723
    # If the string length does not exceed the limit, directly return a list containing the string
    if len(content) <= max:
        return [content]

    # Otherwise, split the string into multiple substrings of length not exceeding the limit
    result = []
    for i in range(0, len(content), max):
        result.append(content[i:i + max])
    
    return result

# Determines whether a string is a link
def is_url(string):
    # Use regular expressions for preliminary checks
    regex = re.compile(
        r'^(https?|ftp)://'
        r'(\S+(:\S*)?@)?'
        r'((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|'
        r'((\d{1,3}\.){3}\d{1,3}))'
        r'(:\d+)?'
        r'(/[\w.-]*)*'
        r'(\?\S*)?'
        r'(#\S*)?$'
    )
    if re.match(regex, string):
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    return False
    