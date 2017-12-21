import sys


def verify_python3_or_exit():
    try:
        assert sys.version_info >= (3, 0)

    except AssertionError:
        print("Must be ran with Python 3 or greater")
        sys.exit()
