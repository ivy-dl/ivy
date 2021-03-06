"""
Collection of MXNet random functions, wrapped to fit Ivy syntax and signature.
"""

# global
import mxnet as _mx

# noinspection PyProtectedMember
from ivy.mxnd.core.general import _mxnet_init_context


def random_uniform(low=0., high=1., shape=None, dev='cpu'):
    ctx = _mxnet_init_context(dev)
    return _mx.nd.random.uniform(low, high, shape, ctx=ctx)


def randint(low, high, shape, dev='cpu'):
    ctx = _mxnet_init_context(dev)
    return _mx.nd.random.randint(low, high, shape, ctx=ctx)


seed = lambda seed_value=0: _mx.random.seed(seed_value)
shuffle = lambda x: _mx.nd.random.shuffle(x)
