import json

from fixtures import PostResponder


def test_one_to_many(post, comment_factory):
    post.comments = [
        comment_factory(id=1, content='My comment'),
        comment_factory(id=2, content='Another comment'),
    ]

    data = PostResponder().respond(post, links=['comments'])

    assert json.loads(data) == {
        'posts': [
            {
                'id': 1,
                'title': 'My title',
                'links': {
                    'comments': [1, 2],
                }
            },
        ],
        'links': {
            'posts.comments': {
                'href': 'http://example.com/comments/{posts.comments}',
                'type': 'comments',
            }
        }
    }