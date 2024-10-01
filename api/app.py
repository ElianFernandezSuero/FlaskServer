from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "¡Hola desde Flask en Vercel!"})

def handler(request):
    with app.test_request_context(
        path=request.path,
        method=request.method,
        headers=request.headers,
        query_string=request.query_string,
        data=request.body
    ):
        response = app.full_dispatch_request()
        return {
            "statusCode": response.status_code,
            "headers": dict(response.headers),
            "body": response.get_data(as_text=True),
        }
