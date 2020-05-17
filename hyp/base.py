"""Base classes for the ``Responders`` and ``Adapters``.
"""
import json
from .collector import Collector

from six import iteritems

from .helpers import *

class NonCompliantException(Exception):
    pass

class BaseResponder(object):
    TYPE = None
    SERIALIZER = None
    LINKS = None
    ADAPTER = None
    # Responder can override this if the key to obtain the ID is
    # something other than "id". responses always use the key "id" as per spec
    id_access_key = "id" 

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

    def _respond(self, instance_or_instances, meta=None, error=False, links=None, related=None, collect=False, compound=False):
        links = self.links(links, related)

        document = {
            "jsonapi": {
                "version": "1.0"
            }
        }

        if meta is not None:
            document['meta'] = build_meta(meta)

        if error:
            #assumes the error object is ok since it's pretty loosely spec-ed 
            if not isinstance(instance_or_instances, list):
                document['errors'] = list(instance_or_instances)
            else:
                document['errors'] = instance_or_instances

        else:
            data = {}
            collector = Collector()

            if related is not None:
                self.collect_included(collector, related)

            if links is not None:
                self.collect_links(collector, links)

            if collect:
                links = list(self.LINKS.keys())
                data = self.build_resources(instance_or_instances, links, collector)
            else:
                data = self.build_resources(instance_or_instances, links)

            if compound:
                document['included'] = collector.get_included_resources() # TODO: maybe call this like get included data or something because relationships dict is different
            
            document['links'] = collector.get_links_dict()

            document['data'] = data

        # Filter out empty lists
        return dict([(k, d) for k, d in list(document.items()) if d])

    def links(self, links, included):
        if included is not None:
            links = list(included.keys())

        return links

    def collect_links(self, collector, links):
        # Use the collector to build the links structure
        for key in links:
            collector.link(self, key)

    def collect_included(self, collector, included):
        for key, instances in iteritems(included):
            link = self.LINKS[key]
            responder = link['responder']()

            for instance in instances:
                resource = responder.build_resource(instance)
                collector.include(responder.TYPE, self.id_access_key, resource)

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
                    collector.link(self, link)

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
                builder = lambda instance: self.collect(collector, responder, link, instance, responder.id_access_key)
            else:
                builder = lambda instance: self.pick(instance, self.id_access_key)
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
            responder_links = list(responder.LINKS.keys())
            resource = responder_instance.build_resource(instance, responder_links, collector)
            collector.include(responder.TYPE, id, resource)
        else:
            collector.include(responder.TYPE, id, instance)

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
