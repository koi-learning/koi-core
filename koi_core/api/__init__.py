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
from koi_core.api.common import BaseAPI, RequestsAPI
import requests
from multiprocessing import Lock

from .model import APIModels
from .instance import APIInstances
from .sample import APISamples


class API(RequestsAPI):
    def __init__(self, base_url: str, username: str, password: str):
        super().__init__(base_url, username, password)

        self.models = APIModels(self)
        self.instances = APIInstances(self)
        self.samples = APISamples(self)

class OfflineAPI(BaseAPI):
    def __init__(self):
        super().__init__()

        self.models = APIModels(self)
        self.instances = APIInstances(self)
        self.samples = APISamples(self)
