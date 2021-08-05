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
from typing import Dict, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from koi_core.caching import CachingObject, CachingDict

import gzip
import pickle


class CachingPersistence:
    _caches: "Dict[int, (CachingObject, CachingDict)]"
    _file: "Union[IOBase,str]"

    def __init__(self, file):
        self._file = file
        try:
            if not isinstance(file, IOBase):
                file = gzip.GzipFile(self._file, "rb")
            self._caches = pickle.load(file)
        except (FileNotFoundError, EOFError):
            self._caches = dict()

    def getCache(self, proxy: "CachingObject"):
        """
        getCache returns a dictionary that should be used for caching action with the object proxy.
        Because this class will hold a reference to the dict object it can later persitify all
        issued dicts. In case the dict was perisitfied before a preloaded dict object will be
        returned.
        """
        id = hash(proxy.id)
        if id not in self._caches:
            self._caches[id] = (None, dict())
        self._caches[id] = (proxy, self._caches[id][1])
        return self._caches[id][1]

    def persistify(self):
        persistance = dict()
        for objectKey, objectVal in self._caches.items():
            objectdict = dict()
            for key, val in objectVal[1].items():
                keyDict = dict()
                for indexkey, indexVal in val.items():
                    if objectVal[0].cachingStrategy.shouldPersist(
                        type(objectVal[0]), key, indexVal[1]
                    ):
                        keyDict[indexkey] = indexVal
                if len(keyDict) > 0:
                    objectdict[key] = keyDict
            if len(objectdict) > 0:
                persistance[objectKey] = (None, objectdict)

        file = self._file
        if isinstance(file, IOBase):
            file.seek(0)
        else:
            file = gzip.GzipFile(file, "wb")
        pickle.dump(persistance, file)
        file.truncate()


class CachingPersistenceMock:
    def getCache(self, proxy: "CachingObject"):
        return dict()

    def persistify(self):
        ...


_CachingPersistenceObject: CachingPersistence = CachingPersistenceMock()


def setCachingPersistence(c: CachingPersistence):
    global _CachingPersistenceObject
    _CachingPersistenceObject = c


def getCachingPersistence() -> CachingPersistence:
    global _CachingPersistenceObject
    return _CachingPersistenceObject
