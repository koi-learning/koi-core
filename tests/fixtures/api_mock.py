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

from typing import TypeVar
import pytest
import datetime
import re
from functools import wraps

# monkey patch JSONEncoder to encode UUIDs as well.

from json import JSONEncoder
from uuid import UUID

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
        "instances": [
            {
                "could_train": False,
                "finalized": True,
                "has_inference": True,
                "has_training": True,
                "instance_description": "Instance Description 0",
                "instance_name": "Instance 0",
                "instance_uuid": UUID("00000000-0002-1000-8000-000000000000"),
            },
            {
                "could_train": True,
                "finalized": True,
                "has_inference": True,
                "has_training": True,
                "instance_description": "Instance Description 1",
                "instance_name": "Instance 1",
                "instance_uuid": UUID("00000000-0002-1000-8000-000000000001"),
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
def api_mock(requests_mock, testing_model):
    data_code["testing_model"] = testing_model

    requests_mock.register_uri("POST", "testing://base/api/login", json=login)
    requests_mock.register_uri("GET", "testing://base/api/model", json=models)
    requests_mock.register_uri(
        "GET", re.compile(r"testing://base/api/model/(\d*)/code"), content=model_code
    )
    requests_mock.register_uri(
        "GET", re.compile(r"testing://base/api/model/(\d*)/instance"), json=instances
    )
    return requests_mock


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
