from typing import Optional

from flask import Flask
from google.cloud.tasks_v2 import CloudTasksClient
from redis import Redis

from .. import get_redis_client, get_cloud_tasks_client
from ..services.impl.InvoiceParserService import InvoiceParserService


class ServiceRegistry:
    def __init__(self):
        self.invoice_parser_service: Optional[InvoiceParserService] = None
        self.redis_client: Optional[Redis] = None
        self.cloud_tasks_client: Optional[CloudTasksClient] = None

    def init_invoice_parser_service(self, app: Flask):
        self.invoice_parser_service = InvoiceParserService(app)

    def init_redis_client(self, app: Flask):
        self.redis_client = get_redis_client(app.config['CONFIGURATION'])

    def init_cloud_tasks_client(self):
        self.cloud_tasks_client = get_cloud_tasks_client()


services = ServiceRegistry()

