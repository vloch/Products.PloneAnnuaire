# -*- coding: utf-8 -*-
##
## Copyright (C) 2012 UNIS - ENS de Lyon

from zope.interface import Interface, Attribute
# -*- Additional Imports Here -*-


class IPloneAnnuaireContact(Interface):
    """Plone Annuaire Contact"""

    def indexObject():
        """Index object in portal catalog and annuaire catalog"""

    def unindexObject():
        """Unindex object in portal catalog and annuaire catalog"""
    
    def reindexObject(idxs=[]):
        """Reindex object in portal catalog and annuaire catalog"""