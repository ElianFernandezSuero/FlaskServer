from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello from Flask on Vercel!'

def handler(event, context):
    return app(event, context)
