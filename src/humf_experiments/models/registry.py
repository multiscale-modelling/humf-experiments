"""This module provides a registry for model factory functions.

Model factory functions create models with varying architectures. We need to
create models at different points in the workflow, including every time we want
to load a model checkopoint. The factory function registry maps model names to
factory functions, so that we can identify a model to be created by a string
that can also be given as a workflow node parameter.
"""

models = {}


def register_factory(fn):
    """Register a factory function for a model."""
    # Factory functions are named after the model they create, with the prefix "create_".
    # Strip the prefix from the function name.
    name = fn.__name__.replace("create_", "")
    models[name] = fn
    return fn
