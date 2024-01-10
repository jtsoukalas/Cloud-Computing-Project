from flask import Blueprint, request
from markupsafe import escape

from library.utils.multiprocessing import Multiprocessing
from library.utils.utils import Utils
import requests
import time
import threading
import _thread

scrape = Blueprint('scrape', __name__)

@scrape.route('/scrape', methods=['GET'])
def article_sentiment_analysis_endpoint():
    url = request.args.get('url')

    response = Utils.article_sentiment_analysis(url)

    start_time, cpu_count, total_mem = Utils.mem_stats()

    mem_used, cpu_percent = Utils.monitor_cpu_ram()

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

    start_time, cpu_count, total_mem = Utils.mem_stats()

    response = []
    total_mem_used = 0
    total_cpu = 0

    for url in urls:
        if url.find("txt") != -1:
            continue
        response.append(Utils.article_sentiment_analysis(url))
        mem_used, cpu_percent = Utils.monitor_cpu_ram()
        total_mem_used += mem_used
        total_cpu += sum(cpu_percent) / len(cpu_percent)

    execution_time = str((time.time() - start_time))
    return {"response": escape(response), "time": execution_time, "cpu_count": cpu_count, "total_mem": total_mem,
            "average_mem": total_mem / len(urls), "average_cpu_percentage": total_cpu / len(urls)}

@scrape.route('/scrape_num', methods=['GET'])
def article_sentiment_analysis_endpoint_num():
    num = request.args.get('amount')

    start_time, cpu_count, total_mem = Utils.mem_stats()

    response = []

    urls = Utils.get_num_cashed_urls(int(num))

    if urls is None:
        return {"response": "Not enough cashed urls", "time": 0, "cpu_count": cpu_count, "total_mem": total_mem,
                "average_mem": 0, "average_cpu_percentage": 0}

    for i in range(int(num)):
        response.append(Utils.article_sentiment_analysis(urls[i], True))

    return Utils.return_result(cpu_count, num, response, start_time, total_mem)

@scrape.route('/scrape_num_multi', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi():
    num = request.args.get('amount')

    start_time, cpu_count, total_mem = Utils.mem_stats()

    urls = Utils.get_num_cashed_urls(int(num))

    if urls is None:
        return {"response": "Not enough cashed urls", "time": 0, "cpu_count": cpu_count, "total_mem": total_mem,
            "average_mem": 0, "average_cpu_percentage": 0}

    response = Multiprocessing.multiproc(Utils.article_sentiment_analysis, [(url, True) for url in urls])

    return Utils.return_result(cpu_count, num, response, start_time, total_mem)

@scrape.route('/scrape_num_multi_thread', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread():
    num = request.args.get('amount')

    start_time, cpu_count, total_mem = Utils.mem_stats()

    response = [None] * int(num)

    urls = Utils.get_num_cashed_urls(int(num))

    threads = []
    for i, url in enumerate(urls):
        t = threading.Thread(target=Utils.article_sentiment_analysis_thread, args=(url, response, i))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

    return Utils.return_result(cpu_count, num, response, start_time, total_mem)

@scrape.route('/scrape_num_multi_thread_2', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread_lock():
    num = request.args.get('amount')

    start_time, cpu_count, total_mem = Utils.mem_stats()

    response = [None] * int(num)

    urls = Utils.get_num_cashed_urls(int(num))

    for i in range(int(num)):
        _thread.start_new_thread(Utils.article_sentiment_analysis_thread, (urls[i], response, i))

    return Utils.return_result(cpu_count, num, response, start_time, total_mem)

@scrape.route('/scrape_num_multi_thread_3', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread_lock_2():
    num = request.args.get('amount')

    start_time, cpu_count, total_mem = Utils.mem_stats()

    urls = Utils.get_num_cashed_urls(int(num))

    response = Multiprocessing.concurrent_func(Utils.article_sentiment_analysis, urls)

    return Utils.return_result(cpu_count, num, response, start_time, total_mem)
