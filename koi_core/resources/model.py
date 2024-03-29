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

from datetime import datetime
import io
from koi_core.caching import cache, offlineFeature
from koi_core.resources.ids import InstanceId, ModelId
import os
import sys
from koi_core.code_import import KoiCodeLoader
from typing import Any, Iterable, List, TYPE_CHECKING
from uuid import uuid4
import zipfile

if TYPE_CHECKING:
    from koi_core.resources.pool import LocalOnlyObjectPool, APIObjectPool
    from koi_core.resources.instance import Instance


class Code:
    def contains(self, sub_path):
        ...

    def read(self, sub_path) -> bytes:
        ...

    def namelist(self):
        ...

    def load(self, instance, temp_dir):
        loader = KoiCodeLoader(self, instance.parameter, temp_dir)
        sys.meta_path.insert(0, loader)
        import user_code as model  # type: ignore

        if hasattr(model, "set_asset_dir"):
            model.set_asset_dir(temp_dir)
        return model

    def toBytes(self):
        ...


class LocalCode(Code):
    def __init__(self, path):
        self._path = path

    def gen_namelist(self):
        for root, _, files in os.walk(self._path):
            for file in files:
                path = os.path.join(root, file)
                common_path = os.path.commonpath([self._path, path])
                rel_root = os.path.relpath(root, common_path)
                if rel_root != ".":
                    file = os.path.join(rel_root, file)
                yield file

    def contains(self, sub_path):
        return os.path.exists(self.build_path(sub_path))

    def build_path(self, sub_path):
        return os.path.join(self._path, sub_path)

    def read(self, sub_path):
        f = open(os.path.join(self._path, sub_path), "rb")
        return f.read()

    def toBytes(self):
        file_like_object = io.BytesIO()
        zipf = zipfile.ZipFile(file_like_object, "w", zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(self._path):
            for file in files:
                filename = os.path.join(root, file)
                zipf.write(filename, arcname=os.path.relpath(filename, self._path))
        zipf.close()
        return file_like_object.getvalue()


class RemoteCode(Code):
    def __init__(self, data: bytes):
        file = io.BytesIO(data)
        self._archive = zipfile.ZipFile(file, mode="r")
        self._namelist = self._archive.namelist()
        self._data = data

    def gen_namelist(self):
        for name in self._namelist:
            yield os.path.normpath(name)

    def contains(self, sub_path):
        return sub_path in self.namelist()

    def build_path(self, sub_path):
        return sub_path

    def read(self, path):
        path_comps = []
        head, tail = os.path.split(path)
        path_comps.append(tail)
        while head != "":
            head, tail = os.path.split(head)
            path_comps.append(tail)

        path_comps.reverse()

        zipPath = ""
        for comp in path_comps:
            zipPath = zipPath + comp + "/"
        zipPath = zipPath[:-1]

        return self._archive.read(zipPath)

    def toBytes(self):
        return self._data


class Model:
    name: str
    description: str
    finalized: bool
    code: Code
    visual_plugin: Any
    request_plugin: Any
    instances: Iterable["Instance"]

    def new_instance(self) -> "Instance":
        ...


class LocalModel(Model):
    _instance_ids: List[InstanceId] = list()

    @property
    def instances(self) -> Iterable["Instance"]:
        return (self.pool.instance(i) for i in self._instance_ids)

    def __init__(self, pool: "LocalOnlyObjectPool", id: ModelId = None) -> None:
        self.pool = pool
        if id is None:
            id = ModelId(uuid4())
        self.id = id

        self.name = ""
        self.description = ""
        self.finalized = False
        self.code = None
        self.visual_plugin = None
        self.request_plugin = None

    def new_instance(self) -> "Instance":
        instance = self.pool.new_instance(self.id)
        self._instance_ids.append(instance.id)
        return instance


class ModelBasicFields:
    name: str
    description: str
    finalized: bool
    last_modified: datetime


class ModelProxy(Model):
    @property
    @cache
    @offlineFeature
    def _basic_fields(self, meta) -> ModelBasicFields:
        return self.pool.api.models.get_model(self.id, meta)

    @_basic_fields.setter
    def _basic_fields(self, value: ModelBasicFields) -> None:
        return self.pool.api.models.update_model(self.id, value)

    def __getattr__(self, name: str) -> Any:
        if name in ModelBasicFields.__annotations__:
            return self._basic_fields.__getattribute__(name)
        if name == "cachingStrategy":
            return self.pool.cachingStrategy
        return self.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ModelBasicFields.__annotations__:
            fields = self._basic_fields
            setattr(fields, name, value)
            self._basic_fields = fields
        super.__setattr__(self, name, value)

    @property
    @cache
    @offlineFeature
    def _code(self, meta) -> bytes:
        return self.pool.api.models.get_model_code(self.id, meta)

    @property
    @cache
    def code(self, meta) -> Code:
        return RemoteCode(self._code), meta

    @code.setter
    def code(self, value: Code) -> None:
        self.pool.api.models.set_model_code(self.id, value.toBytes())

    @property
    @cache
    @offlineFeature
    def request_plugin(self, meta) -> Any:
        return self.pool.api.models.get_model_request_plugin(self.id, meta)

    @request_plugin.setter
    def request_plugin(self, value: Any) -> None:
        self.pool.api.models.set_model_request_plugin(self.id, value)

    @property
    @cache
    @offlineFeature
    def visual_plugin(self, meta) -> Any:
        return self.pool.api.models.get_model_visual_plugin(self.id, meta)

    @visual_plugin.setter
    def visual_plugin(self, value: Any) -> None:
        self.pool.api.models.set_model_visual_plugin(self.id, value)

    @property
    @cache
    def _instance_ids(self, meta) -> List[InstanceId]:
        return self.pool.api.instances.get_instances(self.id, meta)

    @property
    def instances(self) -> Iterable["Instance"]:
        return (self.pool.instance(i) for i in self._instance_ids)

    @property
    @cache
    @offlineFeature
    def parameters(self, meta) -> Iterable[dict]:
        return self.pool.api.models.get_model_parameters(self.id, meta)

    def __init__(self, pool: "APIObjectPool", id: ModelId = None) -> None:
        self.pool = pool
        if id is None:
            id, _ = pool.api.models.new_model()
        self.id = id

    def new_instance(self) -> "Instance":
        instance = self.pool.new_instance(self.id)
        return instance
