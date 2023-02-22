# Start Flask by using command:
# python run.py
# Depreciated: replaced by command "flask run"
from url_shortener import app
if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=3000,
    )