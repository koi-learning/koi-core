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

from typing import Any, Dict, List
from tempfile import TemporaryDirectory
from koi_core.control import actions
from koi_core.resources.instance import Instance
from .runable_instance import RunableInstance
from time import time


_runable_instance: RunableInstance = None
_active_instances: Dict[Instance, List] = {}


def _set_instance(instance: Instance, max_instances: int = 1):
    global _runable_instance
    global _active_instances

    if _runable_instance is not None and _runable_instance.instance == instance:
        # instance is already avaiable as runable_instance - return
        return

    if max_instances > 0 and len(_active_instances) > max_instances:
        # we have too many instances...
        sorted_instances = sorted(_active_instances.items(), key=lambda x: x[1][1], reverse=True)
        sorted_instances = sorted_instances[-(len(sorted_instances)-max_instances):]

        # remove the unused instances
        for elem in sorted_instances:
            elem[1][0].terminate()
            del _active_instances[elem[0]]

    if instance in _active_instances and _active_instances[instance][0].is_alive():
        _runable_instance = _active_instances[instance][0]
        _active_instances[instance][1] = time()
        return
    else:
        # replace the oldest instance if the number is exhausted
        if max_instances > 0 and len(_active_instances) == max_instances:
            elem = sorted(_active_instances.items(), key=lambda x: x[1][1], reverse=True)[-1]
            elem[1][0].terminate()
            del _active_instances[elem[0]]

        # create a new runable instance and add it to the dictionary
        _runable_instance = RunableInstance(instance)
        _active_instances[instance] = [_runable_instance, time()]


def train(instance: Instance, batch_iterable=None, dev=False, max_instances=1):
    global _runable_instance

    if dev:
        temp_dir = TemporaryDirectory()
        model = instance.load_code(temp_dir.name)
        actions.train(model, instance, batch_iterable)
        temp_dir.cleanup()
    else:
        _set_instance(instance, max_instances)
        try:
            _runable_instance.train(batch_iterable)
        except:
            kill_runable_instance()
            raise


def infer(instance: Instance, data, dev=False, model=None, max_instances=1) -> List[Any]:
    global _runable_instance

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
        _set_instance(instance, max_instances)
        try:
            return _runable_instance.infer(data)
        except:
            kill_runable_instance()
            raise


def kill_runable_instance():
    global _runable_instance
    global _active_instances

    if _runable_instance is None:
        return
    
    instance = _runable_instance.instance

    _runable_instance.terminate()
    _runable_instance = None

    if instance in _active_instances:
        del _active_instances[instance]


def terminate():
    for elem in _active_instances.values():
        elem[0].terminate()
