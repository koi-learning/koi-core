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

from typing import Any, List
from tempfile import TemporaryDirectory
from koi_core.control import actions
from koi_core.resources.instance import Instance
from .runable_instance import RunableInstance

_runable_instance: RunableInstance = None


def _set_instance(instance: Instance):
    global _runable_instance
    if _runable_instance is not None:
        if _runable_instance.instance == instance:
            # instance is already avaiable as runable_instance - return
            return

    # we need to load another instance:
    if _runable_instance is not None:
        _runable_instance.terminate()
        _runable_instance = None

    _runable_instance = RunableInstance(instance)


def train(instance: Instance, batch_iterable=None, dev=False):
    if dev:
        temp_dir = TemporaryDirectory()
        model = instance.load_code(temp_dir.name)
        actions.train(model, instance, batch_iterable)
        temp_dir.cleanup()
    else:
        _set_instance(instance)
        _runable_instance.train(batch_iterable)


def infer(instance: Instance, data, dev=False, model=None) -> List[Any]:
    if dev:
        temp_dir = None

        if model is None:
            temp_dir = TemporaryDirectory()
            model = instance.load_code(temp_dir.name)
        ret = actions.infer(model, instance, data)

        if temp_dir:
            temp_dir.cleanup()

        return ret

    else:
        _set_instance(instance)
        return _runable_instance.infer(data)


def terminate():
    if _runable_instance is not None:
        _runable_instance.terminate()
