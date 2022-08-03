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

from koi_core.api.common import BaseAPI, RequestsAPI, is_reachable
from koi_core.api.model import APIModels
from koi_core.api.instance import APIInstances
from koi_core.api.sample import APISamples
from koi_core.api.user import APIUsers
from koi_core.api.role import APIRoles
from koi_core.api.access import APIAccess


def is_koi_reachable(host: str) -> bool:
    return is_reachable(host)


class API(RequestsAPI):
    def __init__(self, base_url: str, username: str, password: str):
        super().__init__(base_url, username, password)

        self.models = APIModels(self)
        self.instances = APIInstances(self)
        self.samples = APISamples(self)
        self.users = APIUsers(self)
        self.roles = APIRoles(self)
        self.access = APIAccess(self)


class OfflineAPI(BaseAPI):
    def __init__(self, base_url: str):
        super().__init__(base_url)

        self.models = APIModels(self)
        self.instances = APIInstances(self)
        self.samples = APISamples(self)
        self.users = APIUsers(self)
        self.roles = APIRoles(self)
        self.access = APIAccess(self)
