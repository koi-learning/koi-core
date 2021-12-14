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

from koi_core.resources.ids import GeneralRoleId, ModelRoleId, InstanceRoleId, InstanceId, ModelId, SampleId, UserId
from koi_core.caching import cache, indexedCache, offlineFeature, setIndexedCache
from koi_core.caching_strategy import ExpireCachingStrategy, LocalOnlyCachingStrategy

from typing import Iterable

from koi_core.resources.instance import Instance, InstanceProxy, LocalInstance
from koi_core.resources.model import LocalModel, Model, ModelProxy
from koi_core.resources.sample import LocalSample, Sample, SampleProxy
from koi_core.resources.user import User, UserProxy
from koi_core.resources.role import GeneralRole, ModelRole, InstanceRole, GeneralRoleProxy, ModelRoleProxy, InstanceRoleProxy
from koi_core.api import API


class LocalOnlyObjectPool:
    cachingStrategy = LocalOnlyCachingStrategy()

    def get_all_models(self) -> Iterable[Model]:
        models, _ = self.api.get_models()
        return (self.model(id) for id in models)

    @indexedCache
    def model(self, id: ModelId, meta) -> Model:
        return LocalModel(self, id), meta

    def new_model(self) -> Model:
        model = LocalModel(self)
        setIndexedCache(self, "model", model.id, model)
        return model

    @indexedCache
    def instance(self, id: InstanceId, meta) -> Instance:
        return LocalInstance(self, id), meta

    def new_instance(self, id: ModelId) -> Instance:
        instance = LocalInstance(self, id)
        setIndexedCache(self, "instance", instance.id, instance)
        return instance

    @indexedCache
    def sample(self, id: SampleId) -> Sample:
        return LocalSample(self, id)

    def new_sample(self, id: InstanceId) -> Sample:
        sample = LocalSample(self, id)
        setIndexedCache(self, "sample", sample.id, sample)
        return sample


class APIObjectPool:
    cachingStrategy = ExpireCachingStrategy()
    api: API

    @property
    def id(self):
        return hash("APIObjectPool" + self.api._base_url)

    def __init__(self, api: API) -> None:
        self.api = api

    @cache
    @offlineFeature
    def _get_models(self, meta):
        return self.api.models.get_models(meta)

    def get_all_models(self) -> Iterable[Model]:
        models = self._get_models()
        return (self.model(id) for id in models)

    @cache
    def _get_users(self, meta):
        return self.api.users.get_users(meta)

    def get_all_users(self) -> Iterable[User]:
        users = self._get_users()
        return (self.user(id) for id in users)

    @cache
    def _get_general_roles(self, meta):
        return self.api.roles.get_general_roles(meta)

    def get_all_general_roles(self) -> Iterable[GeneralRole]:
        roles = self._get_general_roles()
        return (self.generalrole(id) for id in roles)

    @cache
    def _get_model_roles(self, meta):
        return self.api.roles.get_model_roles(meta)

    def get_all_model_roles(self) -> Iterable[ModelRole]:
        roles = self._get_model_roles()
        return (self.modelrole(id) for id in roles)

    @cache
    def _get_instance_roles(self, meta):
        return self.api.roles.get_instance_roles(meta)

    def get_all_instance_roles(self) -> Iterable[InstanceRole]:
        roles = self._get_instance_roles()
        return (self.instancerole(id) for id in roles)

    @indexedCache
    def generalrole(self, id: GeneralRoleId, meta) -> GeneralRole:
        return GeneralRoleProxy(self, id), meta

    @indexedCache
    def modelrole(self, id: ModelRoleId, meta) -> ModelRole:
        return ModelRoleProxy(self, id), meta

    @indexedCache
    def instancerole(self, id: InstanceRoleId, meta) -> InstanceRole:
        return InstanceRoleProxy(self, id), meta

    @indexedCache
    def user(self, id: UserId, meta) -> User:
        return UserProxy(self, id), meta

    @indexedCache
    def model(self, id: ModelId, meta) -> Model:
        return ModelProxy(self, id), meta

    def new_model(self) -> Model:
        model = ModelProxy(self)
        setIndexedCache(self, "model", model.id, model)
        return model

    @indexedCache
    def instance(self, id: InstanceId, meta) -> Instance:
        return InstanceProxy(self, id), meta

    def new_instance(self, id: ModelId) -> Instance:
        instance = InstanceProxy(self, id)
        setIndexedCache(self, "instance", instance.id, instance)
        return instance

    @indexedCache
    def sample(self, id: SampleId, meta) -> Sample:
        return SampleProxy(self, id), meta

    def new_sample(self, id: InstanceId) -> Sample:
        sample = SampleProxy(self, id)
        setIndexedCache(self, "sample", sample.id, sample)
        return sample
