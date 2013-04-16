import logging
from Acquisition import aq_inner
from zope import schema
from zope.interface import implements
from zope.component import getUtility
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.portlet.static import PloneMessageFactory
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget

from plone.i18n.normalizer.interfaces import IIDNormalizer

from ..browser.infovenuesmap_view import InfoVenuesMapKMLView
from ..browser.interfaces import IInfoVenuesMapView
from .. import MessageFactory as _


logger = logging.getLogger('tbfac.content.infovenuesmap')
_DESCRIPTION = _(u"This portlet displays a map of Info Venues locations.")


class IInfoVenuesMapPortlet(IPortletDataProvider):
    """Info Venues Map portlet schema
    """

    header = schema.TextLine(
                    title=PloneMessageFactory(u"Portlet header"),
                    description=PloneMessageFactory(
                                u"Title of the rendered portlet"),
                    default=_(u"Venues"),
                    required=False,
                )

    text = schema.Text(
        title=PloneMessageFactory(u"Text"),
        description=PloneMessageFactory(u"The text to render"),
        required=False)

    height = schema.TextLine(
                    title=_(u"Height"),
                    description=_(u"Height for maps, specified as an absolute "
                            "(like '450px' or '15em'), or relative (like "
                            "'100%') size."),
                    required=True,
                    default=u"200px",
                )

    omit_border = schema.Bool(
        title=PloneMessageFactory(u"Omit portlet border"),
        description=PloneMessageFactory(
                    u"Tick this box if you want to render the text above "
                     "without the standard header, border or footer."),
        required=True,
        default=False)

    footer = schema.TextLine(
        title=PloneMessageFactory(u"Portlet footer"),
        description=PloneMessageFactory(u"Text to be shown in the footer"),
        required=False)

    more_url = schema.ASCIILine(
        title=PloneMessageFactory(u"Details link"),
        description=PloneMessageFactory(u"If given, the header and footer "
                      "will link to this URL."),
        required=False)


class Assignment(base.Assignment):
    """Info Venues Map portlet assignment"""

    implements(IInfoVenuesMapPortlet)

    header = u''
    text = u''
    height = u''
    omit_border = False
    footer = u''
    more_url = ''

    def __init__(self, header=u'', text=u'', height=u'200px',
                 omit_border=False, footer=u'', more_url=''):
        self.header = header
        self.text = text
        self.height = height
        self.omit_border = omit_border
        self.footer = footer
        self.more_url = more_url

    @property
    def title(self):
        return self.header or u'Info Venues Map Portlet'


class Renderer(base.Renderer):
    """Info Venues Map portlet renderer
    """
    implements(IInfoVenuesMapView)

    render = ViewPageTemplateFile('infovenuesmap.pt')

    @property
    def available(self):
        """Check if we got any venues to show on a map"""
        view = InfoVenuesMapKMLView(self.context, self.request)
        try:
            venues = view.get_venues()
        except Exception:
            venues = []
        return len(venues) > 0

    def css_class(self):
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-infovenuesmap-%s" % (normalizer.normalize(header) or
            'empty')

    def has_link(self):
        return bool(self.data.more_url)

    def has_footer(self):
        return bool(self.data.footer)

    def transformed(self, mt='text/x-html-safe'):
        """Use the safe_html transform to protect text output. This also
        ensures that resolve UID links are transformed into real links.
        """
        if not self.data.text:
            return None

        orig = self.data.text

        context = aq_inner(self.context)
        if not isinstance(orig, unicode):
            orig = unicode(orig, 'utf-8', 'ignore')
            logger.warn("InfoVenuesMap portlet at %s has stored non-unicode "
                "text. Assuming utf-8 encoding." % context.absolute_url())

        # Portal transforms needs encoded strings
        orig = orig.encode('utf-8')

        transformer = getToolByName(context, 'portal_transforms')
        data = transformer.convertTo(mt, orig, context=context,
            mimetype='text/html')
        result = data.getData()
        if result:
            return unicode(result, 'utf-8')
        return None

    @property
    def css_style(self):
        return "height: %s" % self.data.height

class AddForm(base.AddForm):
    """Info Venues Map portlet add form
    """
    form_fields = form.Fields(IInfoVenuesMapPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget

    label = _(u"Add Info Venues Map portlet")
    description = _DESCRIPTION

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Info Venues Map portlet edit form
    """
    form_fields = form.Fields(IInfoVenuesMapPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget

    label = _(u"Edit Info Venues Map portlet")
    description = _DESCRIPTION
