import json

from fixtures import PostResponder
from hyp.constants import JSONAPI_VERSION_DICT

class TestBuild(object):
    def test_single(self):
        response = PostResponder.build({'id': 1, 'title': 'My title'})

        assert response == {
            'data': {
                'attributes': {'title': 'My title'},
                'id': 1,
                'type': 'posts'
            },
            'jsonapi': JSONAPI_VERSION_DICT
        }

    def test_multiple(self):
        response = PostResponder.build([
            {'id': 1, 'title': 'A title'},
            {'id': 2, 'title': 'Another title'},
        ])

        assert response == {
            'data': [{
                'attributes': {'title': 'A title'},
                'id': 1,
                'type': 'posts'
            },
            {
                'attributes': {'title': 'Another title'},
                'id': 2,
                'type': 'posts'
            }],
            'jsonapi': JSONAPI_VERSION_DICT
        }


class TestRespond(object):
    def test_single(self):
        response = PostResponder.respond(
            {'id': 1, 'title': 'A title'}
        )

        assert json.loads(response) == {
            'data': {
                'attributes': {'title': 'A title'},
                'id': 1,
                'type': 'posts'
            },
            'jsonapi': JSONAPI_VERSION_DICT
        }


def test_meta():
    response = PostResponder.build(
        {'id': 1, 'title': 'Yeah'},
        meta={'key': 'value'},
    )

    assert response['meta']['key'] == 'value'
