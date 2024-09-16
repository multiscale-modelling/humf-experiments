import importlib


def create_model(name):
    """Create a model identified by a name.

    We need to create models in different nodes of the workflow, including
    every time we want to load a model checkpoint. This function creates models
    using factory functions defined in modules of the `humf_experiments.models`
    package, where the type of the model is identified by a name that can be
    passed to workflow nodes as a string parameter.
    """
    module = importlib.import_module("humf_experiments.models." + name)
    factory = getattr(module, "create_" + name)
    model = factory()
    return model
