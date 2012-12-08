from zope.interface import Interface, Attribute
from zope.annotation.interfaces import IAnnotations

from BTrees.OIBTree import OIBTree


ANNO_KEY = 'tbfac.content.RecommendationsAnno'

class IRecommendable(Interface):
    """Marker interface telling that current object could be recommended"""

class IRecommendations(Interface):
    context = Attribute("Context object")
    recs = Attribute("Recommendations storage")

    def isRecommended():
        """Whether this object is recommended at least by one Advisor"""

    def isRecommendedBy(userid):
        """Whether this object was recommended by given user"""

    def numberOfRecommends():
        """Returns number of recommendations for this object"""

    def recommend(userid):
        """Given user Recommends this object"""

    def unrecommend(userid):
        """Given user Removes Recommends from this object"""

class Recommendations(object):

    def __init__(self, context):
        self.context = context
        anno = IAnnotations(context)
        if ANNO_KEY not in anno:
            anno[ANNO_KEY] = OIBTree()
        self.recs = anno[ANNO_KEY]

    def isRecommended(self):
        """See interface"""
        return len(self.recs) > 0 and True or False

    def isRecommendedBy(self, userid):
        """See interface"""
        return userid in self.recs and True or False

    def numberOfRecommends(self):
        """See interface"""
        return len(self.recs)

    def recommend(self, userid):
        """See interface"""
        self.recs[userid] = 1

    def unrecommend(self, userid):
        """See interface"""
        if userid in self.recs:
            self.recs.pop(userid)
