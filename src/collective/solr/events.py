# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.permissions import ModifyPortalContent

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware

try:
    from Products.Archetypes.CatalogMultiplex import CatalogMultiplex
except ImportError:
    class CatalogMultiplex(object):
        pass

def reorderedEvent(event):
    parent = event.object
    mtool = getToolByName(parent, "portal_membership")
    if mtool.checkPermission(ModifyPortalContent, parent):
        for child in parent.objectValues():
            if isinstance(child, (CatalogMultiplex, CMFCatalogAware)):
                child.reindexObject(["getObjPositionInParent"])
