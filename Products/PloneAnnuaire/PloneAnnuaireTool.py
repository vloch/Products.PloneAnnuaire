# -*- coding: utf-8 -*-
##
## Copyright (C) 2007 Ingeniweb

"""
Tool
"""

__author__ = ''
__docformat__ = 'restructuredtext'

import logging

# Zope imports
from zope.interface import implements
from zope.component import getMultiAdapter
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Acquisition import aq_base
from ZODB.POSException import ConflictError
#from zope.app.component import hooks
from zope.component import hooks

# CMF imports
from Products.CMFCore.utils import UniqueObject, getToolByName

# Plone imports
from plone.memoize.request import memoize_diy_request
from plone.i18n.normalizer.base import baseNormalize

# PloneAnnuaire imports
from Products.PloneAnnuaire.config import PLONEANNUAIRE_TOOL, SITE_CHARSET
from Products.PloneAnnuaire.utils import (
    text2words, find_word, escape_special_chars, encode_ascii)
from interfaces import IAnnuaireTool, IOptionalHighLight

logger = logging.getLogger('Products.PloneAnnuaire')


class PloneAnnuaireTool(PropertyManager, UniqueObject, SimpleItem):
    """Tool for PloneAnnuaire"""
    implements(IAnnuaireTool)

    plone_tool = 1
    id = PLONEANNUAIRE_TOOL
    title = 'PloneAnnuaireTool'
    meta_type = 'PloneAnnuaireTool'

    _properties = (
        {'id': 'title',
         'type': 'string',
         'mode': 'w'},
        {'id': 'highlight_content',
         'type': 'boolean',
         'mode': 'w'},
        {'id': 'use_general_annuaires',
         'type': 'boolean',
         'mode': 'w'},
        {'id': 'general_annuaire_uids',
         'type': 'multiple selection',
         'mode': 'w',
         'select_variable': 'getAnnuaireUIDs'},
        {'id': 'allowed_portal_types',
         'type': 'multiple selection',
         'mode': 'w',
         'select_variable': 'getAvailablePortalTypes'},
        {'id': 'description_length',
         'type': 'int',
         'mode': 'w'},
        {'id': 'description_ellipsis',
         'type': 'string',
         'mode': 'w'},
        {'id': 'not_highlighted_tags',
         'type': 'lines',
         'mode': 'w'},
        {'id': 'available_annuaire_metatypes',
         'type': 'lines',
         'mode': 'w'},
        {'id': 'annuaire_metatypes',
         'type': 'multiple selection', 'mode': 'w',
         'select_variable': 'getAvailableAnnuaireMetaTypes'},
        )

    highlight_content = True
    use_general_annuaires = True
    general_annuaire_uids = []
    allowed_portal_types = ['PloneAnnuaireContact']
    description_length = 0
    description_ellipsis = '..'
    not_highlighted_tags = [
        'a', 'h1', 'input', 'textarea', 'div#kupu-editor-text-config-escaped',
        'div#kupu-editor-text-config'
        ]
    available_annuaire_metatypes = ()
    annuaire_metatypes = ['PloneAnnuaire']

    _actions = ()

    manage_options = PropertyManager.manage_options + SimpleItem.manage_options

    security = ClassSecurityInfo()

    security.declarePublic('getAvailablePortalTypes')
    def getAvailablePortalTypes(self):
        """Returns available portal types"""

        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        portal_types = plone_tools.types()
        return portal_types.listContentTypes()

    security.declarePublic('getAvailableAnnuaireMetaTypes')
    def getAvailableAnnuaireMetaTypes(self):
        """
        Returns available annuaire portal types
        """
        return self.available_annuaire_metatypes

    security.declarePublic('getAllowedPortalTypes')
    def getAllowedPortalTypes(self):
        """Returns allowed portal types.
        Allowed portal types can be highlighted."""

        return self.allowed_portal_types

    security.declarePublic('getUseGeneralAnnuaires')
    def getUseGeneralAnnuaires(self):
        """Returns use_general_annuaires
        """
        return self.use_general_annuaires

    security.declarePublic('showPortlet')
    def showPortlet(self):
        """Returns true if you want to show glosssary portlet"""

        return True
        #return self.show_portlet

    security.declarePublic('highlightContent')
    def highlightContent(self, obj):
        """Returns true if content must be highlighted"""

        portal_type = obj.getTypeInfo().getId()
        allowed_portal_types = self.getAllowedPortalTypes()

        if allowed_portal_types and portal_type not in allowed_portal_types:
            return False

        # Check for an adapter on the object and see if this wants
        # highlighting.
        optional = IOptionalHighLight(obj, None)
        if optional is not None:
            return optional.do_highlight(default=self.highlight_content)

        return self.highlight_content

    security.declarePublic('getUsedAnnuaireUIDs')
    def getUsedAnnuaireUIDs(self, obj):
        """Helper method for the portlet Page Template. Fetches the general
           or local annuaire uids depending on the settings in the annuaire
           tool.
        """
        if self.getUseGeneralAnnuaires():
            return self.getGeneralAnnuaireUIDs()
        else:
            return self.getLocalAnnuaireUIDs(obj)

    security.declarePublic('getLocalAnnuaireUIDs')
    def getLocalAnnuaireUIDs(self, context):
        """Returns annuaire UIDs used to highlight content
        in the context of the current object. This method traverses upwards
        in the navigational tree in search for the neares annuaire.
        This neares annuaire is then returned
        """
        portal_catalog = getToolByName(context, 'portal_catalog')

        context = context.aq_inner
        siteroot = hooks.getSite()
        annuaires = []
        annuaire_metatypes = self.annuaire_metatypes

        while True:
            query = {
                'portal_type': annuaire_metatypes,
                'path': "/".join(context.getPhysicalPath()),
            }

            brains = portal_catalog(query)
            if brains:
                annuaires.extend([x.UID for x in brains])
                break

            # quit after siteroot
            if context == siteroot:
                break

            context = context.aq_parent

        return annuaires

    security.declarePublic('getGeneralAnnuaireUIDs')
    def getGeneralAnnuaireUIDs(self):
        """Returns annuaire UIDs used to highlight content"""
        if self.general_annuaire_uids:
            return self.general_annuaire_uids
        else:
            return self.getAnnuaireUIDs()

    security.declarePublic('getGeneralAnnuaires')
    def getGeneralAnnuaires(self):
        """Returns annuaires used to highlight content"""
        general_annuaire_uids = self.getGeneralAnnuaireUIDs()
        return self.getAnnuaires(general_annuaire_uids)

    security.declarePublic('getAnnuaireUIDs')
    def getAnnuaireUIDs(self):
        """Returns annuaire UIDs defined on portal"""

        uid_cat = getToolByName(self, 'uid_catalog')
        brains = uid_cat(portal_type=self.annuaire_metatypes)
        return tuple([x.UID for x in brains])

    security.declarePublic('getAnnuaires')
    def getAnnuaires(self, annuaire_uids=None):
        """Returns annuaires defined on portal"""

        cat = getToolByName(self, 'portal_catalog')
        query = {}
        query['portal_type'] = self.annuaire_metatypes
        if annuaire_uids is not None:
            query['UID'] = annuaire_uids
        brains = cat(**query)
        annuaires = [_.getObject() for _ in brains]
        return tuple([_ for _ in annuaires if _])

    # Make it private because this method doesn't check term security
    def _getAnnuaireTermItems(self, annuaire_uids):
        """Returns annuaire terms as a list of dictionaries

        Item:
        - path -> term path
        - id -> term id
        - title -> term title
        - variants -> term variants
        - description -> term description
        - phone -> term phone
        - url -> term url

        @param annuaire_uids: uids of annuaire where we get terms
        """

        # Get annuaires
        annuaires = self.getAnnuaires(annuaire_uids)
        if not annuaires:
            return []

        # Get items
        items = []
        for annuaire in annuaires:
            new_items = annuaire._getAnnuaireTermItems()
            items.extend(new_items)
        return tuple(items)

    security.declarePublic('getAnnuaireTermItems')
    def getAnnuaireTermItems(self, annuaire_uids):
        """Returns the same list as _getAnnuaireTermItems but check security.

        @param annuaire_uids: Uids of annuaire where we get term items"""

        # Get annuaires term items
        not_secured_term_items = self._getAnnuaireTermItems(annuaire_uids)

        # Walk into each catalog of annuaires and get terms
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        utool = plone_tools.url()
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

    security.declarePublic('getAnnuaireTerms')
    def getAnnuaireTerms(self, annuaire_uids):
        """Returns term titles stored in annuaires.

        @param annuaire_uids: Uids of annuaire where we get term items"""

        # Get annuaires term items
        term_items = self.getAnnuaireTermItems(annuaire_uids)

        # Returns titles
        return [x['title'] for x in term_items]

    def _getObjectText(self, obj):
        """Returns all text of an object.

        If object is an AT content, get schema and returns all text fields.
        Otherwise returns SearchableText.

        @param obj: Content to analyse"""

        text = ''
        if hasattr(aq_base(obj), 'Schema'):
            schema = obj.Schema()
            data = []

            # Loop on fields
            for field in schema.fields():
                if field.type in ('string', 'text',):
                    method = field.getAccessor(obj)

                    if method is None:
                        continue

                    # Get text/plain content
                    try:
                        datum = method(mimetype="text/plain")
                    except TypeError:
                        # retry in case typeerror was raised because
                        # accessor doesn't handle the mimetype
                        # argument
                        try:
                            datum = method()
                        except ConflictError:
                            raise
                        except:
                            continue

                    # Make sure value is a string
                    if type(datum) == type(''):
                        data.append(datum)
            text = ' '.join(data)
        elif hasattr(aq_base(obj), 'SearchableText'):
            text = obj.SearchableText()

        return text

    def _getTextRelatedTermItems(self, text, annuaire_term_items,
                                 excluded_terms=()):
        """
        @param text: charset encoded text
        @param excluded_terms: charset encoded terms to exclude from search
        """

        utext = text.decode(SITE_CHARSET, "replace")
        usplitted_text_terms = self._split(utext)
        atext = encode_ascii(utext)

        aexcluded_terms = [encode_ascii(t.decode(SITE_CHARSET, "replace"))
                          for t in excluded_terms]

        result = []

        # Search annuaire terms in text
        analyzed_terms = []
        for item in annuaire_term_items:
            # Take into account the word and its variants
            terms = []
            item_title = item['title']
            #item_variants = item['variants']
            item_themes = item['themes']
            #item_phone = item['phone']
            #item_email = item['getEmail']
            
            #terms.append(item_phone)
            #terms.append(item_email)
            if type(item_title) == type(''):
                terms.append(item_title)
            if type(item_themes) in (type([]), type(()), ):
                terms.extend(item_themes)

            # Loop on annuaire terms and intersect with object terms
            for term in terms:
                if term in analyzed_terms:
                    continue

                # Analyze term
                analyzed_terms.append(term)
                uterm = term.decode(SITE_CHARSET, "replace")
                aterm = encode_ascii(uterm)
                if aterm in aexcluded_terms:
                    continue

                # Search the word in the text
                found_pos = find_word(aterm, atext)
                if not found_pos:
                    continue

                # Extract terms from obj text
                term_length = len(aterm)
                text_terms = []
                for pos in found_pos:
                    utext_term = utext[pos:(pos + term_length)]

                    # FIX ME: Workaround for composed words. Works in 99%
                    # Check the word is not a subword but a real word
                    # composing the text.
                    if not [x for x in self._split(utext_term)
                            if x in usplitted_text_terms]:
                        continue

                    # Encode the term and make sure there are no doublons
                    text_term = utext_term.encode(SITE_CHARSET, "replace")
                    if text_term in text_terms:
                        continue
                    text_terms.append(text_term)

                if not text_terms:
                    continue

                # Append object term item
                new_item = item.copy()
                new_item['terms'] = text_terms
                result.append(new_item)

        return result

    # Make it private because this method doesn't check term security
    def _getObjectRelatedTermItems(self, obj, annuaire_term_items):
        """Returns object terms in a specific structure

        Item:
        - terms -> object terms
        - path -> term path
        - id -> term id
        - title -> term title
        - variants -> term variants
        - description -> term description
        - url -> term url

        @param obj: object to analyse

        @param annuaire_term_items: Annuaire term items to check in
            the object text

        Variables starting with a are supposed to be in ASCII

        Variables starting with u are supposed to be in Unicode
        """

        # Get obj properties
        ptype = obj.portal_type
        if callable(obj.title_or_id):
            title = obj.title_or_id()
        else:
            title = obj.title_or_id

        text = self._getObjectText(obj)

        # Words to remove from terms to avoid recursion
        # For example, on a annuaire contact itself, it makes no sense to
        # underline the defined word.
        removed_words = ()
        if ptype in ('PloneAnnuaireContact',):
            removed_words = (title,)

        return self._getTextRelatedTermItems(text, annuaire_term_items,
                                             removed_words,)

    security.declarePublic('getObjectRelatedTermItems')
    def getObjectRelatedTermItems(self, obj, annuaire_term_items,
                                  alpha_sort=False):
        """Returns the same list as _getObjectRelatedTermItems but
        check security.

        @param obj: object to analyse

        @param annuaire_term_items: Annuaire term items to check in
        the object text

        @param alpha_sort: if True, returned items are sorted by title, asc
        """

        # Get annuaires term items
        not_secured_term_items = self._getObjectRelatedTermItems(
            obj, annuaire_term_items)

        # Walk into each catalog of annuaires and get terms
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        utool = plone_tools.url()
        portal_object = utool.getPortalObject()
        term_items = []
        for item in not_secured_term_items:
            path = item['path']
            try:
                obj = portal_object.restrictedTraverse(path)
            except:
                continue
            term_items.append(item)

        if alpha_sort:
            def annuaire_cmp(o1, o2):
                return cmp(o1.get('title', ''), o2.get('title', ''))
            term_items.sort(annuaire_cmp)

        return term_items

    security.declarePublic('getObjectRelatedTerms')
    def getObjectRelatedTerms(self, obj, annuaire_uids, alpha_sort=False):
        """Returns annuaire term titles found in object

        @param obj: Content to analyse and extract related annuaire terms
        @param annuaire_uids: if None tool will search all annuaires
        @param alpha_sort: if True, returned items are sorted by title, asc
        """

        # Get term contacts found in obj
        contacts = self.getObjectRelatedContacts(obj, annuaire_uids,
                                                       alpha_sort=False)

        # Returns titles
        return [x['title'] for x in contacts]

    security.declarePublic('getObjectRelatedContacts')
    def getObjectRelatedContacts(self, obj, annuaire_uids,
                                    alpha_sort=False):
        """Returns object term contacts get from annuaires.

        contact:
        - terms -> exact words in obj text
        - id -> term id
        - path -> term path
        - title -> term title
        - variants -> term variants
        - description -> term contacts
        - url -> term url

        @param obj: Content to analyse and extract related annuaire terms
        @param annuaire_uids: if None tool will search all annuaires
        @param alpha_sort: if True, returned items are sorted by title, asc
        """

        # Get annuaire term items from the annuaire
        # All terms are loaded in the memory as a list of dictionaries

        if not annuaire_uids:
            return []

        annuaire_term_items = self._getAnnuaireTermItems(annuaire_uids)

        marked_contacts = []
        urls = {}
        # Search related contacts in annuaire contacts
        for contact in self.getObjectRelatedTermItems(
                obj, annuaire_term_items, alpha_sort):
            if contact['url'] in urls:
                # The annuaire item is already going to be shown
                contact['show'] = 0
            else:
                # The annuaire item is going to be shown
                urls[contact['url']] = 1
                contact['show'] = 1
            marked_contacts.append(contact)
        return marked_contacts

    security.declarePublic('getContactsForUI')
    @memoize_diy_request(arg=2)
    def getContactsForUI(self, context, request):
        """Provides UI friendly contacts for the context item"""

        # LOG.debug("Running PloneAnnuaireTool.getContactsForUi")
        annuaire_uids = self.getUsedAnnuaireUIDs(context)
        if len(annuaire_uids) == 0:
            annuaire_uids = None
        return self.getObjectRelatedContacts(context, annuaire_uids)

    security.declarePublic('searchResults')
    def searchResults(self, annuaire_uids, **search_args):
        """Returns brains from annuaires.
        annuaire_uids: UIDs of annuaires where to search.
        search_args: Use index of portal_catalog."""

        # Get path of annuaires
        query = dict(search_args)
        annuaires = self.getAnnuaires(annuaire_uids)
        query['path'] = ['/'.join(x.getPhysicalPath()) for x in annuaires]
        plone_tools = getMultiAdapter((self, self.REQUEST), name='plone_tools')
        ctool = plone_tools.catalog()
        query['portal_type'] = self._getContactsMetaTypes(annuaires)
        logger.debug(query)
        return ctool(**query)

    def _getContactsMetaTypes(self, annuaires):
        """
        get annuaire contacts metatypes using annuaires list
        """
        metatypes = []
        for annuaire in annuaires:
            annuaire_def_mts = [deftype \
                                for deftype in annuaire.contact_types\
                                if deftype not in metatypes]
            metatypes.extend(annuaire_def_mts)

        return metatypes

    security.declarePublic('getAsciiLetters')
    def getAsciiLetters(self):
        """Returns list of ascii letters in lower case"""

        return tuple([chr(x) for x in range(97, 123)])

    security.declarePublic('getFirstLetter')
    def getFirstLetter(self, term):
        """ returns first letter """
        if isinstance(term, unicode):
            letter = term[0:1]
            return baseNormalize(letter)
        else:
            try:
                uterm = term.decode(SITE_CHARSET)
                letter = baseNormalize(uterm[0:1]).encode(SITE_CHARSET)
                return letter
            except UnicodeDecodeError:
                letter = term[0:1].decode()  # use python default encoding
                return baseNormalize(letter)

    security.declarePublic('getAbcedaire')
    def getAbcedaire(self, annuaire_uids):
        """Returns abcedaire.
        annuaire_uids: UIDs of annuaires used to build abcedaire"""

        terms = self.getAnnuaireTerms(annuaire_uids)
        letters = []

        for term in terms:
            letter = self.getFirstLetter(term).lower()
            if letter not in letters:
                letters.append(letter)

        # Sort alphabetically
        letters.sort()

        return tuple(letters)

    security.declarePublic('getAbcedaireBrains')
    def getAbcedaireBrains(self, annuaire_uids, letters):
        """Returns brains from portal_catalog.
        annuaire_uids: UIDs of annuaires used to build abcedaire.
        letters: beginning letters of terms to search"""

        abcedaire_brains = []
        brains = self.searchResults(annuaire_uids)

        for brain in brains:
            letter = self.getFirstLetter(brain.Title).lower()
            if letter in letters:
                abcedaire_brains.append(brain)

        # Sort alphabetically
        def cmp_alpha(a, b):
            return cmp(a.Title, b.Title)

        abcedaire_brains.sort(cmp_alpha)

        return abcedaire_brains

    
    security.declarePublic('truncateDescription')
    def truncateDescription(self, text):
        """Truncate contact using tool properties"""

        max_length = self.description_length
        text = text.decode(SITE_CHARSET, "replace")
        text = text.strip()

        if max_length > 0 and len(text) > max_length:
            ellipsis = self.description_ellipsis
            text = text[:max_length]
            text = text.strip()
            text = '%s %s' % (text, ellipsis)

        text = text.encode(SITE_CHARSET, "replace")

        return text

    security.declarePublic('escape')
    def escape(self, text):
        """Returns escaped text."""

        return escape_special_chars(text)

    security.declarePublic('includePloneAnnuaireJS')
    def includePloneAnnuaireJS(self, context, request):
        """Helper for portal_javascripts
        Should we include PloneAnnuaire javascripts
        """
        context_state = getMultiAdapter((context, request),
                                        name=u'plone_context_state')
        if not context_state.is_view_template():
            return False
        return self.showPortlet() or self.highlightContent(context)

    def _split(self, text, removed_words=()):
        """Split unicode text into tuple of unicode terms

        @param text: unicode text to split
        @param remove_words: words to remove from the split result"""

        return tuple([x for x in text2words(text)
                       if len(x) > 1 and x not in removed_words])

InitializeClass(PloneAnnuaireTool)
