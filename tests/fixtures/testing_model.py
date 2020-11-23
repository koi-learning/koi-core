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
