from .interface import MultiaddrInterface


class Multiaddr(MultiaddrInterface):
    def __init__(self, string):
        if string:
            print("Do stuff")

    def __eq__(self, other):
        pass

    def __str__(self):
        pass

    def __bytes__(self):
        pass

    def protocols(self):
        pass

    def encapsulate(self, other):
        pass

    def decapsulate(self, other):
        pass

    def value_for_protocol(self, protocol):
        pass
