import os
from flask_api import app

from dotenv import load_dotenv

load_dotenv()

FLASK_HOST = os.getenv('FLASK_HOST', 'localhost')
FlASK_PORT = int(os.getenv('FLASK_PORT', 5001))

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FlASK_PORT)