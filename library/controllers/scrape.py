from flask import Blueprint, request, jsonify
from library.utils.multiprocessing import Multiprocessing
from library.utils.utils import Utils
import threading
import _thread
import time

scrape = Blueprint('scrape', __name__)

@scrape.route('/scrape', methods=['GET'])
def article_sentiment_analysis_endpoint():
    start_time = time.time()

    url = request.args.get('url')

    response = Utils.article_sentiment_analysis(url)

    return Utils.return_result(1, [response], start_time)

@scrape.route('/scrape_list', methods=['GET'])
def article_sentiment_analysis_endpoint_multi():
    start_time = time.time()
    received_urls = []
    try:
        # Assuming the incoming data is in JSON format
        data = request.get_json()
        # Check if 'strings' key exists in the JSON data
        if 'urls' in data and isinstance(data['urls'], list):
            received_urls = data['urls']
        else:
            return jsonify({"success": False, "message": "Invalid data format. 'strings' key not found or not a list."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

    response = []

    Utils.monitor_cpu_ram()

    for url in received_urls:
        response.append(Utils.article_sentiment_analysis(url))
    return Utils.return_result(len(received_urls), response, start_time, Multiprocessing.pool_size)

@scrape.route('/get_cashed', methods=['GET'])
def get_cashed_urls():
    return jsonify({"urls": Utils.cashed_urls})

@scrape.route('/scrape_num', methods=['GET'])
def article_sentiment_analysis_endpoint_num():
    start_time = time.time()

    num = request.args.get('amount')

    response = []

    urls = Utils.get_num_cashed_urls(int(num))

    if urls is None:
        return "Not enough cashed urls"

    Utils.monitor_cpu_ram()
    for i in range(int(num)):
        response.append(Utils.article_sentiment_analysis(urls[i]))

    return Utils.return_result(num, response, start_time)

@scrape.route('/scrape_num_multi', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi():
    num = request.args.get('amount')

    start_time = time.time()

    urls = Utils.get_num_cashed_urls(int(num))

    if urls is None:
        return "Not enough cashed urls"

    response = Multiprocessing.multiproc(Utils.article_sentiment_analysis, [url for url in urls])

    return Utils.return_result(num, response, start_time, Multiprocessing.pool_size)

# TODO possible wrong cpu calculation
@scrape.route('/scrape_num_threading', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread():
    num = request.args.get('amount')

    start_time = time.time()

    response = [None] * int(num)

    urls = Utils.get_num_cashed_urls(int(num))

    if urls is None:
        return "Not enough cashed urls"

    threads = []
    for i, url in enumerate(urls):
        t = threading.Thread(target=Utils.article_sentiment_analysis_thread, args=(url, response, i))
        threads.append(t)
        t.start()

    active = len(threads)

    for thread in threads:
        thread.join()

    return Utils.return_result(num, response, start_time, active)

@scrape.route('/scrape_num_thread', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread_lock():
    num = request.args.get('amount')

    start_time = time.time()

    response = [None] * int(num)

    urls = Utils.get_num_cashed_urls(int(num))

    if urls is None:
        return "Not enough cashed urls"

    for i in range(int(num)):
        _thread.start_new_thread(Utils.article_sentiment_analysis_thread, (urls[i], response, i))

    return Utils.return_result(num, response, start_time, len(urls))

@scrape.route('/scrape_num_concur', methods=['GET'])
def article_sentiment_analysis_endpoint_num_multi_thread_lock_2():
    num = request.args.get('amount')

    start_time = time.time()

    urls = Utils.get_num_cashed_urls(int(num))

    if urls is None:
        return "Not enough cashed urls"

    response = Multiprocessing.concurrent_func(Utils.article_sentiment_analysis, urls)

    return Utils.return_result(num, response, start_time, Multiprocessing.pool_size)
