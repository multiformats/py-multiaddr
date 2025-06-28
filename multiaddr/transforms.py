import io
from io import BytesIO
from typing import Generator, List, Optional, Tuple

import varint

from . import exceptions
from .codecs import LENGTH_PREFIXED_VAR_SIZE, CodecBase, codec_by_name
from .protocols import Protocol, protocol_with_code, protocol_with_name


def string_to_bytes(string: str) -> bytes:
    bs: List[bytes] = []
    for proto, codec, value in string_iter(string):
        bs.append(varint.encode(proto.code))
        if value is not None:
            try:
                buf = codec.to_bytes(proto, value)
            except Exception as exc:
                raise exceptions.StringParseError(str(exc), string, proto.name, exc) from exc
            if codec.SIZE == LENGTH_PREFIXED_VAR_SIZE:
                bs.append(varint.encode(len(buf)))
            bs.append(buf)
        elif codec is not None and codec.SIZE != 0:
            # If we have a protocol that requires a value but didn't get one, raise an error
            raise exceptions.StringParseError(
                f"Protocol {proto.name} requires a value",
                string,
                proto.name,
                ValueError("Missing required value")
            )
    return b''.join(bs)


def bytes_to_string(buf: bytes) -> str:
    """Convert a binary multiaddr to its string representation

    Raises
    ------
    ~multiaddr.exceptions.BinaryParseError
        The given bytes are not a valid multiaddr.
    """
    if not buf:
        return ""
    bs = BytesIO(buf)
    strings = []
    code = None
    proto = None
    while bs.tell() < len(buf):
        try:
            code = varint.decode_stream(bs)
            proto = protocol_with_code(code)
            if proto.codec is not None:
                codec = codec_by_name(proto.codec)
                if codec.SIZE > 0:
                    value = codec.to_string(proto, bs.read(codec.SIZE // 8))
                else:
                    size = varint.decode_stream(bs)
                    value = codec.to_string(proto, bs.read(size))
                if codec.IS_PATH and value.startswith("/"):
                    strings.append(f"/{proto.name}{value}")
                else:
                    strings.append(f"/{proto.name}/{value}")
            else:
                strings.append("/{0}".format(proto.name))
        except Exception as exc:
            # Use the code as the protocol identifier if proto is not available
            # Ensure we always have either a string or an integer
            protocol_id = proto.name if proto is not None else (code if code is not None else 0)
            raise exceptions.BinaryParseError(
                str(exc), buf, protocol_id, exc
            ) from exc
    return "".join(strings)


def size_for_addr(codec: CodecBase, buf_io: io.BytesIO) -> int:
    if codec.SIZE >= 0:
        return codec.SIZE // 8
    else:
        return varint.decode_stream(buf_io)


def string_iter(string: str) -> Generator[Tuple[Protocol, CodecBase, Optional[str]], None, None]:
    if not string:
        raise exceptions.StringParseError("Empty string", string)
    if not string.startswith('/'):
        raise exceptions.StringParseError("Must begin with /", string)
    # consume trailing slashes
    string = string.rstrip('/')
    sp = string.split('/')

    # skip the first element, since it starts with /
    sp.pop(0)
    while sp:
        element = sp.pop(0)
        if not element:  # Skip empty elements from multiple slashes
            continue
        try:
            proto = protocol_with_name(element)
            if proto.codec is None:
                # Create a dummy codec with size 0 for protocols without a codec
                codec = CodecBase()
                codec.SIZE = 0
                codec.IS_PATH = False
            else:
                codec = codec_by_name(proto.codec)
        except (ImportError, exceptions.ProtocolNotFoundError) as exc:
            raise exceptions.StringParseError("Unknown Protocol", string, element) from exc
        value = None
        if codec is not None and codec.SIZE != 0:
            if proto.name == 'unix':
                # For unix, join all remaining elements as the value
                path_value = '/'.join(sp) if sp else ''
                if not path_value:
                    raise exceptions.StringParseError("Protocol requires path", string, proto.name)
                try:
                    codec.to_bytes(proto, path_value)
                    value = path_value
                    sp.clear()  # All remaining elements are part of the path
                except Exception as exc:
                    raise exceptions.StringParseError(
                        f"Invalid path value for protocol {proto.name}",
                        string,
                        proto.name,
                        exc
                    ) from exc
            else:
                # Skip empty elements for value
                while sp and not sp[0]:
                    sp.pop(0)
                if not sp:
                    raise exceptions.StringParseError(
                        "Protocol requires address",
                        string,
                        proto.name
                    )
                next_elem = sp[0]
                # First try to validate as value for current protocol
                try:
                    codec.to_bytes(proto, next_elem)
                    value = sp.pop(0)
                except Exception as exc:
                    # If value validation fails, check if it's a protocol name
                    if next_elem.isalnum():
                        try:
                            # If this succeeds, it's a protocol name
                            protocol_with_name(next_elem)
                            # If we have a protocol that requires a value and we're seeing
                            # another protocol,
                            # raise a StringParseError
                            raise exceptions.StringParseError(
                                f"Protocol {proto.name} requires a value",
                                string,
                                proto.name,
                                ValueError("Missing required value")
                            )
                        except exceptions.ProtocolNotFoundError:
                            # If it's not a protocol name, raise the original value validation error
                            raise exceptions.StringParseError(
                                f"Invalid value for protocol {proto.name}",
                                string,
                                proto.name,
                                exc
                            ) from exc
                    else:
                        # If it's not alphanumeric, raise the original value validation error
                        raise exceptions.StringParseError(
                            f"Invalid value for protocol {proto.name}",
                            string,
                            proto.name,
                            exc
                        ) from exc
        yield proto, codec, value


def bytes_iter(buf: bytes) -> Generator[Tuple[int, Protocol, CodecBase, bytes], None, None]:
    buf_io = io.BytesIO(buf)
    while buf_io.tell() < len(buf):
        offset = buf_io.tell()
        code = varint.decode_stream(buf_io)
        proto = None
        try:
            proto = protocol_with_code(code)
            codec = codec_by_name(proto.codec)
        except (ImportError, exceptions.ProtocolNotFoundError) as exc:
            raise exceptions.BinaryParseError(
                    "Unknown Protocol",
                    buf,
                    proto.name if proto else code,
                ) from exc

        size = size_for_addr(codec, buf_io)
        yield offset, proto, codec, buf_io.read(size)
