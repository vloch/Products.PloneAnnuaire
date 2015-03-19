# -*- coding: utf-8 -*-
##
## Copyright (C) 2012 UNIS - ENS de Lyon

from zope.interface import Interface, Attribute
# -*- Additional Imports Here -*-


class IOptionalHighLight(Interface):
    """Do we want to highlight terms in this object?
    """
    
    def do_highlight(default):
        """Highlight this object?

        When no preference can be found, return the default value.
        This should be optional
        """
