"""
Collection of tests for templated general functions
"""

# global
import pytest
import numpy as np
from numbers import Number
from collections.abc import Sequence
# noinspection PyPackageRequirements
from jaxlib.xla_extension import Buffer

# local
import ivy
import ivy.numpy
import ivy_tests.helpers as helpers


# Helpers #
# --------#

def _var_fn(a, b=None, c=None):
    return ivy.variable(ivy.array(a, b, c))


def _get_shape_of_list(lst, shape=()):
    if not lst:
        return []
    if not isinstance(lst, Sequence):
        return shape
    if isinstance(lst[0], Sequence):
        l = len(lst[0])
        if not all(len(item) == l for item in lst):
            msg = 'not all lists have the same length'
            raise ValueError(msg)
    shape += (len(lst),)
    shape = _get_shape_of_list(lst[0], shape)
    return shape


# Tests #
# ------#

# array
@pytest.mark.parametrize(
    "object_in", [[], [0.], [1], [True], [[1., 2.]]])
@pytest.mark.parametrize(
    "dtype_str", [None, 'float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64', 'bool'])
def test_array(object_in, dtype_str, dev_str, call):
    if call in [helpers.mx_call] and dtype_str == 'int16':
        # mxnet does not support int16
        pytest.skip()
    # smoke test
    ret = ivy.array(object_in, dtype_str, dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == np.array(object_in).shape
    # value test
    assert np.allclose(call(ivy.array, object_in, dtype_str, dev_str), np.array(object_in).astype(dtype_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting does not support string devices
        return
    helpers.assert_compilable(ivy.array)


# to_numpy
@pytest.mark.parametrize(
    "object_in", [[], [0.], [1], [True], [[1., 2.]]])
@pytest.mark.parametrize(
    "dtype_str", [None, 'float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64', 'bool'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array])
def test_to_numpy(object_in, dtype_str, tensor_fn, dev_str, call):
    if call in [helpers.mx_call] and dtype_str == 'int16':
        # mxnet does not support int16
        pytest.skip()
    if call in [helpers.tf_graph_call]:
        # to_numpy() requires eager execution
        pytest.skip()
    # smoke test
    ret = ivy.to_numpy(tensor_fn(object_in, dtype_str, dev_str))
    # type test
    assert isinstance(ret, np.ndarray)
    # cardinality test
    assert ret.shape == np.array(object_in).shape
    # value test
    assert np.allclose(ivy.to_numpy(tensor_fn(object_in, dtype_str, dev_str)), np.array(object_in).astype(dtype_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting does not support numpy conversion
        return
    helpers.assert_compilable(ivy.to_numpy)


# to_list
@pytest.mark.parametrize(
    "object_in", [[], [0.], [1], [True], [[1., 2.]]])
@pytest.mark.parametrize(
    "dtype_str", [None, 'float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64', 'bool'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array])
def test_to_list(object_in, dtype_str, tensor_fn, dev_str, call):
    if call in [helpers.mx_call] and dtype_str == 'int16':
        # mxnet does not support int16
        pytest.skip()
    if call in [helpers.tf_graph_call]:
        # to_list() requires eager execution
        pytest.skip()
    # smoke test
    ret = ivy.to_list(tensor_fn(object_in, dtype_str, dev_str))
    # type test
    assert isinstance(ret, list)
    # cardinality test
    assert _get_shape_of_list(ret) == _get_shape_of_list(object_in)
    # value test
    assert np.allclose(np.asarray(ivy.to_list(tensor_fn(object_in, dtype_str, dev_str))),
                       np.array(object_in).astype(dtype_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting does not support list conversion
        return
    helpers.assert_compilable(ivy.to_list)


# shape
@pytest.mark.parametrize(
    "object_in", [[], [0.], [1], [True], [[1., 2.]]])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "as_tensor", [None, True, False])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_shape(object_in, dtype_str, as_tensor, tensor_fn, dev_str, call):
    # smoke test
    if len(object_in) == 0 and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    ret = ivy.shape(tensor_fn(object_in, dtype_str, dev_str), as_tensor)
    # type test
    if as_tensor:
        assert isinstance(ret, ivy.Array)
    else:
        assert isinstance(ret, tuple)
        ret = ivy.array(ret)
    # cardinality test
    assert ret.shape[0] == len(np.asarray(object_in).shape)
    # value test
    assert np.array_equal(ivy.to_numpy(ret), np.asarray(np.asarray(object_in).shape, np.int32))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting does not support Union
        return
    helpers.assert_compilable(ivy.shape)


# get_num_dims
@pytest.mark.parametrize(
    "object_in", [[], [0.], [1], [True], [[1., 2.]]])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "as_tensor", [None, True, False])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_get_num_dims(object_in, dtype_str, as_tensor, tensor_fn, dev_str, call):
    # smoke test
    if len(object_in) == 0 and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    ret = ivy.get_num_dims(tensor_fn(object_in, dtype_str, dev_str), as_tensor)
    # type test
    if as_tensor:
        assert isinstance(ret, ivy.Array)
    else:
        assert isinstance(ret, int)
        ret = ivy.array(ret)
    # cardinality test
    assert list(ret.shape) == []
    # value test
    assert np.array_equal(ivy.to_numpy(ret), np.asarray(len(np.asarray(object_in).shape), np.int32))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting does not support Union
        return
    helpers.assert_compilable(ivy.shape)


# minimum
@pytest.mark.parametrize(
    "xy", [([0.7], [0.5]), ([0.7], 0.5), (0.5, [0.7]), ([[0.8, 1.2], [1.5, 0.2]], [0., 1.])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_minimum(xy, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(xy[0], Number) or isinstance(xy[1], Number)) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(xy[0], dtype_str, dev_str)
    y = tensor_fn(xy[1], dtype_str, dev_str)
    ret = ivy.minimum(x, y)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    if len(x.shape) > len(y.shape):
        assert ret.shape == x.shape
    else:
        assert ret.shape == y.shape
    # value test
    assert np.array_equal(call(ivy.minimum, x, y), ivy.numpy.minimum(ivy.to_numpy(x), ivy.to_numpy(y)))
    # compilation test
    helpers.assert_compilable(ivy.minimum)


# maximum
@pytest.mark.parametrize(
    "xy", [([0.7], [0.5]), ([0.7], 0.5), (0.5, [0.7]), ([[0.8, 1.2], [1.5, 0.2]], [0., 1.])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_maximum(xy, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(xy[0], Number) or isinstance(xy[1], Number)) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(xy[0], dtype_str, dev_str)
    y = tensor_fn(xy[1], dtype_str, dev_str)
    ret = ivy.maximum(x, y)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    if len(x.shape) > len(y.shape):
        assert ret.shape == x.shape
    else:
        assert ret.shape == y.shape
    # value test
    assert np.array_equal(call(ivy.maximum, x, y), ivy.numpy.maximum(ivy.to_numpy(x), ivy.to_numpy(y)))
    # compilation test
    helpers.assert_compilable(ivy.maximum)


# clip
@pytest.mark.parametrize(
    "x_min_n_max", [(-0.5, 0., 1.5), ([1.7], [0.5], [1.1]), ([[0.8, 2.2], [1.5, 0.2]], 0.2, 1.4),
                    ([[0.8, 2.2], [1.5, 0.2]], [[1., 1.], [1., 1.]], [[1.1, 2.], [1.1, 2.]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_clip(x_min_n_max, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(x_min_n_max[0], Number) or isinstance(x_min_n_max[1], Number) or isinstance(x_min_n_max[2], Number))\
            and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x_min_n_max[0], dtype_str, dev_str)
    min_val = tensor_fn(x_min_n_max[1], dtype_str, dev_str)
    max_val = tensor_fn(x_min_n_max[2], dtype_str, dev_str)
    if ((min_val.shape != [] and min_val.shape != [1]) or (max_val.shape != [] and max_val.shape != [1]))\
            and call in [helpers.torch_call, helpers.mx_call]:
        # pytorch and mxnet only support numbers or 0 or 1 dimensional arrays for min and max while performing clip
        pytest.skip()
    ret = ivy.clip(x, min_val, max_val)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    max_shape = max([x.shape, min_val.shape, max_val.shape], key=lambda x_: len(x_))
    assert ret.shape == max_shape
    # value test
    assert np.array_equal(call(ivy.clip, x, min_val, max_val),
                          ivy.numpy.clip(ivy.to_numpy(x), ivy.to_numpy(min_val), ivy.to_numpy(max_val)))
    # compilation test
    helpers.assert_compilable(ivy.clip)


# round
@pytest.mark.parametrize(
    "x_n_x_rounded", [(-0.51, -1), ([1.7], [2.]), ([[0.8, 2.2], [1.51, 0.2]], [[1., 2.], [2., 0.]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_round(x_n_x_rounded, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(x_n_x_rounded[0], Number) or isinstance(x_n_x_rounded[1], Number))\
            and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x_n_x_rounded[0], dtype_str, dev_str)
    ret = ivy.round(x)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == x.shape
    # value test
    assert np.array_equal(call(ivy.round, x), np.array(x_n_x_rounded[1]))
    # compilation test
    helpers.assert_compilable(ivy.round)


# floormod
@pytest.mark.parametrize(
    "x_n_divisor_n_x_floormod", [(2.5, 2., 0.5), ([10.7], [5.], [0.7]),
                                 ([[0.8, 2.2], [1.7, 0.2]], [[0.3, 0.5], [0.4, 0.11]], [[0.2, 0.2], [0.1, 0.09]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_floormod(x_n_divisor_n_x_floormod, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(x_n_divisor_n_x_floormod[0], Number) or isinstance(x_n_divisor_n_x_floormod[1], Number) or
            isinstance(x_n_divisor_n_x_floormod[2], Number)) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x_n_divisor_n_x_floormod[0], dtype_str, dev_str)
    divisor = ivy.array(x_n_divisor_n_x_floormod[1], dtype_str, dev_str)
    ret = ivy.floormod(x, divisor)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == x.shape
    # value test
    assert np.allclose(call(ivy.floormod, x, divisor), np.array(x_n_divisor_n_x_floormod[2]))
    # compilation test
    helpers.assert_compilable(ivy.floormod)


# floor
@pytest.mark.parametrize(
    "x_n_x_floored", [(2.5, 2.), ([10.7], [10.]), ([[3.8, 2.2], [1.7, 0.2]], [[3., 2.], [1., 0.]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_floor(x_n_x_floored, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(x_n_x_floored[0], Number) or isinstance(x_n_x_floored[1], Number))\
            and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x_n_x_floored[0], dtype_str, dev_str)
    ret = ivy.floor(x)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == x.shape
    # value test
    assert np.allclose(call(ivy.floor, x), np.array(x_n_x_floored[1]))
    # compilation test
    helpers.assert_compilable(ivy.floor)


# ceil
@pytest.mark.parametrize(
    "x_n_x_ceiled", [(2.5, 3.), ([10.7], [11.]), ([[3.8, 2.2], [1.7, 0.2]], [[4., 3.], [2., 1.]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_ceil(x_n_x_ceiled, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(x_n_x_ceiled[0], Number) or isinstance(x_n_x_ceiled[1], Number))\
            and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x_n_x_ceiled[0], dtype_str, dev_str)
    ret = ivy.ceil(x)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == x.shape
    # value test
    assert np.allclose(call(ivy.ceil, x), np.array(x_n_x_ceiled[1]))
    # compilation test
    helpers.assert_compilable(ivy.ceil)


# abs
@pytest.mark.parametrize(
    "x_n_x_absed", [(-2.5, 2.5), ([-10.7], [10.7]), ([[-3.8, 2.2], [1.7, -0.2]], [[3.8, 2.2], [1.7, 0.2]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_abs(x_n_x_absed, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(x_n_x_absed[0], Number) or isinstance(x_n_x_absed[1], Number))\
            and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x_n_x_absed[0], dtype_str, dev_str)
    ret = ivy.abs(x)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == x.shape
    # value test
    assert np.allclose(call(ivy.abs, x), np.array(x_n_x_absed[1]))
    # compilation test
    helpers.assert_compilable(ivy.abs)


# argmax
@pytest.mark.parametrize(
    "x_n_axis_x_argmax", [([-0.3, 0.1], None, [1]), ([[1.3, 2.6], [2.3, 2.5]], 0, [1, 0]),
                          ([[1.3, 2.6], [2.3, 2.5]], 1, [1, 1])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_argmax(x_n_axis_x_argmax, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x = ivy.array(x_n_axis_x_argmax[0], dtype_str, dev_str)
    axis = x_n_axis_x_argmax[1]
    ret = ivy.argmax(x, axis)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert tuple(ret.shape) == (len(x.shape),)
    # value test
    assert np.allclose(call(ivy.argmax, x, axis), np.array(x_n_axis_x_argmax[2]))
    # compilation test
    helpers.assert_compilable(ivy.argmax)


# argmin
@pytest.mark.parametrize(
    "x_n_axis_x_argmin", [([-0.3, 0.1], None, [0]), ([[1.3, 2.6], [2.3, 2.5]], 0, [0, 1]),
                          ([[1.3, 2.6], [2.3, 2.5]], 1, [0, 0])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_argmin(x_n_axis_x_argmin, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x = tensor_fn(x_n_axis_x_argmin[0], dtype_str, dev_str)
    axis = x_n_axis_x_argmin[1]
    ret = ivy.argmin(x, axis)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert tuple(ret.shape) == (len(x.shape),)
    # value test
    assert np.allclose(call(ivy.argmin, x, axis), np.array(x_n_axis_x_argmin[2]))
    # compilation test
    helpers.assert_compilable(ivy.argmin)


# cast
@pytest.mark.parametrize(
    "object_in", [[1], [True], [[1., 2.]]])
@pytest.mark.parametrize(
    "starting_dtype_str", ['float32', 'int32', 'bool'])
@pytest.mark.parametrize(
    "target_dtype_str", ['float32', 'int32', 'bool'])
def test_cast(object_in, starting_dtype_str, target_dtype_str, dev_str, call):
    # smoke test
    x = ivy.array(object_in, starting_dtype_str, dev_str)
    ret = ivy.cast(x, target_dtype_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == x.shape
    # value test
    assert ivy.dtype_str(ret) == target_dtype_str
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting does not support .type() method
        return
    helpers.assert_compilable(ivy.cast)


# arange
@pytest.mark.parametrize(
    "stop_n_start_n_step", [[10, None, None], [10, 2, None], [10, 2, 2]])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_arange(stop_n_start_n_step, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    stop, start, step = stop_n_start_n_step
    if (isinstance(stop, Number) or isinstance(start, Number) or isinstance(step, Number))\
            and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    if tensor_fn == _var_fn and call is helpers.torch_call:
        # pytorch does not support arange using variables as input
        pytest.skip()
    args = list()
    if stop:
        stop = tensor_fn(stop, dtype_str, dev_str)
        args.append(stop)
    if start:
        start = tensor_fn(start, dtype_str, dev_str)
        args.append(start)
    if step:
        step = tensor_fn(step, dtype_str, dev_str)
        args.append(step)
    ret = ivy.arange(*args, dtype_str=dtype_str, dev_str=dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == (int((ivy.to_list(stop) -
                              (ivy.to_list(start) if start else 0))/(ivy.to_list(step) if step else 1)),)
    # value test
    assert np.array_equal(call(ivy.arange, *args, dtype_str=dtype_str, dev_str=dev_str),
                          ivy.numpy.arange(*[ivy.to_numpy(arg) for arg in args], dtype_str=dtype_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting does not support Number type, or Union for Union[float, int] etc.
        return
    helpers.assert_compilable(ivy.arange)


# linspace
@pytest.mark.parametrize(
    "start_n_stop_n_num_n_axis", [[1, 10, 100, None], [[[0., 1., 2.]], [[1., 2., 3.]], 150, -1],
                                  [[[[-0.1471, 0.4477, 0.2214]]], [[[-0.3048, 0.3308, 0.2721]]], 6, -2]])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_linspace(start_n_stop_n_num_n_axis, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    start, stop, num, axis = start_n_stop_n_num_n_axis
    if (isinstance(start, Number) or isinstance(stop, Number))\
            and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    start = tensor_fn(start, dtype_str, dev_str)
    stop = tensor_fn(stop, dtype_str, dev_str)
    ret = ivy.linspace(start, stop, num, axis, dev_str=dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    target_shape = list(start.shape)
    target_shape.insert(axis + 1 if (axis and axis != -1) else len(target_shape), num)
    assert ret.shape == tuple(target_shape)
    # value test
    assert np.allclose(call(ivy.linspace, start, stop, num, axis, dev_str=dev_str),
                       ivy.numpy.linspace(ivy.to_numpy(start), ivy.to_numpy(stop), num, axis))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting does not support numpy conversion
        return
    helpers.assert_compilable(ivy.linspace)


# concatenate
@pytest.mark.parametrize(
    "x1_n_x2_n_axis", [(1, 10, 0), ([[0., 1., 2.]], [[1., 2., 3.]], 0), ([[0., 1., 2.]], [[1., 2., 3.]], 1),
                       ([[[-0.1471, 0.4477, 0.2214]]], [[[-0.3048, 0.3308, 0.2721]]], -1)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_concatenate(x1_n_x2_n_axis, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x1, x2, axis = x1_n_x2_n_axis
    if (isinstance(x1, Number) or isinstance(x2, Number)) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x1 = tensor_fn(x1, dtype_str, dev_str)
    x2 = tensor_fn(x2, dtype_str, dev_str)
    ret = ivy.concatenate((x1, x2), axis)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    axis_val = (axis % len(x1.shape) if (axis is not None and len(x1.shape) != 0) else len(x1.shape) - 1)
    if x1.shape == ():
        expected_shape = (2,)
    else:
        expected_shape = tuple([item * 2 if i == axis_val else item for i, item in enumerate(x1.shape)])
    assert ret.shape == expected_shape
    # value test
    assert np.allclose(call(ivy.concatenate, [x1, x2], axis),
                       ivy.numpy.concatenate([ivy.to_numpy(x1), ivy.to_numpy(x2)], axis))
    # compilation test
    helpers.assert_compilable(ivy.concatenate)


# flip
@pytest.mark.parametrize(
    "x_n_axis_n_bs", [(1, 0, None), ([[0., 1., 2.]], None, (1, 3)), ([[0., 1., 2.]], 1, (1, 3)),
                       ([[[-0.1471, 0.4477, 0.2214]]], None, None)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_flip(x_n_axis_n_bs, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, axis, bs = x_n_axis_n_bs
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.flip(x, axis, bs)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == x.shape
    # value test
    assert np.allclose(call(ivy.flip, x, axis, bs), ivy.numpy.flip(ivy.to_numpy(x), axis, bs))
    # compilation test
    helpers.assert_compilable(ivy.flip)


# stack
@pytest.mark.parametrize(
    "xs_n_axis", [((1, 0), -1), (([[0., 1., 2.]], [[3., 4., 5.]]), 0), (([[0., 1., 2.]], [[3., 4., 5.]]), 1)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_stack(xs_n_axis, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    (x1, x2), axis = xs_n_axis
    if (isinstance(x1, Number) or isinstance(x2, Number)) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x1 = tensor_fn(x1, dtype_str, dev_str)
    x2 = tensor_fn(x2, dtype_str, dev_str)
    ret = ivy.stack((x1, x2), axis)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    axis_val = (axis % len(x1.shape) if (axis is not None and len(x1.shape) != 0) else len(x1.shape) - 1)
    if x1.shape == ():
        expected_shape = (2,)
    else:
        expected_shape = list(x1.shape)
        expected_shape.insert(axis_val, 2)
    assert ret.shape == tuple(expected_shape)
    # value test
    assert np.allclose(call(ivy.stack, (x1, x2), axis), ivy.numpy.stack((ivy.to_numpy(x1), ivy.to_numpy(x2)), axis))
    # compilation test
    helpers.assert_compilable(ivy.stack)


# unstack
@pytest.mark.parametrize(
    "x_n_axis", [(1, -1), ([[0., 1., 2.]], 0), ([[0., 1., 2.]], 1)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_unstack(x_n_axis, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, axis = x_n_axis
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.unstack(x, axis)
    # type test
    assert isinstance(ret, list)
    # cardinality test
    axis_val = (axis % len(x.shape) if (axis is not None and len(x.shape) != 0) else len(x.shape) - 1)
    if x.shape == ():
        expected_shape = ()
    else:
        expected_shape = list(x.shape)
        expected_shape.pop(axis_val)
    assert ret[0].shape == tuple(expected_shape)
    # value test
    assert np.allclose(call(ivy.unstack, x, axis), ivy.numpy.unstack(ivy.to_numpy(x), axis))
    # compilation test
    helpers.assert_compilable(ivy.unstack)


# split
@pytest.mark.parametrize(
    "x_n_secs_n_axis", [(1, 1, -1), ([[0., 1., 2., 3.]], 2, 1), ([[0., 1., 2.], [3., 4., 5.]], 2, 0)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_split(x_n_secs_n_axis, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, secs, axis = x_n_secs_n_axis
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.split(x, secs, axis)
    # type test
    assert isinstance(ret, list)
    # cardinality test
    axis_val = (axis % len(x.shape) if (axis is not None and len(x.shape) != 0) else len(x.shape) - 1)
    if x.shape == ():
        expected_shape = ()
    else:
        expected_shape = tuple([int(item/secs) if i == axis_val else item for i, item in enumerate(x.shape)])
    assert ret[0].shape == tuple(expected_shape)
    # value test
    assert np.allclose(call(ivy.split, x, secs, axis), ivy.numpy.split(ivy.to_numpy(x), secs, axis))
    # compilation test
    helpers.assert_compilable(ivy.split)


# tile
@pytest.mark.parametrize(
    "x_n_reps", [(1, [1]), (1, 2), (1, [2]), ([[0., 1., 2., 3.]], (2, 1))])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_tile(x_n_reps, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, reps_raw = x_n_reps
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret_from_list = ivy.tile(x, reps_raw)
    reps = ivy.array(reps_raw, 'int32', dev_str)
    ret = ivy.tile(x, reps)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    if x.shape == ():
        expected_shape = tuple(reps_raw) if isinstance(reps_raw, list) else (reps_raw,)
    else:
        expected_shape = tuple([int(item * rep) for item, rep in zip(x.shape, reps_raw)])
    assert ret.shape == expected_shape
    # value test
    assert np.allclose(call(ivy.tile, x, reps), ivy.numpy.tile(ivy.to_numpy(x), ivy.to_numpy(reps)))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting does not support numpy conversion
        return
    helpers.assert_compilable(ivy.tile)


# zero_pad
@pytest.mark.parametrize(
    "x_n_pw", [(1, [[1, 1]]), (1, [[0, 0]]), ([[0., 1., 2., 3.]], [[0, 1], [1, 2]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_zero_pad(x_n_pw, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, pw_raw = x_n_pw
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret_from_list = ivy.zero_pad(x, pw_raw)
    pw = ivy.array(pw_raw, 'int32', dev_str)
    ret = ivy.zero_pad(x, pw)
    # type test
    try:
        assert isinstance(ret, ivy.Array)
    except AssertionError:
        assert isinstance(ret, Buffer)
    # cardinality test
    x_shape = [1] if x.shape == () else x.shape
    expected_shape = tuple([int(item + pw_[0] + pw_[1]) for item, pw_ in zip(x_shape, pw_raw)])
    assert ret.shape == expected_shape
    # value test
    assert np.allclose(call(ivy.zero_pad, x, pw), ivy.numpy.zero_pad(ivy.to_numpy(x), ivy.to_numpy(pw)))
    # compilation test
    if call is helpers.torch_call:
        # pytorch scripting does not support Union or Numbers for type hinting
        return
    helpers.assert_compilable(ivy.zero_pad)


# constant_pad
@pytest.mark.parametrize(
    "x_n_pw_n_val", [(1, [[1, 1]], 1.5), (1, [[0, 0]], -2.7), ([[0., 1., 2., 3.]], [[0, 1], [1, 2]], 11.)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_constant_pad(x_n_pw_n_val, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, pw_raw, val = x_n_pw_n_val
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret_from_list = ivy.constant_pad(x, pw_raw, val)
    pw = ivy.array(pw_raw, 'int32', dev_str)
    ret = ivy.constant_pad(x, pw, val)
    # type test
    try:
        assert isinstance(ret, ivy.Array)
    except AssertionError:
        assert isinstance(ret, Buffer)
    # cardinality test
    x_shape = [1] if x.shape == () else x.shape
    expected_shape = tuple([int(item + pw_[0] + pw_[1]) for item, pw_ in zip(x_shape, pw_raw)])
    assert ret.shape == expected_shape
    # value test
    assert np.allclose(call(ivy.constant_pad, x, pw, val),
                       ivy.numpy.constant_pad(ivy.to_numpy(x), ivy.to_numpy(pw), val))
    # compilation test
    if call is helpers.torch_call:
        # pytorch scripting does not support Union or Numbers for type hinting
        return
    helpers.assert_compilable(ivy.constant_pad)


# swapaxes
@pytest.mark.parametrize(
    "x_n_ax0_n_ax1", [([[1.]], 0, 1), ([[0., 1., 2., 3.]], 1, 0), ([[[0., 1., 2.], [3., 4., 5.]]], -2, -1)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_swapaxes(x_n_ax0_n_ax1, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, ax0, ax1 = x_n_ax0_n_ax1
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.swapaxes(x, ax0, ax1)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    expected_shape = list(x.shape)
    expected_shape[ax0], expected_shape[ax1] = expected_shape[ax1], expected_shape[ax0]
    assert ret.shape == tuple(expected_shape)
    # value test
    assert np.allclose(call(ivy.swapaxes, x, ax0, ax1),
                       ivy.numpy.swapaxes(ivy.to_numpy(x), ax0, ax1))
    # compilation test
    helpers.assert_compilable(ivy.swapaxes)


# transpose
@pytest.mark.parametrize(
    "x_n_axes", [([[1.]], [1, 0]), ([[0., 1., 2., 3.]], [1, 0]), ([[[0., 1., 2.], [3., 4., 5.]]], [0, 2, 1])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_transpose(x_n_axes, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, axes = x_n_axes
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.transpose(x, axes)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    x_shape = x.shape
    assert ret.shape == tuple([x.shape[idx] for idx in axes])
    # value test
    assert np.allclose(call(ivy.transpose, x, axes), ivy.numpy.transpose(ivy.to_numpy(x), axes))
    # compilation test
    helpers.assert_compilable(ivy.transpose)


# expand_dims
@pytest.mark.parametrize(
    "x_n_axis", [(1., 0), (1., -1), ([1.], 0), ([[0., 1., 2., 3.]], -2), ([[[0., 1., 2.], [3., 4., 5.]]], -3)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_expand_dims(x_n_axis, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, axis = x_n_axis
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.expand_dims(x, axis)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    expected_shape = list(x.shape)
    expected_shape.insert(axis, 1)
    assert ret.shape == tuple(expected_shape)
    # value test
    assert np.allclose(call(ivy.expand_dims, x, axis), ivy.numpy.expand_dims(ivy.to_numpy(x), axis))
    # compilation test
    helpers.assert_compilable(ivy.expand_dims)


# where
@pytest.mark.parametrize(
    "cond_n_x1_n_x2", [(True, 2., 3.), (0., 2., 3.), ([True], [2.], [3.]), ([[0.]], [[2., 3.]], [[4., 5.]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_where(cond_n_x1_n_x2, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    cond, x1, x2 = cond_n_x1_n_x2
    if (isinstance(cond, Number) or isinstance(x1, Number) or isinstance(x2, Number))\
            and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    cond = tensor_fn(cond, dtype_str, dev_str)
    x1 = tensor_fn(x1, dtype_str, dev_str)
    x2 = tensor_fn(x2, dtype_str, dev_str)
    ret = ivy.where(cond, x1, x2)
    # type test
    try:
        assert isinstance(ret, ivy.Array)
    except AssertionError:
        assert isinstance(ret, Buffer)
    # cardinality test
    assert ret.shape == x1.shape
    # value test
    assert np.allclose(call(ivy.where, cond, x1, x2),
                       ivy.numpy.where(ivy.to_numpy(cond), ivy.to_numpy(x1), ivy.to_numpy(x2)))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting does not support .type() method
        return
    helpers.assert_compilable(ivy.where)


# indices_where
@pytest.mark.parametrize(
    "x", [[True], [[0., 1.], [2., 3.]]])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_indices_where(x, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.indices_where(x)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape[-1] == len(x.shape)
    # value test
    assert np.allclose(call(ivy.indices_where, x), ivy.numpy.indices_where(ivy.to_numpy(x)))
    # compilation test
    helpers.assert_compilable(ivy.indices_where)


# reshape
@pytest.mark.parametrize(
    "x_n_shp", [(1., (1, 1)), (1., []), ([[1.]], []), ([[0., 1.], [2., 3.]], (1, 4, 1))])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_reshape(x_n_shp, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, new_shape = x_n_shp
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.reshape(x, new_shape)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == tuple(new_shape)
    # value test
    assert np.allclose(call(ivy.reshape, x, new_shape), ivy.numpy.reshape(ivy.to_numpy(x), new_shape))
    # compilation test
    helpers.assert_compilable(ivy.reshape)


# squeeze
@pytest.mark.parametrize(
    "x_n_axis", [(1., 0), (1., -1), ([[1.]], None), ([[[0.], [1.]], [[2.], [3.]]], -1)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_squeeze(x_n_axis, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, axis = x_n_axis
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.squeeze(x, axis)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    if axis is None:
        expected_shape = [item for item in x.shape if item != 1]
    elif x.shape == ():
        expected_shape = []
    else:
        expected_shape = list(x.shape)
        expected_shape.pop(axis)
    assert ret.shape == tuple(expected_shape)
    # value test
    assert np.allclose(call(ivy.squeeze, x, axis), ivy.numpy.squeeze(ivy.to_numpy(x), axis))
    # compilation test
    helpers.assert_compilable(ivy.squeeze)


# zeros
@pytest.mark.parametrize(
    "shape", [(), (1, 2, 3), tuple([1]*10)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_zeros(shape, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    ret = ivy.zeros(shape, dtype_str, dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == tuple(shape)
    # value test
    assert np.allclose(call(ivy.zeros, shape, dtype_str, dev_str), ivy.numpy.zeros(shape, dtype_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting cannot assign a torch.device value with a string
        return
    helpers.assert_compilable(ivy.zeros)


# zeros_like
@pytest.mark.parametrize(
    "x", [1, [1], [[1], [2], [3]]])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_zeros_like(x, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.zeros_like(x, dtype_str, dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == x.shape
    # value test
    assert np.allclose(call(ivy.zeros_like, x, dtype_str, dev_str), ivy.numpy.zeros_like(ivy.to_numpy(x), dtype_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting cannot assign a torch.device value with a string
        return
    helpers.assert_compilable(ivy.zeros_like)


# ones
@pytest.mark.parametrize(
    "shape", [(), (1, 2, 3), tuple([1]*10)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_ones(shape, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    ret = ivy.ones(shape, dtype_str, dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == tuple(shape)
    # value test
    assert np.allclose(call(ivy.ones, shape, dtype_str, dev_str), ivy.numpy.ones(shape, dtype_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting cannot assign a torch.device value with a string
        return
    helpers.assert_compilable(ivy.ones)


# ones_like
@pytest.mark.parametrize(
    "x", [1, [1], [[1], [2], [3]]])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_ones_like(x, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if isinstance(x, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.ones_like(x, dtype_str, dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == x.shape
    # value test
    assert np.allclose(call(ivy.ones_like, x, dtype_str, dev_str), ivy.numpy.ones_like(ivy.to_numpy(x), dtype_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting cannot assign a torch.device value with a string
        return
    helpers.assert_compilable(ivy.ones_like)


# one_hot
@pytest.mark.parametrize(
    "ind_n_depth", [([0], 1), ([0, 1, 2], 3), ([[1, 3], [0, 0], [8, 4], [7, 9]], 10)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_one_hot(ind_n_depth, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    ind, depth = ind_n_depth
    if isinstance(ind, Number) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    ind = ivy.array(ind, 'int32', dev_str)
    ret = ivy.one_hot(ind, depth, dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == ind.shape + (depth,)
    # value test
    assert np.allclose(call(ivy.one_hot, ind, depth, dev_str), ivy.numpy.one_hot(ivy.to_numpy(ind), depth, dev_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting cannot assign a torch.device value with a string
        return
    helpers.assert_compilable(ivy.one_hot)


# cross
@pytest.mark.parametrize(
    "x1_n_x2", [([0., 1., 2.], [3., 4., 5.]), ([[0., 1., 2.], [2., 1., 0.]], [[3., 4., 5.], [5., 4., 3.]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_cross(x1_n_x2, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x1, x2 = x1_n_x2
    if (isinstance(x1, Number) or isinstance(x2, Number)) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x1 = ivy.array(x1, dtype_str, dev_str)
    x2 = ivy.array(x2, dtype_str, dev_str)
    ret = ivy.cross(x1, x2)
    # type test
    try:
        assert isinstance(ret, ivy.Array)
    except AssertionError:
        assert isinstance(ret, Buffer)
    # cardinality test
    assert ret.shape == x1.shape
    # value test
    assert np.allclose(call(ivy.cross, x1, x2), ivy.numpy.cross(ivy.to_numpy(x1), ivy.to_numpy(x2)))
    # compilation test
    helpers.assert_compilable(ivy.cross)


# matmul
@pytest.mark.parametrize(
    "x1_n_x2", [([[0., 1., 2.]], [[3.], [4.], [5.]]), ([[0., 1., 2.], [2., 1., 0.]], [[3., 4.], [5., 5.], [4., 3.]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_matmul(x1_n_x2, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x1, x2 = x1_n_x2
    if (isinstance(x1, Number) or isinstance(x2, Number)) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x1 = ivy.array(x1, dtype_str, dev_str)
    x2 = ivy.array(x2, dtype_str, dev_str)
    ret = ivy.matmul(x1, x2)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == x1.shape[:-1] + (x2.shape[-1],)
    # value test
    assert np.allclose(call(ivy.matmul, x1, x2), ivy.numpy.matmul(ivy.to_numpy(x1), ivy.to_numpy(x2)))
    # compilation test
    helpers.assert_compilable(ivy.matmul)


# cumsum
@pytest.mark.parametrize(
    "x_n_axis", [([[0., 1., 2.]], -1), ([[0., 1., 2.], [2., 1., 0.]], 0), ([[0., 1., 2.], [2., 1., 0.]], 1)])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_cumsum(x_n_axis, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    x, axis = x_n_axis
    x = ivy.array(x, dtype_str, dev_str)
    ret = ivy.cumsum(x, axis)
    # type test
    try:
        assert isinstance(ret, ivy.Array)
    except AssertionError:
        assert isinstance(ret, Buffer)
    # cardinality test
    assert ret.shape == x.shape
    # value test
    assert np.allclose(call(ivy.cumsum, x, axis), ivy.numpy.cumsum(ivy.to_numpy(x), axis))
    # compilation test
    helpers.assert_compilable(ivy.cumsum)


# identity
@pytest.mark.parametrize(
    "dim_n_bs", [(3, None), (1, (2, 3)), (5, (1, 2, 3))])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_identity(dim_n_bs, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    dim, bs = dim_n_bs
    ret = ivy.identity(dim, dtype_str, bs, dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == (tuple(bs) if bs else ()) + (dim, dim)
    # value test
    assert np.allclose(call(ivy.identity, dim, dtype_str, bs, dev_str), ivy.numpy.identity(dim, dtype_str, bs))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting cannot assign a torch.device value with a string
        return
    helpers.assert_compilable(ivy.identity)


# scatter_flat
@pytest.mark.parametrize(
    "inds_n_upd_n_size", [([0, 4, 1, 2], [1, 2, 3, 4], 8), ([0, 4, 1, 2, 0], [1, 2, 3, 4, 5], 8)])
@pytest.mark.parametrize(
    "red", ['sum', 'min', 'max', 'replace'])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_scatter_flat(inds_n_upd_n_size, red, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (red == 'sum' or red == 'min' or red == 'max') and call is helpers.mx_call:
        # mxnet does not support sum, min or max reduction for scattering
        pytest.skip()
    if red == 'replace' and call is not helpers.mx_call:
        # mxnet is the only backend which supports the replace reduction
        pytest.skip()
    inds, upd, size = inds_n_upd_n_size
    inds = ivy.array(inds, 'int32', dev_str)
    upd = tensor_fn(upd, dtype_str, dev_str)
    ret = ivy.scatter_flat(inds, upd, size, red, dev_str)
    # type test
    try:
        assert isinstance(ret, ivy.Array)
    except AssertionError:
        assert isinstance(ret, Buffer)
    # cardinality test
    assert ret.shape == (size,)
    if red == 'replace':
        return
    # value test
    assert np.allclose(call(ivy.scatter_flat, inds, upd, size, red, dev_str),
                       ivy.numpy.scatter_flat(ivy.to_numpy(inds), ivy.to_numpy(upd), size, red, dev_str))
    # compilation test
    if call in [helpers.torch_call]:
        # global torch_scatter var not supported when scripting
        return
    helpers.assert_compilable(ivy.scatter_flat)


# scatter_nd
@pytest.mark.parametrize(
    "inds_n_upd_n_shape", [([[4], [3], [1], [7]], [9, 10, 11, 12], [8]), ([[0, 1, 2]], [1], [3, 3, 3]),
                           ([[0], [2]], [[[5, 5, 5, 5], [6, 6, 6, 6], [7, 7, 7, 7], [8, 8, 8, 8]],
                                         [[5, 5, 5, 5], [6, 6, 6, 6], [7, 7, 7, 7], [8, 8, 8, 8]]], [4, 4, 4])])
@pytest.mark.parametrize(
    "red", ['sum', 'min', 'max', 'replace'])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_scatter_nd(inds_n_upd_n_shape, red, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (red == 'sum' or red == 'min' or red == 'max') and call is helpers.mx_call:
        # mxnet does not support sum, min or max reduction for scattering
        pytest.skip()
    if red == 'replace' and call is not helpers.mx_call:
        # mxnet is the only backend which supports the replace reduction
        pytest.skip()
    inds, upd, shape = inds_n_upd_n_shape
    inds = ivy.array(inds, 'int32', dev_str)
    upd = tensor_fn(upd, dtype_str, dev_str)
    ret = ivy.scatter_nd(inds, upd, shape, red, dev_str)
    # type test
    try:
        assert isinstance(ret, ivy.Array)
    except AssertionError:
        assert isinstance(ret, Buffer)
    # cardinality test
    assert ret.shape == tuple(shape)
    if red == 'replace':
        return
    # value test
    assert np.allclose(call(ivy.scatter_nd, inds, upd, shape, red, dev_str),
                       ivy.numpy.scatter_nd(ivy.to_numpy(inds), ivy.to_numpy(upd), shape, red, dev_str))
    # compilation test
    if call in [helpers.torch_call]:
        # global torch_scatter var not supported when scripting
        return
    helpers.assert_compilable(ivy.scatter_nd)


# gather_flat
@pytest.mark.parametrize(
    "prms_n_inds", [([9, 8, 7, 6, 5, 4, 3, 2, 1, 0], [0, 4, 7])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_gather_flat(prms_n_inds, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    prms, inds = prms_n_inds
    prms = tensor_fn(prms, dtype_str, dev_str)
    inds = ivy.array(inds, 'int32', dev_str)
    ret = ivy.gather_flat(prms, inds, dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == inds.shape
    # value test
    assert np.allclose(call(ivy.gather_flat, prms, inds, dev_str),
                       ivy.numpy.gather_flat(ivy.to_numpy(prms), ivy.to_numpy(inds), dev_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting cannot assign a torch.device value with a string
        return
    helpers.assert_compilable(ivy.gather_flat)


# gather_nd
@pytest.mark.parametrize(
    "prms_n_inds", [([[[0.0, 1.0], [2.0, 3.0]], [[0.1, 1.1], [2.1, 3.1]]], [[0, 1], [1, 0]]),
                    ([[[0.0, 1.0], [2.0, 3.0]], [[0.1, 1.1], [2.1, 3.1]]], [[[0, 1]], [[1, 0]]]),
                    ([[[0.0, 1.0], [2.0, 3.0]], [[0.1, 1.1], [2.1, 3.1]]], [[[0, 1, 0]], [[1, 0, 1]]])])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_gather_nd(prms_n_inds, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    prms, inds = prms_n_inds
    prms = tensor_fn(prms, dtype_str, dev_str)
    inds = ivy.array(inds, 'int32', dev_str)
    ret = ivy.gather_nd(prms, inds, dev_str)
    # type test
    assert isinstance(ret, ivy.Array)
    # cardinality test
    assert ret.shape == inds.shape[:-1] + prms.shape[inds.shape[-1]:]
    # value test
    assert np.allclose(call(ivy.gather_nd, prms, inds, dev_str),
                       ivy.numpy.gather_nd(ivy.to_numpy(prms), ivy.to_numpy(inds), dev_str))
    # compilation test
    if call in [helpers.torch_call]:
        # pytorch scripting cannot assign a torch.device value with a string
        return
    helpers.assert_compilable(ivy.gather_nd)


# dev
@pytest.mark.parametrize(
    "x", [1, [], [1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_dev(x, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.dev(x)
    # type test
    assert isinstance(ret, ivy.Device)
    # compilation test
    helpers.assert_compilable(ivy.dev)


# dev_to_str
@pytest.mark.parametrize(
    "x", [1, [], [1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_dev_to_str(x, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    dev = ivy.dev(x)
    ret = ivy.dev_to_str(dev)
    # type test
    assert isinstance(ret, str)
    # value test
    assert ret == dev_str
    # compilation test
    helpers.assert_compilable(ivy.dev_to_str)


# dev_str
@pytest.mark.parametrize(
    "x", [1, [], [1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_dev_str(x, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.dev_str(x)
    # type test
    assert isinstance(ret, str)
    # value test
    assert ret == dev_str
    # compilation test
    helpers.assert_compilable(ivy.dev_str)


# dtype
@pytest.mark.parametrize(
    "x", [1, [], [1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "dtype_str", [None, 'float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64', 'bool'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array])
def test_dtype(x, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if call in [helpers.mx_call] and dtype_str == 'int16':
        # mxnet does not support int16
        pytest.skip()
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.dtype(x)
    # type test
    assert isinstance(ret, ivy.Dtype)
    # compilation test
    helpers.assert_compilable(ivy.dtype)


# dtype_to_str
@pytest.mark.parametrize(
    "x", [1, [], [1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "dtype_str", ['float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64', 'bool'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array])
def test_dtype_to_str(x, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if call is helpers.mx_call and dtype_str == 'int16':
        # mxnet does not support int16
        pytest.skip()
    if call is helpers.jnp_call and dtype_str in ['int64', 'float64']:
        # jax does not support int64 or float64 arrays
        pytest.skip()
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    dtype = ivy.dtype(x)
    ret = ivy.dtype_to_str(dtype)
    # type test
    assert isinstance(ret, str)
    # value test
    assert ret == dtype_str
    # compilation test
    helpers.assert_compilable(ivy.dtype_to_str)


# dtype_str
@pytest.mark.parametrize(
    "x", [1, [], [1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "dtype_str", ['float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64', 'bool'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array])
def test_dtype_str(x, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if call is helpers.mx_call and dtype_str == 'int16':
        # mxnet does not support int16
        pytest.skip()
    if call is helpers.jnp_call and dtype_str in ['int64', 'float64']:
        # jax does not support int64 or float64 arrays
        pytest.skip()
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    ret = ivy.dtype_str(x)
    # type test
    assert isinstance(ret, str)
    # value test
    assert ret == dtype_str
    # compilation test
    helpers.assert_compilable(ivy.dtype_str)


# compile_fn
def _fn_1(x):
    return x**2


def _fn_2(x):
    return (x + 10)**0.5 - 5


@pytest.mark.parametrize(
    "x", [[1], [[0.0, 1.0], [2.0, 3.0]]])
@pytest.mark.parametrize(
    "fn", [_fn_1, _fn_2])
@pytest.mark.parametrize(
    "dtype_str", ['float32'])
@pytest.mark.parametrize(
    "tensor_fn", [ivy.array, _var_fn])
def test_compile_fn(x, fn, dtype_str, tensor_fn, dev_str, call):
    # smoke test
    if (isinstance(x, Number) or len(x) == 0) and tensor_fn == _var_fn and call is helpers.mx_call:
        # mxnet does not support 0-dimensional variables
        pytest.skip()
    x = tensor_fn(x, dtype_str, dev_str)
    comp_fn = ivy.compile_fn(fn)
    # type test
    assert callable(comp_fn)
    # value test
    non_compiled_return = fn(x)
    compiled_return = comp_fn(x)
    assert np.allclose(ivy.to_numpy(non_compiled_return), ivy.to_numpy(compiled_return))
