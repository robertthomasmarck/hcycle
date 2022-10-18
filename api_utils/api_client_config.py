import os

import attr
import toml

from paths import get_paths



@attr.s
class ApiCliConfig:
    api_key = attr.ib(default='')
    server = attr.ib(default='')
    version = attr.ib(default=3)
    headers = attr.ib(default=attr.Factory(dict))
    verbose = attr.ib(default=True)

    def set_request_config(self, env):
        self.server = self.env_url(env)
        self.api_key = self.get_key()[env]
        self.headers['x-api-key'] = self.get_key()[env]
        self.server = self.env_url(env)

    def get_key(self):
        with open(f"{os.path.dirname(__file__)}\\api_keys.toml") as keys:
            data = toml.load(keys)
        return data['api_keys']

    def env_url(self, env):
        return f"https://api.na-{env}.ktiops.net"
