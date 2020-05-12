import pytest
from hyp.helpers import *
from hyp.base import BaseResponder, BaseAdapter

from fixtures import CommentSerializer

class TestBuildResourceIdentifier(object):

    def test_resource_identifier_creation(self):
        resource_id = {'id': 1, 'type': 'item'}

        assert build_resource_identifier("item", 1) == resource_id

class TestBuildMeta(object):

    def test_meta(self):
        meta_info = {"hello": "world"}

        assert build_meta(meta_info) == meta_info

class TestBuildLinksObject(object):

    class ResponderClass(BaseResponder):
        TYPE = 'comments'
        SERIALIZER = CommentSerializer
        ADAPTER = BaseAdapter

    def test_build_string_link(self):
        url = "https://www.example.com/url/for/self/"
        assert build_link(url) == url


    def test_build_object_link(self):
        meta_info = {"hello": "world"}
        url = "https://www.example.com/url/for/self/"
        result = {
            "href": url,
            "meta": meta_info
        }

        assert build_link(url, meta=meta_info) == result


    def test_creating_string_links(self):

        links_input = {
            'comments': {
                'responder': self.ResponderClass,
                'href': 'http://example.com/comments/'
            }
        }

        links_output = {
            "comments": "http://example.com/comments/"
        }

        assert build_links_object(links_input) == links_output

    def test_creating_object_links(self):

        links_input = {
            'comments': {
                'responder': self.ResponderClass,
                'href': 'http://example.com/comments/',
                'meta': { "whatever": "data", "here": True }
            }
        }

        links_output = {
            "comments": {
                "href": "http://example.com/comments/",
                "meta": { "whatever": "data", "here": True }
            }
        }

        assert build_links_object(links_input) == links_output