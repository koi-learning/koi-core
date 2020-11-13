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

from koi_core.resources.instance import Instance
import itertools


class SimpleBatchGenerator():
    batchSize: int = None

    def __init__(self, instance: Instance):
        self._samples = instance.samples_unconsumed

    def __iter__(self):
        if self.batchSize is None:
            raise Exception("Batch Size must be set before iterating")
        return self

    def __next__(self):
        batch = list()
        sub_gen = itertools.islice(self._samples, self.batchSize)
        for item in sub_gen:
            batch.append(item)

        if len(batch) == 0:
            raise StopIteration

        return batch
