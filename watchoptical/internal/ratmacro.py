import inspect


def ratmacro(attenuation: str) -> str:
    attenuation = "%.6e" % attenuation
    return inspect.cleandoc(f"""
    /rat/db/set OPTICS[water] ABSLENGTH_value1 60.0 200.0 800.0
    /rat/db/set OPTICS[water] ABSLENGTH_value2 {attenuation} {attenuation} {attenuation}
    /rat/db/set OPTICS[water] RSLENGTH_value1 60.0 200.0 800.0
    /rat/db/set OPTICS[water] RSLENGTH_value2 {attenuation} {attenuation} {attenuation}

    /rat/db/set OPTICS[salt_water] ABSLENGTH_value1 60.0 200.0 800.0
    /rat/db/set OPTICS[salt_water] ABSLENGTH_value2 {attenuation} {attenuation} {attenuation}
    /rat/db/set OPTICS[salt_water] RSLENGTH_value1 60.0 200.0 800.0
    /rat/db/set OPTICS[salt_water] RSLENGTH_value2 {attenuation} {attenuation} {attenuation}
    """)