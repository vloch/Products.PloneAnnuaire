# -*- coding: utf-8 -*-
##
## Copyright (C) 2012 UNIS - ENS de Lyon


"""
Patch to ZCTextIndex such it searches for term and synonyms
"""

from Products.CMFCore.utils import getToolByName

from config import PATCH_ZCTextIndex, INDEX_SEARCH_ANNUAIRE
from config import PLONEANNUAIRE_TOOL

from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex

from Products.PluginIndexes.common.util import parseIndexRequest
from Products.ZCTextIndex.QueryParser import QueryParser
from Products.ZCTextIndex.ParseTree import OrNode, AndNode, AtomNode

from Products.PloneAnnuaire.utils import LOG


def __getNOTWords(tree):
    """
    Return a list of words to exclude from search
    """
    exclude_words = []
    for subnode in tree.getValue():
        if isinstance(subnode, basestring):
            continue
        if subnode.nodeType() in ('OR', 'AND'):
            exclude_words.extend(__getNOTWords(subnode))

        if subnode.nodeType() == 'NOT':
            exclude_words.extend(subnode.getValue().terms())

    return exclude_words


def flatten(seq):
    """
    >>> flatten([0, [1, 2, 3], [4, 5, [6, 7]]])
    [0, 1, 2, 3, 4, 5, 6, 7]
    """
    ans = []
    for i in seq:
        if (i.__class__ is list):
            ans.extend(flatten(i))
        else:
            ans.append(i)
    return ans


def replaceWordsQuery(tree, parseQuery, gtool, gloss_items, excluded):
    """
    Change the tree query: all Atom or Phrase found in the annuaire (term or
    variant) are replaced by an"OR" query between all this terms, i.e if
    annuaire contains the term 'lorem' with variant 'ipsum', then
    replaceWordsQuery(AtomNode('lorem')) returns
    OrNode([AtomNode('lorem'), AtomNode('ipsum')])

    @param tree: the current node to process
    @param gtool: a PloneAnnuaireTool instance
    @param gloss_items: the list of annuaire item to search within query
    @param excluded: dict of words (as keys) to skip
    """
    if isinstance(tree, AtomNode):
        nodes = [tree]
    else:
        nodes = tree.getValue()

    for node_idx in range(len(nodes)):

        subnode = nodes[node_idx]

        nodetype = subnode.nodeType()
        if nodetype in ('OR', 'AND'):
            nodes[node_idx] = replaceWordsQuery(
                subnode, parseQuery, gtool, gloss_items, excluded)
            continue
        elif nodetype == 'NOT':
            continue
        elif nodetype == 'GLOB':
            continue

        # flatten is needed because PhraseNode.terms => [['term1', 'term2']]
        text = ' '.join(flatten(subnode.terms()))
        terms = gtool._getTextRelatedTermItems(text, gloss_items)
        final_terms = []
        for t in terms:
            #t_list = (t['title'],) + t['variants']
            t_list = (t['title'],) + t['themes']
            exclude_term = False
            for item in t_list:
                exclude_term |= item in excluded
            if exclude_term:
                continue

            # parseQuery will choose for us AtomNode or PhraseNode
            final_terms.append([parseQuery('"%s"' % i) for i in t_list])

        final_gloss_query = [(len(i) > 1 and OrNode(i)) or i[0]
                             for i in final_terms if len(i)]
        term_count = len(final_gloss_query)
        if term_count == 0:
            final_gloss_query = None
        elif term_count > 1:
            final_gloss_query = AndNode(final_gloss_query)
        else:
            final_gloss_query = final_gloss_query[0]

        if final_gloss_query is not None:
            nodes[node_idx] = final_gloss_query

    if len(nodes) == 1:
        return nodes[0]
    elif len(nodes) > 1:
        if isinstance(tree, AtomNode):
            return AndNode(nodes)
        else:
            tree._value = nodes
            return tree


def zctidx_ApplyIndexWithSynonymous(self, request, cid=''):
        """Apply query specified by request, a mapping containing the query.

        Returns two object on success, the resultSet containing the
        matching record numbers and a tuple containing the names of
        the fields used

        Returns None if request is not valid for this index.

        If this index id is listed in
        PloneAnnuaire.config.INDEX_SEARCH_ANNUAIRE, the query tree is
        changed to look for terms and their variants found in general
        annuaires.
        """
        record = parseIndexRequest(request, self.id, self.query_options)
        if record.keys is None:
            return None
        query_str = ' '.join(record.keys)
        if not query_str:
            return None

        parseQuery = QueryParser(self.getLexicon()).parseQuery
        tree = parseQuery(query_str)

        if self.getId() in INDEX_SEARCH_GLOSSARY:

            gtool = getToolByName(self, PLONEANNUAIRE_TOOL)
            annuaire_uids = gtool.getGeneralAnnuaireUIDs()
            all_term_items = gtool._getAnnuaireTermItems(annuaire_uids)

            #get atoms from query and build related term query
            # text = ' '.join(flatten(tree.terms()))
            excluded = dict.fromkeys(__getNOTWords(tree), True)

            tree = replaceWordsQuery(tree, parseQuery, gtool, all_term_items,
                                     excluded)

        results = tree.executeQuery(self.index)
        return  results, (self.id,)


if PATCH_ZCTextIndex:
    ZCTextIndex._apply_index = zctidx_ApplyIndexWithSynonymous
    LOG.info('Applied patch: ZCTextIndex._apply_index method')
