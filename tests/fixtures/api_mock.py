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

import json
from typing import TypeVar
import pytest
import datetime
import re
from functools import wraps

# monkey patch JSONEncoder to encode UUIDs as well.

from json import JSONEncoder
from uuid import UUID
import requests
import requests_mock

JSONEncoder_olddefault = JSONEncoder.default


def JSONEncoder_newdefault(self, o):
    if isinstance(o, UUID):
        return str(o)
    return JSONEncoder_olddefault(self, o)


JSONEncoder.default = JSONEncoder_newdefault

data_models = [
    {
        "finalized": True,
        "has_code": True,
        "has_label_plugin": True,
        "has_visual_plugin": True,
        "model_description": "Description 0",
        "model_name": "Model 0",
        "model_uuid": UUID("00000000-0001-1000-8000-000000000000"),
        "code": "testing_model",
        "parameter": [
            {
                "param_uuid": UUID("00000000-1001-1000-8000-000000000000"),
                "name": "param1",
                "description": "description of param1",
                "constraint": "",
                "type": "int",
            },
            {
                "param_uuid": UUID("00000000-1002-1000-8000-000000000000"),
                "name": "param2",
                "description": "description of param2",
                "constraint": "",
                "type": "int",
            },
        ],
        "instances": [
            {
                "could_train": False,
                "finalized": True,
                "has_inference": True,
                "has_training": True,
                "instance_description": "Instance Description 0",
                "instance_name": "Instance 0",
                "instance_uuid": UUID("00000000-0002-1000-8000-000000000000"),
                "parameter": [
                    {
                        "param_uuid": UUID("00000000-1001-1000-8000-000000000000"),
                        "name": "param1",
                        "description": "description of param1",
                        "constraint": "",
                        "type": "int",
                        "value": "1",
                    },
                    {
                        "param_uuid": UUID("00000000-1002-1000-8000-000000000000"),
                        "name": "param2",
                        "description": "description of param2",
                        "constraint": "",
                        "type": "float",
                        "value": "10.0",
                    },
                ],
            },
            {
                "could_train": True,
                "finalized": True,
                "has_inference": True,
                "has_training": True,
                "instance_description": "Instance Description 1",
                "instance_name": "Instance 1",
                "instance_uuid": UUID("00000000-0002-1000-8000-000000000001"),
                "parameter": [
                    {
                        "param_uuid": UUID("00000000-1001-1000-8000-000000000000"),
                        "name": "param1",
                        "description": "description of param1",
                        "constraint": "",
                        "type": "int",
                        "value": "10",
                    },
                    {
                        "param_uuid": UUID("00000000-1002-1000-8000-000000000000"),
                        "name": "param2",
                        "description": "description of param2",
                        "constraint": "",
                        "type": "float",
                        "value": "0.5",
                    },
                ],
            },
        ],
    },
    {
        "finalized": True,
        "has_code": True,
        "has_label_plugin": True,
        "has_visual_plugin": True,
        "model_description": "Description 1",
        "model_name": "Model 1",
        "model_uuid": UUID("00000000-0001-1000-8000-000000000001"),
        "parameter": [],
        "instances": [],
    },
]

data_code = dict()

T = TypeVar("T")


