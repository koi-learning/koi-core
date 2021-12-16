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
from uuid import UUID
from typing import Any, TYPE_CHECKING, Union
from koi_core.resources.model import Model
from koi_core.resources.instance import Instance
from koi_core.resources.role import GeneralRole, ModelRole, InstanceRole
from koi_core.resources.ids import UserId, BaseRoleId
from koi_core.caching import cache


if TYPE_CHECKING:
    from koi_core.resources.pool import APIObjectPool


class User:
    id: UserId
    name: str
    password: str
    essential: bool
    created: datetime


class UserBasicFields:
    name: str
    essential: bool
    created: datetime


class LocalUser(User):
    pass


class UserProxy(User):
    @property
    @cache
    def _basic_fields(self, meta) -> UserBasicFields:
        return self.pool.api.users.get_user(self.id, meta)

    @_basic_fields.setter
    def _basic_fields(self, value: UserBasicFields) -> None:
        return self.pool.api.users.update_user(self.id, value)

    def __getattr__(self, name: str) -> Any:
        if name in UserBasicFields.__annotations__:
            return self._basic_fields.__getattribute__(name)
        if name == "cachingStrategy":
            return self.pool.cachingStrategy
        return self.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in UserBasicFields.__annotations__:
            fields = self._basic_fields
            setattr(fields, name, value)
            self._basic_fields = fields
        super.__setattr__(self, name, value)

    def __init__(self, pool: "APIObjectPool", id: UserId) -> None:
        self.pool = pool
        if not isinstance(id, UserId):
            id, _ = pool.api.users.new_user(id)
        self.id = id

    @property
    def password(self) -> str:
        return ""

    @password.setter
    def password(self, value: str) -> None:
        self.pool.api.users.update_user(self.id, value)

    def grant_access(self, role: Union[GeneralRole, ModelRole, InstanceRole], object: Union[Model, Instance]=None) -> None:
        if object is None and isinstance(role, GeneralRole):
            self.pool.api.access.grant_general_access(self.id, role.id)
        else:
            if isinstance(object, Model) and isinstance(role, ModelRole):
                self.pool.api.access.grant_model_access(self.id, role.id, object.id)
            elif isinstance(object, Instance) and isinstance(role, InstanceRole):
                self.pool.api.access.grant_instance_access(self.id, role.id, object.id)
            else:
                raise ValueError("Unknown object type or role/object mismatch")

    def revoke_access(self, role: Union[GeneralRole, ModelRole, InstanceRole], object: Union[Model, Instance]=None) -> None:
        if object is None and isinstance(role, GeneralRole):
            self.pool.api.access.revoke_general_access(self.id, role.id)
        else:
            if isinstance(object, Model) and isinstance(role, ModelRole):
                self.pool.api.access.revoke_model_access(self.id, role.id, object.id)
            elif isinstance(object, Instance) and isinstance(role, InstanceRole):
                self.pool.api.access.revoke_instance_access(self.id, role.id, object.id)
            else:
                raise ValueError("Unknown object type or role/object mismatch")

    def has_role(self, role: Union[GeneralRole, ModelRole, InstanceRole], object: Union[Model, Instance] = None) -> bool:
        collection = []
        if object is None:
            collection, _ = self.pool.api.access._get_general_access_collection()
        else:
            if isinstance(object, Model):
                collection = self.pool.api.access._get_model_access_collection(object.id)
            elif isinstance(object, Instance):
                collection = self.pool.api.access._get_instance_access_collection(object.id)
            else:
                raise ValueError("Unknown object type")

        for access in collection:
            if BaseRoleId(role_uuid=UUID(access["role_uuid"])) == role.id:
                return True

        return False
