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
            SimpleTerm(value='KeelungCity', title=_(u'Keelung City')),
            SimpleTerm(value='TaipeiCity', title=_(u'Taipei City')),
            SimpleTerm(value='NewTaipeiCity', title=_(u'New Taipei City')),
            SimpleTerm(value='TaoyuanCounty', title=_(u'Taoyuan County')),
            SimpleTerm(value='HsinchuCounty', title=_(u'Hsinchu County')),
            SimpleTerm(value='HsinchuCity', title=_(u'Hsinchu City')),
            SimpleTerm(value='MiaoliCounty', title=_(u'Miaoli County')),
            SimpleTerm(value='TaichungCity', title=_(u'Taichung City')),
            SimpleTerm(value='NantouCounty', title=_(u'Nantou County')),
            SimpleTerm(value='ChanghuaCounty', title=_(u'Changhua County')),
            SimpleTerm(value='YunlinCounty', title=_(u'Yunlin County')),
            SimpleTerm(value='ChiayiCity', title=_(u'Chiayi City')),
            SimpleTerm(value='ChiayiCounty', title=_(u'Chiayi County')),
            SimpleTerm(value='TainanCity', title=_(u'Tainan City')),
            SimpleTerm(value='KaohsiungCity', title=_(u'Kaohsiung City')),
            SimpleTerm(value='PingtungCounty', title=_(u'Pingtung County')),
            SimpleTerm(value='YilanCounty', title=_(u'Yilan County')),
            SimpleTerm(value='HualienCounty', title=_(u'Hualien County')),
            SimpleTerm(value='TaitungCounty', title=_(u'Taitung County')),
            SimpleTerm(value='PenghuCounty', title=_(u'Penghu County')),
            SimpleTerm(value='LienchiangCounty', title=_(u'Lienchiang County')),
            SimpleTerm(value='KinmenCounty', title=_(u'Kinmen County')),
        )
        return SimpleVocabulary(items)
regionsFactory = regions()

