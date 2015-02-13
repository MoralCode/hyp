"""Base classes for the ``Responders`` and ``Adapters``.
"""
import json
from .collector import Collector

from six import iteritems


class BaseResponder(object):
    TYPE = None
    SERIALIZER = None
    LINKS = None
    ADAPTER = None

    def __init__(self):
        if not self.ADAPTER:
            raise NotImplementedError('Responder must define ADAPTER class variable')
        self.adapter = self.ADAPTER(self.SERIALIZER)

    @classmethod
    def build(cls, *args, **kwargs):
        return cls()._respond(*args, **kwargs)

    @classmethod
    def respond(cls, *args, **kwargs):
        return json.dumps(cls()._respond(*args, **kwargs))

    def _respond(self, instance_or_instances, meta=None, links=None, linked=None, collect=False):
        links = self.links(links, linked)

        document = {}

        if meta is not None:
            document['meta'] = self.build_root_meta(meta)

        if linked is not None:
            document['linked'] = self.build_root_linked(linked)

        if collect:
            collector = Collector()

            links = self.LINKS.keys()
            document[self.TYPE] = self.build_resources(instance_or_instances, links, collector)
            document['linked'] = collector.get_linked_dict()
            document['links'] = collector.get_links_dict()
        else:
            if links is not None:
                document['links'] = self.build_root_links(links)
            document[self.TYPE] = self.build_resources(instance_or_instances, links)

        return document

    def links(self, links, linked):
        if linked is not None:
            links = linked.keys()

        return links

    def build_root_meta(self, meta):
        return meta

    def build_root_links(self, links):
        # Use the collector to build the links structure
        collector = Collector()
        for key in links:
            collector.use_link(self, key)

        return collector.get_links_dict()

    def build_root_linked(self, linked):
        collector = Collector()

        for key, instances in iteritems(linked):
            link = self.LINKS[key]
            responder = link['responder']()

            for instance in instances:
                id = self.pick(instance, 'id')
                resource = responder.build_resource(instance)
                collector.add_linked(responder.TYPE, id, resource)

        return collector.get_linked_dict()

    def build_resources(self, instance_or_instances, links=None, collector=None):
        builder = lambda instance: self.build_resource(instance, links, collector)
        return self.apply_to_object_or_list(builder, instance_or_instances)

    def build_resource(self, instance, links=None, collector=None):
        resource = self.adapter(instance)
        if links is not None:
            resource['links'] = self.build_resource_links(instance, links, collector)
        return resource

    def build_resource_links(self, instance, links, collector=None):
        resource_links = {}

        for link in links:
            properties = self.LINKS[link]

            try:
                key = properties.get('key', link)
                associated = self.pick(instance, key)
                if collector:
                    collector.use_link(self, link)

            except KeyError:
                # Ignore links when not defined in the object
                continue

            if isinstance(associated, list):
                associated = [i for i in associated if i is not None]
                if len(associated) == 0:
                    continue
            else:
                if associated is None:
                    continue

            if collector is not None:
                responder = properties['responder']
                builder = lambda instance: self.collect(collector, responder, link, instance, 'id')
            else:
                builder = lambda instance: self.pick(instance, 'id')
            resource_links[link] = self.apply_to_object_or_list(builder, associated)

        return resource_links

    def apply_to_object_or_list(self, func, object_or_list):
        if isinstance(object_or_list, list):
            return list(map(func, object_or_list))
        else:
            return func(object_or_list)

    def collect(self, collector, responder, type, instance, key):
        responder_instance = responder()
        id = self.pick(instance, key)

        if responder.LINKS and self.pick(instance, key):
            responder_links = responder.LINKS.keys()
            resource = responder_instance.build_resource(instance, responder_links, collector)
            collector.add_linked(type, id, resource)
        else:
            collector.add_linked(type, id, instance)

        return id

    def pick(self, instance, key):
        try:
            return getattr(instance, key)
        except AttributeError:
            return instance[key]


class BaseAdapter(object):
    """Base class from which all :class:`Adapter` classes inherit.
    """

    def __call__(self, instance):
        """Serialize ``instance`` to a dictionary of Python primitives."""
        raise NotImplementedError('Adapter class must define __call__')
