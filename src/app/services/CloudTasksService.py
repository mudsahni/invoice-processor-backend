from google.cloud import tasks_v2
from google.cloud.tasks_v2 import CloudTasksClient


def create_task(client: CloudTasksClient, parent: str, job_id: str):
    task = {
        'http_request': {
            'http_method': tasks_v2.HttpMethod.POST,
            'url': f'{os.getenv("SERVICE_URL")}/tasks/process',
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                'job_id': job_id,
                'prompt': prompt
            }).encode()
        }
    }

    return client.create_task(request={'parent': parent, 'task': task})
