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

from koi_core.caching_persistence import (
    CachingPersistence,
    getCachingPersistence,
    setCachingPersistence,
)
from koi_core.api import API
from koi_core.resources.model import LocalCode
from koi_core.resources.instance import Instance
from koi_core.resources.pool import APIObjectPool, LocalOnlyObjectPool
import koi_core.control


def init():
    pass


def deinit():
    getCachingPersistence().persistify()


def create_api_object_pool(
    host: str, username: str, password: str, persistance_file=None
):
    if persistance_file:
        setCachingPersistence(CachingPersistence(persistance_file))
    api = API(host, username, password)
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
