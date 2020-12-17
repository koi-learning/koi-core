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

from koi_core.caching import cache
from koi_core.resources.ids import InstanceId, SampleDatumId, SampleId
from koi_core.resources.sample_instance_util import (
    SampleDataAccessor,
    SampleLabelsAccessor,
    SampleTagAccessor,
)

from uuid import UUID, uuid4
from typing import Any, Iterable, List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from koi_core.resources.pool import LocalOnlyObjectPool, APIObjectPool
    from koi_core.resources.instance import Instance


class SampleDatum:
    key: str
    raw: bytes


class SampleLabel:
    key: str
    raw: bytes


class SampleDatumBasicFields:
    key: str


class Sample:
    id: SampleId
    finalized: bool
    instance: "Instance"

    def request_label(self) -> None:
        ...


class LocalSample(Sample):
    _data: List[SampleDatum]
    _labels: List[SampleLabel]

    @property
    def instance(self) -> "Instance":
        return self.pool.instance(id.InstanceId)

    @property
    def uuid(self) -> UUID:
        return self.id.sample_uuid

    def __init__(
        self, pool: "LocalOnlyObjectPool", id: Union[SampleId, InstanceId]
    ) -> None:
        self.pool = pool
        if not isinstance(id, SampleId):
            id = SampleId(id.model_uuid, id.instance_uuid, uuid4())
        self.id = id
        self._data = list()
        self._labels = list()
        self._tags = list()
        self.data = SampleDataAccessor(self)
        self.labels = SampleLabelsAccessor(self)
        self.tags = SampleTagAccessor(self)
        self.finalized = False

    def _get_data(self) -> Iterable[SampleDatum]:
        return self._data

    def _new_datum(self, key: str, raw: Any) -> None:
        datum = SampleDatum()
        datum.key = key
        datum.raw = raw
        self._data.append(datum)

    def _get_labels(self) -> Iterable[SampleDatum]:
        return self._labels

    def _new_label(self, key: str, raw: Any) -> None:
        datum = SampleLabel()
        datum.key = key
        datum.raw = raw
        self._labels.append(datum)

    def _add_tag(self, tag) -> None:
        self._tags.add(tag)

    def _remove_tag(self, tag) -> None:
        self._tags.discard(tag)

    def request_label(self) -> None:
        print("Label Request")


class SampleBasicFields:
    finalized: bool


class SampleDatumProxy(SampleDatum):
    @property
    @cache
    def _basic_fields(self, meta) -> SampleDatumBasicFields:
        return self.pool.api.get_sample_datum(self.id, meta)

    @_basic_fields.setter
    def _basic_fields(self, value: SampleDatumBasicFields) -> None:
        return self.pool.api.update_sample_datum(self.id, value)

    def __getattr__(self, name: str) -> Any:
        if name in SampleDatumBasicFields.__annotations__:
            return self._basic_fields.__getattribute__(name)
        if name == "cachingStrategy":
            return self.pool.cachingStrategy
        return self.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in SampleDatumBasicFields.__annotations__:
            fields = self._basic_fields
            setattr(fields, name, value)
            self._basic_fields = fields
        super.__setattr__(self, name, value)

    @property
    @cache
    def raw(self, meta) -> bytes:
        return self.pool.api.get_sample_datum_file(self.id, meta)

    @raw.setter
    def raw(self, value: bytes):
        self.pool.api.set_sample_datum_file(self.id, value)

    def __init__(self, pool: "APIObjectPool", id: SampleDatumId) -> None:
        self.pool = pool
        self.id = id


class SampleLabelProxy(SampleLabel):
    @property
    @cache
    def _basic_fields(self, meta) -> SampleDatumBasicFields:
        return self.pool.api.get_sample_label(self.id, meta)

    @_basic_fields.setter
    def _basic_fields(self, value: SampleDatumBasicFields) -> None:
        return self.pool.api.update_sample_label(self.id, value)

    def __getattr__(self, name: str) -> Any:
        if name in SampleDatumBasicFields.__annotations__:
            return self._basic_fields.__getattribute__(name)
        if name == "cachingStrategy":
            return self.pool.cachingStrategy
        return self.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in SampleDatumBasicFields.__annotations__:
            fields = self._basic_fields
            setattr(fields, name, value)
            self._basic_fields = fields
        super.__setattr__(self, name, value)

    @property
    @cache
    def raw(self, meta) -> bytes:
        return self.pool.api.get_sample_label_file(self.id, meta)

    @raw.setter
    def raw(self, value: bytes):
        self.pool.api.set_sample_label_file(self.id, value)

    def __init__(self, pool: "APIObjectPool", id: SampleDatumId) -> None:
        self.pool = pool
        self.id = id


class SampleProxy(Sample):
    @property
    @cache
    def _basic_fields(self, meta) -> SampleBasicFields:
        return self.pool.api.get_sample(self.id, meta)

    @_basic_fields.setter
    def _basic_fields(self, value: SampleBasicFields) -> None:
        return self.pool.api.update_sample(self.id, value)

    @property
    @cache
    def _tags(self, meta):
        return self.pool.api.get_tags(self.id, meta)

    def __getattr__(self, name: str) -> Any:
        if name in SampleBasicFields.__annotations__:
            return self._basic_fields.__getattribute__(name)
        if name == "cachingStrategy":
            return self.pool.cachingStrategy
        return self.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in SampleBasicFields.__annotations__:
            fields = self._basic_fields
            setattr(fields, name, value)
            self._basic_fields = fields
        super.__setattr__(self, name, value)

    def __init__(self, pool: "APIObjectPool", id: Union[SampleId, InstanceId]) -> None:
        self.pool = pool
        if not isinstance(id, SampleId):
            id, _ = pool.api.new_sample(id)
        self.id = id
        self.data = SampleDataAccessor(self)
        self.labels = SampleLabelsAccessor(self)
        self.tags = SampleTagAccessor(self)

    @property
    @cache
    def __get_data(self, meta) -> List[SampleDatumId]:
        return self.pool.api.get_sample_data(self.id)

    def _get_data(self, meta) -> Iterable[SampleDatum]:
        return [SampleDatumProxy(self.pool, d) for d in self.__get_data]

    def _new_datum(self, key: str, raw: Any) -> None:
        datumId, _ = self.pool.api.new_sample_datum(self.id)
        datum = SampleDatumProxy(self.pool, datumId)
        datum.key = key
        datum.raw = raw

    @property
    @cache
    def __get_labels(self, meta) -> List[SampleLabel]:
        return self.pool.api.get_sample_labels(self.id)

    @cache
    def _get_labels(self) -> Iterable[SampleLabel]:
        return [SampleLabelProxy(self.pool, d) for d in self.__get_labels]

    def _new_label(self, key: str, raw: Any) -> None:
        labelId, _ = self.pool.api.new_sample_label(self.id)
        label = SampleLabelProxy(self.pool, labelId)
        label.key = key
        label.raw = raw

    def _add_tag(self, tag) -> None:
        self.pool.api.add_tag(self.id, tag)

    def _remove_tag(self, tag) -> None:
        self.pool.api.remove_tag(self.id, tag)

    def request_label(self) -> None:
        self.pool.api.request_label(self.id)
