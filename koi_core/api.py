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

from requests.models import Response
from koi_core.resources.sample import SampleBasicFields, SampleDatumBasicFields
from koi_core.resources.instance import InstanceBasicFields, DescriptorBasicFields
from requests.auth import AuthBase
from koi_core.resources.model import ModelBasicFields
from koi_core.resources.ids import (
    InstanceId,
    ModelId,
    SampleDatumId,
    SampleId,
    SampleLableId,
    DescriptorId,
)
from koi_core.caching import CachingMeta
from uuid import UUID
import requests
import functools
from typing import Any, Tuple, TypeVar, Union
from datetime import datetime

from multiprocessing import Lock

T = TypeVar("T")


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def authenticated_head(request_func: T) -> T:
    @functools.wraps(request_func)
    def func(self: "API", *args, **kwargs):
        self._lock.acquire()
        if not hasattr(self, "_token") or not self._token:
            self.authenticate()
            self._lock.release()
        else:
            self._lock.release()

        response = request_func(self, *args, auth=BearerAuth(self._token), **kwargs)

        if response.status_code != 200:
            raise Exception(f"{response.status_code}: {response.content}")

        meta = None
        if "Expires" in response.headers and "Last-Modified" in response.headers:
            meta = CachingMeta()
            meta.expires = datetime.strptime(
                response.headers["Expires"], "%a, %d %b %Y %H:%M:%S GMT"
            )
            meta.last_modified = datetime.strptime(
                response.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S GMT"
            )

        return meta

    return func


def authenticated_json(request_func: T) -> T:
    @functools.wraps(request_func)
    def func(self: "API", *args, **kwargs):
        self._lock.acquire()
        if not hasattr(self, "_token") or not self._token:
            self.authenticate()
            self._lock.release()
        else:
            self._lock.release()

        response = request_func(self, *args, auth=BearerAuth(self._token), **kwargs)
        response: Response
        if response.status_code != 200:
            raise Exception(f"{response.status_code}: {response.content}")

        # TODO check for not authenticated request

        meta = None
        if "Expires" in response.headers:
            meta = CachingMeta()
            meta.expires = datetime.strptime(
                response.headers["Expires"], "%a, %d %b %Y %H:%M:%S GMT"
            )
            meta.last_modified = datetime.strptime(
                response.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S GMT"
            )

        return response.json(), meta

    return func


def authenticated_raw(request_func: T) -> T:
    @functools.wraps(request_func)
    def func(self: "API", *args, **kwargs):
        self._lock.acquire()
        if not hasattr(self, "_token") or not self._token:
            self.authenticate()
            self._lock.release()
        else:
            self._lock.release()

        response = request_func(self, *args, auth=BearerAuth(self._token), **kwargs)
        response: Response
        if response.status_code != 200:
            if response.status_code == 404:
                raise LookupError()
            raise Exception(f"{response.status_code}: {response.content}")

        # TODO check for not authenticated request

        meta = None
        if "Expires" in response.headers:
            meta = CachingMeta()
            meta.expires = datetime.strptime(
                response.headers["Expires"], "%a, %d %b %Y %H:%M:%S GMT"
            )
            meta.last_modified = datetime.strptime(
                response.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S GMT"
            )

        return response.content, meta

    return func


def _parse(response, cls, mapping):
    object = cls()
    for key in cls.__annotations__:
        setattr(object, key, response[0][mapping[key]])
    return object, response[1]


def _encode(object, cls, mapping):
    ret = dict()
    for key in cls.__annotations__:
        ret[mapping[key]] = getattr(object, key)
    return ret


_model_mapping = {
    "name": "model_name",
    "description": "model_description",
    "finalized": "finalized",
}


def _parse_model(response) -> Tuple[ModelBasicFields, CachingMeta]:
    return _parse(response, ModelBasicFields, _model_mapping)


def _encode_model(model: ModelBasicFields):
    return _encode(model, ModelBasicFields, _model_mapping)


_instance_mapping = {
    "name": "instance_name",
    "description": "instance_description",
    "finalized": "finalized",
    "could_train": "could_train",
}


def _parse_instance(response) -> Tuple[InstanceBasicFields, CachingMeta]:
    return _parse(response, InstanceBasicFields, _instance_mapping)


def _encode_instance(model: InstanceBasicFields):
    return _encode(model, InstanceBasicFields, _instance_mapping)


_instance_descriptor_mapping = {"key": "key"}


def _parse_instance_descriptor(response) -> Tuple[DescriptorBasicFields, CachingMeta]:
    return _parse(response, DescriptorBasicFields, _instance_descriptor_mapping)


