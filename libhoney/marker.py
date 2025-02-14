import requests
import datetime
import random
from contextlib import contextmanager

from libhoney import state
from libhoney.fields import FieldHolder


class Marker:
    def __init__(self, start_time, message, end_time, type, url=None, client=None):
        if client is None:
            client = state.G_CLIENT

        # copy configuration from client
        self.client = client
        if self.client:
            self.writekey = client.writekey
            self.dataset = client.dataset
            self.api_host = client.api_host
            self.sample_rate = client.sample_rate

        else:
            self.writekey = None
            self.dataset = None
            self.api_host = "https://api.honeycomb.io"
            self.sample_rate = 1
        self.session = requests.Session()

    def send_marker(self, start_time, message, end_time=None, type=None, url=None):
        headers = {
            "X-Honeycomb-Team": self.writekey,
            "Content-Type": "application/json",
        }
        url = f"{self.api_host}/1/markers/{self.dataset}"
        data = {"start_time": start_time, "message": message}
        if end_time is not None:
            data["end_time"] = end_time
        if type is not None:
            data["type"] = type
        if url is not None:
            data["url"] = url

        try:
            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create marker: {str(e)}")
