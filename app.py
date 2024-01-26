if __name__ == '__main__':
    from flask import Flask
    from library.controllers.scrape import scrape
    from library.utils.utils import Utils

    app = Flask(__name__)

    app.register_blueprint(scrape)
    Utils.cashing_urls()

    app.run()
