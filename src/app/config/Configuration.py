import os
from typing import Dict

import yaml
from deepmerge import always_merger

from ..constants.EnvConstants import EnvConstants


def load_yaml_file(path: str) -> Dict:
    try:
        with open(path, 'r') as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        print(f"Config file not found: {path}")
        return {}


def load_config() -> Dict:
    # Load base configuration first
    base_config = load_yaml_file('resources/application.yaml')

    # Load environment specific config
    env = os.getenv(EnvConstants.ENV.value, 'dev')
    env_config = load_yaml_file(f'resources/{env}.yaml')

    # Merge configs, with env-specific values overriding base values
    return always_merger.merge(base_config, env_config)


class Configuration(object):
    def __init__(self):
        self._config = load_config()

    def get(self, *keys, default=None):
        value = self._config
        for key in keys:
            try:
                value = value[key]
            except (KeyError, TypeError):
                return default
        return value

    @property
    def tenant_id(self):
        key_from_env = os.getenv('TENANT_ID')
        if key_from_env is not None and key_from_env != '':
            self._config['tenant']['id'] = key_from_env
        return self._config['tenant']['id']

    @property
    def env(self):
        return os.getenv(EnvConstants.ENV.value, 'dev')

    @property
    def bucket_name(self):
        return self._config['storage']['bucket']

    @property
    def cloud_tasks_queue(self):
        return self._config['cloud_tasks']['queue']

    @property
    def cloud_tasks_location(self):
        return self._config['cloud_tasks']['location']

    @property
    def cloud_tasks_project(self):
        return self._config['cloud_tasks']['project']

    @property
    def redis_port(self):
        return self._config['redis']['port']

    @property
    def redis_host(self):
        return self._config['redis']['host']

    @property
    def open_ai_api_key(self):
        key_from_env = os.getenv(EnvConstants.OPENAI_API_KEY.value)
        if key_from_env is not None and key_from_env != '':
            self._config['ai']['openai']['key'] = key_from_env
        return self._config['ai']['openai']['key']

    @property
    def anthropic_api_key(self):
        key_from_env = os.getenv(EnvConstants.ANTHROPIC_API_KEY.value)
        if key_from_env is not None and key_from_env != '':
            self._config['ai']['anthropic']['key'] = key_from_env
        return self._config['ai']['anthropic']['key']

    @property
    def upload_folder(self):
        return self._config['file']['upload_folder']

    @property
    def processed_folder(self):
        return self._config['file']['processed_folder']
