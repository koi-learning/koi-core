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

from koi_core.caching import cache, offlineFeature
from koi_core.resources.model import Model
from koi_core.resources.ids import InstanceId, ModelId, SampleId, DescriptorId
from koi_core.resources.sample_instance_util import InstanceDescriptorAccessor, InstanceParameterAccessor
from typing import Any, Dict, Iterable, List, TYPE_CHECKING, Union
from uuid import uuid4
from koi_core.resources.sample import Sample

if TYPE_CHECKING:
    from koi_core.resources.pool import LocalOnlyObjectPool, APIObjectPool


def _consumed_filter(s: Sample):
    return s.consumed and not s.obsolete


def _unconsumed_filter(s: Sample):
    return not s.consumed and not s.obsolete


class Descriptor:
    id: DescriptorId
    key: str
    raw: bytes


class DescriptorBasicFields:
    key: str


class LocalDescriptor:
    def __init__(
        self, pool: "LocalOnlyObjectPool", id: Union[DescriptorId, InstanceId, ModelId]
    ) -> None:
        self.pool = pool
        if not isinstance(id, DescriptorId):
            id = DescriptorId(id.model_uuid, id.instance_uuid, uuid4())
        self.id = id
        self.key = ""
        self.raw = b""


class DescriptorProxy(Descriptor):
    def __init__(
        self, pool: "APIObjectPool", id: Union[DescriptorId, InstanceId, ModelId]
    ) -> None:
        self.pool = pool
        if not isinstance(id, DescriptorId):
            id = DescriptorId(id.model_uuid, id.instance_uuid, uuid4())
        self.id = id

    @property
    @cache
    @offlineFeature
    def _basic_fields(self, meta) -> DescriptorBasicFields:
        return self.pool.api.instances.get_descriptor(self.id, meta)

    @_basic_fields.setter
    def _basic_fields(self, value: DescriptorBasicFields) -> None:
        return self.pool.api.instances.update_descriptor(self.id, value)

    def __getattr__(self, name: str) -> Any:
        if name in DescriptorBasicFields.__annotations__:
            return self._basic_fields.__getattribute__(name)
        if name == "cachingStrategy":
            return self.pool.cachingStrategy
        return self.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in DescriptorBasicFields.__annotations__:
            fields = self._basic_fields
            setattr(fields, name, value)
            self._basic_fields = fields
        super.__setattr__(self, name, value)

    @property
    @cache
    @offlineFeature
    def raw(self, meta) -> bytes:
        return self.pool.api.instances.get_descriptor_data(self.id, meta)

    @raw.setter
    def raw(self, value):
        self.pool.api.instances.set_descriptor_data(self.id, value)


class Instance:
    name: str
    description: str
    finalized: bool
    training_data: Any
    inference_data: Any
    parameter: Dict
    samples: List[Sample]
    samples_consumed: List[Sample]
    samples_unconsumed: List[Sample]
    descriptors: List[Descriptor]

    def new_sample(self) -> Sample:
        ...

    @property
    def model(self) -> "Model":
        return self.pool.model(ModelId(self.id.model_uuid))

    def load_code(self):
        return self.model.code.load(self)


class LocalInstance(Instance):
    _sample_ids: List[SampleId] = list()

    def get_samples(self, filter_include: list = None, filter_exclude: list = None):
        all_samples = [self.pool.sample(s) for s in self._sample_ids]

        if filter_include is None and filter_exclude is None:
            return all_samples
        else:
            if filter_include is None:
                return [
                    sample
                    for sample in all_samples
                    if not any((tag in filter_exclude for tag in sample._tags))
                ]

            if filter_exclude is None:
                return [
                    sample
                    for sample in all_samples
                    if any((tag in filter_include for tag in sample._tags))
                ]

            return [
                sample
                for sample in all_samples
                if any((tag in filter_include for tag in sample._tags))
                and not any((tag in filter_exclude for tag in sample._tags))
            ]

    def __init__(
        self, pool: "LocalOnlyObjectPool", id: Union[InstanceId, ModelId]
    ) -> None:
        self.pool = pool
        if not isinstance(id, InstanceId):
            id = InstanceId(id.model_uuid, uuid4())
        self.id = id
        self.name = ""
        self.description = ""
        self.finalized = False
        self.training_data = None
        self.inference_data = None
        self.parameter = dict()
        self._descriptors = list()
        self.descriptors = InstanceDescriptorAccessor(self)
        self.could_train = True

    def new_sample(self):
        sample = self.pool.new_sample(self.id)
        self._sample_ids.append(sample.id)
        return sample

    def _get_descriptors(self):
        return self._descriptors

    def _new_descriptor(self, key: str, raw: Any):
        local_desc = LocalDescriptor(self.pool, self.id)
        local_desc.key = key
        local_desc.raw = raw
        self._descriptors.append(local_desc)


