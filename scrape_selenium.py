import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

def scrape_turnbackhoax(driver, num_pages):
    data_list = []

    for page in range(55, num_pages + 1):
        url = f'https://turnbackhoax.id/page/{page}/'
        driver.get(url)
        time.sleep(45)
        page_source = driver.page_source
        sop = BeautifulSoup(page_source, 'html.parser')
        li = sop.find('div', id='main-content', class_='mh-loop mh-content')

        if li:
            for x in li.find_all('article'):
                link = x.find('a')['href']
                date = x.find('span', class_='mh-meta-date updated').text
                headline_element = x.find('h3', class_='entry-title mh-loop-title')
                headline = headline_element.text if headline_element else "No headline found"

                retries = 10
                for attempt in range(retries):
                    try:
                        # Visit the link using Selenium
                        driver.get(link)
                        time.sleep(8)  # Wait for the page to load
                        article_source = driver.page_source
                        article_soup = BeautifulSoup(article_source, 'html.parser')
                        content = article_soup.find('div', class_='entry-content mh-clearfix')
                        content_text = content.text.strip() if content else "No content found"
                        data_list.append({'Headline': headline, 'Link': link, 'Date': date, 'Content': content_text})
                        break  # Break out of the retry loop if successful
                    except Exception as e:
                        print(f"Error: {e}. Retrying...")
                        time.sleep(2**attempt)
                else:
                    print("Failed to retrieve article:", link)
        else:
            print("Unable to find the 'list-content' container.")

    if data_list:
        # Use pd.concat to create a DataFrame
        df = pd.concat([pd.DataFrame([data_dict]) for data_dict in data_list], ignore_index=True)
    else:
        df = pd.DataFrame()  # Empty DataFrame when there is no data
    
    return df

if __name__ == '__main__':
    # Set up the Chrome driver
    driver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=driver_service)
    num_pages = 56
    df = scrape_turnbackhoax(driver, num_pages)
    df.to_excel('dataset_hoax_temp_3.xlsx')
    driver.quit()
