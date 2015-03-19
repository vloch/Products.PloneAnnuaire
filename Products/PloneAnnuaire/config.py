# -*- coding: utf-8 -*-
##
## Copyright (C) 2012 UNIS - ENS de Lyon

"""Common configuration constants
"""
__author__ = 'Vutheany LOCH <vutheany.loch@ens-lyon.fr>'
__docformat__ = 'restructuredtext'

from Products.PloneAnnuaire.customconfig import SITE_CHARSET, BATCH_SIZE

# Prevent pyflakes warnings ;o)
dummy = (SITE_CHARSET, BATCH_SIZE)
del dummy

# ZCTextIndex patch setup
# don't patch by default
PATCH_ZCTextIndex = False

# condition for adding glossaries items in indexed text
INDEX_SEARCH_ANNUAIRE = ('SearchableText',)


from Products.CMFPlone.utils import getFSVersionTuple
PLONE_VERSION = getFSVersionTuple()[:2]  # as (2, 1)
del getFSVersionTuple

PROJECTNAME = 'Products.PloneAnnuaire'
I18N_DOMAIN = 'ploneannuaire'
GLOBALS = globals()
SKINS_DIR = 'skins'

CONFIGLET_ICON = "ploneannuaire_tool.gif"
PLONEANNUAIRE_TOOL = 'portal_annuaire'
PLONEANNUAIRE_CATALOG = 'annuaire_catalog'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'PloneAnnuaireContact': 'Products.PloneAnnuaire: Add PloneAnnuaireContact',
    'PloneAnnuaire': 'Products.PloneAnnuaire: Add PloneAnnuaire',
}
