from flask import Flask
from routes import main_routes
from dotenv import load_dotenv
from utils import check_access_token


load_dotenv()
app = Flask(__name__)
app.register_blueprint(main_routes)


if __name__ == "__main__":
    check_access_token()
    app.run(debug=True)
