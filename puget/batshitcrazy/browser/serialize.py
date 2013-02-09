from Products.Five.browser import BrowserView
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from zope.component import queryUtility
from zope.component import getAdapter
from zope.component import ComponentLookupError
import logging
import datetime
import json


class SerializeToJson(BrowserView):
    """Serialize a Dexterity content type to JSON
    """
    def __call__(self):
        import pdb;pdb.set_trace()
        item = self.context
        meta = {'type': item.portal_type,
               'id': item.id,
               # ??? allow this section to be turned off 
               'creator': item.Creator(),
               'created': str(item.creation_date),
               'url': item.absolute_url(),
               # DateTime is not JSON serializable
               'modfied': str(item.modification_date),
        }
        # ??? indicate version of schema and schema name
        # look up the base schema
        fti = queryUtility(IDexterityFTI, name=item.portal_type)
        model = fti.lookupModel()
        schema = model.schema
        fields = {}
        for name in schema.names():
            # don't barf on missing/bad attrs
            value = getattr(item, name, '')
            fields[name] = value

        # look up activated behavior schemas
        for b_schema in getAdditionalSchemata(context=item):
            try:
                # behaviors have adapters for accessors
                access = getAdapter(item, b_schema)
                for name in b_schema._v_attrs.keys():
                    # then.... is getattr correct?
                    fields[name] = getattr(access, name, '')
            except ComponentLookupError, e:
                logging.debug("Couldn't find adapter for %s with schema %s " %
                              item, b_schema)
                pass

        # check security

        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        marshall = {
            'meta': meta,
            'fields': fields,
        }
        return json.dumps(marshall, cls=IsoDateTimeEncoder)


class IsoDateTimeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime) or \
            isinstance(obj, datetime.date):
            # standard JSON time format
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
