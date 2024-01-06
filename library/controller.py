from flask import Blueprint, request
from markupsafe import escape
from library.utils import article_sentiment_analysis, monitor_CPU_Ram, mem_stats
import requests
import time

endpoints = Blueprint('endpoints', __name__)

@endpoints.route('/scrape', methods=['GET'])
def article_sentiment_analysis_endpoint():
    url = request.args.get('url')

    response = article_sentiment_analysis(url)

    start_time = mem_stats()
    monitor_CPU_Ram()
    execution_time = str((time.time() - start_time))
    print("Execution time: ", execution_time)

    return {"response": escape(response), "time": execution_time}

# endpoint for an array of urls
@endpoints.route('/scrape_array', methods=['GET'])
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
    print("Execution time: ", execution_time)
    return {"response": escape(response), "time": execution_time}

@endpoints.route('/scrape_num', methods=['GET'])
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
    print("Execution time: ", execution_time)
    return {"response": escape(response), "time": execution_time}
