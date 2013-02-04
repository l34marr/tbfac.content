from five import grok
from zope import schema
from plone.directives import form, dexterity
from plone.namedfile.field import NamedBlobImage

from tbfac.content import MessageFactory as _
from Products.CMFCore.utils import getToolByName

class IFolder(form.Schema):
    """TBFAC Folder Type
    """

    image = NamedBlobImage(
        title=_(u"Link Image"),
        required=False,
    )

    link = schema.TextLine(
        title=_(u"Link URL"),
        required=False,
    )

class Folder(dexterity.Container):
    grok.implements(IFolder)

    # Add your class methods and properties here

# Note that we use the standard folder_listing view for this type, so there
# is no specific view here

class View(grok.View):
    grok.context(IFolder)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        membership = getToolByName(self.context, 'portal_membership')
        if membership.isAnonymousUser():
            self.request.set('disable_border', True)

