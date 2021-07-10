# About
*koi-core* is part of the [KOI-System](https://github.com/koi-learning) and implements its runtime environment.
The runtime depends on a connection to a running instance of [koi-api](https://github.com/koi-learning/koi-api)

# What is KOI?
The *KOI-System* is a framework for the lifecycle management and deployment of machine learning solutions.
As such, it allows the user to create, train, and deploy ML solutions.

The lifecycle management involves:
- Continuous Training of ML-Models
- Collecting new Samples from multiple sources
- Control visibility and access through user account management and roles
- Distributed training using multiple workers  

"*KOI*" is an abbreviation of the German name "Kognitive Objekt-orientierte Intelligenz", which translates to "cognitive object-oriented intelligence".

The system defines three types of objects to simplify the development and deployment of different ML solutions: 
- **Models**
- **Instances**
- **Samples**

Models define how data is processed and how the machine learning application learns.
Samples are an atomic piece of training information used for a specific problem.
Instances are specific implementations of models trained with associated samples to reach a state suitable for inference.

The project is written in Python and uses Flask.
It does not depend on ML-Frameworks and enables the user to choose what is best for their Model.

# Installation

## Local Installation
If you want to install *koi-core* for production use, simply run:
> pip install git+https://github.com/koi-learning/koi-core.git

For development purposes it is best to check out the repository and install all dependencies listet in *requirements.txt*

## Using Docker
If you want to use *koi-core* from within a docker container see the included example [dockerfile](dockerfile).

Switch to the source folder and build it with: 
```
docker build . -t <name of your container>
```

To use the worker inside the docker container run:

```
docker exec -it <name of your container> koi-worker.py <options>
```

For a complete setup using docker see [koi-deploy](https://github.com/koi-learning/koi-deploy) 

# Using koi-core
*koi-core* comes with a worker-client.
This client fetches models from a remote or local [*koi-api*](https://github.com/koi-learning/koi-pi) and trains instances. 
## Running a worker
If you wan to run the default worker included in the *koi-core* runtime: you have to specify at least the koi-api-host, username, and password:
```
koi-worker.py -s=<koi-api-host> -u=<user> -p=<password>
```
The roles associated with the authenticating user account define what models and instances are visible and which actions are allowed. If you want to filter the models and instances you could run:

```
koi-worker.py -s=<koi-api-host> -u=<user> -p=<password> -m=<model_name> -i=<instance_name>
```
There are some options available, which control the runtime behaviour of the client.
To only train each visible or selected instance once:
```
koi-worker.py -s=<koi-api-host> -u=<user> -p=<password> --once
```
To force a retraining of an already trained instance use:
```
koi-worker.py -s=<koi-api-host> -u=<user> -p=<password> --force
```
If you want the worker to sleep for an amount of time after it trained all visible instances:
```
koi-worker.py -s=<koi-api-host> -u=<user> -p=<password> --sleep=<seconds>
```
All these options can be combined at will.
For a complete list of options available run:
```
koi-worker.py --help
```
## Embedding into other software
To use the koi-core lib from your own code include it like so:
```
import koi_core as koi
...
koi.init()
```

Creeate an object pool by using:
```
pool = koi.koi.create_api_object_pool("koi-host", "username", "password")
```

Now you can create objects and edit them like so:
```
# get alist of all models visible to me
models = pool.get_all_models()

# iterate over the models
for model in models:

    # create new instance and set name and description
    new_instance = model.new_instance()
    new_instance.name = "newly created"
    new_instance.description = "just created now"

    # set an instance parameter as exported by the model
    new_instance.parameters["param1"] = 10.5

    # finalize the instance and mark it ready for training
    new_instance.finalized = True

    # iterate over all instances of each model
    for instance in model.instances:
        #access basic information about the objects
        print(instance.name, instance.description)

        # train an instance
        koi.control.train(instance)

        # use an instance for inference
        output = koi.control.infer(instance, input)

    # add new instances
    new_instance = model.new_instance()
```

# Copying & Contributing
*koi-core* was originally written by Johannes Richter (GÖPEL electronics, Jena) and Johannes Nau (Technische Universität Ilmenau).
The source code is licensed under the terms of LGPLv3, please see [COPYING](COPYING) and [COPYING.LESSER](COPYING.LESSER) for details.

If you are working with the KOI-System and find any bugs, please report them as an issue in the respective projects on Github.com.

If you want to contribute to this project, take a look at the open issues and send us your pull-requests. 

# Citation
If you are using the *KOI-System* for academic research, please cite our [accompanying publication](http://dx.doi.org/10.1007/978-3-030-68527-0_8) . Here we give an overview of the architecture and discuss some design decisions.