from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from config import Config
from routes import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable global CORS with explicit origins, methods, and headers
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        supports_credentials=False
    )

    # Catch-all preflight OPTIONS handler
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            res = make_response()
            res.headers["Access-Control-Allow-Origin"] = "*"
            res.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
            return res, 200

    # Ensure every response (including errors) has CORS headers
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
        return response

    # Direct Health Check Routes on the App
    @app.route('/', methods=['GET'])
    @app.route('/health', methods=['GET'])
    @app.route('/api/health', methods=['GET'])
    def root_health():
        return jsonify({
            'status': 'online',
            'service': 'FrameStudio Flask API'
        }), 200

    # Register API Blueprint under /api
    app.register_blueprint(api, url_prefix='/api')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)