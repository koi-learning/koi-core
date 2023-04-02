# The goal of this Dockerfile is to build a container that can run the Koi worker
# on a CPU-only machine. It is based on the official TensorFlow image. For your
# convenience, we added tensorflow-hub to the image, so you can use pretrained
# models from TensorFlow Hub.

FROM tensorflow/tensorflow:2.11.0

COPY ./dist/ /wheels/

RUN python -m pip install --upgrade pip

# add tensorflow hub to have access to pretrained models
RUN pip install tensorflow-hub==0.13.0

RUN pip install --find-links /wheels/ koi_core

ENTRYPOINT ["koi-worker"]
