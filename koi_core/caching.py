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

from functools import wraps
from typing import Dict, TypeVar


class CachingObject:
    _cache: Dict


class CachingMeta:
    pass


T = TypeVar("T")


def setCache(self, key: str, value: T) -> T:
    if not hasattr(self, "_cache"):
        self._cache = dict()
    self._cache[key] = value
    return value


def setIndexedCache(self, key: str, index, value: T) -> T:
    if not hasattr(self, "_cache"):
        self._cache = dict()
    if key not in self._cache:
        self._cache[key] = dict()
    self._cache[key][index] = (value, None)
    return value


def cache(func: T) -> T:
    key = func.__name__

    def wrapper(self: CachingObject):
        if not hasattr(self, "_cache"):
            self._cache = dict()

        if key not in self._cache:
            self._cache[key] = func(self, None)
        elif not self.cachingStrategy.isValid(self, key, self._cache[key][1]):
            obj, new_meta = func(self, self._cache[key][1])
            if obj is None:
                # we receive None in case no update was needed
                self._cache[key] = (self._cache[key][0], new_meta)
            else:
                self._cache[key] = (obj, new_meta)
        return self._cache[key][0]

    return wrapper


def indexedCache(func: T) -> T:
    key = func.__name__

    @wraps(func)
    def wrapper(self, index):
        if not hasattr(self, "_cache"):
            self._cache = dict()
        if key not in self._cache:
            self._cache[key] = dict()

        if index not in self._cache[key]:
            self._cache[key][index] = func(self, index, None)
        elif not self.cachingStrategy.isValid(self, key, self._cache[key][index][1]):
            obj, new_meta = func(self, index, self._cache[key][index][1])
            if obj is None:
                # we receive None in case no update was needed
                self._cache[key][index] = (self._cache[key][index][0], new_meta)
            else:
                self._cache[key][index] = (obj, new_meta)
        return self._cache[key][index][0]

    return wrapper
