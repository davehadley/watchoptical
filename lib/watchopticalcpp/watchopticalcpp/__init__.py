def convert_ratpacbonsai_to_analysis(
    ratpac: str, bonsai: str, analysisfile: str
) -> None:
    from ._watchopticalcpp import convert_ratpacbonsai_to_analysis  # noqa

    convert_ratpacbonsai_to_analysis(ratpac, bonsai, analysisfile)
