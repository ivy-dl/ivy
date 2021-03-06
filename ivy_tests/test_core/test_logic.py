"""
Collection of tests for templated logic functions
"""

# global
import numpy as np

# local
import ivy
import ivy_tests.helpers as helpers


def test_logical_and(dev_str, call):
    assert np.array_equal(call(ivy.logical_and, ivy.array([True, True]),
                               ivy.array([False, True])),
                          np.logical_and(np.array([True, True]), np.array([False, True])))
    assert np.array_equal(call(ivy.logical_and, ivy.array([[0.]]),
                               ivy.array([[1.]])),
                          np.logical_and(np.array([[0.]]), np.array([[1.]])))
    if call in [helpers.torch_call]:
        # pytorch scripting does not support .type() method
        return
    helpers.assert_compilable(ivy.logical_and)


def test_logical_or(dev_str, call):
    assert np.array_equal(call(ivy.logical_or, ivy.array([True, True]),
                               ivy.array([False, True])),
                          np.logical_or(np.array([True, True]), np.array([False, True])))
    assert np.array_equal(call(ivy.logical_or, ivy.array([[0.]]),
                               ivy.array([[1.]])),
                          np.logical_or(np.array([[0.]]), np.array([[1.]])))
    if call in [helpers.torch_call]:
        # pytorch scripting does not support .type() method
        return
    helpers.assert_compilable(ivy.logical_or)


def test_logical_not(dev_str, call):
    assert np.array_equal(call(ivy.logical_not, ivy.array([True, True])),
                          np.logical_not(np.array([True, True])))
    assert np.array_equal(call(ivy.logical_not, ivy.array([[0.]])),
                          np.logical_not(np.array([[0.]])))
    if call in [helpers.torch_call]:
        # pytorch scripting does not support .type() method
        return
    helpers.assert_compilable(ivy.logical_not)
