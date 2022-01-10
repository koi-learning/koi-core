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

import os
import zipfile
import io
import pytest


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            filename = os.path.join(root, file)
            ziph.write(filename, arcname=os.path.relpath(filename, path))


@pytest.fixture
def testing_model():
    file_like_object = io.BytesIO()
    zipf = zipfile.ZipFile(file_like_object, "w", zipfile.ZIP_DEFLATED)
    model_dir = os.path.dirname(__file__) + os.path.sep + "testing_model"
    zipdir(model_dir, zipf)
    zipf.close()
    return file_like_object.getvalue()
