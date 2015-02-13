from hyp.schematics import Responder as SchematicsResponder

from fixtures import PostResponder, PostSerializer, CommentResponder


class TestCollect(object):
    def test_one_to_one_with_collect(self):
        author = {'id': 1}
        post = {'id': 1, 'title': 'My title', 'author': author}

        response = PostResponder.build(post, collect=True)

        assert response == {
            'posts': {
                'id': 1,
                'title': 'My title',
                'links': {
                    'author': 1,
                }
            },
            'linked': {
                'author': [author],
            },
            'links': {
                'posts.author': {
                    'href': 'http://example.com/people/{posts.author}',
                    'type': 'people',
                },
                'posts.comments': {
                    'href': 'http://example.com/comments/{posts.comments}',
                    'type': 'comments',
                },
            }
        }

    def test_nested_collection(self):
        author = {'id': 1}
        flamer = {'id': 2}
        comment = {'id': 1, 'content': '<redacted>', 'author': flamer}
        post = {
            'id': 1,
            'title': 'My title',
            'author': author,
            'comments': [comment],
        }

        response = PostResponder.build(post, collect=True)

        assert response == {
            'posts': {
                'id': 1,
                'title': 'My title',
                'links': {
                    'author': 1,
                    'comments': [1],
                }
            },
            'linked': {
                'author': [author, flamer],
                'comments': [
                    {
                        'id': 1,
                        'content': '<redacted>',
                        'links': {
                            'author': 2
                        }
                    }
                ],
            },
            'links': {
                'posts.author': {
                    'href': 'http://example.com/people/{posts.author}',
                    'type': 'people',
                },
                'posts.comments': {
                    'href': 'http://example.com/comments/{posts.comments}',
                    'type': 'comments',
                },
            }
        }


