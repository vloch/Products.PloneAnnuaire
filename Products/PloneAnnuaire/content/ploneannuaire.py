# -*- coding: utf-8 -*-
##
## Copyright (C) 2012 UNIS - ENS de Lyon

"""Definition of the PloneAnnuaire content type
"""
# Zope imports
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from zope.component import getMultiAdapter

# CMF imports
from Products.CMFCore import permissions

try:
    from Products.LinguaPlone.public import registerType
    registerType  # pyflakes
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import registerType

from zope.interface import implements

from Products.Archetypes import atapi

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from Products.PloneAnnuaire.interfaces import IPloneAnnuaire
from Products.PloneAnnuaire.config import PROJECTNAME, PLONEANNUAIRE_CATALOG
from Products.PloneAnnuaire.PloneAnnuaireCatalog import manage_addPloneAnnuaireCatalog
from Products.PloneAnnuaire.utils import LOG
from Products.PloneAnnuaire.interfaces import IPloneAnnuaire


PloneAnnuaireSchema = folder.ATFolderSchema.copy()

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

PloneAnnuaireSchema['title'].storage = atapi.AnnotationStorage()
PloneAnnuaireSchema['description'].storage = atapi.AnnotationStorage()
PloneAnnuaireSchema['description'].schemata = 'default'

schemata.finalizeATCTSchema(
    PloneAnnuaireSchema,
    folderish=True,
    moveDiscussion=False
)


class PloneAnnuaire(folder.ATFolder):
    """Plone Annuaire"""
    implements(IPloneAnnuaire)

    contact_types = ('PloneAnnuaireContact',)
    meta_type = "PloneAnnuaire"
    schema = PloneAnnuaireSchema
    _at_rename_after_creation = True
    
    security = ClassSecurityInfo()
    
    

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security.declareProtected(permissions.View, 'getAnnuaireContacts')
    def getAnnuaireContacts(self, terms):
        """Returns annuaire contacts.
        Returns tuple of dictionnary title, text.
        Definition is based on catalog getText metadata."""

        # Get annuaire catalog
        title_request = ' OR '.join(['"%s"' % x for x in terms if len(x) > 0])
        if not title_request:
            return []

        # Get # Get annuaire related entry brains
        cat = self.getCatalog()
        brains = cat(Title=title_request)
        if not brains:
            return []

        # Build contacts
        contacts = []
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        mtool = plone_tools.membership()
        # mtool = getToolByName(self, 'portal_membership')
        check_perm = mtool.checkPermission
        for brain in brains:
            # Check view permission
            # FIXME: Maybe add allowed roles and user index in annuaire catalog
            obj = brain.getObject()
            has_view_permission = (
                check_perm(permissions.View, obj) and
                check_perm(permissions.AccessContentsInformation, obj))
            if not has_view_permission:
                continue

            # Make sure the title of annuaire entry is not empty
            title = brain.Title
            if not title:
                continue

            # Build contact
            item = {
                'id': brain.id,
                'title': brain.Title,
                'themes': brain.Themes,
                'phone': brain.Phone,
                'email':brain.Email,
                'description': brain.Description,
                'url': brain.getURL()}
            contacts.append(item)

        return tuple(contacts)
        
    security.declareProtected(permissions.View, 'getAnnuaireTerms')
    def getAnnuaireTerms(self):
        """Returns annuaire entries title."""

        # Get annuaire entry titles
        return [x['title'] for x in self.getAnnuaireTermItems()]

    # Make it private because this method doesn't check entry security
    def _getAnnuaireTermItems(self):
        """Returns annuaire entries in a specific structure

        Item:
        - path -> entry path
        - id -> entry id
        - title -> entry title
        - description -> entry description
        - url -> entry url
        """

        # Returns all annuaire entry brains
        cat = self.getCatalog()
        brains = cat(REQUEST={})

        # Build items
        items = []
        for brain in brains:
            items.append({'path': brain.getPath(),
                          'id': brain.id,
                          'title': brain.Title,
                          'themes': brain.Themes,
                          'phone': brain.Phone,
                          'email': brain.Email,
                          'description': brain.Description,
                          'url': brain.getURL()})
        return items

    security.declarePublic('getAnnuaireTermItems')
    def getAnnuaireTermItems(self):
        """Returns the same list as _getAnnuaireTermItems but check security.
        """

        # Get glossaries term items
        not_secured_term_items = self._getAnnuaireTermItems()

        # Walk into each catalog of glossaries and get terms
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        utool = plone_tools.url()
        # utool = getToolByName(self, 'portal_url')
        portal_object = utool.getPortalObject()
        term_items = []
        for item in not_secured_term_items:
            path = item['path']
            try:
                portal_object.restrictedTraverse(path)
            except:
                continue
            term_items.append(item)
        return term_items
        
        
    security.declarePublic('getCatalog')
    def getCatalog(self):
        """Returns catalog of annuaire"""

        if not hasattr(self, PLONEANNUAIRE_CATALOG):
            # Build catalog if it doesn't exist
            catalog = self._initCatalog()
        else:
            catalog = getattr(self, PLONEANNUAIRE_CATALOG)

        return catalog
        
        
    def _initCatalog(self):
        """Add Annuaire catalog"""

        if not hasattr(self, PLONEANNUAIRE_CATALOG):
            add_catalog = manage_addPloneAnnuaireCatalog
            add_catalog(self)

        catalog = getattr(self, PLONEANNUAIRE_CATALOG)
        catalog.manage_reindexIndex()
        return catalog
        
    security.declareProtected(permissions.ManagePortal, 'rebuildCatalog')
    def rebuildCatalog(self):
        """don't Delete old catalog of annuaire and build a new one
        but only clear it, for tests to pass
        """

        if not hasattr(self, PLONEANNUAIRE_CATALOG):
            # Add a new catalog if not exists
            cat = self._initCatalog()
        else:
            cat = self.getCatalog()

        # clear catalog
        cat.manage_catalogClear()

        # Reindex annuaire contacts
        for obj in self.objectValues():
            if obj.portal_type in self.contact_types:
                cat.catalog_object(obj)
        
        
atapi.registerType(PloneAnnuaire, PROJECTNAME)

###
## Events handlers
###

def annuaireAdded(annuaire, event):
    """A annuaire has been added"""

    container = event.newParent
    # FIXME: Fix this when AT don't need manage_afterAdd any more
    super(annuaire.__class__, annuaire).manage_afterAdd(annuaire, container)
    annuaire._initCatalog()
    LOG.info("Event: A %s has been added.", annuaire.meta_type)
    return

def annuaireMoved(annuaire, event):
    """A annuaire has been moved or renamed"""

    annuaire.rebuildCatalog()
    LOG.info("Event: A %s has been moved.", annuaire.meta_type)
    return
