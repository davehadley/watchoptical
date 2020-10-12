import inspect
from typing import List, Optional


def ratmacro() -> Optional[str]:
    snippets: List[str] = []
    # this doesn't actually work, need to use makeratdb instead
    # if attenuation is not None:
    #     snippets.append(_attenuationmacro(attenuation))
    if len(snippets) > 0:
        return "\n".join(snippets)
    else:
        return None


def _attenuationmacro(attenuation: float) -> str:
    attstring = "%.6e" % attenuation
    return inspect.cleandoc(
        f"""
    /rat/db/set OPTICS[water] ABSLENGTH_value1 60.0 200.0 800.0
    /rat/db/set OPTICS[water] ABSLENGTH_value2 {attstring} {attstring} {attstring}
    /rat/db/set OPTICS[salt_water] ABSLENGTH_value1 60.0 200.0 800.0
    /rat/db/set OPTICS[salt_water] ABSLENGTH_value2 {attstring} {attstring} {attstring}
    """  # noqa
    )
