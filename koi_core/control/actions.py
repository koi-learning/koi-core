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

from koi_core.data.simple_batch_generator import SimpleBatchGenerator


def train(model, instance, batch_iterable):
    if batch_iterable is None:
        if "batch_generator" in model.__dict__:
            batch_iterable = model.batch_generator(instance)
        else:
            batch_iterable = SimpleBatchGenerator(instance)
            batch_iterable.batchSize = 25

    if instance.training_data is None:
        # if no training_data is available
        model.initialize_training()
    else:
        model.load_training_data(instance.training_data)

    for batch in batch_iterable:
        model.train(batch)

    if model.should_create_training_data():
        instance.training_data = model.save_training_data()
    if model.should_create_inference_data():
        instance.inference_data = model.save_inference_data()

    return


def infer(model, instance, batch_iterable):
    model.load_inference_data(instance.inference_data)
    result_list = list()
    for batch in batch_iterable:
        result = dict()
        model.infer(batch, result)
        result_list.append(result)

    return result_list
