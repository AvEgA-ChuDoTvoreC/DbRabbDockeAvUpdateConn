from time import time
import functools


class Meta(type):

    def __new__(mcs, name, bases, dict_: dict):
        for key, value in dict_.items():
            if isinstance(value, int):
                dict_[key] = value + 1
        return super().__new__(mcs, name, bases, dict_)


class A(metaclass=Meta):
    a = 1
    b = 1


class B:
    b = 1
    c = 1


class C(A, B):
    b = 1


# print(C.a)
# print(C.b)
# print(C.c)


def decorator(func):
    """Example sample

    Initialization:

    @decorator      |       The same as:
    def my_func():  |  -->   my_func = decorator(my_func)
        pass        |

    """

    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # Do something before
        value = func(*args, **kwargs)
        # Do something after
        return value

    return wrapper_decorator()


def my_timer(func):
    """Print the runtime of the decorated function"""

    def wrapper_timer(*args, **kwargs):
        start_time = time()                # 1
        value = func(*args, **kwargs)
        end_time = time()                  # 2
        run_time = end_time - start_time   # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} sec")
        return value

    return wrapper_timer

