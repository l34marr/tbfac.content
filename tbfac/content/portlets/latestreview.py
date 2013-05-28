from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope.formlib import form
from zope.interface import implements
from zope import schema

from Acquisition import aq_inner, aq_parent
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base


class ILatestReviewPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Portlet Header"),
        required=False,
        default=u"Latest Review")

    count = schema.Int(
        title=_(u'Number of items to display'),
        description=_(u'How many items to list.'),
        required=True,
        default=5)


class Assignment(base.Assignment):
    implements(ILatestReviewPortlet)

    header = u''
    count = 5

    def __init__(self, header=u'', count=5):
        self.count = count
        self.header = header

    @property
    def title(self):
        return _(self.header or u"Latest Review")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('latestreview.pt')

    def render(self):
        return self._template()

    @property
    def available(self):
        return self.data.count > 0 and len(self.latest_review())

    @memoize
    def latest_review(self):
        context = aq_inner(self.context)

        # get all reviews from catalog and filter it out from the same author
        added = [] # keeps track of added author
        reviews = []
        catalog = getToolByName(context, 'portal_catalog')
        for brain in catalog(portal_type='tbfac.Review', sort_on='created',
            sort_order='descending'):
            if brain.Creator and brain.Creator not in added:
                added.append(brain.Creator)
                reviews.append(brain)

        # exclude current author
        parent_ids = []
        parent = context
        while not IPloneSiteRoot.providedBy(parent):
            parent_ids.append(parent.getId())
            parent = aq_parent(parent)

        return [r for r in reviews if r.Creator not in parent_ids
            ][:self.data.count]

    def getAuthorInfo(self, userid):
        acl_users = getToolByName(aq_inner(self.context), 'acl_users')
        user = acl_users.getUserById(userid)
        if not user:
            return None
        else:
            return {
                'id': userid,
                'name': user.getProperty('fullname'),
                'url': '%s/author/%s' % (self.purl(), userid)}

    @memoize
    def purl(self):
        """Return portal url"""
        return getToolByName(self.context, 'portal_url')()

    def toLocalizedTime(self, value):
        if value:
            return DateTime(value).strftime('%Y/%m/%d')
        else:
            return None

class AddForm(base.AddForm):
    form_fields = form.Fields(ILatestReviewPortlet)
    label = _(u"Add Latest Review Portlet")
    description = _(u"Display list of latest Other Juries Reviews.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ILatestReviewPortlet)
    label = _(u"Edit Latest Review Portlet")
    description = _(u"Display list of latest Other Juries Reviews.")
