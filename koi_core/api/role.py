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
from koi_core.caching import CachingMeta
from koi_core.api.common import BaseAPI, _parse, _encode
from koi_core.resources.ids import GeneralRoleId, ModelRoleId, InstanceRoleId
from koi_core.resources.role import GeneralRoleBasicFields, ModelRoleBasicFields, InstanceRoleBasicFields


_general_role_mapping = {
    "name": "role_name",
    "description": "role_description",
    "grant_access": "grant_access",
    "edit_users": "edit_users",
    "edit_modes": "edit_models",
    "edit_roles": "edit_roles",
}


def _parse_general_role(response):
    return _parse(response, GeneralRoleBasicFields, _general_role_mapping)


def _encode_general_role(role):
    return _encode(role, GeneralRoleBasicFields, _general_role_mapping)


_model_role_mapping = {
    "name": "role_name",
    "description": "role_description",
    "see_model": "can_see_model",
    "instantiate_model": "instantiate_model",
    "edit_model": "edit_model",
    "download_code": "download_model",
    "grant_access": "grant_access_model",
}


def _parse_model_role(response):
    return _parse(response, ModelRoleBasicFields, _model_role_mapping)


def _encode_model_role(role):
    return _encode(role, ModelRoleBasicFields, _model_role_mapping)


_instance_role_mapping = {
    "name": "role_name",
    "description": "role_description",
    "see_instance": "can_see_instance",
    "add_sample": "add_sample",
    "get_training_data": "get_training_data",
    "get_inference_data": "get_inference_data",
    "edit_instance": "edit_instance",
    "grant_access": "grant_access_instance",
    "request_label": "request_labels",
    "response_label": "response_labels",
}


def _parse_instance_role(response):
    return _parse(response, InstanceRoleBasicFields, _instance_role_mapping)


def _encode_instance_role(role):
    return _encode(role, InstanceRoleBasicFields, _instance_role_mapping)


class APIRoles:
    def __init__(self, base: BaseAPI):
        self.base = base

    def new_general_role():
        pass

    def new_model_role():
        pass

    def new_instance_role():
        pass

    def get_general_roles(self, meta: CachingMeta = None):
        path = self.base._build_path() + "/userroles/general"
        roles, meta = self.base.GET_paged(path)
        return ([GeneralRoleId(role_uuid=UUID(r["role_uuid"])) for r in roles], meta)

    def get_model_roles(self, meta: CachingMeta = None):
        path = self.base._build_path() + "/userroles/model"
        roles, meta = self.base.GET_paged(path)
        return ([ModelRoleId(role_uuid=UUID(r["role_uuid"])) for r in roles], meta)

    def get_instance_roles(self, meta: CachingMeta = None):
        path = self.base._build_path() + "/userroles/instance"
        roles, meta = self.base.GET_paged(path)
        return ([InstanceRoleId(role_uuid=UUID(r["role_uuid"])) for r in roles], meta)

    def get_general_role(self, id: GeneralRoleId, meta: CachingMeta = None):
        path = self.base._build_path(id)
        return _parse_general_role(self.base.GET(path, meta))

    def get_model_role(self, id: ModelRoleId, meta: CachingMeta = None):
        path = self.base._build_path(id)
        return _parse_model_role(self.base.GET(path, meta))

    def get_instance_role(self, id: InstanceRoleId, meta: CachingMeta = None):
        path = self.base._build_path(id)
        return _parse_instance_role(self.base.GET(path, meta))

    def update_general_role(self, id: GeneralRoleId, role: GeneralRoleBasicFields):
        path = self.base._build_path(id)
        self.base.PUT(path, _encode_general_role(role))

    def update_model_role(self, id: ModelRoleId, role: ModelRoleBasicFields):
        path = self.base._build_path(id)
        self.base.PUT(path, _encode_model_role(role))

    def update_instance_role(self, id: InstanceRoleId, role: InstanceRoleBasicFields):
        path = self.base._build_path(id)
        self.base.PUT(path, _encode_instance_role(role))
