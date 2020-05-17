import json

from fixtures import PostResponder


class TestBuild(object):
    def test_single(self):
        response = PostResponder.build({'id': 1, 'title': 'My title'})

        assert response == {
            'data': {
                'attributes': {'title': 'My title'},
                'id': 1,
                'type': 'posts'
            },
            'jsonapi': {'version': '1.0'}
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
            'jsonapi': {'version': '1.0'}
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
            'jsonapi': {'version': '1.0'}
        }


def test_meta():
    response = PostResponder.build(
        {'id': 1, 'title': 'Yeah'},
        meta={'key': 'value'},
    )

    assert response['meta']['key'] == 'value'
