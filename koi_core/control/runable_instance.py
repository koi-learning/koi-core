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

import multiprocessing
from koi_core.resources.instance import Instance
from koi_core.control import actions


class _TrainCommand():
    def __init__(self, batch_iterable):
        self.batch_iterable = batch_iterable


class _TrainResponse():
    pass


class _InferCommand():
    def __init__(self, batch_iterable):
        self.batch_iterable = batch_iterable


class _InferResponse():
    def __init__(self, batch_iterable):
        self.batch_iterable = batch_iterable


class _ExceptionResponse():
    def __init__(self, exception):
        self.exception = exception


class _ExitCommand():
    pass


class _ExitResponse():
    pass


def _train(pipe, model, instance, command: _TrainCommand):
    actions.train(model, instance, command.batch_iterable)
    pipe.send(_TrainResponse())


def _infer(pipe, model, instance, command: _InferCommand):
    result = actions.infer(model, instance, command.batch_iterable)
    pipe.send(_InferResponse(result))


def _process_run(pipe, instance: Instance):
    # import code object from instance:
    model = instance.load_code()

    while(True):
        def default(pipe, model, instance, command):
            raise Exception(f"unknown command: {type(command)}")

        commandLookup = {_TrainCommand: _train, _InferCommand: _infer}

        command = pipe.recv()
        if type(command) == _ExitCommand:
            break
        else:
            try:
                commandLookup.get(type(command), default)(pipe, model, instance, command)
            except Exception as e:
                pipe.send(_ExceptionResponse(e))

    pipe.send(_ExitResponse())
    return 0


def _check_for_exceptions(response):
    if type(response) == _ExceptionResponse:
        raise response.exception


class RunableInstance():
    def __init__(self, instance: Instance):
        self._process_name = f"koi_runable_{instance.name}"
        self.instance = instance

        a, b = multiprocessing.Pipe()
        self._pipe = a
        self._process = multiprocessing.Process(
            target=_process_run, args=(b, instance), name=self._process_name)
        self._process.start()

    def train(self, batch_iterable=None):
        self._pipe.send(_TrainCommand(batch_iterable))
        response = self._pipe.recv()
        _check_for_exceptions(response)
        if not type(response) == _TrainResponse:
            raise Exception("Communication Error")

    def infer(self, batch_iterable):
        self._pipe.send(_InferCommand(batch_iterable))
        response = self._pipe.recv()
        _check_for_exceptions(response)
        if not type(response) == _InferResponse:
            raise Exception("Communication Error")
        return response.batch_iterable

    def terminate(self):
        # send the exit command to the process
        self._pipe.send(_ExitCommand())

        # wait for the process to finish
        self._process.join(0.5)

        # check the processes exit code
        if self._process.exitcode is not None:
            # kill if necessary
            self._process.terminate()
