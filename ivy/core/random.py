"""
Collection of random Ivy functions
"""

# local
from ivy.framework_handler import get_framework as _get_framework


def random_uniform(low=0.0, high=0.0, shape=None, dev='cpu', f=None):
    """
    Draws samples from a uniform distribution.
    Samples are uniformly distributed over the half-open interval [low, high) (includes low, but excludes high).
    In other words, any value within the given interval is equally likely to be drawn by uniform.

    :param low: Lower boundary of the output interval. All values generated will be greater than or equal to low.
                The default value is 0.
    :type low: float
    :param high: Upper boundary of the output interval. All values generated will be less than high.
                The default value is 1.0.
    :type high: float
    :param shape: Output shape. If the given shape is, e.g., (m, n, k), then m * n * k samples are drawn.
                    If size is None (default), a single value is returned.
    :param dev: device on which to create the array 'cuda:0', 'cuda:1', 'cpu' etc.
    :type dev: str
    :param f: Machine learning framework. Inferred from inputs if None.
    :type f: ml_framework, optional
    :return: Drawn samples from the parameterized uniform distribution.
    """
    return _get_framework(f=f).random_uniform(low, high, shape, dev)


def randint(low, high, shape, dev='cpu', f=None):
    """
    Returns a tensor filled with random integers generated uniformly between low (inclusive) and high (exclusive).

    :param low: Lowest integer to be drawn from the distribution.
    :type low: int
    :param high: One above the highest integer to be drawn from the distribution.
    :type high: int
    :param shape: a tuple defining the shape of the output tensor.
    :type shape: tuple
    :param dev: device on which to create the array 'cuda:0', 'cuda:1', 'cpu' etc.
    :type dev: str
    :param f: Machine learning framework. Inferred from inputs if None.
    :type f: ml_framework, optional
    :return:
    """
    return _get_framework(f=f).randint(low, high, shape, dev)


def seed(seed_value=0, f=None):
    """
    Sets the seed for random number generation.

    :param seed_value: Seed for random number generation.
    :type seed_value: int
    :param f: Machine learning framework. Inferred from inputs if None.
    :type f: ml_framework, optional
    """
    return _get_framework(f=f).seed(seed_value)


def shuffle(x, f=None):
    """
    Shuffles the given array along axis 0.

    :param x: An array object, in the specific Machine learning framework.
    :type x: array
    :param f: Machine learning framework. Inferred from inputs if None.
    :type f: ml_framework, optional
    :return: An array object, shuffled along the first dimension.
    """
    return _get_framework(x, f=f).shuffle(x)
