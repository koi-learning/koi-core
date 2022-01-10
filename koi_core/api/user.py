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
from koi_core.resources.ids import UserId
from koi_core.resources.user import UserBasicFields


_user_mapping = {
    "name": "user_name",
    "essential": "user_essential",
    "created": "user_created",
}

_user_mapping_update = {
    "name": "user_name",
    "password": "user_password",
}


def _parse_user(response):
    return _parse(response, UserBasicFields, _user_mapping)


def _encode_user(user):
    return _encode(user, UserBasicFields, _user_mapping_update)


class APIUsers:
    def __init__(self, base: BaseAPI):
        self.base = base

    def new_user(self):
        pass

    def get_users(self, meta: CachingMeta = None):
        path = self.base._build_path() + "/user"
        users, meta = self.base.GET_paged(path)
        return ([UserId(user_uuid=UUID(u["user_uuid"])) for u in users], meta)

    def get_user(self, id: UserId, meta: CachingMeta = None):
        path = self.base._build_path(id)
        return _parse_user(self.base.GET(path, meta=meta))

    def update_user(self, user_id, update: UserBasicFields):
        self.base._PUT(self.base._build_path(user_id), data=_encode_user(update))

    def update_user_password(self, user_id, new_password: str):
        self.base._PUT(self.base._build_path(user_id), data={"user_password": new_password})
