FROM tensorflow/tensorflow
COPY . /src
RUN pip install ./src