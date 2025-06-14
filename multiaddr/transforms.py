import io
from io import BytesIO
from typing import Generator, List, Optional, Tuple, Iterator

import varint

from . import exceptions
from .codecs import LENGTH_PREFIXED_VAR_SIZE, CodecBase, codec_by_name
from .protocols import Protocol, protocol_with_code, protocol_with_name
from .codecs.utf8 import Codec


def string_to_bytes(string: str) -> bytes:
    bs: List[bytes] = []
    for proto, codec, value in string_iter(string):
        print(f"[DEBUG string_to_bytes] LOOP: proto={proto.name}, codec={codec}, value={value}")
        print(f"[DEBUG string_to_bytes] Processing: proto={proto.name}, codec.SIZE={getattr(codec, 'SIZE', None)}, value={value}")
        print(f"[DEBUG string_to_bytes] Protocol code: {proto.code}")
        encoded_code = varint.encode(proto.code)
        print(f"[DEBUG string_to_bytes] Encoded protocol code: {encoded_code}")
        bs.append(encoded_code)
        if value is not None:
            print(f"[DEBUG] proto={proto.name}, codec.SIZE={getattr(codec, 'SIZE', None)}, value={value}")
            try:
                print(f"[DEBUG string_to_bytes] Raw CID value before encoding: {value}")
                buf = codec.to_bytes(proto, value)
                print(f"[DEBUG string_to_bytes] Generated buf: proto={proto.name}, buf={buf}")
            except Exception as exc:
                raise exceptions.StringParseError(str(exc), string, proto.name, exc) from exc
            print(f"[DEBUG string_to_bytes] Checking if length prefix needed: proto={proto.name}, codec.SIZE={getattr(codec, 'SIZE', None)}")
            if codec.SIZE <= 0:
                bs.append(varint.encode(len(buf)))
                print(f"[DEBUG string_to_bytes] Added length prefix: proto={proto.name}, length={len(buf)}")
            bs.append(buf)
            if codec is not None:
                print(f"[DEBUG string_to_bytes] codec type: {type(codec)}, codec.SIZE: {getattr(codec, 'SIZE', None)} for proto={proto.name}")
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
            print(f"[DEBUG bytes_to_string] Decoded protocol code: {code}")
            proto = protocol_with_code(code)
            print(f"[DEBUG bytes_to_string] Protocol name: {proto.name}")
            if proto.codec is not None:
                codec = codec_by_name(proto.codec)
                if codec.SIZE > 0:
                    value = codec.to_string(proto, bs.read(codec.SIZE // 8))
                else:
                    size = varint.decode_stream(bs)
                    value = codec.to_string(proto, bs.read(size))
                print(f"[DEBUG] bytes_to_string: proto={proto.name}, value='{value}'")  # DEBUG
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


def string_iter(string: str) -> Iterator[Tuple[Protocol, Optional[Codec], Optional[str]]]:
    """Iterate over the protocols in a multiaddr string.

    Yields
    ------
    tuple
        A tuple of (protocol, codec, value) for each protocol in the string.
    """
    if not string:
        return
    parts = string.split("/")
    if parts[0] != "":
        raise exceptions.StringParseError(
            "Multiaddr must start with a /",
            string,
            parts[0],
            ValueError("Invalid multiaddr format")
        )
    i = 1
    while i < len(parts):
        part = parts[i]
        if not part:
            i += 1
            continue
        print(f"[DEBUG string_iter] Processing part: {part}")
        proto = protocol_with_name(part)
        print(f"[DEBUG string_iter] Identified protocol: {proto.name}, code: {proto.code}")
        codec = None
        if proto.codec is not None:
            codec = codec_by_name(proto.codec)
            print(f"[DEBUG string_iter] Protocol codec size: {codec.SIZE}")
        value = None
        if codec is not None:
            # If there's a next part, use it as the value
            if i + 1 < len(parts):
                value = parts[i + 1]
                i += 1  # Skip the next part since we used it as value
                print(f"[DEBUG string_iter] Using next part as value: {value}")
            else:
                print(f"[DEBUG string_iter] No value found for protocol {proto.name}")
        print(f"[DEBUG string_iter] Yielding: proto={proto.name}, codec={codec}, value={value}")
        yield proto, codec, value
        i += 1


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
