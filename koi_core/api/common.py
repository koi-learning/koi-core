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
from requests.auth import AuthBase
from koi_core.resources.ids import (
    InstanceId,
    ModelId,
    SampleDatumId,
    SampleId,
    SampleLableId,
    DescriptorId,
)
from koi_core.caching import CachingMeta
import requests
import functools
from typing import Any, Tuple, Union, TypeVar
from datetime import datetime


T = TypeVar("T")


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def getCachingMeta(header) -> CachingMeta:
    """Parse all relevant information from the headers into a CachingMeta object"""
    meta = None
    if "Expires" in header and "Last-Modified" in header:
        meta = CachingMeta()
        meta.expires = datetime.strptime(header["Expires"], "%a, %d %b %Y %H:%M:%S GMT")
        meta.last_modified = datetime.strptime(header["Last-Modified"], "%a, %d %b %Y %H:%M:%S GMT")

    if meta is not None and "Etag" in header:
        meta.etag = header["Etag"]

    return meta


def authenticate_locked(baseAPI: "BaseAPI", force=False):
    baseAPI._lock.acquire()
    if force or not hasattr(baseAPI, "_token") or not baseAPI._token:
        baseAPI.authenticate()
        baseAPI._lock.release()
    else:
        baseAPI._lock.release()


def authenticated_head(request_func: T) -> T:
    @functools.wraps(request_func)
    def func(self: "BaseAPI", *args, **kwargs):
        authenticate_locked(self)

        response = request_func(self, *args, auth=BearerAuth(self._token), **kwargs)

        if response.status_code != 200:
            if response.status_code == 404:
                raise LookupError()
            elif response.status_code == 401:
                authenticate_locked(self, True)
                response = request_func(self, *args, auth=BearerAuth(self._token), **kwargs)
                if response.status_code != 200:
                    raise Exception(f"{response.status_code}: {response.content}")
            else:
                raise Exception(f"{response.status_code}: {response.content}")

        meta = getCachingMeta(response.headers)

        return meta

    return func


def authenticated_json(request_func: T) -> T:
    @functools.wraps(request_func)
    def func(self: "BaseAPI", *args, **kwargs):
        authenticate_locked(self)

        response = request_func(self, *args, auth=BearerAuth(self._token), **kwargs)

        if response.status_code != 200:
            if response.status_code == 404:
                raise LookupError()
            elif response.status_code == 401:
                authenticate_locked(self, True)
                response = request_func(self, *args, auth=BearerAuth(self._token), **kwargs)
                if response.status_code != 200:
                    raise Exception(f"{response.status_code}: {response.content}")
            else:
                raise Exception(f"{response.status_code}: {response.content}")

        meta = getCachingMeta(response.headers)

        return response.json(), meta

    return func


def authenticated_raw(request_func: T) -> T:
    @functools.wraps(request_func)
    def func(self: "BaseAPI", *args, **kwargs):
        authenticate_locked(self)

        response = request_func(self, *args, auth=BearerAuth(self._token), **kwargs)

        if response.status_code != 200:
            if response.status_code == 404:
                raise LookupError()
            elif response.status_code == 401:
                authenticate_locked(self, True)
                response = request_func(self, *args, auth=BearerAuth(self._token), **kwargs)
                if response.status_code != 200:
                    raise Exception(f"{response.status_code}: {response.content}")
            else:
                raise Exception(f"{response.status_code}: {response.content}")

        meta = getCachingMeta(response.headers)

        return response.content, meta

    return func


def _parse(response, cls, mapping):
    if response[0] is None:
        return response
    object = cls()
    for key in cls.__annotations__:
        setattr(object, key, response[0][mapping[key]])
    return object, response[1]


def _encode(object, cls, mapping):
    ret = dict()
    for key in cls.__annotations__:
        ret[mapping[key]] = getattr(object, key)
    return ret


class BaseAPI:
    def __init__(self, lock, base_url, username, password, session):
        self._lock = lock
        self._base_url = base_url
        self._user = username
        self._password = password
        self._session = session

    def authenticate(self):
        response = self._session.post(
            self._base_url + "/api/login", json={"user_name": self._user, "password": self._password},
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

    def GET(self, path: str, meta: CachingMeta = None):
        if meta is None:
            return self._GET(path)
        else:
            new_meta = self._HEAD(path)
            if new_meta != meta:
                return self._GET(path)
            else:
                return None, new_meta

    def GET_RAW(self, path: str, meta: CachingMeta = None) -> Tuple[bytes, CachingMeta]:
        if meta is None:
            return self._GET_raw(path)
        else:
            new_meta = self._HEAD(path)
            if new_meta != meta:
                return self._GET_raw(path)
            else:
                return None, new_meta

    def _build_path(
        self, id: Union[ModelId, InstanceId, SampleId, SampleDatumId, SampleLableId, DescriptorId],
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
