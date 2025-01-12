import warnings

# individual cell formatting defaults
DEFAULT_FORMATS = {
    "bold": False,
    "italic": False,
    "color": None,
    "escape": True,
    "class": None,
    "id": None,
}


def validate_format_dict(format_dict: dict) -> None:
    assert "value" in format_dict.keys()
    for key in format_dict.keys():
        if key == "value":
            continue
        if key not in DEFAULT_FORMATS.keys():
            warnings.warn(f"`{key}` in format dict will be unused.")
