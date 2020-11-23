import pytest
import datetime
import re
from uuid import UUID

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


@pytest.fixture
def api_mock(requests_mock, testing_model):
    data_code["testing_model"] = testing_model

    requests_mock.register_uri("POST", "testing://base/api/login", json=login)
    requests_mock.register_uri("GET", "testing://base/api/model", json=models)
    requests_mock.register_uri(
        "GET", re.compile("testing://base/api/model/(\d*)/code"), content=model_code
    )
    requests_mock.register_uri(
        "GET", re.compile("testing://base/api/model/(\d*)/instance"), json=instances
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


def model_code(request, context):
    match = re.search("testing://base/api/model/(\d*)/code", str(request))
    model_id = UUID(match[1])

    model = next(
        (model for model in data_models if model["model_uuid"] == model_id), None
    )
    return data_code[model["code"]]


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
    match = re.search("testing://base/api/model/(\d*)/instance", str(request))
    model_id = UUID(match[1])

    model = next(
        (model for model in data_models if model["model_uuid"] == model_id), None
    )
    return [{key: instance[key] for key in keys} for instance in model["instances"]]
