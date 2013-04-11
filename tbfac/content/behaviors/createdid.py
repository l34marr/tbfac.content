from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements
from zope.component import getUtility
from plone.app.content.interfaces import INameFromTitle
from Products.CMFCore.interfaces import ISiteRoot
from zope.annotation.interfaces import IAnnotations

ANNOTATION_NEXT_ID = 'tbfac.content.behavior.nextid'

class INameFromCreated(Interface):
    """Marker interface to enable name from creation date behavior"""

class NameFromCreated(object):
    implements(INameFromTitle)
    adapts(INameFromCreated)

    def __new__(cls, context):
        instance = super(NameFromCreated, cls).__new__(cls)
        site = getUtility(ISiteRoot)
        storage = IAnnotations(site, {})
        next = storage.get(ANNOTATION_NEXT_ID , 1)
        storage[ANNOTATION_NEXT_ID] = next + 1
        cdate = context.creation_date
        instance.title = '%d%s%s%s' % (cdate.year() , cdate.mm() , cdate.dd() , str(next).zfill(2))
        return instance

    def __init__(self, context):
        self.context = context
