from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from zope import schema

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base

from ..util import getAddThisSharedURLs


class IMostLikedPortlet(IPortletDataProvider):

    header = schema.TextLine(
        title=_(u"Portlet Header"),
        required=False,
        default=u"Most Liked")

    count = schema.Int(
        title=_(u'Number of items to display'),
        description=_(u'How many items to list.'),
        required=True,
        default=5)


class Assignment(base.Assignment):
    implements(IMostLikedPortlet)

    header = u''
    count = 5

    def __init__(self, header=u'', count=5):
        self.count = count
        self.header = header

    @property
    def title(self):
        return _(self.header or u"Events")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('mostliked.pt')

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.data.count > 0 and len(self._data())

    def most_liked(self):
        return self._data()

    def _data(self):
        data = getAddThisSharedURLs()
        if not data:
            return []

        # check if we are on site root
        context = aq_inner(self.context)
        cstate = getMultiAdapter((context, self.request),
            name='plone_context_state')
        url_tool = getToolByName(context, 'portal_url')
        purl, ppath = url_tool(), url_tool.getPortalPath()
        limit = self.data.count or 5
        counter = 0
        folder = cstate.folder()
        paths = []
        if IPloneSiteRoot.providedBy(folder): # site root
            for info in data:
                if counter >= limit:
                    break

                path = self._getPath(info['url'], purl, ppath)
                if path and path not in paths:
                    counter += 1
                    paths.append(path)
        else: # nested folder
            url = folder.absolute_url()

            # debug code for localhost
            # url = folder.absolute_url().replace(purl,
            #     'http://talks.taishinart.org.tw')

            for info in data:
                if counter >= limit:
                    break

                # skipt anything that's not within current folder
                if not info['url'].startswith(url):
                    continue

                path = self._getPath(info['url'], purl, ppath)
                if path and path not in paths:
                    counter += 1
                    paths.append(path)

        if not paths:
            return []

        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(path={'query': paths, 'depth': 0})
        if len(brains) == 0:
            return []

        brains_dict = {}
        for b in brains:
            brains_dict[b.getPath()] = b

        result = []
        for p in paths:
            if not brains_dict.has_key(p):
                continue
            result.append(brains_dict[p])

        return result

    def _getPath(self, url, portal_url, portal_path):
        """Convert addthis.com url to plone path"""
        # debug code for localhost
        # portal_url = u'http://talks.taishinart.org.tw'
        # portal_path = u'/www'

        path = u''
        if url.startswith(portal_url):
            path = u'%s%s' % (portal_path, url[len(portal_url):])

            # clean up the path
            if u'#' in path:
                path = path[:path.index(u'#')]
            elif u'?' in path:
                path = path[:path.index(u'?')]

        return path

class AddForm(base.AddForm):
    form_fields = form.Fields(IMostLikedPortlet)
    label = _(u"Add Most Liked Portlet")
    description = _(u"This portlet lists Most Liked objects.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IMostLikedPortlet)
    label = _(u"Edit Most Liked Portlet")
    description = _(u"This portlet lists Most Liked objects.")
