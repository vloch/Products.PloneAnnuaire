# -*- coding: utf-8 -*-
##
## Copyright (C) 2012 UNIS - ENS de Lyon

from zope.interface import Interface, Attribute
# -*- Additional Imports Here -*-


class IPloneAnnuaire(Interface):
    """Plone Annuaire"""
    
    contact_types = Attribute("""tuple of contacts content metatypes""")

    def getAnnuaireContacts(self, terms):
        """Returns annuaire contacts.
        Returns tuple of dictionnary title, text.
        Contact is based on catalog getText metadata."""
    
    def getAnnuaireTerms():
        """Returns annuaire terms title."""
        
        
    def getAnnuaireTermItems():
        """Returns annuaire terms in a specific structure

        Item:
        - path -> term path
        - id -> term id
        - title -> term title
        - description -> term description
        - url -> term url
        - phone -> term phone
        - email -> Email

         check security."""
    
    def getCatalog():
        """Returns catalog of annuaire"""
        
    def rebuildCatalog():
        """Delete old catalog of annuaire and build a new one"""
