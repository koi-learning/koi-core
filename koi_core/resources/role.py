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

from typing import Any, TYPE_CHECKING
from koi_core.resources.ids import GeneralRoleId, ModelRoleId, InstanceRoleId
from koi_core.caching import cache


if TYPE_CHECKING:
    from koi_core.resources.pool import APIObjectPool


class GeneralRole:
    name: str
    description: str
    grant_access: bool
    edit_users: bool
    edit_modes: bool
    edit_roles: bool


class GeneralRoleBasicFields:
    name: str
    description: str
    grant_access: bool
    edit_users: bool
    edit_modes: bool
    edit_roles: bool


class GeneralRoleProxy(GeneralRole):
    @property
    @cache
    def _basic_fields(self, meta) -> GeneralRoleBasicFields:
        return self.pool.api.roles.get_role(self.id, meta)

    @_basic_fields.setter
    def _basic_fields(self, value: GeneralRoleBasicFields):
        self.pool.api.roles.update_role(self.id, value)

    def __getattr__(self, name: str) -> Any:
        if name in GeneralRoleBasicFields.__annotations__:
            return self._basic_fields.__getattribute__(name)
        if name == "cachingStrategy":
            return self.pool.cachingStrategy
        return self.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in GeneralRoleBasicFields.__annotations__:
            fields = self._basic_fields
            setattr(fields, name, value)
            self._basic_fields = fields
        super.__setattr__(self, name, value)

    def __init__(self, pool: "APIObjectPool", id: GeneralRoleId) -> None:
        self.pool = pool
        if not isinstance(id, GeneralRoleId):
            id, _ = pool.api.roles.new_general_role(id)
        self.id = id


class ModelRole:
    name: str
    description: str
    see_model: bool
    instantiate_model: bool
    edit_model: bool
    download_code: bool
    grant_access: bool


class ModelRoleBasicFields:
    name: str
    description: str
    see_model: bool
    instantiate_model: bool
    edit_model: bool
    download_code: bool
    grant_access: bool


class ModelRoleProxy(ModelRole):
    @property
    @cache
    def _basic_fields(self, meta) -> ModelRoleBasicFields:
        return self.pool.api.roles.get_role(self.id, meta)

    @_basic_fields.setter
    def _basic_fields(self, value: ModelRoleBasicFields):
        self.pool.api.roles.update_role(self.id, value)

    def __getattr__(self, name: str) -> Any:
        if name in ModelRoleBasicFields.__annotations__:
            return self._basic_fields.__getattribute__(name)
        if name == "cachingStrategy":
            return self.pool.cachingStrategy
        return self.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ModelRoleBasicFields.__annotations__:
            fields = self._basic_fields
            setattr(fields, name, value)
            self._basic_fields = fields
        super.__setattr__(self, name, value)

    def __init__(self, pool: "APIObjectPool", id: ModelRoleId) -> None:
        self.pool = pool
        if not isinstance(id, ModelRoleId):
            id, _ = pool.api.roles.new_model_role(id)
        self.id = id


class InstanceRole:
    name: str
    description: str
    see_instance: bool
    add_sample: bool
    get_training_data: bool
    get_inference_data: bool
    edit_instance: bool
    grant_access: bool
    request_label: bool
    response_label: bool


class InstanceRoleBasicFields:
    name: str
    description: str
    see_instance: bool
    add_sample: bool
    get_training_data: bool
    get_inference_data: bool
    edit_instance: bool
    grant_access: bool
    request_label: bool
    response_label: bool


class InstanceRoleProxy(InstanceRole):
    @property
    @cache
    def _basic_fields(self, meta) -> InstanceRoleBasicFields:
        return self.pool.api.roles.get_role(self.id, meta)

    @_basic_fields.setter
    def _basic_fields(self, value: InstanceRoleBasicFields):
        self.pool.api.roles.update_role(self.id, value)

    def __getattr__(self, name: str) -> Any:
        if name in InstanceRoleBasicFields.__annotations__:
            return self._basic_fields.__getattribute__(name)
        if name == "cachingStrategy":
            return self.pool.cachingStrategy
        return self.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in InstanceRoleBasicFields.__annotations__:
            fields = self._basic_fields
            setattr(fields, name, value)
            self._basic_fields = fields
        super.__setattr__(self, name, value)

    def __init__(self, pool: "APIObjectPool", id: InstanceRoleId) -> None:
        self.pool = pool
        if not isinstance(id, InstanceRoleId):
            id, _ = pool.api.roles.new_instance_role(id)
        self.id = id
