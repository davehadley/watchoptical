import inspect
import json
from typing import Any, NamedTuple, Optional

import numpy as np


class RatDbConfig(NamedTuple):
    attenuation: Optional[float] = None
    scattering: Optional[float] = None


class RatDb(NamedTuple):
    json: Optional[str]
    config: RatDbConfig


def makeratdb(
    attenuation: Optional[float] = None, scattering: Optional[float] = None
) -> RatDb:
    config = RatDbConfig(attenuation=attenuation, scattering=scattering)
    return RatDb(json=makeratdbjson(config), config=config)


def makeratdbjson(config: RatDbConfig) -> Optional[str]:
    snippets: Any = []
    if config.attenuation is not None:
        snippets.append(_attenuationjson(config.attenuation))
    if config.scattering is not None:
        snippets.append(_scatteringjson(config.scattering))
    if len(snippets) > 0:
        snippets = "\n".join(snippets)
        result = inspect.cleandoc(
            f"""
        {{
        "name": "OPTICS",
        "index": "doped_water",
        {snippets}
        "run_range": [-1,-1]
        }}
        """
        )
        print("DEBUG", result)
        assert json.loads(result)
        return result
    else:
        return None


# Nominal values
_nominal_doped_water_RSLENGTH_value1 = [
    190.0,
    200.0,
    210.0,
    220.0,
    230.0,
    240.0,
    250.0,
    260.0,
    270.0,
    280.0,
    290.0,
    300.0,
    310.0,
    320.0,
    330.0,
    340.0,
    350.0,
    360.0,
    370.0,
    380.0,
    390.0,
    400.0,
    410.0,
    420.0,
    430.0,
    440.0,
    450.0,
    460.0,
    470.0,
    480.0,
    490.0,
    500.0,
    510.0,
    520.0,
    530.0,
    540.0,
    550.0,
    560.0,
    570.0,
    580.0,
    590.0,
    600.0,
    610.0,
    620.0,
    630.0,
    640.0,
    650.0,
    660.0,
    670.0,
    680.0,
    690.0,
    700.0,
    710.0,
    720.0,
    730.0,
]
_nominal_doped_water_RSLENGTH_value2 = [
    2122.03,
    3054.65,
    3987.27,
    5131.29,
    6518.85,
    8184.56,
    10165.5,
    12501.0,
    15232.8,
    18405.0,
    22064.0,
    26258.1,
    31038.4,
    36457.4,
    42570.3,
    49433.5,
    57106.6,
    65650.2,
    75126.9,
    85602.8,
    97142.7,
    109816.0,
    123694.0,
    138847.0,
    155351.0,
    173280.0,
    192716.0,
    213734.0,
    236413.0,
    260843.0,
    287105.0,
    315279.0,
    345470.0,
    377750.0,
    412223.0,
    448973.0,
    488103.0,
    529706.0,
    573879.0,
    620737.0,
    670356.0,
    722859.0,
    778345.0,
    836919.0,
    898711.0,
    963791.0,
    1032330.0,
    1104370.0,
    1180080.0,
    1259550.0,
    1342950.0,
    1430320.0,
    1521840.0,
    1617650.0,
    1717830.0,
]
_nominal_doped_water_ABSLENGTH_value1 = [
    190.0,
    200.0,
    210.0,
    220.0,
    230.0,
    240.0,
    250.0,
    260.0,
    270.0,
    280.0,
    290.0,
    300.0,
    310.0,
    320.0,
    330.0,
    340.0,
    350.0,
    360.0,
    370.0,
    380.0,
    390.0,
    400.0,
    410.0,
    420.0,
    430.0,
    440.0,
    450.0,
    460.0,
    470.0,
    480.0,
    490.0,
    500.0,
    510.0,
    520.0,
    530.0,
    540.0,
    550.0,
    560.0,
    570.0,
    580.0,
    590.0,
    600.0,
    610.0,
    620.0,
    630.0,
    640.0,
    650.0,
    660.0,
    670.0,
    680.0,
    690.0,
    700.0,
    710.0,
    720.0,
    730.0,
]
_nominal_doped_water_ABSLENGTH_value2 = [
    0.0,
    3086.42,
    7936.51,
    12422.4,
    16806.7,
    20703.9,
    26595.7,
    32467.5,
    42372.9,
    45045.0,
    61349.7,
    80645.2,
    89285.7,
    100000.0,
    50000.0,
    30769.2,
    49019.6,
    64102.6,
    87719.3,
    87950.7,
    117509.0,
    150830.0,
    211416.0,
    220264.0,
    202020.0,
    157480.0,
    108460.0,
    102145.0,
    94339.6,
    78740.2,
    66666.7,
    49019.6,
    30769.2,
    24449.9,
    23041.5,
    21097.0,
    17699.1,
    16155.1,
    14388.5,
    11160.7,
    7401.92,
    4496.4,
    3782.15,
    3629.76,
    3429.36,
    3217.5,
    2941.18,
    2439.02,
    2277.9,
    2150.54,
    1937.98,
    1602.56,
    1209.19,
    812.348,
    0.0,
]


def _attenuationjson(attenuation: float) -> str:
    abslength1 = json.dumps(_nominal_doped_water_ABSLENGTH_value1)
    abslength2 = json.dumps(
        list(np.array(_nominal_doped_water_ABSLENGTH_value2) * attenuation)
    )
    return inspect.cleandoc(
        f"""
      "ABSLENGTH_option": "wavelength",
      "ABSLENGTH_value1": {abslength1},
      "ABSLENGTH_value2": {abslength2},
    """
    )


def _scatteringjson(scatteringlength: float) -> str:
    rslength1 = json.dumps(_nominal_doped_water_RSLENGTH_value1)
    rslength2 = json.dumps(
        list(np.array(_nominal_doped_water_RSLENGTH_value2) * scatteringlength)
    )
    return inspect.cleandoc(
        f"""
      "RSLENGTH_option": "wavelength",
      "RSLENGTH_value1": {rslength1},
      "RSLENGTH_value2": {rslength2},
    """
    )
