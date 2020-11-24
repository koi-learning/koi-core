# About
*koi-core* is part of the [KOI-System](https://github.com/koi-learning) and implements its runtime environment.
The *KOI-System* is framework for lifecycle-management of machine learning solutions.
As such it allows the user to create, train, and deploy ML-solutions.
"*KOI*" is an abbreviation of the german name "Kognitive Objekt-orientierte Intelligenz", which translates to "cognitive object-oriented intelligence".

To simplify the development and deployment of different ML-solutions the system defines three types of objects: **Models**, **Instances**, and **Samples**


# Installation

## Local Installation
If you want to install *koi-core* for production use, simply run:
> pip install git+https://github.com/koi-learning/koi-core.git

For development purposes it is best to check out the repository and install all dependencies listet in *requirements.txt*

## Using Docker
comming soon...

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
    # iterate over all instances of each model
    for instance in model.instances:
        #access basic information about the objects
        print(instance.name, instance.description)

        # train an instance
        koi.control.train(instance)

        # ase an instance for inference
        output = koi.control.infer(instance, input)

    # add new instances
    new_instance = model.new_instance()
```

# Copying & Contributing
*koi-core* was originally written by Johannes Richter (GÖPEL electronics, Jena) and Johannes Nau (Technische Universität Ilmenau).
The source code is licensed under the terms of LGPLv3, please see [COPYING](COPYING) and [COPYING.LESSER](COPYING.LESSER) for details.

If you are working with the KOI-System and find any bugs, please report them as an issue in the respective projects on Github.com.

If you want to contribute to this project, take a look at the open issues and send us your pull-requests. 