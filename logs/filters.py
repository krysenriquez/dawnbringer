from pprint import pformat
import logging


class PasswordMaskingFilter(logging.Filter):
    """Demonstrate how to filter sensitive data:"""

    def filter(self, record):
        # The call signature matches string interpolation: args can be a tuple or a lone dict
        if isinstance(record.args, dict):
            record.args = self.sanitize_dict(record.args)
        else:
            record.args = tuple(self.sanitize_dict(i) for i in record.args)

        return True

    @staticmethod
    def sanitize_dict(d):
        if not isinstance(d, dict):
            return d

        if any(i for i in d.keys() if "password" in i):
            d = d.copy()  # Ensure that we won't clobber anything critical

            for k, v in d.items():
                if "password" in k:
                    d[k] = "*** PASSWORD ***"

        return d


class CustomFormatter(logging.Formatter):
    def format(self, record):
        res = super(CustomFormatter, self).format(record)

        if hasattr(record, "request"):
            filtered_request = PasswordMaskingFilter.sanitize_dict(record.request)
            res += "\n\t" + pformat(filtered_request, indent=4).replace("\n", "\n\t")
        return res
