from telegram.ext import ExtBot


def to_camel_case(snake_str):
    """https://stackoverflow.com/a/19053800"""
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + ''.join(x.title() for x in components[1:])


class TestCamelCase:
    def test_camel_case(self):
        invalid_camel_case_functions = []
        for function_name, function in ExtBot.__dict__.items():
            if (
                callable(function)
                and (camel_case_function := getattr(ExtBot, to_camel_case(function_name), False))
                and camel_case_function != function
            ):
                invalid_camel_case_functions.append(function_name)
        assert invalid_camel_case_functions == []
