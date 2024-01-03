from flask import Blueprint, request
from markupsafe import escape
from library.utils import article_sentiment_analysis

endpoints = Blueprint('endpoints', __name__)

@endpoints.route('/scrape', methods=['GET'])
def article_sentiment_analysis_endpoint():
    url = request.args.get('url')

    return escape(article_sentiment_analysis(url))

#endpoint for an array of urls
@endpoints.route('/scrape_array', methods=['GET'])
def article_sentiment_analysis_endpoint_array():
    urls = request.args.get('urls')
    urls = urls.replace('"', '')
    urls = urls.replace('[', '')
    urls = urls.replace(']', '')
    urls = urls.split(",")
    response = []
    for url in urls:
        if url.find("txt") != -1:
            continue
        response.append(article_sentiment_analysis(url))
    return escape(response)