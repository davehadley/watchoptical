from watchoptical.internal.utils.retry import retry


class _DummyException(Exception):
    pass


def test_retry_function_always_fails():
    count = [0]

    def inc(*args, **kwargs):
        count[0] += 1
        raise _DummyException()

    decorated = retry(3)(inc)

    try:
        decorated("ignored", key="wordargs")
    except _DummyException:
        pass
    finally:
        assert count == [3]


def test_retry_function_always_succeeds():
    count = [0]

    def inc(*args, **kwargs):
        count[0] += 1

    decorated = retry(3)(inc)

    try:
        decorated("ignored", key="wordargs")
    finally:
        assert count == [1]


def test_retry_function_fails_once():
    count = [0]

    def inc(*args, **kwargs):
        count[0] += 1
        if count[0] == 1:
            raise _DummyException

    decorated = retry(3)(inc)

    try:
        decorated("ignored", key="wordargs")
    finally:
        assert count == [2]
