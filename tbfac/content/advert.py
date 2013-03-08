from five import grok
from plone.directives import dexterity, form

from zope import schema

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage

from tbfac.content import MessageFactory as _


# Interface class; used to define content-type schema.

class IAdvert(form.Schema, IImageScaleTraversable):
    """
    TBFAC Advert Type
    """
    
    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/advert.xml to define the content type
    # and add directives here as necessary.
    
    #form.model("models/advert.xml")
    
    image = NamedBlobImage(
        title=_(u'Lead Image'),
        description=_(u"Upload a Image of Size 230x230."),
        required=True,
    )

    url = schema.TextLine(
        title=_(u'URL'),
        required=False,
    )

    above = schema.TextLine(
        title=_(u'Text Above'),
        description=_(u"Text Above the Title."),
        required=False,
    )

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

    
class Advert(dexterity.Item):
    grok.implements(IAdvert)
    
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


class View(grok.View):
    grok.context(IAdvert)
    grok.require('zope2.View')
    grok.name('view')

