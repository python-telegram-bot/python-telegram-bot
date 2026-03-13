import re


def to_camel_case(snake_str):
    """https://stackoverflow.com/a/19053800"""
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


def to_snake_case(camel_str):
    """https://stackoverflow.com/a/1176023"""
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
