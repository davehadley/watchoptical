import inspect
from typing import Optional


def ratmacro(attenuation: Optional[float]=None, scattering: Optional[float]=None) -> Optional[str]:
    snippets = []
    if attenuation is not None:
        snippets.append(_attenuationmacro(attenuation))
    if scattering is not None:
        snippets.append(_scatteringmacro(scattering))
    if len(snippets) > 0:
        return "\n".join(snippets)
    else:
        return None


def _attenuationmacro(attenuation: float) -> str:
    attenuation = "%.6e" % attenuation
    return inspect.cleandoc(f"""
    /rat/db/set OPTICS[water] ABSLENGTH_value1 60.0 200.0 800.0
    /rat/db/set OPTICS[water] ABSLENGTH_value2 {attenuation} {attenuation} {attenuation}
    /rat/db/set OPTICS[salt_water] ABSLENGTH_value1 60.0 200.0 800.0
    /rat/db/set OPTICS[salt_water] ABSLENGTH_value2 {attenuation} {attenuation} {attenuation}
    """)


def _scatteringmacro(scattering: float) -> str:
    scattering = "%.6e" % scattering
    return inspect.cleandoc(f"""
    /rat/db/set OPTICS[water] RSLENGTH_value1 60.0 200.0 800.0
    /rat/db/set OPTICS[water] RSLENGTH_value2 {scattering} {scattering} {scattering}
    /rat/db/set OPTICS[salt_water] RSLENGTH_value1 60.0 200.0 800.0
    /rat/db/set OPTICS[salt_water] RSLENGTH_value2 {scattering} {scattering} {scattering}
    """)
