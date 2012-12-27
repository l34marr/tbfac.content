from zope.interface import implements
from zope.component import queryMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.geo.kml.browser.kmldocument import Feature, Placemark, KMLBaseDocument, KMLFolderDocument as BaseKMLFolderDocument
from collective.geo.kml.interfaces import IFeature, IContainer


class Info(Placemark):

    implements(IContainer)
    __name__ = 'kml-info'

    @property
    def item_type(self):
        return self.context.portal_type

    @property
    def item_url(self):
        return self.context.absolute_url()

    @property
    def use_custom_styles(self):
        return False

    def display_properties(self, document):
        return []

    @property
    def hasMultiLineString(self):
        return False

    @property
    def hasPoint(self):
        return False

    @property
    def hasLineString(self):
        return False

    @property
    def hasMultiPolygon(self):
        return False

    @property
    def hasPolygon(self):
        return False

    @property
    def hasMultiPoint(self):
        return False

    @property
    def features(self):
        if self.context.venue:
            for ref in self.context.venue:
                item = ref.to_object
                feature = queryMultiAdapter((item, self.request), IFeature)
                if not feature:
                    continue
                yield feature

class KMLFolderDocument(BaseKMLFolderDocument):
    template = ViewPageTemplateFile('templates/kmldocument.pt')
