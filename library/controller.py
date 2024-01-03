from flask import Blueprint, request
from markupsafe import escape
from library.utils import article_sentiment_analysis

endpoints = Blueprint('endpoints', __name__)

@endpoints.route('/scrape', methods=['GET'])
def article_sentiment_analysis_endpoint():
    url = request.args.get('url')

    return escape(article_sentiment_analysis(url))