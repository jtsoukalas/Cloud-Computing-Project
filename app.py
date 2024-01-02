from flask import Flask
from library.controller import endpoints

app = Flask(__name__)

app.register_blueprint(endpoints)
app.run()
