import ssl

import certifi
from flask import Flask
from flask_cors import CORS

from .config.CloudTasksConfiguration import get_cloud_tasks_client
from .config.RedisConfiguration import get_redis_client
from .controllers.v1.InvoiceParserController import invoice_bp
from .services import services
from .config.Configuration import Configuration
import os


# Create SSL context with system certificates
ssl_context = ssl.create_default_context(
    cafile=certifi.where(),
    capath="/etc/ssl/certs"
)
# Set SSL cert verification globally
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['HTTPX_SSL_VERIFY'] = certifi.where()

config: Configuration = Configuration()

def create_app():
    app: Flask = Flask(__name__)
    app.config.from_object(config)
    app.config.update({
        'UPLOAD_FOLDER': str(config.upload_folder),
        'PROCESSED_FOLDER': str(config.processed_folder),
        'CONFIGURATION': config
    })

    # Initialize extensions
    CORS(app)

    # initialize the invoice parser service
    services.init_invoice_parser_service(app)
    services.init_redis_client(app)
    services.init_cloud_tasks_client()

    # Register blueprints
    app.register_blueprint(invoice_bp, url_prefix='/api/v1')

    # Create required directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

    return app
