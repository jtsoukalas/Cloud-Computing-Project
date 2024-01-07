from flask import Blueprint, request
from markupsafe import escape
from library.utils import article_sentiment_analysis, monitor_CPU_Ram, mem_stats, article_sentiment_analysis_thread
import requests
import time
from multiprocessing import Pool
import threading
import _thread
import concurrent.futures

scrape = Blueprint('scrape', __name__)

@scrape.route('/scrape', methods=['GET'])
def article_sentiment_analysis_endpoint():
    url = request.args.get('url')

    response = article_sentiment_analysis(url)

    start_time = mem_stats()
    monitor_CPU_Ram()
    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time}

# endpoint for an array of urls
@scrape.route('/scrape_array', methods=['GET'])
def article_sentiment_analysis_endpoint_array():
    urls = request.args.get('urls')
    urls = urls.replace('"', '')
    urls = urls.replace('[', '')
    urls = urls.replace(']', '')
    urls = urls.split(",")

    start_time = mem_stats()

    response = []
    for url in urls:
        if url.find("txt") != -1:
            continue
        response.append(article_sentiment_analysis(url))
        monitor_CPU_Ram()

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time}

@scrape.route('/scrape_num', methods=['GET'])
def article_sentiment_analysis_endpoint_num():
    num = request.args.get('amount')
    # request from https://en.wikipedia.org/wiki/Special:Random amount of times
    start_time = mem_stats()

    response = []
    for i in range(int(num)):
        url = requests.get("https://en.wikipedia.org/wiki/Special:Random")
        response.append(article_sentiment_analysis(url.url))
        monitor_CPU_Ram()

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time}

@scrape.route('/scrape_num_multi', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi():
    num = request.args.get('amount')
    pool_num = int(request.args.get('pool_num'))
    # request from https://en.wikipedia.org/wiki/Special:Random amount of times
    start_time = mem_stats()

    response = []

    with Pool(pool_num) as p:
        urls = p.map(requests.get, ["https://en.wikipedia.org/wiki/Special:Random" for i in range(int(num))])
        response = p.map(article_sentiment_analysis, [url.url for url in urls])
        monitor_CPU_Ram()

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time}

@scrape.route('/scrape_num_multi_thread', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread():
    num = request.args.get('amount')
    # request from https://en.wikipedia.org/wiki/Special:Random amount of times
    start_time = mem_stats()

    response = [None] * int(num)

    urls = []
    for i in range(int(num)):
        urls.append(requests.get("https://en.wikipedia.org/wiki/Special:Random"))

    threads = []
    for i, url in enumerate(urls):
        t = threading.Thread(target=article_sentiment_analysis_thread, args=(url.url, response, i))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time}

@scrape.route('/scrape_num_multi_thread_2', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread_lock():
    num = request.args.get('amount')

    # request from https://en.wikipedia.org/wiki/Special:Random amount of times

    start_time = mem_stats()

    response = [None] * int(num)

    urls = []
    for i in range(int(num)):
        urls.append(requests.get("https://en.wikipedia.org/wiki/Special:Random"))

    for i in range(int(num)):
        _thread.start_new_thread(article_sentiment_analysis_thread, (urls[i].url, response, i))

    while None in response:
        pass

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time}

@scrape.route('/scrape_num_multi_thread_3', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread_lock_2():
    num = request.args.get('amount')

    # request from https://en.wikipedia.org/wiki/Special:Random amount of times

    start_time = mem_stats()

    response = [None] * int(num)

    urls = []
    for i in range(int(num)):
        urls.append(requests.get("https://en.wikipedia.org/wiki/Special:Random"))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(int(num)):
            executor.submit(article_sentiment_analysis_thread, urls[i].url, response, i)

    while None in response:
        pass

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time}
