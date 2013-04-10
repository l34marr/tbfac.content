# from zope import schema
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements
from zope.component import getUtility
from plone.app.content.interfaces import INameFromTitle
# from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot

# from Acquisition import aq_inner, aq_base, aq_chain
# from zope.container.interfaces import INameChooser
# from plone.app.content.namechooser import NormalizingNameChooser
from zope.annotation.interfaces import IAnnotations

ANNOTATION_NEXT_ID = 'tbfac.content.behavior.nextid'

class INameFromCreated(Interface):
    """Marker interface to enable name from creation date behavior"""
    # def title(): """Returns date computed title"""
    # id = schema.TextLine(title=u"Identifier", description=u"This is a unique identifier for this object.", required=True)

class NameFromCreated(object):
    implements(INameFromTitle)
    adapts(INameFromCreated)

    def __new__(cls, context):
        #return None
        instance = super(NameFromCreated, cls).__new__(cls)
        site=getUtility(ISiteRoot)
        # raise Exception("site:%s" % str(site))
        storage = IAnnotations(site, None)
        next = storage.get(ANNOTATION_NEXT_ID , 1)
        storage[ANNOTATION_NEXT_ID] = next + 1
        cdate = context.creation_date
        instance.title = '%d%s%s%s' % (cdate.year() , cdate.mm() , cdate.dd() , str(next).zfill(2))
        return instance
    def __init__(self, context):
        self.context = context
        # raise Exception("site:%s" % str([]))

    # @property def title(self): pass
    # catalog = getToolByName(aq_base(self.context), 'portal_catalog')
