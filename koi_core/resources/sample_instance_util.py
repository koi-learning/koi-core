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

from typing import Any, Iterable, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from koi_core.resources.sample import SampleDatum, SampleLabel, Sample
    from koi_core.resources.instance import Instance, Descriptor


class NamedDataLabelAccessor:
    def __init__(self, key: str) -> None:
        self.key = key

    def _get_data() -> Iterable[Union['SampleDatum', 'SampleLabel', 'Descriptor']]:
        ...

    def _new_datum(key: str, raw: Any) -> None:
        ...

    def filter_fun(self, datum: Union['SampleDatum', 'SampleLabel', 'Descriptor']):
        return datum.key == self.key

    def __iter__(self) -> Union['SampleDatum', 'SampleLabel', 'Descriptor']:
        return filter(self.filter_fun, self._get_data())

    def append(self, raw: Any):
        self._new_datum(self.key, raw)

    @property
    def raw(self) -> bytes:
        iter = filter(self.filter_fun, self._get_data())
        try:
            datum = next(iter)
        except StopIteration:
            raise Exception('No datum with key found')
        # make sure that this is the only element:
        try:
            next(iter)
            raise Exception('There is more data with the key')
        except StopIteration:
            pass
        return datum.raw

    @raw.setter
    def raw(self, value):
        iter = filter(self.filter_fun, self._get_data())
        try:
            datum = next(iter)
        except StopIteration:
            self.append(value)
            return
        # make sure that this is the only element:
        try:
            next(iter)
            raise Exception('There is more data with the key')
        except StopIteration:
            pass
        datum.raw = value


class SampleDataAccessor:
    def __init__(self, sample: 'Sample') -> None:
        self.sample = sample

    def __getitem__(self, key: str):
        accessor = NamedDataLabelAccessor(key)
        accessor._get_data = self.sample._get_data
        accessor._new_datum = self.sample._new_datum
        return accessor


class SampleLabelsAccessor:
    def __init__(self, sample: 'Sample') -> None:
        self.sample = sample

    def __getitem__(self, key: str):
        accessor = NamedDataLabelAccessor(key)
        accessor._get_data = self.sample._get_labels
        accessor._new_datum = self.sample._new_label
        return accessor


class InstanceDescriptorAccessor:
    def __init__(self, instance: 'Instance') -> None:
        self.instance = instance

    def __getitem__(self, key: str):
        accessor = NamedDataLabelAccessor(key)
        accessor._get_data = self.instance._get_descriptors
        accessor._new_datum = self.instance._new_descriptor
        return accessor


class SampleTagAccessor:
    def __init__(self, sample: 'Sample') -> None:
        self.sample = sample

    def __len__(self):
        return len(self.sample._tags)

    def __contains__(self, item):
        return item in self.sample._tags

    def add(self, item):
        self.sample._add_tag(item)

    def discard(self, item):
        self.sample._remove_tag(item)

    def __str__(self):
        return self.sample._tags.__str__()
