

# https://jsonapi.org/format/#document-resource-identifier-objects
def build_resource_identifier(type, id):
    return {"type": type, "id": id}


# https://jsonapi.org/format/#document-links
def build_links_object(links):
    links_object = {}

    #links is a dict, loop through it and build_link
    # {
    # 'key': {
    #     'responder': ResponderClass,
    #     'href': 'http://example.com/comments/{posts.comments}',
    #     'meta': {"whatever": "data", "here": true}
    #     },
    # "more keys" : {...},
    # ...
    # }
    for key, value in links:
        try:
            meta_info = value['meta']
        except KeyError:
            meta_info = None

        links_object[key] = build_link(
            value['responder'].TYPE,
            value['href'],
            meta = meta_info
        )

    return links_object
    

#builds an individual link inside a links object
#returns either a string or a "link object"
# see https://jsonapi.org/format/#document-links
def build_link(key, url, meta=None):
    if meta is not None:
        link = {}
        link['href'] = url
        link['meta'] = self.build_meta(meta)
        return link
    else:
        return url

