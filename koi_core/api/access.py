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

from uuid import UUID
from koi_core.api.common import BaseAPI
from koi_core.resources.ids import (
    GeneralAccessId,
    GeneralRoleId,
    ModelAccessId,
    ModelId,
    ModelRoleId,
    InstanceAccessId,
    InstanceRoleId,
    InstanceId,
    UserId,
)


class APIAccess:
    def __init__(self, base: BaseAPI):
        self.base = base

    def _get_general_access_collection(self):
        path = self.base._build_path() + "/access"
        access, meta = self.base.GET_paged(path)
        return access, meta

    def grant_general_access(self, user: UserId, role: GeneralRoleId):
        path = self.base._build_path() + "/access"
        self.base._POST(path, data={"user_uuid": user.user_uuid.hex, "role_uuid": role.role_uuid.hex})

    def revoke_general_access(self, user: UserId, role: GeneralRoleId):
        access_collection, _ = self._get_general_access_collection()

        access = next(
            filter(
                lambda x: UserId(user_uuid=UUID(x["user_uuid"])) == user and GeneralRoleId(role_uuid=UUID(x["role_uuid"])) == role,
                access_collection,
            ),
            None,
        )

        if access is not None:
            path = self.base._build_path(GeneralAccessId(access_uuid=UUID(access["access_uuid"])))
            self.base._DELETE(path)

    def _get_model_access_collection(self, model: ModelId):
        path = self.base._build_path(model) + "/access"
        access, meta = self.base.GET_paged(path)
        return access, meta

    def grant_model_access(self, user: UserId, role: ModelRoleId, model: ModelId):
        path = self.base._build_path(model) + "/access"
        self.base._POST(path, data={"user_uuid": user.user_uuid.hex, "role_uuid": role.role_uuid.hex})

    def revoke_model_access(self, user: UserId, role: ModelRoleId, model: ModelId):
        access_collection, _ = self._get_model_access_collection(model)

        access = next(
            filter(
                lambda x: UserId(user_uuid=x["user_uuid"]) == user and ModelRoleId(role_uuid=x["role_uuid"]) == role,
                access_collection,
            ),
            None,
        )

        if access is not None:
            path = self.base._build_path(ModelAccessId(role_uuid=access["access_uuid"]))
            self.base._DELETE(path)

    def _get_instance_access_collection(self, instance: UUID):
        path = self.base._build_path(instance) + "/access"
        access, meta = self.base.GET_paged(path)
        return access, meta

    def grant_instance_access(self, user: UserId, role: InstanceRoleId, instance: InstanceId):
        path = self.base._build_path(instance) + "/access"
        self.base._POST(path, data={"user_uuid": user.user_uuid.hex, "role_uuid": role.role_uuid.hex})

    def revoke_instance_access(self, user: UserId, role: InstanceRoleId, instance: InstanceId):
        access_collection, _ = self._get_instance_access_collection(instance)

        access = next(
            filter(
                lambda x: UserId(user_uuid=x["user_uuid"]) == user and InstanceRoleId(role_uuid=x["role_uuid"]) == role,
                access_collection,
            ),
            None,
        )

        if access is not None:
            path = self.base._build_path(InstanceAccessId(role_uuid=access["access_uuid"]))
            self.base._DELETE(path)
