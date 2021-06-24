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
from typing import Iterable, Tuple

from .common import BaseAPI, _parse, _encode
from koi_core.caching import CachingMeta
from koi_core.resources.ids import ModelId, InstanceId, DescriptorId

from koi_core.resources.instance import InstanceBasicFields, DescriptorBasicFields


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


class APIInstances(BaseAPI):
    def get_instances(self, id: ModelId):
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
            if new_meta != meta:
                return _parse_instance(self._GET(path))
            else:
                return None, new_meta

    def update_instance(self, id: InstanceId, update: InstanceBasicFields):
        self._PUT(self._build_path(id), data=_encode_instance(update))

    def get_instance_inference_data(self, id: InstanceId, meta: CachingMeta = None):
        path = self._build_path(id) + "/inference"
        return self.GET_RAW(path, meta)

    def set_instance_inference_data(self, id: InstanceId, data: bytes):
        self._POST_raw(self._build_path(id) + "/inference", data=data)

    def get_instance_training_data(self, id: InstanceId, meta: CachingMeta):
        path = self._build_path(id) + "/training"
        return self.GET_RAW(path, meta)

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
        path = self._build_path(id)
        if meta is None:
            return _parse_instance_descriptor(self._GET(path))
        else:
            new_meta = self._HEAD(path)
            if new_meta != meta:
                return _parse_instance_descriptor(self._GET(path))
            else:
                return None, new_meta

    def update_descriptor(self, id: DescriptorId, update: DescriptorBasicFields):
        self._PUT(self._build_path(id), data=_encode_instance_descriptor(update))

    def get_descriptor_data(self, id: DescriptorId, meta: CachingMeta = None):
        path = self._build_path(id) + "/file"
        return self.GET_RAW(path, meta)

    def set_descriptor_data(self, id: DescriptorId, data: bytes):
        self._POST_raw(self._build_path(id) + "/file", data=data)

    def get_parameters(self, id: InstanceId, meta: CachingMeta = None):
        path = self._build_path(id) + "/parameter"
        return self.GET(path, meta)

    def update_parameter(self, id: InstanceId, parameter):
        path = self._build_path(id) + "/parameter"
        self._POST(path, data=parameter)

    def merge_instances(self, id: InstanceId, merge: Iterable):
        path = self._build_path(id) + "/merge"

        json_object = {"instance_uuid": [merge_instance.id.instance_uuid.hex for merge_instance in merge]}

        self._POST(path, data=json_object)
