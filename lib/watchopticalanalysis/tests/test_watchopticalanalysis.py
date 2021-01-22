from watchopticalanalysis import __version__


def test_version():
    assert __version__ == "0.1.0"


def test_import_watchoptical_mc():
    import watchopticalmc

    assert watchopticalmc
