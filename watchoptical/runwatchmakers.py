import os


def path_to_watchmakers_script() -> str:
    return os.sep.join((os.env['WATCHENV'],
                        "watchmakers.py"
                        ))