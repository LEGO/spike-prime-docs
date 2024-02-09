"""
Example implementation of the Consistent Overhead Byte Stuffing (COBS) algorithm
used by the SPIKE™ Prime BLE protocol.

This implementation prioritizes readability and simplicity over performance and
should be used for educational purposes only.
"""

DELIMITER = 0x02
"""Delimiter used to mark end of frame"""

NO_DELIMITER = 0xFF
"""Code word indicating no delimiter in block"""

COBS_CODE_OFFSET = DELIMITER
"""Offset added to code word"""

MAX_BLOCK_SIZE = 84
"""Maximum block size (incl. code word)"""

XOR = 3
"""XOR mask for encoding"""


def encode(data: bytes):
    """
    Encode data using COBS algorithm, such that no delimiters are present.
    """
    buffer = bytearray()
    code_index = block = 0
    def begin_block():
        """Append code word to buffer and update code_index and block"""
        nonlocal code_index, block
        code_index = len(buffer)  # index of incomplete code word
        buffer.append(NO_DELIMITER)  # updated later if delimiter is encountered
        block = 1  # no. of bytes in block (incl. code word)

    begin_block()
    for byte in data:
        if byte > DELIMITER:
            # non-delimeter value, write as-is
            buffer.append(byte)
            block += 1

        if byte <= DELIMITER or block > MAX_BLOCK_SIZE:
            # block completed because size limit reached or delimiter found
            if byte <= DELIMITER:
                # reason for block completion is delimiter
                # update code word to reflect block size
                delimiter_base = byte * MAX_BLOCK_SIZE
                block_offset = block + COBS_CODE_OFFSET
                buffer[code_index] = delimiter_base + block_offset
            # begin new block
            begin_block()

    # update final code word
    buffer[code_index] = block + COBS_CODE_OFFSET

    return buffer


def decode(data: bytes):
    """
    Decode data using COBS algorithm.
    """
    buffer = bytearray()

    def unescape(code: int):
        """Decode code word, returning value and block size"""
        if code == 0xFF:
            # no delimiter in block
            return None, MAX_BLOCK_SIZE + 1
        value, block = divmod(code - COBS_CODE_OFFSET, MAX_BLOCK_SIZE)
        if block == 0:
            # maximum block size ending with delimiter
            block = MAX_BLOCK_SIZE
            value -= 1
        return value, block

    value, block = unescape(data[0])
    for byte in data[1:]:  # first byte already processed
        block -= 1
        if block > 0:
            buffer.append(byte)
            continue

        # block completed
        if value is not None:
            buffer.append(value)

        value, block = unescape(byte)

    return buffer


def pack(data: bytes):
    """
    Encode and frame data for transmission.
    """
    buffer = encode(data)

    # XOR buffer to remove problematic ctrl+C
    for i in range(len(buffer)):
        buffer[i] ^= XOR

    # add delimiter
    buffer.append(DELIMITER)
    return bytes(buffer)


def unpack(frame: bytes):
    """
    Unframe and decode frame.
    """
    start = 0
    if frame[0] == 0x01:  # unused priority byte
        start += 1
    # unframe and XOR
    unframed = bytes(map(lambda x: x ^ XOR, frame[start:-1]))
    return bytes(decode(unframed))
