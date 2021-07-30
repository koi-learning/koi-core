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

import datetime
from functools import wraps
from koi_core.api.common import KoiApiOfflineException
from koi_core.caching_strategy import CachingStrategy
from koi_core.caching_persistence import getCachingPersistence
from typing import Any, Dict, Hashable, Tuple, TypeVar


class CachingMeta:
    expires: datetime = None
    last_modified: datetime = None
    etag: str = None

    def __eq__(self, other):
        if other is None:
            return False

        if self.etag is not None and other.etag is not None:
            return self.etag == other.etag

        return self.last_modified == other.last_modified


CachingDict = Dict[str, Dict[Any, Tuple[Any, CachingMeta]]]


class CachingObject:
    _cache: CachingDict
    id: Hashable
    cachingStrategy: CachingStrategy


T = TypeVar("T")


def setCache(self: CachingObject, key: str, value: T) -> T:
    if not hasattr(self, "_cache"):
        self._cache = getCachingPersistence().getCache(self)
    self._cache[key] = value  # type: ignore
    return value


def setIndexedCache(self, key: str, index, value: T) -> T:
    if not hasattr(self, "_cache"):
        self._cache = getCachingPersistence().getCache(self)
    if key not in self._cache:
        self._cache[key] = dict()  # type: ignore
    self._cache[key][index] = (value, None)  # type: ignore
    return value


def offlineFeature(func: T) -> T:
    func._offline_feature_ = True
    return func


def cache(func: T) -> T:
    key = func.__name__

    @wraps(func)
    def wrapper(self):
        if not hasattr(self, "_cache"):
            self._cache = getCachingPersistence().getCache(self)
        if key not in self._cache:
            self._cache[key] = dict()  # type: ignore

        try:
            if 0 not in self._cache[key]:
                self._cache[key][0] = func(self, None)  # type: ignore
            elif not self.cachingStrategy.isValid(type(self), key, self._cache[key][0][1]):
                obj, new_meta = func(self, self._cache[key][0][1])
                if obj is None:
                    # we receive None in case no update was needed
                    self._cache[key][0] = (self._cache[key][0][0], new_meta)  # type: ignore
                else:
                    self._cache[key][0] = (obj, new_meta)  # type: ignore
            return self._cache[key][0][0]
        except KoiApiOfflineException:
            if hasattr(func, "_offline_feature_"):
                if 0 not in self._cache[key]:
                    raise KoiApiOfflineException("The Data for this Feature was cached")
                else:
                    return self._cache[key][0][0]
            else:
                raise KoiApiOfflineException(
                    "This Feature is not available in Offline Mode"
                )

    return wrapper


def indexedCache(func: T) -> T:
    key = func.__name__

    @wraps(func)
    def wrapper(self, index):
        if not hasattr(self, "_cache"):
            self._cache = getCachingPersistence().getCache(self)
        if key not in self._cache:
            self._cache[key] = dict()  # type: ignore

        try:
            if index not in self._cache[key]:
                self._cache[key][index] = func(self, index, None)  # type: ignore
            elif not self.cachingStrategy.isValid(
                type(self), key, self._cache[key][index][1]
            ):
                obj, new_meta = func(self, index, self._cache[key][index][1])
                if obj is None:
                    # we receive None in case no update was needed
                    self._cache[key][index] = (self._cache[key][index][0], new_meta)  # type: ignore
                else:
                    self._cache[key][index] = (obj, new_meta)  # type: ignore
            return self._cache[key][index][0]
        except KoiApiOfflineException:
            if hasattr(func, "_offline_feature_"):
                if index not in self._cache[key]:
                    raise KoiApiOfflineException("The Data for this Feature was cached")
                else:
                    return self._cache[key][index][0]
            else:
                raise KoiApiOfflineException(
                    "This Feature is not available in Offline Mode"
                )

    return wrapper
