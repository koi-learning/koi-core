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

from datetime import datetime


class CachingStrategy:
    def isValid(self, proxy_cls, key, meta):
        ...

    def shouldPersist(self, proxy_cls, key, meta):
        ...


class ExpireCachingStrategy:
    def isValid(self, proxy_cls, key, meta):
        now = datetime.utcnow()

        # Cache all PoolObjects
        t = proxy_cls.__name__
        if t in ["LocalOnlyObjectPool", "APIObjectPool"]:
            if key in ["_get_models"]:
                return False
            else:
                return True

        if meta is None or now >= meta.expires:
            return False
        else:
            return True

    def shouldPersist(self, proxy_cls, key, meta):
        t = proxy_cls.__name__

        if t == "ModelProxy":
            if key in [
                "_basic_fields",
                "_code",
                "request_plugin",
                "visual_plugin",
                "_instance_ids",
                "parameters",
            ]:
                return True
            return False
        if t == "InstanceProxy":
            if key in [
                "_basic_fields",
                "training_data",
                "inference_data",
                "_samples",
                "_get_parameter_values",
                "__get_descriptors",
                "_get_available_parameters",
            ]:
                return True
            return False
        if t == "DescriptorProxy":
            if key in ["_basic_fields", "raw"]:
                return True
            return False
        if t == "SampleProxy":
            if key in ["_basic_fields", "__get_data", "__get_labels"]:
                return True
            return False
        if t in ["SampleDatumProxy", "SampleLabelProxy"]:
            if key in ["_basic_fields", "raw"]:
                return True
            return False
        if t in ["LocalOnlyObjectPool", "APIObjectPool"]:
            if key in ["_get_models"]:
                return True
            return False
        return False


class LocalOnlyCachingStrategy:
    def isValid(self, proxy_cls, key, meta):
        return True

    def shouldPersist(self, proxy_cls, key, meta):
        return False
