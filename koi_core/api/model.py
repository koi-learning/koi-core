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
from typing import Tuple

from .common import BaseAPI, _parse, _encode
from koi_core.caching import CachingMeta
from koi_core.resources.ids import ModelId

from koi_core.resources.model import ModelBasicFields


_model_mapping = {
    "name": "model_name",
    "description": "model_description",
    "finalized": "finalized",
}


def _parse_model(response) -> Tuple[ModelBasicFields, CachingMeta]:
    return _parse(response, ModelBasicFields, _model_mapping)


def _encode_model(model: ModelBasicFields):
    return _encode(model, ModelBasicFields, _model_mapping)


class APIModels:
    def __init__(self, base: BaseAPI):
        self.base = base

    def get_models(self, meta: CachingMeta = None):
        data, meta = self.base._GET("/api/model")
        return (
            [ModelId(model_uuid=UUID(d["model_uuid"])) for d in data],
            meta,
        )

    def new_model(self):
        data, meta = self.base._POST("/api/model", data={})
        return (
            ModelId(model_uuid=UUID(data["model_uuid"])),
            meta,
        )

    def get_model(self, id: ModelId, meta: CachingMeta = None):
        path = self.base._build_path(id)
        return _parse_model(self.base.GET(path, meta))

    def update_model(self, id: ModelId, update: ModelBasicFields):
        self.base._PUT(self.base._build_path(id), data=_encode_model(update))

    def get_model_code(self, id: ModelId, meta: CachingMeta = None):
        path = self.base._build_path(id) + "/code"
        return self.base.GET_RAW(path, meta)

    def set_model_code(self, id: ModelId, data: bytes) -> None:
        self.base._POST_raw(self.base._build_path(id) + "/code", data=data)

    def get_model_visual_plugin(self, id: ModelId, meta: CachingMeta = None):
        path = self.base._build_path(id) + "/visualplugin"
        return self.base.GET_RAW(path, meta)

    def set_model_visual_plugin(self, id: ModelId, data: bytes) -> None:
        self.base._POST_raw(self.base._build_path(id) + "/visualplugin", data=data)

    def get_model_request_plugin(self, id: ModelId, meta: CachingMeta = None):
        path = self.base._build_path(id) + "/requestplugin"
        return self.base.GET_RAW(path, meta)

    def set_model_request_plugin(self, id: ModelId, data: bytes) -> None:
        self.base._POST_raw(self.base._build_path(id) + "/requestplugin", data=data)

    def get_model_parameters(self, id: ModelId, meta: CachingMeta):
        path = self.base._build_path(id) + "/parameter"
        return self.base.GET(path, meta)
