import koi_core as koi


def test_training(api_mock):
    koi.init()
    pool = koi.create_api_object_pool(
        host="testing://base", username="user", password="password"
    )

    models = pool.get_all_models()
    for model in models:
        instances = model.instances
        for instance in instances:
            koi.control.train(instance, dev=True)