def _encode_instance_descriptor(descriptor: DescriptorBasicFields):
    return _encode(descriptor, DescriptorBasicFields, _instance_descriptor_mapping)


_sample_mapping = {
    "finalized": "finalized",
    "consumed": "consumed",
    "obsolete": "obsolete",
}


def _parse_sample(response) -> Tuple[SampleBasicFields, CachingMeta]:
    return _parse(response, SampleBasicFields, _sample_mapping)


def _encode_sample(model: SampleBasicFields):
    return _encode(model, SampleBasicFields, _sample_mapping)


_sample_datum_mapping = {"key": "key"}


def _parse_sample_datum(response) -> Tuple[SampleDatumBasicFields, CachingMeta]:
    return _parse(response, SampleDatumBasicFields, _sample_datum_mapping)


def _encode_sample_datum(model: SampleDatumBasicFields):
    return _encode(model, SampleDatumBasicFields, _sample_datum_mapping)


class API:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self._lock = Lock()
        self._base_url = base_url
        self._user = username
        self._password = password
        self._session = requests.Session()

    def authenticate(self):
        response = self._session.post(
            self._base_url + "/api/login",
            json={"user_name": self._user, "password": self._password},
        )
        if not response.status_code == 200:
            raise ValueError("invalid login")
        self._token = response.json()["token"]

    @authenticated_head
    def _HEAD(self, path: str, auth: AuthBase):
        return self._session.head(self._base_url + path, auth=auth)

    @authenticated_json
    def _DELETE(self, path: str, auth: AuthBase):
        return self._session.delete(self._base_url + path, auth=auth)

    @authenticated_json
    def _POST(self, path: str, auth: AuthBase, data: Any = None):
        return self._session.post(self._base_url + path, json=data, auth=auth)

    @authenticated_json
    def _GET(self, path: str, auth: AuthBase, parameter=None):
        return self._session.get(self._base_url + path, params=parameter, auth=auth)

    @authenticated_json
    def _PUT(self, path: str, auth: AuthBase, data: Any = None):
        return self._session.put(self._base_url + path, json=data, auth=auth)

    @authenticated_raw
    def _GET_raw(self, path, auth: AuthBase) -> Tuple[bytes, CachingMeta]:
        return self._session.get(self._base_url + path, auth=auth)

    @authenticated_json
    def _POST_raw(self, path: str, auth: AuthBase, data: bytes = None):
        return self._session.post(self._base_url + path, data=data, auth=auth)

    def _build_path(
        self,
        id: Union[
            ModelId, InstanceId, SampleId, SampleDatumId, SampleLableId, DescriptorId
        ],
    ):
        path = "/api"

        if isinstance(id, ModelId):
            path = path + f"/model/{id.model_uuid.hex}"
        if isinstance(id, InstanceId):
            path = path + f"/instance/{id.instance_uuid.hex}"
        if isinstance(id, DescriptorId):
            path = path + f"/descriptor/{id.descriptor_uuid.hex}"
        if isinstance(id, SampleId):
            path = path + f"/sample/{id.sample_uuid.hex}"
        if isinstance(id, SampleDatumId):
            path = path + f"/data/{id.sample_datum_uuid.hex}"
        if isinstance(id, SampleLableId):
            path = path + f"/label/{id.sample_label_uuid.hex}"

        return path

    # region model
    def get_models(self, meta: CachingMeta = None):
        data, meta = self._GET("/api/model")
        return (
            [ModelId(model_uuid=UUID(d["model_uuid"])) for d in data],
            meta,
        )

    def new_model(self):
        data, meta = self._POST("/api/model", data={})
        return (
            ModelId(model_uuid=UUID(data["model_uuid"])),
            meta,
        )

    def get_model(self, id: ModelId, meta: CachingMeta = None):
        if meta is None:
            return _parse_model(self._GET(self._build_path(id)))
        else:
            new_meta = self._HEAD(self._build_path(id))
            if new_meta.last_modified > meta.last_modified:
                return _parse_model(self._GET(self._build_path(id)))
            else:
                return None, new_meta

    def update_model(self, id: ModelId, update: ModelBasicFields):
        self._PUT(self._build_path(id), data=_encode_model(update))

    def get_model_code(self, id: ModelId, meta: CachingMeta = None):
        path = self._build_path(id) + "/code"
        if meta is None:
            return self._GET_raw(path)
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return self._GET_raw(path)
            else:
                return None, new_meta

    def set_model_code(self, id: ModelId, data: bytes) -> None:
        self._POST_raw(self._build_path(id) + "/code", data=data)

    def get_model_visual_plugin(self, id: ModelId, meta: CachingMeta = None):
        path = self._build_path(id) + "/visualplugin"
        if meta is None:
            return self._GET_raw(path)
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return self._GET_raw(path)
            else:
                return None, new_meta

    def set_model_visual_plugin(self, id: ModelId, data: bytes) -> None:
        self._POST_raw(self._build_path(id) + "/visualplugin", data=data)

    def get_model_request_plugin(self, id: ModelId, meta: CachingMeta = None):
        path = self._build_path(id) + "/requestplugin"
        if meta is None:
            return self._GET_raw(path)
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return self._GET_raw(path)
            else:
                return None, new_meta

    def set_model_request_plugin(self, id: ModelId, data: bytes) -> None:
        self._POST_raw(self._build_path(id) + "/requestplugin", data=data)

    # endregion

    # region instance
    def get_instances(self, id: ModelId, last_modified=None):
        data, meta = self._GET(self._build_path(id) + "/instance")
        return (
            [InstanceId(id=id, instance_uuid=UUID(d["instance_uuid"])) for d in data],
            meta,
        )

    def new_instance(self, id: ModelId):
        data, meta = self._POST(self._build_path(id) + "/instance", data={})
        return (
            InstanceId(id=id, instance_uuid=UUID(data["instance_uuid"])),
            meta,
        )

    def get_instance(self, id: InstanceId, meta: CachingMeta = None):
        path = self._build_path(id)
        if meta is None:
            return _parse_instance(self._GET(path))
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return _parse_instance(self._GET_raw(path))
            else:
                return None, new_meta

    def update_instance(self, id: InstanceId, update: InstanceBasicFields):
        self._PUT(self._build_path(id), data=_encode_instance(update))

    def get_instance_inference_data(self, id: InstanceId, meta: CachingMeta = None):
        path = self._build_path(id) + "/inference"
        if meta is None:
            return self._GET_raw(path)
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return self._GET_raw(path)
            else:
                return None, new_meta

    def set_instance_inference_data(self, id: InstanceId, data: bytes):
        self._POST_raw(self._build_path(id) + "/inference", data=data)

    def get_instance_training_data(self, id: InstanceId, meta: CachingMeta):
        path = self._build_path(id) + "/training"
        if meta is None:
            return self._GET_raw(path)
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return self._GET_raw(path)
            else:
                return None, new_meta

    def set_instance_training_data(self, id: InstanceId, data: bytes):
        self._POST_raw(self._build_path(id) + "/training", data=data)

    # endregion

    # region descriptor
    def get_descriptors(self, id: InstanceId, meta: CachingMeta = None):
        data, meta = self._GET(self._build_path(id) + "/descriptor")
        return (
            [
                DescriptorId(id=id, descriptor_uuid=UUID(d["descriptor_uuid"]))
                for d in data
            ],
            meta,
        )

    def new_descriptor(self, id: InstanceId):
        data, meta = self._POST(self._build_path(id) + "/descriptor", data={})
        return (
            DescriptorId(id=id, descriptor_uuid=UUID(data["descriptor_uuid"])),
            meta,
        )

    def get_descriptor(self, id: DescriptorId, meta: CachingMeta = None):
        return _parse_instance_descriptor(self._GET(self._build_path(id)))

    def update_descriptor(self, id: DescriptorId, update: DescriptorBasicFields):
        self._PUT(self._build_path(id), data=_encode_instance_descriptor(update))

    def get_descriptor_data(self, id: DescriptorId, meta: CachingMeta = None):
        return self._GET_raw(self._build_path(id) + "/file")

    def set_descriptor_data(self, id: DescriptorId, data: bytes):
        self._POST_raw(self._build_path(id) + "/file", data=data)

    # endregion descriptor

    # region sample
    def get_samples(self, id: InstanceId, filter_include: list = None, filter_exclude: list = None):
        params = {}
        if filter_include is not None:
            params["inc_tags"] = filter_include
        if filter_exclude is not None:
            params["exc_tags"] = filter_exclude
        cont = True
        data = []
        meta = None
        offset = 0
        while cont:
            params["page_offset"] = offset
            data_part, meta = self._GET(
                self._build_path(id) + "/sample",
                parameter=params,
            )
            data = data + data_part
            offset += len(data_part)
            if len(data_part) == 0:
                cont = False
        return (
            [SampleId(id=id, sample_uuid=UUID(d["sample_uuid"])) for d in data],
            meta,
        )

    def new_sample(self, id: InstanceId):
        data, meta = self._POST(self._build_path(id) + "/sample", data={},)
        return (
            SampleId(id=id, sample_uuid=UUID(data["sample_uuid"])),
            meta,
        )

    def get_sample(self, id: SampleId, meta: CachingMeta = None):
        path = self._build_path(id)
        if meta is None:
            return _parse_sample(self._GET(path))
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return _parse_sample(self._GET(path))
            else:
                return None, new_meta

    def update_sample(self, id: SampleId, update: SampleBasicFields):
        self._PUT(self._build_path(id), data=_encode_sample(update))

    def get_tags(self, id: SampleId, meta: CachingMeta = None):
        path = self._build_path(id) + "/tags"
        if meta is None:
            json_resp, new_meta = self._GET(path)
            return {obj["name"] for obj in json_resp}, new_meta
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                json_resp, new_meta = self._GET(path)
                return {obj["name"] for obj in json_resp}, new_meta
            else:
                return None, new_meta

    def update_tags(self, id: SampleId, update: set):
        new_tags = [{"name": x} for x in update]
        self._DELETE(self._build_path(id) + "/tags")
        self._PUT(self._build_path(id) + "/tags", data=new_tags)

    def add_tag(self, id: SampleId, item: str):
        self._PUT(self._build_path(id) + "/tags", data=[{"name": item},])

    def remove_tag(self, id: SampleId, item: str):
        self._DELETE(self._build_path(id) + "/tags/" + item)

    def request_label(self, id: SampleId):
        self._POST(
            self._build_path(id.InstanceId) + "/label_request",
            data={"sample_uuid": id.sample_uuid.hex},
        )

    # endregion

    # region sample_datum
    def get_sample_data(self, id: SampleId):
        data, meta = self._GET(self._build_path(id) + "/data")
        return (
            [
                SampleDatumId(id=id, sample_datum_uuid=UUID(d["data_uuid"]))
                for d in data
            ],
            meta,
        )

    def new_sample_datum(self, id: SampleId):
        data, meta = self._POST(self._build_path(id) + "/data", data={},)
        return (
            SampleDatumId(id=id, sample_datum_uuid=UUID(data["data_uuid"])),
            meta,
        )

    def get_sample_datum(self, id: SampleDatumId, meta: CachingMeta):
        path = self._build_path(id)
        if meta is None:
            return _parse_sample_datum(self._GET(path))
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return _parse_sample_datum(self._GET(path))
            else:
                return None, new_meta

    def update_sample_datum(self, id: SampleDatumId, update: SampleDatumBasicFields):
        self._PUT(self._build_path(id), data=_encode_sample_datum(update))

    def get_sample_datum_file(self, id: SampleDatumId, meta: CachingMeta = None):
        path = self._build_path(id) + "/file"
        if meta is None:
            return self._GET_raw(path)
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return self._GET_raw(path)
            else:
                return None, new_meta

    def set_sample_datum_file(self, id: SampleDatumId, data: bytes):
        self._POST_raw(self._build_path(id) + "/file", data=data)

    # endregion

    # region sample_label
    def get_sample_labels(self, id: SampleId):
        data, meta = self._GET(self._build_path(id) + "/label")
        return (
            [
                SampleLableId(id=id, sample_label_uuid=UUID(d["label_uuid"]))
                for d in data
            ],
            meta,
        )

    def new_sample_label(self, id: SampleId):
        response = self._POST(self._build_path(id) + "/label", data={})
        return (
            SampleLableId(id=id, sample_label_uuid=UUID(response[0]["label_uuid"])),
            response[1],
        )

    def get_sample_label(self, id: SampleLableId, meta: CachingMeta):
        path = self._build_path(id)
        if meta is None:
            return _parse_sample_datum(self._GET(path))
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return _parse_sample_datum(self._GET(path))
            else:
                return None, new_meta

    def update_sample_label(self, id: SampleLableId, update: SampleDatumBasicFields):
        self._PUT(self._build_path(id), data=_encode_sample_datum(update))

    def get_sample_label_file(self, id: SampleLableId, meta: CachingMeta = None):
        path = self._build_path(id) + "/file"
        if meta is None:
            return self._GET_raw(path)
        else:
            new_meta = self._HEAD(path)
            if new_meta.last_modified > meta.last_modified:
                return self._GET_raw(path)
            else:
                return None, new_meta

    def set_sample_label_file(self, id: SampleLableId, data: bytes):
        self._POST_raw(self._build_path(id) + "/file", data=data)

    # endregion
