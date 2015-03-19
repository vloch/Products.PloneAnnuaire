# -*- coding: utf-8 -*-
##
## Copyright (C) 2012 UNIS - ENS de Lyon
"""Definition of the PloneAnnuaireContact content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import LinesWidget
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import ImageField
from Products.Archetypes.atapi import ImageWidget
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import RichWidget

from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.configuration import zconf

from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.CMFPlone.utils import getToolByName

# Archetypes imports
try:
    from Products.LinguaPlone.public import registerType
    registerType  # pyflakes
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import registerType
    
# -*- Message Factory Imported Here -*-

from Products.PloneAnnuaire.interfaces import IPloneAnnuaireContact
from Products.PloneAnnuaire.config import PROJECTNAME
from Products.PloneAnnuaire.utils import PloneAnnuaireMessageFactory as _
from Products.PloneAnnuaire.utils import html2text

PloneAnnuaireContactSchema = ATContentTypeSchema.copy() + atapi.Schema((
           StringField(
        'title',
        required=True,
        searchable=True,
        default='',
        accessor='Title',
        widget=StringWidget(
            label=_(u'label_annuaire_contact', default=u"Contact Name"),
            description=_(u'help_annuaire_contact',
                              default=u"Enter your name."),
            visible={'view': 'invisible'}),
        ),
        
   ImageField(
        'portrait',
        required=False,
        primary=True,
        languageIndependent=True,
        storage = AnnotationStorage(migrate=True),
        allowable_content_types=('image/gif','image/jpeg','image/jpg','image/png'),
        sizes={'thumb': (80,80),
               'mini': (200,200)},
        accessor='Portrait',
        widget = ImageWidget(
            label=_(u'label_annuaire_portrait', default=u"Portrait"),
            description=_(u'help_annuaire_portrait',
                              default=u"Upload your picture."),
        ),
        ),
        
    StringField(
        'grade',
        required=True,
        searchable=True,
        default='',
        accessor='Grade',
        widget=StringWidget(
            label=_(u'label_annuaire_grade', default=u"Statut"),
            description=_(u'help_annuaire_grade',
                              default=u"Ex : IGR Hors Classe - CNRS."),
            visible={'view': 'invisible'}),
        ),
    StringField(
        'institution',
        required=False,
        searchable=True,
        default='',
        accessor='Institution',
        widget=StringWidget(
            label=_(u'label_annuaire_institution', default=u"Present status"),
            description=_(u'help_annuaire_institution',
                              default=u"Ex : ENS de Lyon."),
            visible={'view': 'invisible'}),
        ),
    StringField(
        'building',
        required=False,
        searchable=True,
        default='',
        accessor='Building',
        widget=StringWidget(
            label=_(u'label_annuaire_building', default=u"Building"),
            description=_(u'help_annuaire_building',
                              default=u""),
            visible={'view': 'invisible'}),
        ),
    StringField(
        'floor',
        required=False,
        default='',
        accessor='Floor',
        widget=StringWidget(
            label=_(u'label_annuaire_floor', default=u"Year"),
            description=_(u'help_annuaire_floor',
                              default=u""),
            visible={'view': 'invisible'}),
        ),
    
    StringField(
        'office',
        required=False,
        searchable=False,
        default='',
        accessor='Office',
        widget=StringWidget(
            label=_(u'label_annuaire_office', default=u"Office"),
            description=_(u'help_annuaire_office',
                              default=u"Your Office Number. Ex : LE D 55."),
            visible={'view': 'invisible'}),
        ),
    
    LinesField(
        'phone',
        required=True,
        searchable=True,
        default=(),
        accessor='Phone',
        widget=LinesWidget(
            label=_(u'label_annuaire_phone', default=u"Phone"),
            description=_(u'help_annuaire_phone',
                              default=u"Your Phone Number, one per line."),
            visible={'view': 'invisible'}),
        ),
        
    
    StringField(
        'fax',
        required=False,
        searchable=False,
        default='',
        accessor='Fax',
        widget=StringWidget(
            label=_(u'label_annuaire_fax', default=u"Fax"),
            description=_(u'help_annuaire_fax',
                              default=u"Your fax."),
            visible={'view': 'invisible'}),
        ),
        
    StringField(
        'email',
        required=True,
        searchable=True,
        default='',
        accessor='Email',
        widget=StringWidget(
            label=_(u'label_annuaire_email', default=u"E-mail"),
            description=_(u'help_annuaire_email',
                              default=u"Your address E-mail."),
            visible={'view': 'invisible'}),
        ),
        
     StringField(
        'website',
        required=False,
        searchable=False,
        default='http://',
        accessor='Website',
        widget=StringWidget(
            label=_(u'label_annuaire_website', default=u"Website"),
            description=_(u'help_annuaire_website',
                              default=u"URL."),
            visible={'view': 'invisible'}),
        ),
    StringField(
        'team',
        required=False,
        searchable=True,
        default='',
        accessor='Team',
        widget=StringWidget(
            label=_(u'label_annuaire_team', default=u"Team"),
            description=_(u'help_annuaire_team',
                              default=u"Your research team."),
            visible={'view': 'invisible'}),
        ),
         
    LinesField(
        'themes',
        required=False,
        searchable=True,
        default=(),
        widget=LinesWidget(
            label=_(u'label_annuaire_themes', default=u"Research Themes"),
            description=_(
                u'help_annuaire_themes',
                default=u"Enter the resarch themes, one per line."),
            visible={'view': 'invisible'}),
        ),
        
    TextField(
        'definition',
        required=False,
        searchable=True,
        default_content_type=zconf.ATDocument.default_content_type,
        default_output_type='text/x-html-safe',
        allowable_content_types=zconf.ATDocument.allowed_content_types,
        widget=RichWidget(
            label=_(u'label_annuaire_autres_text', default=u"More informations"),
            description=_(u'help_annuaire_autres_text',
                          default=u"Enter more information about you here."),
            rows=25),
        ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

#PloneAnnuaireContactSchema['title'].storage = atapi.AnnotationStorage()
#PloneAnnuaireContactSchema['description'].storage = atapi.AnnotationStorage()

del PloneAnnuaireContactSchema['description']
schemata.finalizeATCTSchema(PloneAnnuaireContactSchema, moveDiscussion=False)


class PloneAnnuaireContact(base.ATCTContent):
    """Plone Annuaire Contact"""
    implements(IPloneAnnuaireContact)

    meta_type = "PloneAnnuaireContact"
    schema = PloneAnnuaireContactSchema
    _at_rename_after_creation = True
    
    security = ClassSecurityInfo()

    #title = atapi.ATFieldProperty('title')
    #description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    
    security.declareProtected(permissions.View, 'Description')
    def Description(self, from_catalog=False):
        """Returns cleaned text"""

        if from_catalog:
            cat = self.getCatalog()
            brains = cat.searchResults(id=self.getId())

            if not brains:
                return self.Description()

            brain = brains[0]
            return brain.Description
        else:
            html = self.getDefinition()
            return html2text(html)
            
    security.declareProtected(permissions.ModifyPortalContent, 'indexObject')
    def indexObject(self):
        """Index object in portal catalog and annuaire catalog"""
        cat = getToolByName(self, 'portal_catalog')
        cat.indexObject(self)
        cat = self.getCatalog()
        cat.indexObject(self)

    security.declareProtected(permissions.ModifyPortalContent, 'unindexObject')
    def unindexObject(self):
        """Unindex object in portal catalog and annuaire catalog"""
        cat = getToolByName(self, 'portal_catalog')
        cat.unindexObject(self)
        cat = self.getCatalog()
        cat.unindexObject(self)

    security.declareProtected(permissions.ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        """Reindex object in portal catalog and annuaire catalog"""
        cat = getToolByName(self, 'portal_catalog')
        cat.reindexObject(self, idxs)
        cat = self.getCatalog()
        cat.reindexObject(self, idxs)

atapi.registerType(PloneAnnuaireContact, PROJECTNAME)
