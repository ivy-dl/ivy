"""
Collection of Jax general functions, wrapped to fit Ivy syntax and signature.
"""

# global
from functools import reduce as _reduce
from operator import mul as _mul
import numpy as _onp
import jax as _jax
import jax.numpy as _jnp

DTYPE_DICT = {_jnp.dtype('int32'): 'int32',
              _jnp.dtype('int64'): 'int64',
              _jnp.dtype('float32'): 'float32',
              _jnp.dtype('float64'): 'float64'}


def _to_dev(x, dev):
    if dev is not None:
        if 'cpu' in dev or 'gpu' in dev or 'tpu' in dev:
            dev_split = dev.split(':')
            dev_str = dev_split[0]
            if len(dev_split) > 1:
                idx = int(dev_split[1])
            else:
                idx = 0
            _jax.device_put(x, _jax.devices(dev_str)[idx])
        else:
            raise Exception('Invalid device specified, must be in the form [ "cpu:idx" | "gpu:idx" | "tpu:id" ]')
    return x


# noinspection PyShadowingNames
def tensor(object_in, dtype_str=None, dev=None):
    if dtype_str:
        if dtype_str == 'bool':
            dtype_str += '_'
        dtype = _jnp.__dict__[dtype_str]
    else:
        dtype = None
    return _to_dev(_jnp.array(object_in, dtype=dtype), dev)


to_numpy = _onp.asarray
to_list = lambda x: x.tolist()
shape = lambda x, as_tensor=False: _jnp.asarray(_jnp.shape(x)) if as_tensor else x.shape
get_num_dims = lambda x, as_tensor=False: _jnp.asarray(len(_jnp.shape(x))) if as_tensor else len(x.shape)
minimum = _jnp.minimum
maximum = _jnp.maximum
clip = _jnp.clip
# noinspection PyShadowingBuiltins
round = _jnp.round
floormod = lambda x, y: x % y
floor = _jnp.floor
ceil = _jnp.ceil
# noinspection PyShadowingBuiltins
abs = _jnp.absolute
argmax = lambda x, axis=0: _jnp.argmax(x, axis)
argmin = lambda x, axis=0: _jnp.argmin(x, axis)


def cast(x, dtype_str):
    dtype_val = _jnp.__dict__[dtype_str if dtype_str != 'bool' else 'bool_']
    return x.astype(dtype_val)


# noinspection PyShadowingNames
def arange(stop, start=0, step=1, dtype_str=None, dev=None):
    if dtype_str:
        dtype = _jnp.__dict__[dtype_str]
    else:
        dtype = None
    return _to_dev(_jnp.arange(start, stop, step=step, dtype=dtype), dev)


def linspace(start, stop, num, axis=None, dev=None):
    if axis is None:
        axis = -1
    return _to_dev(_jnp.linspace(start, stop, num, axis=axis), dev)


def concatenate(xs, axis=None):
    if axis is None:
        xs = [reshape(a, (-1,)) for a in xs]
        axis = 0
    return _jnp.concatenate(xs, axis)


def flip(x, axis=None, batch_shape=None):
    if isinstance(axis, list) or isinstance(axis, tuple):
        if len(axis) == 1:
            axis = axis[0]
        else:
            raise Exception('Jax does not support flip() across multiple indices')
    return _jnp.flip(x, axis)


stack = _jnp.stack


def unstack(x, axis, num_outputs=None):
    dim_size = x.shape[axis]
    x_split = _jnp.split(x, dim_size, axis)
    res = [_jnp.squeeze(item, axis) for item in x_split]
    return res


def split(x, num_sections=None, axis=0):
    if num_sections is None:
        num_sections = x.shape[axis]
    return _jnp.split(x, num_sections, axis)


tile = _jnp.tile
constant_pad = lambda x, pad_width, value=0, x_shape=None: _jnp.pad(x, pad_width, constant_values=value)
zero_pad = lambda x, pad_width, x_shape=None: _jnp.pad(x, pad_width, constant_values=0)
swapaxes = _jnp.swapaxes


def transpose(x, axes=None):
    if axes is None:
        num_dims = len(x.shape)
        axes = list(range(num_dims))
        axes.reverse()
    return _jnp.transpose(x, axes)


expand_dims = _jnp.expand_dims
where = lambda condition, x1, x2, condition_shape=None, x_shape=None: _jnp.where(condition, x1, x2)


def indices_where(x):
    where_x = _jnp.where(x)
    ret = _jnp.concatenate([_jnp.expand_dims(item, -1) for item in where_x], -1)
    return ret


reshape = _jnp.reshape
squeeze = _jnp.squeeze


# noinspection PyShadowingNames
def zeros(shape, dtype_str='float32', dev=None):
    dtype = _jnp.__dict__[dtype_str]
    return _to_dev(_jnp.zeros(shape, dtype), dev)


# noinspection PyShadowingNames
def zeros_like(x, dtype_str=None, dev=None):
    if dtype_str:
        dtype = _jnp.__dict__[dtype_str]
    else:
        dtype = x.dtype
    return _to_dev(_jnp.zeros_like(x, dtype=dtype), dev)


# noinspection PyShadowingNames
def ones(shape, dtype_str='float32', dev=None):
    dtype = _jnp.__dict__[dtype_str]
    return _to_dev(_jnp.ones(shape, dtype), dev)


# noinspection PyShadowingNames
def ones_like(x, dtype_str=None, dev=None):
    if dtype_str:
        dtype = _jnp.__dict__[dtype_str]
    else:
        dtype = x.dtype
    return _to_dev(_jnp.ones_like(x, dtype=dtype), dev)


