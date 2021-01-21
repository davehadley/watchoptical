from watchoptical.internal.stringconstants import StringConstants


def issignalfile(filename: str) -> bool:
    return StringConstants.WATCHMAKERS_SIGNAL_PATTERN in filename


def isbackgroundfile(filename: str) -> bool:
    return StringConstants.WATCHMAKERS_SIGNAL_PATTERN not in filename
