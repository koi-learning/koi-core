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

import io
from koi_core.caching_strategy import ExpireCachingStrategy
import os
from koi_core.resources.instance import Instance
import uuid
from koi_core.resources.ids import InstanceId
from koi_core.exceptions import KoiApiOfflineException
import koi_core
import pytest
import requests
import inspect


def test_offline_mocking(api_mock):
    # check if the api mocking works
    model = requests.get("testing://base/api/model").json()
    api_mock.set_offline()
    with pytest.raises(Exception):
        requests.get("testing://base/api/model")
    api_mock.set_online()
    assert requests.get("testing://base/api/model").json() == model


def test_offline_detection(api_mock):
    koi_core.init()
    pool = koi_core.create_api_object_pool(
        host="testing://base", username="user", password="password"
    )

    # check that the api reports as online and continous to do so after authentication
    assert pool.api.online == True
    pool.api.authenticate()
    pool.get_all_models()  # make sure the models are cached
    assert pool.api.online == True

    # check if the api detects the offline server when doing something
    api_mock.set_offline()
    pool.get_all_models()  # just do something, so that the API can detect the absence of the server
    assert pool.api.online == False

    koi_core.deinit()


def test_offline_authentication(api_mock):
    koi_core.init()
    pool = koi_core.create_api_object_pool(
        host="testing://base", username="user", password="password"
    )

    # check that the api reports as online
    assert pool.api.online == True

    # check if the api detects the offline server when trying to authenticate
    api_mock.set_offline()
    with pytest.raises(KoiApiOfflineException):
        pool.api.authenticate()
    assert pool.api.online == False

    koi_core.deinit()


def test_offline_model_inference(api_mock):
    persistence = io.BytesIO()

    koi_core.init()
    pool = koi_core.create_api_object_pool(
        host="testing://base",
        username="user",
        password="password",
        persistance_file=persistence,
    )
    instance: Instance = pool.instance(
        InstanceId(
            uuid.UUID("00000000-0001-1000-8000-000000000000"),
            uuid.UUID("00000000-0002-1000-8000-000000000000"),
        )
    )
    koi_core.control.infer(instance, [], dev=True)
    koi_core.deinit()

    api_mock.set_offline()
    persistence.seek(0)
    koi_core.init()
    pool = koi_core.create_api_object_pool(
        host="testing://base",
        username="user",
        password="password",
        persistance_file=persistence,
    )
    instance = pool.instance(
        InstanceId(
            uuid.UUID("00000000-0001-1000-8000-000000000000"),
            uuid.UUID("00000000-0002-1000-8000-000000000000"),
        )
    )
    koi_core.control.infer(instance, [], dev=True)
    koi_core.deinit()


def test_offline_features_are_persistived():
    def all_classes(obj):
        classes = []
        modules = [obj]
        modules_checked = []
        while len(modules):
            obj = modules.pop()
            modules_checked.append(obj)
            for name, obj in inspect.getmembers(obj):
                if (
                    inspect.ismodule(obj)
                    and obj.__name__.startswith("koi_core")
                    and obj not in modules_checked
                ):
                    modules.append(obj)
                elif inspect.isclass(obj):
                    classes.append(obj)
        return classes

    def find_offlineFeature(cls):
        methods = []
        source = inspect.getsourcelines(cls)[0]
        for i, line in enumerate(source):
            line = line.strip()
            if line.startswith("@offlineFeature"):
                methods.append(source[i + 1].split("def")[1].split("(")[0].strip())
        return methods

    classes = all_classes(koi_core)

    strategy = ExpireCachingStrategy()
    for cls in classes:
        features = find_offlineFeature(cls)
        for feature in features:
            assert (
                strategy.shouldPersist(cls, feature, None) == True
            ), f"Method {feature} of class {cls.__name__} is marked as Offline Feature but is not persitified in ExpireCachingStrategy"
    pass


def test_offline_api(api_mock):
    persistence = io.BytesIO()

    koi_core.init()
    pool = koi_core.create_api_object_pool(
        host="testing://base",
        username="user",
        password="password",
        persistance_file=persistence,
    )
    instance: Instance = pool.instance(
        InstanceId(
            uuid.UUID("00000000-0001-1000-8000-000000000000"),
            uuid.UUID("00000000-0002-1000-8000-000000000000"),
        )
    )
    koi_core.control.infer(instance, [], dev=True)
    koi_core.deinit()

    api_mock.requests_mock.reset_mock()
    persistence.seek(0)
    koi_core.init()
    pool = koi_core.create_offline_object_pool(persistance_file=persistence)
    instance = pool.instance(
        InstanceId(
            uuid.UUID("00000000-0001-1000-8000-000000000000"),
            uuid.UUID("00000000-0002-1000-8000-000000000000"),
        )
    )
    koi_core.control.infer(instance, [], dev=True)
    koi_core.deinit()
    assert api_mock.requests_mock.call_count==0, f"The Offline API should not make any HTTP Request"

    api_mock.set_offline()
    persistence.seek(0)
    koi_core.init()
    pool = koi_core.create_offline_object_pool(persistance_file=persistence)
    instance = pool.instance(
        InstanceId(
            uuid.UUID("00000000-0001-1000-8000-000000000000"),
            uuid.UUID("00000000-0002-1000-8000-000000000000"),
        )
    )
    koi_core.control.infer(instance, [], dev=True)
    koi_core.deinit()
