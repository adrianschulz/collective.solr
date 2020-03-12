# -*- coding: utf-8 -*-
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from collective.solr.browser.interfaces import IThemeSpecific
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import TextField
from zope.interface import implementer

from collective.solr import SolrMessageFactory as _


class ExtentionTextField(ExtensionField, TextField):
    pass


class ExtensionBooleanField(ExtensionField, BooleanField):
    pass


@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class SearchExtender(object):
    """Adapter that adds search metadata."""

    layer = IThemeSpecific

    _fields = [
        ExtensionBooleanField(
            "showinsearch",
            languageIndependent=True,
            schemata="settings",
            default=True,
            widget=BooleanWidget(
                label=_("label_showinsearch", default=u"Show in search"),
                visible={"edit": "visible", "view": "invisible"},
                description="",
            ),
        ),
        ExtentionTextField(
            "searchwords",
            searchable=True,
            schemata="settings",
            languageIndependent=False,
            widget=TextAreaWidget(
                label=_("label_searchwords", default=u"Search words"),
                description=_(
                    "help_searchwords",
                    u"Specify words for which this item will show up "
                    u"as the first search result. Multiple words can be "
                    u"specified on new lines.",
                ),
                visible={"edit": "visible", "view": "invisible"},
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self._fields
