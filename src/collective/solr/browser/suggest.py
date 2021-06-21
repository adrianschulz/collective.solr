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
        suggestions = []
        term = self.request.get("term", "")
        if not term:
            return json.dumps(suggestions)
        manager = getUtility(ISolrConnectionManager)
        connection = manager.getConnection()

        if connection is None:
            return json.dumps(suggestions)

        params = {}
        params["q"] = term
        params["wt"] = "json"

        params = six.moves.urllib.parse.urlencode(params, doseq=True)
        response = connection.doGet(connection.solrBase + "/spell?" + params, {})
        results = json.loads(response.read())

        # Check for spellcheck
        spellcheck = results.get("spellcheck", None)
        if not spellcheck:
            return json.dumps(suggestions)

        # Check for existing spellcheck suggestions
        spellcheck_suggestions = spellcheck.get("suggestions", None)
        spellcheck_collations = spellcheck.get("collations", [])
        correctly_spelled = spellcheck_suggestions == [u"correctlySpelled", True]

        # Autocomplete
        if correctly_spelled:
            return json.dumps([x["Title"] for x in results["response"]["docs"]])

        for i, spellcheck_collation in enumerate(spellcheck_collations):
            # skip collationname
            if i % 2 == 0:
                continue

            # effective collation
            collation = spellcheck_collation
            collation_suggestion = collation['collationQuery']

            if collation_suggestion:
                suggestions.append(dict(label=collation_suggestion, value=collation_suggestion))

        if not spellcheck_suggestions:
            return json.dumps(suggestions)

        # Collect suggestions
        if spellcheck_suggestions[1]:
            for suggestion in spellcheck_suggestions[1]["suggestion"]:
                suggestions.append(dict(label=suggestion['word'], value=suggestion['word']))

        return json.dumps(suggestions)


class AutocompleteView(BrowserView):
    def __call__(self):
        term = self.request.get("term", "")
        if not term:
            return json.dumps([])
        manager = getUtility(ISolrConnectionManager)
        connection = manager.getConnection()

        if connection is None:
            return json.dumps([])

        params = {}
        params["q"] = term
        params["wt"] = "json"

        params = six.moves.urllib.parse.urlencode(params, doseq=True)
        url = connection.solrBase + "/autocomplete?" + params
        response = connection.doGet(url, {})
        results = json.loads(response.read())

        # unwrap suggestions
        if 'suggest' not in results:
            return json.dumps([])
        if 'suggest' not in results['suggest']:
            return json.dumps([])
        if term not in results['suggest']['suggest']:
            return json.dumps([])

        suggestions = results['suggest']['suggest'][term]
        if 'numFound' not in suggestions:
            return json.dumps([])
        if not suggestions['numFound']:
            return json.dumps([])

        suggestions_terms = [suggestion['term'] for suggestion in suggestions['suggestions']]

        result = []
        for suggestion_term in suggestions_terms:
            result.append(dict(label=suggestion_term, value=suggestion_term))
        return json.dumps(result)