class InstanceBasicFields:
    name: str
    description: str
    finalized: bool
    could_train: bool


class InstanceProxy(Instance):
    @property
    @cache
    @offlineFeature
    def _basic_fields(self, meta) -> InstanceBasicFields:
        return self.pool.api.instances.get_instance(self.id, meta)

    @_basic_fields.setter
    def _basic_fields(self, value: InstanceBasicFields) -> None:
        return self.pool.api.instances.update_instance(self.id, value)

    def __getattr__(self, name: str) -> Any:
        if name in InstanceBasicFields.__annotations__:
            return self._basic_fields.__getattribute__(name)
        if name == "cachingStrategy":
            return self.pool.cachingStrategy
        return self.__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in InstanceBasicFields.__annotations__:
            fields = self._basic_fields
            setattr(fields, name, value)
            self._basic_fields = fields
        super.__setattr__(self, name, value)

    @property
    @cache
    @offlineFeature
    def training_data(self, meta) -> bytes:
        t_dat = None
        new_meta = None
        try:
            t_dat, new_meta = self.pool.api.instances.get_instance_training_data(self.id, meta)
        except LookupError:
            t_dat = None
            new_meta = None
        return t_dat, new_meta

    @training_data.setter
    def training_data(self, value):
        self.pool.api.instances.set_instance_training_data(self.id, value)

    @property
    @cache
    def inference_data(self, meta) -> bytes:
        i_dat = None
        new_meta = None
        try:
            i_dat, new_meta = self.pool.api.instances.get_instance_inference_data(self.id, meta)
        except LookupError:
            i_dat = None
            new_meta = None
        return i_dat, new_meta

    @inference_data.setter
    def inference_data(self, value):
        self.pool.api.instances.set_instance_inference_data(self.id, value)

    def get_samples(self, filter_include: list = None, filter_exclude: list = None):
        data, _ = self.pool.api.samples.get_samples(self.id, filter_include, filter_exclude)
        return [self.pool.sample(id) for id in data]

    @property
    @cache
    @offlineFeature
    def __get_descriptors(self, meta) -> List[DescriptorId]:
        return self.pool.api.instances.get_descriptors(self.id)

    def _get_descriptors(self) -> Iterable[Descriptor]:
        return [DescriptorProxy(self.pool, d) for d in self.__get_descriptors]

    def _new_descriptor(self, key: str, raw: Any) -> None:
        descriptorId, _ = self.pool.api.instances.new_descriptor(self.id)
        descriptor = DescriptorProxy(self.pool, descriptorId)
        descriptor.key = key
        descriptor.raw = raw

    @cache
    @offlineFeature
    def _get_available_parameters(self, meta):
        return self.pool.api.models.get_model_parameters(ModelId(self.id.model_uuid), meta)

    @cache
    @offlineFeature
    def _get_parameter_values(self, meta):
        return self.pool.api.instances.get_parameters(self.id, meta)

    def _set_parameter_value(self, parameter):
        self.pool.api.instances.update_parameter(self.id, parameter)

    def __init__(self, pool: "APIObjectPool", id: Union[InstanceId, ModelId]) -> None:
        self.pool = pool
        if not isinstance(id, InstanceId):
            id, _ = pool.api.instances.new_instance(id)
        self.id = id

        self.descriptors = InstanceDescriptorAccessor(self)
        self.parameter = InstanceParameterAccessor(self)

    def new_sample(self):
        sample = self.pool.new_sample(self.id)
        return sample

    def merge(self, instances: Iterable):
        self.pool.api.instances.merge_instances(self.id, instances)
