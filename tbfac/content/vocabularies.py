from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from tbfac.content import MessageFactory as _

class regions(object):
    """ regions
    """
    implements(IVocabularyFactory)
    def __call__(self, context=None):
        items = (
            SimpleTerm(value='TaipeiCity', title=_(u'Taipei City')),
            SimpleTerm(value='NewTaipeiCity', title=_(u'New Taipei City')),
            SimpleTerm(value='TaichungCity', title=_(u'Taichung City')),
            SimpleTerm(value='TainanCity', title=_(u'Tainan City')),
            SimpleTerm(value='KaohsiungCity', title=_(u'Kaohsiung City')),
        )
        return SimpleVocabulary(items)
regionsFactory = regions()

