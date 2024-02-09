:orphan:

Glossary
########

.. glossary::
  :sorted:

  array
    An array of values of the same type, in the format ``<type>[<length>?]``.
    If ``<length>`` is omitted, then the array is of variable size (typically given in a preceding field).

  COBS
    Consistent Overhead Byte Stuffing (COBS) is an algorithm for encoding data such that the encoded data
    does not contain any delimiter bytes.

    In the context of SPIKE™ Prime, COBS is used to replace bytes with a value of ``0x02`` and below
    with another byte that does not have a value of ``0x02`` or below.
    For more details, see :ref:`Encoding: COBS <COBS>`.

  CRC32
    CRC-32 (32bit Cyclic Redundancy Check) is a checksum algorithm used to detect errors in data.
    For SPIKE™ Prime, the CRC must be calculated on a multiple of 4 bytes.

    For data that is not a multiple of 4 bytes, append ``0x00`` until the data is a multiple of 4 bytes
    before calculating the CRC.

  hub
    SPIKE™ Prime hub.

  int
    An integer in the format ``u?int\d+``.
    The ``u``-prefix indicates whether the integer is signed (if omitted) or unsigned (if present).
    The number after ``int`` is the number of bits.
    (e.g., ``int8`` is an 8-bit signed integer, ``uint32`` is a 32-bit unsigned integer)

  null-terminated string
    A character string terminated with ``NUL`` (``0x00``), given in the format ``string[<n>]``,
    where ``<n>`` is the maximum length of the string (including the terminating ``NUL``).

    .. attention::
      Strings **must** be terminated with ``NUL``, so the effective length of the string is ``<n> - 1``.

  program slot
    One of the 20 program slots on the hub, indexed from 0 to 19.

  smart coast/brake
    A method of stopping a motor, while attempting to compensate for inaccuracies in following commands.


