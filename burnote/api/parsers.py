from datetime import timedelta

from flask_restful import reqparse, inputs


class NotesArgsParser:

    def __init__(self):
        self.get = reqparse.RequestParser()
        self.post = reqparse.RequestParser(bundle_errors=True)
        self.add_arguments()

    def add_arguments(self):
        self.get.add_argument('key', type=str, required=True,
                              help='The `key` parameter is required.')
        self.get.add_argument('password', type=str, required=False,
                              help='The `password` parameter is optional.')

        self.post.add_argument('title', type=str, required=False,
                               help='Parameter is optional.')
        self.post.add_argument('text', type=str, required=True,
                               help='Parameter is required.')
        self.post.add_argument('expiration', type=str, required=False,
                               default=None,
                               choices=['1m', '10m', '1h', '1d', '1w',
                                        '2w', '1M', '3M', '6M', '1y'],
                               help='Parameter should be one of '
                                    'the following values: 1m, 10m, 1h, 1d, '
                                    '1w, 2w, 1M, 3M, 6M, 1y.')
        self.post.add_argument('burn_after_reading', type=inputs.boolean,
                               required=False,
                               default=False,
                               help='Must be a boolean.')
        self.post.add_argument('password', type=str, required=False,
                               help='Parameter is optional.')


def parse_time_unit(time_string):
    """
    Converts a time string (e.g., '1m', '10m', '1h', '1d', '1w', '1M', '1y')
    into a timedelta object.
    """
    if not time_string:
        return None

    unit_mapping = {
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'w': 'weeks',
        'M': 'months',  # Approximation: 1 month = 30 days
        'y': 'years'    # Approximation: 1 year = 365 days
    }

    num = int(time_string[:-1])
    unit = time_string[-1]

    if unit == 'M':
        return timedelta(days=num * 30)
    elif unit == 'y':
        return timedelta(days=num * 365)

    if unit in unit_mapping:
        kwargs = {unit_mapping[unit]: num}
        return timedelta(**kwargs)

    raise ValueError(f"Unsupported time unit in '{time_string}'")
