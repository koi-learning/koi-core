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
from koi_core.resources.ids import InstanceId, SampleId, SampleDatumId, SampleLableId

from koi_core.resources.sample import SampleBasicFields, SampleDatumBasicFields


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


class APISamples:
    def __init__(self, base: BaseAPI):
        self.base = base

    def get_samples(
        self, id: InstanceId, filter_include: list = None, filter_exclude: list = None
    ):
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
            data_part, meta = self.base._GET(
                self.base._build_path(id) + "/sample",
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
        data, meta = self.base._POST(
            self.base._build_path(id) + "/sample",
            data={},
        )
        return (
            SampleId(id=id, sample_uuid=UUID(data["sample_uuid"])),
            meta,
        )

    def get_sample(self, id: SampleId, meta: CachingMeta = None):
        path = self.base._build_path(id)
        if meta is None:
            return _parse_sample(self.base._GET(path))
        else:
            new_meta = self.base._HEAD(path)
            if new_meta != meta:
                return _parse_sample(self.base._GET(path))
            else:
                return None, new_meta

    def update_sample(self, id: SampleId, update: SampleBasicFields):
        self.base._PUT(self.base._build_path(id), data=_encode_sample(update))

    def get_tags(self, id: SampleId, meta: CachingMeta = None):
        path = self.base._build_path(id) + "/tags"
        if meta is None:
            json_resp, new_meta = self.base._GET(path)
            return {obj["name"] for obj in json_resp}, new_meta
        else:
            new_meta = self.base._HEAD(path)
            if new_meta != meta:
                json_resp, new_meta = self.base._GET(path)
                return {obj["name"] for obj in json_resp}, new_meta
            else:
                return None, new_meta

    def update_tags(self, id: SampleId, update: set):
        new_tags = [{"name": x} for x in update]
        self.base._DELETE(self.base._build_path(id) + "/tags")
        self.base._PUT(self.base._build_path(id) + "/tags", data=new_tags)

    def add_tag(self, id: SampleId, item: str):
        self.base._PUT(
            self.base._build_path(id) + "/tags",
            data=[
                {"name": item},
            ],
        )

    def remove_tag(self, id: SampleId, item: str):
        self.base._DELETE(self.base._build_path(id) + "/tags/" + item)

    def request_label(self, id: SampleId):
        self.base._POST(
            self.base._build_path(id.InstanceId) + "/label_request",
            data={"sample_uuid": id.sample_uuid.hex},
        )

    # endregion

    # region sample_datum
    def get_sample_data(self, id: SampleId):
        data, meta = self.base._GET(self.base._build_path(id) + "/data")
        return (
            [
                SampleDatumId(id=id, sample_datum_uuid=UUID(d["data_uuid"]))
                for d in data
            ],
            meta,
        )

    def new_sample_datum(self, id: SampleId):
        data, meta = self.base._POST(
            self.base._build_path(id) + "/data",
            data={},
        )
        return (
            SampleDatumId(id=id, sample_datum_uuid=UUID(data["data_uuid"])),
            meta,
        )

    def get_sample_datum(self, id: SampleDatumId, meta: CachingMeta):
        path = self.base._build_path(id)
        if meta is None:
            return _parse_sample_datum(self.base._GET(path))
        else:
            new_meta = self.base._HEAD(path)
            if new_meta != meta:
                return _parse_sample_datum(self.base._GET(path))
            else:
                return None, new_meta

    def update_sample_datum(self, id: SampleDatumId, update: SampleDatumBasicFields):
        self.base._PUT(self.base._build_path(id), data=_encode_sample_datum(update))

    def get_sample_datum_file(self, id: SampleDatumId, meta: CachingMeta = None):
        path = self.base._build_path(id) + "/file"
        if meta is None:
            return self.base._GET_raw(path)
        else:
            new_meta = self.base._HEAD(path)
            if new_meta != meta:
                return self.base._GET_raw(path)
            else:
                return None, new_meta

    def set_sample_datum_file(self, id: SampleDatumId, data: bytes):
        self.base._POST_raw(self.base._build_path(id) + "/file", data=data)

    # endregion

    # region sample_label
    def get_sample_labels(self, id: SampleId):
        data, meta = self.base._GET(self.base._build_path(id) + "/label")
        return (
            [
                SampleLableId(id=id, sample_label_uuid=UUID(d["label_uuid"]))
                for d in data
            ],
            meta,
        )

    def new_sample_label(self, id: SampleId):
        response = self.base._POST(self.base._build_path(id) + "/label", data={})
        return (
            SampleLableId(id=id, sample_label_uuid=UUID(response[0]["label_uuid"])),
            response[1],
        )

    def get_sample_label(self, id: SampleLableId, meta: CachingMeta):
        path = self.base._build_path(id)
        if meta is None:
            return _parse_sample_datum(self.base._GET(path))
        else:
            new_meta = self.base._HEAD(path)
            if new_meta != meta:
                return _parse_sample_datum(self.base._GET(path))
            else:
                return None, new_meta

    def update_sample_label(self, id: SampleLableId, update: SampleDatumBasicFields):
        self.base._PUT(self.base._build_path(id), data=_encode_sample_datum(update))

    def get_sample_label_file(self, id: SampleLableId, meta: CachingMeta = None):
        path = self.base._build_path(id) + "/file"
        if meta is None:
            return self.base._GET_raw(path)
        else:
            new_meta = self.base._HEAD(path)
            if new_meta != meta:
                return self.base._GET_raw(path)
            else:
                return None, new_meta

    def set_sample_label_file(self, id: SampleLableId, data: bytes):
        self.base._POST_raw(self.base._build_path(id) + "/file", data=data)
