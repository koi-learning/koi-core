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

from io import BytesIO
from koi_core.caching import cache, setCache
from koi_core.resources.sample import SampleDatum, SampleLabel
from typing import Union
import numpy as np


@cache
def get_np(self: Union[SampleDatum, SampleLabel], meta) -> np.ndarray:
    f = BytesIO(self.raw)
    return np.load(f, allow_pickle=False), meta


def set_np(self: Union[SampleDatum, SampleLabel], value: np.ndarray) -> None:
    f = BytesIO()
    np.save(f, value, allow_pickle=False)
    self.raw = f.getvalue()
    setCache(self, 'np', None)


@cache
def get_txt(self: Union[SampleDatum, SampleLabel], meta) -> str:
    return self.raw.decode(), meta


def set_txt(self: Union[SampleDatum, SampleLabel], value: str) -> None:
    self.raw = str.encode(value)
    setCache(self, 'txt', None)
