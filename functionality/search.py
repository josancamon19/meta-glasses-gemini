import threading
from bs4 import BeautifulSoup
from utils.gemini import *
from utils.redis_utils import *
import requests
from tenacity import retry, stop_after_attempt


@retry(stop=stop_after_attempt(2))
def get_organic_results_serper_dev(query, num_results=3, location="United States"):
    print('get_organic_results_serper_dev', query, num_results, location)
    if cached := get_generic_cache('get_organic_results_serper_dev:' + query):
        return cached

    headers = {'X-API-KEY': os.getenv('SERPER_DEV_API_KEY'), 'Content-Type': 'application/json'}

    data = json.dumps({"q": query, "location": "United States", "num": num_results, "page": 1})
    response = requests.request("POST", 'https://google.serper.dev/search', headers=headers, data=data)

    organic = response.json().get('organic', [])
    urls = [result['link'] for result in organic]
    print('get_organic_results_serper_dev', urls)
    set_generic_cache('get_organic_results_serper_dev:' + query, urls, 60 * 60 * 12)
    return urls


@retry(stop=stop_after_attempt(2))
def scrape_website_crawlbase(url: str):
    try:
        response = requests.get(f'https://api.crawlbase.com/?token={os.getenv("CRAWLBASE_API_KEY")}&url=' + url)
    except Exception as e:
        print('Failed to scrape website: ' + url, e)
        return ''
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        scraped_data = [p.get_text() for p in paragraphs]
        formatted_data = "\n".join(scraped_data)
        print(formatted_data)
        set_generic_cache('scrape_website:' + url, formatted_data)
        return formatted_data
    print('Failed to scrape website: ' + url, response.status_code, response.content)


def scrape_url_with_timeout(news_data, url):
    try:
        # result = scrape_website(url)
        result = scrape_website_crawlbase(url)
        if not result:
            return
        news_data.append(result)
    except Exception as e:
        print('Failed to scrape website: ' + url, e)


def scrape_urls_threaded(news_data: list, news_urls: list):
    threads = []
    for url in news_urls:
        thread = threading.Thread(target=scrape_url_with_timeout, args=(news_data, url))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete (with timeout)
    for thread in threads:
        thread.join(timeout=45)


# Scenarios where it can fail
# - Scrape not possible (mostly in famous news sites)
# - Scraped data is blocked as previously, but returns text, that has no context about it

def google_search_pipeline(message: str):
    print('google_search_pipeline', message)
    google_search_query = generate_google_search_query(message)
    print('google_search_query', google_search_query)
    news_urls = get_organic_results_serper_dev(google_search_query)
    if not news_urls:
        return "No news data found for this query"
    news_data = []
    scrape_urls_threaded(news_data, news_urls)
    if not news_data:
        return "No news data found for this query"
    response = retrieve_scraped_data_short_answer('\n\n'.join(news_data), message)
    print('google_search_pipeline', response)
    return response
