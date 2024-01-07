from flask import Flask
from library.controllers.scrape import scrape

app = Flask(__name__)

app.register_blueprint(scrape)

if __name__ == '__main__':
    app.run()
