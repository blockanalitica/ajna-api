import contextlib
import datetime
import decimal
import json
import uuid

from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.functional import Promise
from rest_framework.renderers import JSONRenderer as DRFJSONRenderer


class JSONEncoder(json.JSONEncoder):
    """
    Custom JSONEncoder to encode Decimal objects as string and not float
    """

    def default(self, obj):
        # For Date Time string spec, see ECMA 262
        # https://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15
        if isinstance(obj, Promise):
            return force_str(obj)
        elif isinstance(obj, datetime.datetime):
            representation = obj.isoformat()
            if representation.endswith("+00:00"):
                representation = representation[:-6] + "Z"
            return representation
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            if timezone and timezone.is_aware(obj):
                raise ValueError("JSON can't represent timezone-aware times.")
            representation = obj.isoformat()
            return representation
        elif isinstance(obj, datetime.timedelta):
            return str(obj.total_seconds())
        elif isinstance(obj, decimal.Decimal):  # noqa: SIM114
            return str(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, QuerySet):
            return tuple(obj)
        elif isinstance(obj, bytes):
            # Best-effort for binary blobs. See #4187.
            return obj.decode()
        elif hasattr(obj, "tolist"):
            # Numpy arrays and array scalars.
            return obj.tolist()
        elif hasattr(obj, "__getitem__"):
            cls = list if isinstance(obj, (list, tuple)) else dict
            with contextlib.suppress(Exception):
                return cls(obj)
        elif hasattr(obj, "__iter__"):
            return tuple(item for item in obj)
        return super().default(obj)


class JSONRenderer(DRFJSONRenderer):
    encoder_class = JSONEncoder
