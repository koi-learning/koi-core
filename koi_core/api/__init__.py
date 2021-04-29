# Copyright (c) individual contributors.
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of
# the License, or any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details. A copy of the
# GNU Lesser General Public License is distributed along with this
# software and can be found at http://www.gnu.org/licenses/lgpl.html
import requests
from multiprocessing import Lock

from .model import APIModels
from .instance import APIInstances
from .sample import APISamples


class API:
    def __init__(self, base_url: str, username: str, password: str):
        self._lock = Lock()
        self._base_url = base_url
        self._user = username
        self._password = password
        self._session = requests.Session()

        self.models = APIModels(self._lock, base_url, username, password, self._session)
        self.instances = APIInstances(self._lock, base_url, username, password, self._session)
        self.samples = APISamples(self._lock, base_url, username, password, self._session)
