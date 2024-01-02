from flask import current_app as app
from markupsafe import escape
from utils import article_sentiment_analysis


@app.route('/')
def hello_world():
    return 'Hello World! my friend'


@app.route('/scrape/<url>')
def article_sentiment_analysis_endpoint(url):
    return escape(article_sentiment_analysis(url))
