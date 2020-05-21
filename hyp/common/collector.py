from collections import defaultdict

# Handles the collection of used links along with the included items,
# centralizes building of the links and included documents for the output
class Collector(object):

    def __init__(self):
        self.included = defaultdict(dict) # the resources that are used, ready for inclusion in a possible compound document response
        self.links = defaultdict(set) #the links objects themselves

    def include(self, type, id, resource):
        # Added to a dict to strip duplicates and sort results.
        self.included[type][id] = resource

    def link(self, responder, key):
        # Flag each entry as they are used, final structure will
        # be built at the end.
        self.links[responder].add(key)

    def get_included_resources(self):
        # Convert the defaultdict(dict) structure to a dict(list) structure
        return dict([(k, list(items.values())) for k, items in list(self.included.items())])

    def get_links_dict(self):
        # Build the links structure for the links that have been used
        rv = {}

        for responder, keys in list(self.links.items()):
            for key in keys:
                link = responder.LINKS[key]
                association = "%s.%s" % (responder.TYPE, key)

                rv[association] = {'type': link['responder'].TYPE}
                if 'href' in link:
                    rv[association]['href'] = link['href']

        return rv
