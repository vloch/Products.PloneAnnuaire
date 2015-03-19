## Controller Python Script "ploneannuaire_management_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title= Manage PloneAnnuaire
##

from Products.CMFCore.utils import getToolByName
from Products.PloneAnnuaire.utils import PloneAnnuaireMessageFactory as _

request = context.REQUEST
gtool = getToolByName(context, 'portal_annuaire')
putils = getToolByName(context, 'plone_utils')

properties = {}
properties['show_portlet'] = request.get('show_portlet', 0)
properties['highlight_content'] = request.get('highlight_content', 0)
properties['use_general_annuaires'] = request.get('use_general_annuaires', 0)
properties['allowed_portal_types'] = request.get('allowed_portal_types', [])
properties['general_annuaire_uids'] = request.get('general_annuaire_uids', [])
properties['description_length'] = request.get('description_length', 0)
properties['description_ellipsis'] = request.get('description_ellipsis', 0)
properties['not_highlighted_tags'] = request.get('not_highlighted_tags', [])

gtool.manage_changeProperties(**properties)

putils.addPortalMessage(_(u'tool_properties_saved',
                           default=u"Tool properties saved"))
return state.set(status='success')
