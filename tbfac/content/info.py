from five import grok
from plone.directives import dexterity, form
from plone.indexer import indexer
from DateTime import DateTime

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from tbfac.content import MessageFactory as _
from tbfac.content.venue import IVenue

from plone.memoize.instance import memoize
from Products.ATContentTypes.utils import dt2DT

# Interface class; used to define content-type schema.

class IInfo(form.Schema, IImageScaleTraversable):
    """
    TBFAC Info Type
    """
    
    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/info.xml to define the content type
    # and add directives here as necessary.
    
    #form.model("models/info.xml")
    
    organizer = schema.TextLine(
        title=_(u'Organizer'),
        required=False,
    )

    category = schema.List(
        title=_(u'Category'),
        value_type=schema.Choice(
            values=[_(u'Show'), _(u'Dancing'), _(u'Music'), _(u'Drama'), _(u'Opera')]
        ),
        required=False,
    )

    startDate = schema.Date(
        title=_(u'Start Date'),
    )

    endDate = schema.Date(
        title=_(u'End Date'),
    )
 
    dateDetails = schema.Text(
        title=_(u'Date Details'),
        description=_(u'Date Details Description'),
        required=False,
    )

    region = schema.List(
        title=_(u"Region"),
        value_type=schema.Choice(
            vocabulary='regions',
            required=False,
        ),
    )

    venue = RelationList(
        title=_(u'Venue'),
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                object_provides=IVenue.__identifier__,
                #navigation_tree_query={
                #    'path': {'query': '/taishin/venues'}
                #},
            ),
        ),
        required=False,
    )

    text = RichText(
        title=_(u'Body'),
        required=False,
    )

    feeDetails = schema.Text(
        title=_(u'Fee Details'),
        description=_(u'Fee Details Description'),
        required=False,
    )

    ticketURL = schema.TextLine(
        title=_(u'Ticket URL'),
        required=False,
    )

    contactPhone = schema.TextLine(
        title=_(u'Contact Phone'),
        required=False,
    )

    contactName = schema.TextLine(
        title=_(u'Contact Name'),
        required=False,
    )

    eventURL = schema.TextLine(
        title=_(u'Event URL'),
        required=False,
    )

    image = NamedBlobImage(
        title=_(u'Lead Image'),
        required=False,
    )

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

    
class Info(dexterity.Item):
    grok.implements(IInfo)
    
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# info_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

# add custom indexers to store the start and end values
# in Zope DateTime Format to maintain compatibility with
# The current CalendarTool and portlet

@indexer(IInfo)
def startIndexer(obj):
    if obj.startDate is None:
        return None
    return DateTime(obj.startDate.isoformat())
grok.global_adapter(startIndexer, name="start")

@indexer(IInfo)
def endIndexer(obj):
    if obj.endDate is None:
        return None
    return DateTime(obj.endDate.isoformat())
grok.global_adapter(endIndexer, name="end")

@indexer(IInfo)
def categoryIndexer(obj):
    if obj.category is None:
        return None
    return obj.category
grok.global_adapter(categoryIndexer, name="category")

@indexer(IInfo)
def regionIndexer(obj):
    if obj.region is None:
        return None
    return obj.region
grok.global_adapter(regionIndexer, name="region")


class View(grok.View):
    grok.context(IInfo)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        """Prepare information for the template
        """
        if self.context.startDate is not None:
            self.startDateFormatted = self.context.startDate.strftime(
                "%d %b %Y")

        if self.context.endDate is not None:
            self.endDateFormatted = self.context.endDate.strftime("%d %b %Y")

    @memoize
    def venueInfo(self):
        venues = []
        if self.context.venue is not None:
            for ref in self.context.venue:
                obj = ref.to_object
                venues.append({
                    'url': obj.absolute_url(),
                    'title': obj.title,
                    'address': obj.address
                })
        return venues

