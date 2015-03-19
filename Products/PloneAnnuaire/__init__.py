"""Main product initializer
"""
# Python imports
import os
import sys

# CMF imports
from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFCore.DirectoryView import registerDirectory
# Archetypes imports
from Products.Archetypes.public import process_types, listTypes

# Products imports
from Products.PloneAnnuaire.config import SKINS_DIR, GLOBALS, PROJECTNAME
from Products.PloneAnnuaire.PloneAnnuaireTool import PloneAnnuaireTool
from Products.PloneAnnuaire import content as content_module

from zope.i18nmessageid import MessageFactory
from Products.PloneAnnuaire import config

from Products.Archetypes import atapi
from Products.CMFCore import utils

# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

# BBB: Make migrations easier.
sys.modules['Products.PloneAnnuaire.types'] = content_module

registerDirectory(SKINS_DIR, GLOBALS)

PloneAnnuaireMessageFactory = MessageFactory('Products.PloneAnnuaire')


def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types=(atype, ),
            permission=config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors=(constructor,),
            ).initialize(context)
            
            
    # Import tool
    ToolInit(
        '%s Tool' % PROJECTNAME,
        tools=(PloneAnnuaireTool,),
        icon='tool.gif').initialize(context)
