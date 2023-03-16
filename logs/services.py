import logging
import json
from django.core import serializers

logger = logging.getLogger(__name__)


def create_log(log_type=None, message=None, obj=None):
    print(type(obj))
    match log_type:
        case "DEBUG":
            return logger.debug(message + ": " + json.dumps(obj))
        case "INFO":
            return logger.info(message + ": " + serializers.serialize("json", [obj]))
        case "WARNING":
            return logger.warning(message + ": " + json.dumps(obj))
        case "ERROR":
            return logger.error(message + ": " + json.dumps(obj))
        case "CRITICAL":
            return logger.critical(message + ": " + json.dumps(obj))