def cache_controlled(func: T) -> T:
    @wraps(func)
    def wrapper(request, context):
        context.headers["Expires"] = datetime.datetime(2050, 12, 10).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )
        context.headers["Last-Modified"] = datetime.datetime(2020, 12, 10).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )
        return func(request, context)

    return wrapper


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

            self.requests_mock.register_uri(
                "POST", "testing://base/api/login", json=login
            )
            self.requests_mock.register_uri(
                "GET", "testing://base/api/model", json=models
            )
            self.requests_mock.register_uri(
                "GET",
                re.compile(r"testing://base/api/model/(\d*)/parameter"),
                json=model_parameter,
            )

            self.requests_mock.register_uri(
                "GET",
                re.compile(r"testing://base/api/model/(\d*)/code"),
                content=model_code,
            )

            self.requests_mock.register_uri(
                "GET",
                re.compile(r"testing://base/api/model/(\d*)/instance"),
                json=instances,
            )
            self.requests_mock.register_uri(
                "GET",
                re.compile(r"testing://base/api/model/(\d*)/instance/(\d*)"),
                json=instance,
            )
            self.requests_mock.register_uri(
                "GET",
                re.compile(r"testing://base/api/model/(\d*)/instance/(\d*)/parameter"),
                json=instance_parameter,
            )
            self.requests_mock.register_uri(
                "POST",
                re.compile(r"testing://base/api/model/(\d*)/instance/(\d*)/parameter"),
                json=instance_parameter_set,
            )

        def set_offline(self):
            if self.requests_mock:
                self.requests_mock.stop()
            self.requests_mock = requests_mock.MockerCore()
            self.requests_mock.start()

            self.requests_mock.register_uri(
                "POST",
                "testing://base/api/login",
                exc=requests.exceptions.ConnectTimeout,
            )
            self.requests_mock.register_uri(
                "GET",
                "testing://base/api/model",
                exc=requests.exceptions.ConnectTimeout,
            )
            self.requests_mock.register_uri(
                "GET",
                re.compile(r"testing://base/api/model/(\d*)/parameter"),
                exc=requests.exceptions.ConnectTimeout,
            )

            self.requests_mock.register_uri(
                "GET",
                re.compile(r"testing://base/api/model/(\d*)/code"),
                exc=requests.exceptions.ConnectTimeout,
            )

            self.requests_mock.register_uri(
                "GET",
                re.compile(r"testing://base/api/model/(\d*)/instance"),
                exc=requests.exceptions.ConnectTimeout,
            )
            self.requests_mock.register_uri(
                "GET",
                re.compile(r"testing://base/api/model/(\d*)/instance/(\d*)/parameter"),
                exc=requests.exceptions.ConnectTimeout,
            )
            self.requests_mock.register_uri(
                "POST",
                re.compile(r"testing://base/api/model/(\d*)/instance/(\d*)/parameter"),
                exc=requests.exceptions.ConnectTimeout,
            )

    yield ApiMock()


def login(request, context):
    token_valid = datetime.datetime.now() + datetime.timedelta(minutes=500)

    context.status_code = 200
    return {
        "user_uuid": "00000000-0000-1000-8000-000000000000",
        "token": "00000000000000000000000000000000",
        "expires": token_valid.isoformat(),
    }


@cache_controlled
def models(request, context):
    keys = [
        "finalized",
        "has_code",
        "has_label_plugin",
        "has_visual_plugin",
        "model_description",
        "model_name",
        "model_uuid",
    ]
    return [{key: model[key] for key in keys} for model in data_models]


@cache_controlled
def model_code(request, context):
    match = re.search(r"testing://base/api/model/(\d*)/code", str(request))
    model_id = UUID(match[1])

    model = next(
        (model for model in data_models if model["model_uuid"] == model_id), None
    )
    return data_code[model["code"]]


@cache_controlled
def model_parameter(request, context):
    match = re.search(r"testing://base/api/model/(\d*)/parameter", str(request))
    model_id = UUID(match[1])

    model = next(
        (model for model in data_models if model["model_uuid"] == model_id), None
    )
    if model is not None:
        return model["parameter"]
    else:
        return []


@cache_controlled
def instances(request, context):
    keys = [
        "could_train",
        "finalized",
        "has_inference",
        "has_training",
        "instance_description",
        "instance_name",
        "instance_uuid",
    ]
    match = re.search(r"testing://base/api/model/(\d*)/instance", str(request))
    model_id = UUID(match[1])

    model = next(
        (model for model in data_models if model["model_uuid"] == model_id), None
    )
    return [{key: instance[key] for key in keys} for instance in model["instances"]]


@cache_controlled
def instance(request, context):
    match = re.search(r"testing://base/api/model/(\d*)/instance/(\d*)", str(request))
    model_id = UUID(match[1])
    instance_id = UUID(match[2])

    model = next(
        (model for model in data_models if model["model_uuid"] == model_id), None
    )

    instance = next(
        (
            instance
            for instance in model["instances"]
            if instance["instance_uuid"] == instance_id
        ),
        None,
    )
    return instance


@cache_controlled
def instance_parameter(request, context):
    return instance(request, context)["parameter"]


@cache_controlled
def instance_parameter_set(request, context):
    match = re.search(
        r"testing://base/api/model/(\d*)/instance/(\d*)/parameter", str(request)
    )
    model_id = UUID(match[1])
    instance_id = UUID(match[2])

    req = json.loads(request.text)
    param_id = UUID(req["param_uuid"])
    param_value = req["value"]

    for idx_m, model in enumerate(data_models):
        if model["model_uuid"] == model_id:
            for idx_i, instance in enumerate(model["instances"]):
                if instance["instance_uuid"] == instance_id:
                    for idx_p, param in enumerate(instance["parameter"]):
                        if param_id == param["param_uuid"]:
                            data_models[idx_m]["instances"][idx_i]["parameter"][idx_p][
                                "value"
                            ] = param_value
                            context.status_code = 200
                            return {}

    context.status_code = 404
    return {}
