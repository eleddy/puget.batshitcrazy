from Products.Five.browser import BrowserView
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from plone.namedfile.file import NamedBlobImage
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
        fields = item.asDictionary()

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
        elif isinstance(obj, NamedBlobImage):
            # ideally this actually resturns url but given that the
            # caller alerady has context, they can do it for now
            return obj.filename

        return json.JSONEncoder.default(self, obj)
