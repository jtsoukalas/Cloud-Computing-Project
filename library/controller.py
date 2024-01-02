from flask import Blueprint, request
from markupsafe import escape
from library.utils import article_sentiment_analysis

endpoints = Blueprint('endpoints', __name__)

@endpoints.route('/', methods=['GET'])
def hello_world():
    return 'Hello World! my friend'


@endpoints.route('/scrape')
def article_sentiment_analysis_endpoint():
    url = request.args.get('url')
    print(url)
    return escape(article_sentiment_analysis(url))