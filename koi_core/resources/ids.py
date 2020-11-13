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


class ModelId:
    model_uuid: UUID

    def __init__(self, model_uuid: UUID = None, id=None) -> None:
        self.model_uuid = model_uuid if model_uuid else id.model_uuid

    def __hash__(self):
        return hash(self.model_uuid)

    def __eq__(self, other):
        return self.model_uuid == other.model_uuid


class InstanceId(ModelId):
    instance_uuid: UUID

    def __init__(
        self, model_uuid: UUID = None, instance_uuid: UUID = None, id=None
    ) -> None:
        self.model_uuid = model_uuid if model_uuid else id.model_uuid
        self.instance_uuid = instance_uuid if instance_uuid else id.instance_uuid

    def __hash__(self):
        return hash(self.instance_uuid)

    def __eq__(self, other):
        return self.instance_uuid == other.instance_uuid

    @property
    def ModelId(self) -> ModelId:
        return ModelId(self)


class DescriptorId(InstanceId):
    descriptor_uuid: UUID

    def __init__(
        self,
        model_uuid: UUID = None,
        instance_uuid: UUID = None,
        descriptor_uuid: UUID = None,
        id=None,
    ) -> None:
        self.model_uuid = model_uuid if model_uuid else id.model_uuid
        self.instance_uuid = instance_uuid if instance_uuid else id.instance_uuid
        self.descriptor_uuid = descriptor_uuid if descriptor_uuid else id.descriptor_uuid

    def __hash__(self):
        return hash(self.descriptor_uuid)

    def __eq__(self, other):
        return self.descriptor_uuid == other.descriptor_uuid

    @property
    def InstanceId(self) -> InstanceId:
        return InstanceId(id=self)


class SampleId(InstanceId):
    sample_uuid: UUID

    def __init__(
        self,
        model_uuid: UUID = None,
        instance_uuid: UUID = None,
        sample_uuid: UUID = None,
        id=None,
    ) -> None:
        self.model_uuid = model_uuid if model_uuid else id.model_uuid
        self.instance_uuid = instance_uuid if instance_uuid else id.instance_uuid
        self.sample_uuid = sample_uuid if sample_uuid else id.sample_uuid

    def __hash__(self):
        return hash(self.sample_uuid)

    def __eq__(self, other):
        return self.sample_uuid == other.sample_uuid

    @property
    def InstanceId(self) -> InstanceId:
        return InstanceId(id=self)


class SampleDatumId(SampleId):
    sample_datum_uuid: UUID

    def __init__(
        self,
        model_uuid: UUID = None,
        instance_uuid: UUID = None,
        sample_uuid: UUID = None,
        sample_datum_uuid: UUID = None,
        id=None,
    ) -> None:
        self.model_uuid = model_uuid if model_uuid else id.model_uuid
        self.instance_uuid = instance_uuid if instance_uuid else id.instance_uuid
        self.sample_uuid = sample_uuid if sample_uuid else id.sample_uuid
        self.sample_datum_uuid = (
            sample_datum_uuid if sample_datum_uuid else id.sample_datum_uuid
        )

    def __hash__(self):
        return hash(self.sample_datum_uuid)

    def __eq__(self, other):
        return self.sample_datum_uuid == other.sample_datum_uuid

    @property
    def SampleId(self) -> SampleId:
        return SampleId(id=self)


class SampleLableId(SampleId):
    sample_label_uuid: UUID

    def __init__(
        self,
        model_uuid: UUID = None,
        instance_uuid: UUID = None,
        sample_uuid: UUID = None,
        sample_label_uuid: UUID = None,
        id=None,
    ) -> None:
        self.model_uuid = model_uuid if model_uuid else id.model_uuid
        self.instance_uuid = instance_uuid if instance_uuid else id.instance_uuid
        self.sample_uuid = sample_uuid if sample_uuid else id.sample_uuid
        self.sample_label_uuid = (
            sample_label_uuid if sample_label_uuid else id.sample_label_uuid
        )

    def __hash__(self):
        return hash(self.sample_label_uuid)

    def __eq__(self, other):
        return self.sample_label_uuid == other.sample_label_uuid

    @property
    def SampleId(self) -> SampleId:
        return SampleId(id=self)
