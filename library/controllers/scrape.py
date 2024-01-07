from flask import Blueprint, request
from markupsafe import escape
from library.utils import article_sentiment_analysis, monitor_cpu_ram, mem_stats, article_sentiment_analysis_thread, \
    article_sentiment_analysis_mem
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

    start_time, cpu_count, total_mem = mem_stats()

    mem_used, cpu_percent = monitor_cpu_ram()

    # cpu is a list of cpu percentages for each core, so we take the average
    cpu_percent = sum(cpu_percent) / len(cpu_percent)

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time, "cpu_count": cpu_count, "total_mem": total_mem,
            "average_mem": mem_used, "average_cpu_percentage": cpu_percent}

# endpoint for an array of urls
@scrape.route('/scrape_array', methods=['GET'])
def article_sentiment_analysis_endpoint_array():
    urls = request.args.get('urls')
    urls = urls.replace('"', '')
    urls = urls.replace('[', '')
    urls = urls.replace(']', '')
    urls = urls.split(",")

    start_time, cpu_count, total_mem = mem_stats()

    response = []
    total_mem_used = 0
    total_cpu = 0

    for url in urls:
        if url.find("txt") != -1:
            continue
        response.append(article_sentiment_analysis(url))
        mem_used, cpu_percent = monitor_cpu_ram()
        total_mem_used += mem_used
        total_cpu += sum(cpu_percent) / len(cpu_percent)

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time, "cpu_count": cpu_count, "total_mem": total_mem,
            "average_mem": total_mem / len(urls), "average_cpu_percentage": total_cpu / len(urls)}

@scrape.route('/scrape_num', methods=['GET'])
def article_sentiment_analysis_endpoint_num():
    num = request.args.get('amount')
    # request from https://en.wikipedia.org/wiki/Special:Random amount of times
    start_time, cpu_count, total_mem = mem_stats()

    response = []
    total_mem_used = 0
    total_cpu = 0

    for i in range(int(num)):
        url = requests.get("https://en.wikipedia.org/wiki/Special:Random")
        response.append(article_sentiment_analysis(url.url))
        mem_used, cpu_percent = monitor_cpu_ram()
        total_mem_used += mem_used
        total_cpu += sum(cpu_percent) / len(cpu_percent)

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time, "cpu_count": cpu_count, "total_mem": total_mem,
            "average_mem": total_mem_used / int(num), "average_cpu_percentage": total_cpu / int(num)}

@scrape.route('/scrape_num_multi', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi():
    num = request.args.get('amount')
    pool_num = int(request.args.get('pool_num'))
    # request from https://en.wikipedia.org/wiki/Special:Random amount of times
    start_time, cpu_count, total_mem = mem_stats()

    response = []

    with Pool(pool_num) as p:
        urls = p.map(requests.get, ["https://en.wikipedia.org/wiki/Special:Random" for i in range(int(num))])
        response = p.map(article_sentiment_analysis_mem, [url.url for url in urls])

    total_mem_used = 0
    total_cpu = 0

    for i in range(len(response)):
        total_mem_used += response[i][2]
        total_cpu += response[i][3]
        response[i] = response[i][:2]

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time, "cpu_count": cpu_count, "total_mem": total_mem,
            "average_mem": total_mem_used / int(num), "average_cpu_percentage": total_cpu / int(num)}

@scrape.route('/scrape_num_multi_thread', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread():
    num = request.args.get('amount')
    # request from https://en.wikipedia.org/wiki/Special:Random amount of times
    start_time, cpu_count, total_mem = mem_stats()

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

    total_mem_used = 0
    total_cpu = 0

    for i in range(len(response)):
        total_mem_used += response[i][2]
        total_cpu += response[i][3]
        response[i] = response[i][:2]

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time, "cpu_count": cpu_count, "total_mem": total_mem,
            "average_mem": total_mem_used / int(num), "average_cpu_percentage": total_cpu / int(num)}

@scrape.route('/scrape_num_multi_thread_2', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread_lock():
    num = request.args.get('amount')

    # request from https://en.wikipedia.org/wiki/Special:Random amount of times

    start_time, cpu_count, total_mem = mem_stats()

    response = [None] * int(num)

    urls = []
    for i in range(int(num)):
        urls.append(requests.get("https://en.wikipedia.org/wiki/Special:Random"))

    for i in range(int(num)):
        _thread.start_new_thread(article_sentiment_analysis_thread, (urls[i].url, response, i))

    while None in response:
        pass

    total_mem_used = 0
    total_cpu = 0

    for i in range(len(response)):
        total_mem_used += response[i][2]
        total_cpu += response[i][3]
        response[i] = response[i][:2]

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time, "cpu_count": cpu_count, "total_mem": total_mem,
            "average_mem": total_mem_used / int(num), "average_cpu_percentage": total_cpu / int(num)}

@scrape.route('/scrape_num_multi_thread_3', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread_lock_2():
    num = request.args.get('amount')

    # request from https://en.wikipedia.org/wiki/Special:Random amount of times

    start_time, cpu_count, total_mem = mem_stats()

    response = [None] * int(num)

    urls = []
    for i in range(int(num)):
        urls.append(requests.get("https://en.wikipedia.org/wiki/Special:Random"))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(int(num)):
            executor.submit(article_sentiment_analysis_thread, urls[i].url, response, i)

    while None in response:
        pass

    total_mem_used = 0
    total_cpu = 0

    for i in range(len(response)):
        total_mem_used += response[i][2]
        total_cpu += response[i][3]
        response[i] = response[i][:2]

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time, "cpu_count": cpu_count, "total_mem": total_mem,
            "average_mem": total_mem_used / int(num), "average_cpu_percentage": total_cpu / int(num)}
