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

import pytest
import re
from json import JSONEncoder
from uuid import UUID
import requests
import requests_mock
from requests_mock import ANY

from .common_data import data_code
from .handlers_model import models, model_parameter, model_code
from .handlers_instance import instance_parameter, instance_parameter_set, instances, instance
from .handlers_user import users, user, login
from .handlers_roles import roles, role, access_general, access_model, access_instance

# monkey patch JSONEncoder to encode UUIDs as well.
JSONEncoder_olddefault = JSONEncoder.default


def JSONEncoder_newdefault(self, o):
    if isinstance(o, UUID):
        return str(o)
    return JSONEncoder_olddefault(self, o)


JSONEncoder.default = JSONEncoder_newdefault


@pytest.fixture
def api_mock(testing_model):
    data_code["testing_model"] = testing_model

    class ApiMock:
        requests_mock = None

        def __init__(self):
            self.set_online()

        def set_online(self):
            if self.requests_mock:
                self.requests_mock.stop()
            self.requests_mock = requests_mock.MockerCore()
            self.requests_mock.start()

            self.requests_mock.register_uri("POST", "http://base/api/login", json=login)
            self.requests_mock.register_uri("GET", "http://base/api/model", json=models)
            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/parameter"), json=model_parameter,
            )

            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/code"), content=model_code,
            )

            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance"), json=instances,
            )
            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)"), json=instance,
            )
            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)/parameter"), json=instance_parameter,
            )
            self.requests_mock.register_uri(
                "POST", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)/parameter"), json=instance_parameter_set,
            )

            self.requests_mock.register_uri(ANY, re.compile(r"http://base/api/user/([0-9,a-f,-]*)"), json=user)
            self.requests_mock.register_uri(ANY, "http://base/api/user", json=users)

            self.requests_mock.register_uri(ANY, re.compile(r"http://base/api/userroles/(\w*)"), json=roles)
            self.requests_mock.register_uri(ANY, re.compile(r"http://base/api/userroles/(\w*)/([0-9,a-f,-]*)"), json=role)

            self.requests_mock.register_uri(ANY, re.compile("http://base/api/access"), json=access_general)
            self.requests_mock.register_uri(ANY, re.compile(r"http://base/api/model/([0-9,a-f,-]*)/access"), json=access_model)
            self.requests_mock.register_uri(ANY, re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)/access"), json=access_instance)

        def set_offline(self):
            if self.requests_mock:
                self.requests_mock.stop()
            self.requests_mock = requests_mock.MockerCore()
            self.requests_mock.start()

            self.requests_mock.register_uri(
                "POST", "http://base/api/login", exc=requests.exceptions.ConnectTimeout,
            )
            self.requests_mock.register_uri(
                "GET", "http://base/api/model", exc=requests.exceptions.ConnectTimeout,
            )
            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/parameter"), exc=requests.exceptions.ConnectTimeout,
            )

            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/code"), exc=requests.exceptions.ConnectTimeout,
            )

            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance"), exc=requests.exceptions.ConnectTimeout,
            )
            self.requests_mock.register_uri(
                "GET",
                re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)/parameter"),
                exc=requests.exceptions.ConnectTimeout,
            )
            self.requests_mock.register_uri(
                "POST",
                re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)/parameter"),
                exc=requests.exceptions.ConnectTimeout,
            )

        def set_connectionError(self):
            if self.requests_mock:
                self.requests_mock.stop()
            self.requests_mock = requests_mock.MockerCore()
            self.requests_mock.start()

            self.requests_mock.register_uri(
                "POST", "http://base/api/login", exc=requests.exceptions.ConnectionError,
            )
            self.requests_mock.register_uri(
                "GET", "http://base/api/model", exc=requests.exceptions.ConnectionError,
            )
            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/parameter"), exc=requests.exceptions.ConnectionError,
            )

            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/code"), exc=requests.exceptions.ConnectionError,
            )

            self.requests_mock.register_uri(
                "GET", re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance"), exc=requests.exceptions.ConnectionError,
            )
            self.requests_mock.register_uri(
                "GET",
                re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)/parameter"),
                exc=requests.exceptions.ConnectionError,
            )
            self.requests_mock.register_uri(
                "PUT",
                re.compile(r"http://base/api/model/([0-9,a-f,-]*)/instance/([0-9,a-f,-]*)/parameter"),
                exc=requests.exceptions.ConnectionError,
            )

    yield ApiMock()
