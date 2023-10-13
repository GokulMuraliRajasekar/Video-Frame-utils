import time


def timeit(func):

    def wrapper():
        start_time = time.time()
        func()
        time_elapsed = time.time() - start_time
        print(f"{func.__name__} executed in {round(time_elapsed, 2)}'s")

    return wrapper


@timeit
def decFunc():
    time.sleep(2)


decFunc()
