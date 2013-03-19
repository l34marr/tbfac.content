from five import grok
from zope import schema
from plone.directives import form, dexterity
from plone.namedfile.field import NamedBlobImage

from tbfac.content import MessageFactory as _
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from tbfac.content.info import IInfo
from tbfac.content.article import IArticle

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

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context, domain='plonelocales')

    def getItems(self):
        """ Get Items to Display
        """
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        portal_state = getMultiAdapter((context, self.request),
            name=u'plone_portal_state')
        if context.absolute_url().endswith('/event/info'): end = '/event/info'
        if context.absolute_url().endswith('/event/talks'): end = '/event/talks'
        path = portal_state.navigation_root_path() + end
        return catalog(object_provides=(IArticle.__identifier__, IInfo.__identifier__),
                       review_state='published',
                       path=path,
                       sort_on='created',
                       sort_order='descending')

