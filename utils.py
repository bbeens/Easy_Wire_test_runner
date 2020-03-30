import time


def wait_helper(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                value = func(*args, **kwargs)
                return value
            except kwargs['exception_to_handle']:
                print('Confirm Easy-Wire window has focus')
                time.sleep(1)
            except:
                time.sleep(1)

    return wrapper
