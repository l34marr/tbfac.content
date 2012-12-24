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
from tbfac.content.info import IInfo

from plone.memoize.instance import memoize


class INomination(form.Schema):
    """
    TBFAC Nomination Type
    """

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    category = schema.List(
        title=_(u'Award Category'),
        value_type=schema.Choice(
            values=[_(u'Visual Arts'), _(u'Performing Arts'), _(u'Uncatrgorized')]
        ),
        required=False,
    )

    info = RelationList(
        title=_(u'Nominated Info'),
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                object_provides=IInfo.__identifier__,
                #navigation_tree_query={
                #    'path': {'query': '/taishin/event/info'}
                #},
            ),
        ),
    )

    text = RichText(
        title=_(u'Body'),
        required=False,
    )


# View class

class View(grok.View):
    grok.context(INomination)
    grok.require('zope2.View')
    grok.name('view')

