# -*- coding: utf-8 -*-


class AppVersion(object):
    """
    Sample APP Version
    """
    def __init__(self, ios=None, android=None, web=None):
        assert (ios or android or web), "Must specified a version"
        self.ios = ios
        self.android = android
        self.web = web

        self.platform_priority = ('ios', 'android', 'web')

        self._is_specific = 1 == [bool(getattr(self, platform))
                                  for platform in self.platform_priority
                                  ].count(True)

    def __cmp__(self, other):
        if isinstance(other, NoAppVersion):
            # AppVersion always greater than NoAppVersion
            return 1

        assert (other._is_specific or self._is_specific),\
            "Both AppVersions are NOT specific version objects"

        # Only one platform version has at least one of self and other
        for key in self.platform_priority:
            a = getattr(self, key)
            b = getattr(other, key) if isinstance(other, AppVersion) else other
            if a and b:
                cmp(a, b)
        raise Exception('Invalid version given.')

    def __eq__(self, other):
        try:
            return self.__cmp__(other) == 0
        except Exception:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        ret = ['<AppVersion: ', ]
        if self.ios:
            ret.append('(IOS:%s)' % self.ios)
        if self.android:
            ret.append('(Android:%s)' % self.android)
        if self.web:
            ret.append('(WEB:%s)' % self.web)
        ret.append('>')
        return "".join(ret)


class NoAppVersion(object):
    """
    No AppVersion
    """
    is_ios = False
    is_android = False
    is_web = False

    def __cmp__(self, other):
        if isinstance(other, NoAppVersion):
            return 0
        return -1

    def __str__(self):
        return "<NoAppVersion>"

    def __nonzero__(self):
        """be boolean False"""
        return False

    def __eq__(self, other):
        if isinstance(other, NoAppVersion):
            return True
        return False

    def __ne__(self, other):
        return not (self == other)
