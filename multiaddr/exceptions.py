from typing import Any, Optional, Union


class Error(Exception):
    pass


class MultiaddrLookupError(LookupError, Error):
    pass


class ProtocolLookupError(MultiaddrLookupError):
    """
    MultiAddr did not contain a protocol with the requested code
    """

    def __init__(self, proto: Any, string: str) -> None:
        self.proto = proto
        self.string = string

        super().__init__(
            "MultiAddr {0!r} does not contain protocol {1}".format(string, proto)
        )


class ParseError(ValueError, Error):
    pass


class StringParseError(ParseError):
    """
    MultiAddr string representation could not be parsed
    """

    def __init__(
        self,
        message: str,
        string: str,
        protocol: Optional[str] = None,
        original: Optional[Exception] = None,
    ) -> None:
        self.message = message
        self.string = string
        self.protocol = protocol
        self.original = original

        if protocol:
            message = (
                "Invalid MultiAddr {0!r} protocol {1}: {2}".format(
                    string, protocol, message
                )
            )
        else:
            message = "Invalid MultiAddr {0!r}: {1}".format(string, message)

        super().__init__(message)

    def __str__(self):
        base = super().__str__()
        if self.protocol is not None:
            base += f" (protocol: {self.protocol})"
        if self.string is not None:
            base += f" (string: {self.string})"
        if self.original is not None:
            base += f" (cause: {self.original})"
        return base


class BinaryParseError(ParseError):
    """
    MultiAddr binary representation could not be parsed
    """

    def __init__(
        self,
        message: str,
        binary: bytes,
        protocol: Union[str, int],
        original: Optional[Exception] = None,
    ) -> None:
        self.message = message
        self.binary = binary
        self.protocol = protocol
        self.original = original

        message = (
            "Invalid binary MultiAddr protocol {0}: {1}".format(protocol, message)
        )

        super().__init__(message)

    def __str__(self):
        base = super().__str__()
        if self.protocol is not None:
            base += f" (protocol: {self.protocol})"
        if self.binary is not None:
            base += f" (binary: {self.binary})"
        if self.original is not None:
            base += f" (cause: {self.original})"
        return base


class ProtocolRegistryError(Error):
    pass


ProtocolManagerError = ProtocolRegistryError


class ProtocolRegistryLocked(Error):
    """Protocol registry was locked and doesn't allow any further additions"""
    def __init__(self) -> None:
        super().__init__("Protocol registry is locked and does not accept any new values")


class ProtocolExistsError(ProtocolRegistryError):
    """Protocol with the given name or code already exists"""
    def __init__(self, proto: Any, kind: str = "name") -> None:
        self.proto = proto
        self.kind = kind

        super().__init__(
            "Protocol with {0} {1!r} already exists".format(kind, getattr(proto, kind))
        )


class ProtocolNotFoundError(ProtocolRegistryError):
    """No protocol with the given name or code found"""
    def __init__(self, value: Union[str, int], kind: str = "name") -> None:
        self.value = value
        self.kind = kind

        super().__init__(
            "No protocol with {0} {1!r} found".format(kind, value)
        )
