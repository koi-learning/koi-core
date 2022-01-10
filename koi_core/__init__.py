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

from io import IOBase
from typing import Union
from koi_core.caching_persistence import (
    CachingPersistence,
    CachingPersistenceMock,
    getCachingPersistence,
    setCachingPersistence,
)
from koi_core.api import API, OfflineAPI
from koi_core.resources.model import LocalCode
from koi_core.resources.instance import Instance
from koi_core.resources.pool import APIObjectPool, LocalOnlyObjectPool
from koi_core.exceptions import KoiInitializationError
import koi_core.control  # noqa: F401

_isInitialized = False


def init():
    global _isInitialized
    if _isInitialized:
        raise KoiInitializationError("KOI Core must be initialized only once")
    setCachingPersistence(CachingPersistenceMock())
    _isInitialized = True


def deinit():
    global _isInitialized
    if not _isInitialized:
        raise KoiInitializationError(
            "KOI Core must be initialized before deinitialization"
        )
    getCachingPersistence().persistify()
    _isInitialized = False


def create_api_object_pool(
    host: str, username: str, password: str, persistance_file: Union[IOBase, str] = None
):
    if persistance_file:
        setCachingPersistence(CachingPersistence(persistance_file))
    api = API(host, username, password)
    return APIObjectPool(api)


def create_offline_object_pool(persistance_file: Union[IOBase, str]):
    setCachingPersistence(CachingPersistence(persistance_file))
    api = OfflineAPI()
    return APIObjectPool(api)


def create_local_object_pool():
    return LocalOnlyObjectPool()


def local_instance(path, parameter) -> Instance:
    pool = create_local_object_pool()
    model = pool.new_model()
    model.code = LocalCode(path)
    instance = model.new_instance()
    instance.parameter = parameter
    return instance
