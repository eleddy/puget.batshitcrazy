from Products.Five.browser import BrowserView
import json


class SerializeToJson(BrowserView):
    """Serialize a Dexterity content type to JSON
    """
    def __call__(self):
        item = {'it works':'maybe'}
        # indicate version of schema and schema name

        # check security

        self.request.response.setHeader('Content-Type', 'application/json; charset=utf-8')
        return json.dumps(item)
