from watchoptical.internal.ignoreerrors import ignoreerrors


def test_ignoreerrors_with_exception():
    @ignoreerrors
    def f():
        raise ValueError()

    assert f() is None


def test_ignoreerrors_without_exception():
    @ignoreerrors
    def f():
        return 1.0

    assert f() == 1.0
