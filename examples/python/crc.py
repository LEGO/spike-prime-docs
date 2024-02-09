from binascii import crc32 as _crc32


def crc(data: bytes, seed=0, align=4):
    """
    Calculate the CRC32 of data with an optional seed and alignment.
    """
    remainder = len(data) % align
    if remainder:
        data += b"\x00" * (align - remainder)
    return _crc32(data, seed)
