import io
from collections.abc import Generator
from io import BytesIO

import varint

from . import exceptions
from .codecs import CodecBase, codec_by_name
from .protocols import Protocol, protocol_with_code, protocol_with_name


def string_to_bytes(string: str) -> bytes:
    bs: list[bytes] = []
    for proto, codec, value in string_iter(string):
        encoded_code = varint.encode(proto.code)
        bs.append(encoded_code)

        # Special case: protocols with codec=None or SIZE=0 are flag protocols
        # (no value, no length prefix, no buffer)
        if codec is None or getattr(codec, "SIZE", None) == 0:
            continue

        if value is None:
            raise ValueError("Value cannot be None")
        try:
            buf = codec.to_bytes(proto, value)
        except Exception as exc:
            raise exceptions.StringParseError(str(exc), string) from exc
        # Only add length prefix for variable-sized codecs (SIZE <= 0)
        if codec.SIZE <= 0:
            bs.append(varint.encode(len(buf)))
        # Only append the buffer if it's not empty
        if buf:
            bs.append(buf)
    return b"".join(bs)


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
                    # For variable-sized codecs,
                    # read the length prefix but don't pass it to the codec
                    size = varint.decode_stream(bs)
                    value = codec.to_string(proto, bs.read(size))
                if codec.IS_PATH and value.startswith("/"):
                    # For path protocols, the codec already handles URL encoding
                    strings.append("/" + proto.name + value)  # type: ignore[arg-type]
                else:
                    strings.append("/" + proto.name + "/" + value)  # type: ignore[arg-type]
            else:
                strings.append("/" + proto.name)  # type: ignore[arg-type]
        except Exception as exc:
            # Use the code as the protocol identifier if proto is not available
            # Ensure we always have either a string or an integer
            protocol_id = proto.name if proto is not None else (code if code is not None else 0)
            raise exceptions.BinaryParseError(str(exc), buf, protocol_id, exc) from exc
    return "".join(strings)


def size_for_addr(codec: CodecBase, buf_io: io.BytesIO) -> int:
    if codec.SIZE >= 0:
        return codec.SIZE // 8
    else:
        return varint.decode_stream(buf_io)


def string_iter(
    string: str,
) -> Generator[tuple[Protocol, CodecBase | None, str | None], None, None]:
    """Iterate over the parts of a string multiaddr.

    Args:
        string: The string multiaddr to iterate over

    Yields:
        A tuple of (protocol, codec, value) for each part of the multiaddr
    """
    if not string:
        return

    parts = string.strip("/").split("/")
    i = 0
    while i < len(parts):
        proto_name = parts[i]
        try:
            proto = protocol_with_name(proto_name)
        except exceptions.ProtocolNotFoundError as exc:
            raise exceptions.StringParseError(str(exc), string) from exc

        codec = codec_by_name(proto.codec)
        value = None

        if proto.codec is not None:
            if i + 1 >= len(parts):
                raise exceptions.StringParseError(
                    f"missing value for protocol: {proto_name}", string
                )

            if codec.IS_PATH:
                value = "/".join(parts[i + 1 :])
                i = len(parts) - 1
            else:
                value = parts[i + 1]
                i += 1  # Skip the next part since we used it as value
            yield proto, codec, value
        else:
            yield proto, codec, None
        i += 1


def bytes_iter(buf: bytes) -> Generator[tuple[int, Protocol, CodecBase, bytes], None, None]:
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
        part = buf_io.read(size)
        if len(part) != size:
            raise exceptions.BinaryParseError(
                f"unexpected end of data for protocol {proto.name if proto else code}",
                buf,
                proto.name if proto else code,
            )
        yield offset, proto, codec, part
