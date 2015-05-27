# -*- coding: utf-8 -*-

from django.http import Http404
from piston.handler import BaseHandler, HandlerMetaClass

from version import AppVersion, NoAppVersion


_call_map = {
    'read': 'get',
    'create': 'post',
    'update': 'put',
    'delete': 'delete',
}


class VersionedApi(object):
    """
    Versioned API decorators

    Usually, use "va" (by default) shorts for VersionedApi.
    Support 4 classic HTTP:
        GET
        POST
        PUT
        DELETE
    with different decorators.

    Usage:
        Use as a decorator, with a version and some optional parameters,
        like: @va.get('1.4.2'), @va.post('1.1', exact=True),
              or @va.delete('2.0'), etc.

        Version params:
            version - By default, the rules is to find the biggest version
                      that smaller than the request version.
                      E.g. there are handlers for v1.0, v1.4 and v3.0
                           Request Version --> Handler Version
                                      v1.0 --> v1.0
                                      v1.2 --> v1.0
                                      v1.4 --> v1.4
                                      v2.0 --> v1.4
                                      v4.0 --> v3.0

        Optional params:
            exact - Boolean, default is False, means this handler is invoked
                    ONLY when the version exactly equales.

        Examples:
            ```
            @va.get('1.0')
            def get_handler_func(...):
                print 'GET handler for >= v1.0'

            @va.get('1.1', exact=True)
            def get_handler_func(...):
                print 'GET handler for == v1.1, but v1.2 will use handler v1.0'

            @va.get('1.3')
            def get_handler_func(...):
                print 'GET handler for >= v1.3'

            @va.post('1.0')
            def post_handler_func(...):
                print 'POST handler for >= v1.0'
            ```
    """
    # Some version types:
    #   exact - Only if the request version equals exactly to
    #           the handler version.
    VERSION_TYPES = {'exact': False, }

    @classmethod
    def parse_version(cls, *args, **kwargs):
        """
        Overwrite this method to parse the Version from decorator parameters
        """
        version = NoAppVersion()
        all_version = args[0] if args else None
        ios = kwargs.get('ios', all_version)
        android = kwargs.get('android', all_version)
        web = kwargs.get('web', all_version)

        if any([all_version, ios, android, web]):
            version = AppVersion(ios=ios, android=android, web=web)
        return version

    @classmethod
    def build_http_methods(cls):
        """
        Build 4 decorators: @get, @post, @put and @delete
        """
        def __factory(name):
            @classmethod
            def func(cls, *args, **kwargs):
                def wrap(http_handler):
                    def _decorated(*args, **kwargs):
                        return http_handler(*args, **kwargs)
                    setattr(_decorated, '__bt_version', (name, version))
                    setattr(_decorated, '__bt_version_types', version_types)
                    return _decorated

                version_types = [v_type for v_type in cls.VERSION_TYPES
                                 if kwargs.pop(v_type, cls.VERSION_TYPES[v_type])]

                if len(args) == 1 and not kwargs and callable(args[0]):
                    # for @va.get
                    version = cls.parse_version()
                    return wrap(args[0])
                else:
                    # for @va.get() or @va.get('1.0')
                    version = cls.parse_version(*args, **kwargs)
                    return wrap

            return func

        for name in _call_map.values():
            setattr(cls, name, __factory(name))


VersionedApi.build_http_methods()
va = VersionedApi  # 'va' is shortcut for VersionApi


class VersionedHandlerMeta(HandlerMetaClass):
    """
    Meta class of VersionedHandler

    While initialing a handler, register each function that has been
    decorated with version.
    """
    def __new__(metacls, name, bases, dct):
        _versioned_handlers = dict((v, {}) for v in _call_map.values())
        _exact_versioned_handlers = dict((v, {}) for v in _call_map.values())

        dct.setdefault('_versioned_handlers', _versioned_handlers)
        dct.setdefault('_exact_versioned_handlers', _exact_versioned_handlers)

        for k in dct:
            func = dct[k]
            method, version = getattr(func, '__bt_version', (None, None))
            version_types = getattr(func, '__bt_version_types', None)

            if method in _versioned_handlers:
                if 'exact' in version_types:
                    dct['_exact_versioned_handlers'][method][version] = func
                else:
                    dct['_versioned_handlers'][method][version] = func

        return super(VersionedHandlerMeta, metacls).__new__(
            metacls, name, bases, dct
        )


class VersionedHandler(BaseHandler):
    __metaclass__ = VersionedHandlerMeta

    def get_version(self, request):
        """
        Overwrite this method if you want to customize version getter
        """
        raise NotImplemented

    def __get_v_handler(self, meth, request):
        v = self.get_version(request)

        exact_handlers = self._exact_versioned_handlers[meth]
        for version in exact_handlers:
            if v == version:
                return exact_handlers[version]

        handlers = self._versioned_handlers[meth]
        for version in sorted(handlers.keys(), reverse=True):
            if v < version:
                continue
            return handlers[version]
        raise Http404

    def format_response_data(self, data):
        """
        Format your response data, as a professional API.

        Rewrite this method to customize format.
        """
        return data

    def read(self, request, *args, **kwargs):
        data = self.__get_v_handler('get', request)(self, request, *args, **kwargs)
        return self.format_response_data(data)

    def create(self, request, *args, **kwargs):
        data = self.__get_v_handler('post', request)(self, request, *args, **kwargs)
        return self.format_response_data(data)

    def update(self, request, *args, **kwargs):
        data = self.__get_v_handler('put', request)(self, request, *args, **kwargs)
        return self.format_response_data(data)

    def delete(self, request, *args, **kwargs):
        data = self.__get_v_handler('delete', request)(self, request, *args, **kwargs)
        return self.format_response_data(data)
