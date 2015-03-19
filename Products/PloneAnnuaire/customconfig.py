# -*- coding: utf-8 -*-
##
## Copyright (C) 2012 UNIS - ENS de Lyon
"""
Global customizable configuration data

To customize the values add this to your zope.conf:

<product-config ploneannuaire>
  charset utf-8 # Or any valid charset
  batch-size 50       # Any positive integer
</product-config>
"""

SITE_CHARSET = None  # Default: UTF-8
BATCH_SIZE = None  # Default: 30


def readZopeConf():
    """Read custom config from zope.conf or use defaults
    """
    global SITE_CHARSET, BATCH_SIZE
    from App.config import getConfiguration
    import codecs
    default_config = {
        'charset': 'UTF-8',
        'batch-size': 30
        }
    try:
        pg_config = getConfiguration().product_config['ploneannuaire']
    except (KeyError, AttributeError):
        pg_config = default_config

    getConfData = lambda key: pg_config.get(key, default_config[key])

    SITE_CHARSET = getConfData('charset')
    BATCH_SIZE = int(getConfData('batch-size'))

    # Validating
    try:
        codecs.lookup(SITE_CHARSET)
    except LookupError:
        raise ValueError("%s is not a valid charset." % SITE_CHARSET)
    return

readZopeConf()
del readZopeConf
