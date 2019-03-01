"""Utilities."""
# -- XXX This module must not use translation as that causes
# -- a recursive loader import!
from __future__ import absolute_import, unicode_literals

import datetime

from django.conf import settings
from django.utils import timezone

is_aware = timezone.is_aware

# see Issue #222
now_localtime = getattr(timezone, 'template_localtime', timezone.localtime)


def make_aware(value):
    """Force datatime to have timezone information."""
    if getattr(settings, 'USE_TZ', False):
        # naive datetimes are assumed to be in UTC.
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
        # then convert to the Django configured timezone.
        default_tz = timezone.get_default_timezone()
        value = timezone.localtime(value, default_tz)
    else:
        # naive datetimes are assumed to be in UTC.
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
        else:
            # Convert aware datetime to UTC.
            value = timezone.localtime(value, timezone.utc)
    return value


def maybe_make_unaware(value):
    """Remove tz if not configured."""
    if not getattr(settings, 'USE_TZ', False) and timezone.is_aware(value):
        # Convert to UTC and then remove the timezone.
        value = timezone.localtime(value, timezone.utc)
        value = value.replace(tzinfo=None)
    return value


def now():
    """Return the current date and time."""
    if getattr(settings, 'USE_TZ', False):
        return now_localtime(timezone.now())
    else:
        # Return UTC Time.
        return datetime.datetime.utcnow().replace(tzinfo=timezone.utc)


def is_database_scheduler(scheduler):
    """Return true if Celery is configured to use the db scheduler."""
    if not scheduler:
        return False
    from kombu.utils import symbol_by_name
    from .schedulers import DatabaseScheduler
    return (
        scheduler == 'django' or
        issubclass(symbol_by_name(scheduler), DatabaseScheduler)
    )
