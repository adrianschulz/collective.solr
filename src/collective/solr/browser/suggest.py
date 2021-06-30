# -*- coding: utf-8 -*-
import json
import six.moves.urllib.request
import six.moves.urllib.parse
import six.moves.urllib.error

from collective.solr.interfaces import ISolrConnectionManager
from Products.Five.browser import BrowserView
from zope.component import getUtility


class SuggestView(BrowserView):
    def __call__(self):
        retval = {
            'suggestions': [],
            'categoryTitle': 'Spellchecking',
            'category': 'spellchecking'
        }
        term = self.request.get("term", "")
        if not term:
            return json.dumps(retval)
        manager = getUtility(ISolrConnectionManager)
        connection = manager.getConnection()

        if connection is None:
            return json.dumps(retval)

        params = {}
        params["q"] = term
        params["wt"] = "json"

        params = six.moves.urllib.parse.urlencode(params, doseq=True)
        response = connection.doGet(connection.solrBase + "/spell?" + params, {})
        results = json.loads(response.read())

        # Check for spellcheck
        spellcheck = results.get("spellcheck", None)
        if not spellcheck:
            return json.dumps(retval)

        # Check for existing spellcheck suggestions
        spellcheck_suggestions = spellcheck.get("suggestions", None)
        spellcheck_collations = spellcheck.get("collations", [])
        correctly_spelled = spellcheck_suggestions == [u"correctlySpelled", True]

        # Autocomplete
        if correctly_spelled:
            retval['suggestions'] = [x["Title"] for x in results["response"]["docs"]]
            return json.dumps(retval)

        for i, spellcheck_collation in enumerate(spellcheck_collations):
            # skip collationname
            if i % 2 == 0:
                continue

            # effective collation
            collation = spellcheck_collation
            collation_suggestion = collation['collationQuery']

            if collation_suggestion:
                retval['suggestions'].append(dict(label=collation_suggestion, value=collation_suggestion))

        if not spellcheck_suggestions:
            return json.dumps(retval)

        # Collect suggestions
        if spellcheck_suggestions[1]:
            for suggestion in spellcheck_suggestions[1]["suggestion"]:
                retval['suggestions'].append(dict(label=suggestion['word'], value=suggestion['word']))

        return json.dumps(retval)


class AutocompleteView(BrowserView):
    def __call__(self):
        retval = {
            'suggestions': [],
            'categoryTitle': 'Autocomplete',
            'category': 'autocomplete'
        }
        term = self.request.get("term", "")
        if not term:
            return json.dumps(retval)
        manager = getUtility(ISolrConnectionManager)
        connection = manager.getConnection()

        if connection is None:
            return json.dumps(retval)

        params = {}
        params["q"] = term
        params["wt"] = "json"

        params = six.moves.urllib.parse.urlencode(params, doseq=True)
        url = connection.solrBase + "/autocomplete?" + params
        response = connection.doGet(url, {})
        results = json.loads(response.read())

        # unwrap suggestions
        if 'suggest' not in results:
            return json.dumps(retval)
        if 'suggest' not in results['suggest']:
            return json.dumps(retval)
        if term not in results['suggest']['suggest']:
            return json.dumps(retval)

        suggestions = results['suggest']['suggest'][term]
        if 'numFound' not in suggestions:
            return json.dumps(retval)
        if not suggestions['numFound']:
            return json.dumps(retval)

        suggestions_terms = [suggestion['term'] for suggestion in suggestions['suggestions']]

        for suggestion_term in suggestions_terms:
            retval['suggestions'] .append(dict(label=suggestion_term, value=suggestion_term))
        return json.dumps(retval)
