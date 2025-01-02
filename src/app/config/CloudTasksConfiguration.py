from google.cloud import tasks_v2
from google.cloud.tasks_v2 import CloudTasksClient

from .Configuration import Configuration


def get_cloud_tasks_client() -> CloudTasksClient:
    return tasks_v2.CloudTasksClient()


def get_cloud_tasks_queue_path(config: Configuration, client: CloudTasksClient) -> str:
    return client.queue_path(config.cloud_tasks_project, config.cloud_tasks_location, config.cloud_tasks_queue)