# noinspection PyUnusedLocal
def one_hot(indices, depth, dev=None):
    # from https://stackoverflow.com/questions/38592324/one-hot-encoding-using-numpy
    res = _jnp.eye(depth)[_jnp.array(indices).reshape(-1)]
    return res.reshape(list(indices.shape) + [depth])


cross = _jnp.cross
matmul = lambda x1, x2, batch_shape=None: _jnp.matmul(x1, x2)
cumsum = _jnp.cumsum


# noinspection PyShadowingNames
def identity(n, dtype_str='float32', batch_shape=None, dev=None):
    dtype = _jnp.__dict__[dtype_str]
    mat = _jnp.identity(n, dtype=dtype)
    if batch_shape is None:
        return_mat = mat
    else:
        reshape_dims = [1]*len(batch_shape) + [n, n]
        tile_dims = list(batch_shape) + [1, 1]
        return_mat = _jnp.tile(_jnp.reshape(mat, reshape_dims), tile_dims)
    return _to_dev(return_mat, dev)


def scatter_flat(indices, updates, size, reduction='sum', dev=None):
    if dev is None:
        dev = dev_str(updates)
    if reduction == 'sum':
        target = _jnp.zeros([size], dtype=updates.dtype)
        target = target.at[indices].add(updates)
    elif reduction == 'min':
        target = _jnp.ones([size], dtype=updates.dtype)*1e12
        target = target.at[indices].min(updates)
        target = _jnp.where(target == 1e12, 0., target)
    elif reduction == 'max':
        target = _jnp.ones([size], dtype=updates.dtype)*-1e12
        target = target.at[indices].max(updates)
        target = _jnp.where(target == -1e12, 0., target)
    else:
        raise Exception('reduction is {}, but it must be one of "sum", "min" or "max"'.format(reduction))
    return _to_dev(target, dev)


# noinspection PyShadowingNames
def scatter_nd(indices, updates, shape, num_idx_dims=None, reduction='sum', dev=None):
    if dev is None:
        dev = dev_str(updates)
    shape = list(shape)
    indices_flat = indices.reshape(-1, indices.shape[-1]).T
    indices_tuple = tuple(indices_flat) + (Ellipsis,)
    if reduction == 'sum':
        target = _jnp.zeros(shape, dtype=updates.dtype)
        target = target.at[indices_tuple].add(updates)
    elif reduction == 'min':
        target = _jnp.ones(shape, dtype=updates.dtype)*1e12
        target = target.at[indices_tuple].min(updates)
        target = _jnp.where(target == 1e12, 0., target)
    elif reduction == 'max':
        target = _jnp.ones(shape, dtype=updates.dtype)*-1e12
        target = target.at[indices_tuple].max(updates)
        target = _jnp.where(target == -1e12, 0., target)
    else:
        raise Exception('reduction is {}, but it must be one of "sum", "min" or "max"'.format(reduction))
    return _to_dev(target, dev)


def gather_flat(params, indices, dev=None):
    if dev is None:
        dev = dev_str(params)
    return _to_dev(_jnp.take(params, indices, 0), dev)


def gather_nd(params, indices, indices_shape=None, dev=None):
    if dev is None:
        dev = dev_str(params)
    if indices_shape is None:
        indices_shape = indices.shape
    params_shape = params.shape
    num_index_dims = indices_shape[-1]
    res_dim_sizes_list = [_reduce(_mul, params_shape[i + 1:], 1) for i in range(len(params_shape) - 1)] + [1]
    result_dim_sizes = _jnp.array(res_dim_sizes_list)
    implicit_indices_factor = int(result_dim_sizes[num_index_dims - 1].item())
    flat_params = _jnp.reshape(params, (-1,))
    new_shape = [1] * (len(indices_shape) - 1) + [num_index_dims]
    indices_scales = _jnp.reshape(result_dim_sizes[0:num_index_dims], new_shape)
    indices_for_flat_tiled = _jnp.tile(_jnp.reshape(_jnp.sum(indices * indices_scales, -1, keepdims=True), (-1, 1)), (1, implicit_indices_factor))
    implicit_indices = _jnp.tile(_jnp.expand_dims(_jnp.arange(implicit_indices_factor), 0), (indices_for_flat_tiled.shape[0], 1))
    indices_for_flat = indices_for_flat_tiled + implicit_indices
    flat_indices_for_flat = _jnp.reshape(indices_for_flat, (-1,)).astype(_jnp.int32)
    flat_gather = _jnp.take(flat_params, flat_indices_for_flat, 0)
    new_shape = list(indices_shape[:-1]) + list(params_shape[num_index_dims:])
    ret = _jnp.reshape(flat_gather, new_shape)
    return _to_dev(ret, dev)


dev = lambda x: x.device_buffer


def dev_to_str(dev_in):
    p, dev_id = (dev_in.platform(), dev_in.device().id)
    return p + ':' + str(dev_id)


dev_str = lambda x: dev_to_str(dev(x))


def _dev_is_available(base_dev_str):
    try:
        _jax.devices(base_dev_str)
        return True
    except RuntimeError:
        return False


gpu_is_available = lambda: _dev_is_available('gpu')
tpu_is_available = lambda: _dev_is_available('tpu')
dtype = lambda x: x.dtype
dtype_to_str = lambda dtype_in: DTYPE_DICT[dtype_in]
dtype_str = lambda x: dtype_to_str(dtype(x))
compile_fn = lambda fn, dynamic=True, example_inputs=None: _jax.jit(fn)