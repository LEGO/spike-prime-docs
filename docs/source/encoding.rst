Encoding
########

Message encoding and framing can be broken into three steps:

1. Byte values ``0x00``, ``0x01``, and ``0x02`` are escaped using :term:`COBS`.
2. All bytes are XORed with ``0x03`` to ensure output contains no problematic control characters.
3. A delimiter is added to the end of the message.

Deframing and decoding is the reverse of these steps.

.. _COBS:

Consistent Overhead Byte Stuffing (COBS)
****************************************

**COBS** is an algorithm that can be used to escape certain values in a byte
stream with a minimal overhead.
This frees up the values to be used for special purposes, such as message
delimiters or other control characters.

The typical implementations of COBS only escape ``0x00``, but the SPIKE™ Prime
implementation additionally escapes ``0x01`` and ``0x02``, as they are used for
message delimiters.

Delimeters are replaced with a special code word that indicates the number of
bytes until the next delimiter and its value.
The code word is calculated as follows:

.. math::

  \text{code_word} = \text{block_size} + 2 + \text{delimiter} \times 84

The minimum value of :math:`\text{block_size}` is 1, as it will aways contain at
least the code word itself. Therefore, by adding 2, the minimum value of
:math:`\text{code_word}` is 3, ensuring no overlap with any delimiters.

This leaves ``0xFF - 3`` bytes to be used for the block size, which must be
divided by 3 (the number of different delimiters), resulting in a maximum block
size of 84.

For blocks with no delimiters, the code word :math:`255` is used.
Thus, the code word can be decoded as follows:

.. list-table::
  :widths: 20 20 20
  :header-rows: 1

  + - Code word
    - Block size
    - Delimeter

  + - :math:`0 \leq n \leq 2`
    - N/A
    - N/A

  + - :math:`3 \leq n \leq 86`
    - :math:`n - 3`
    - :math:`0`

  + - :math:`87 \leq n \leq 170`
    - :math:`n - 87`
    - :math:`1`

  + - :math:`171 \leq n \leq 254`
    - :math:`n - 171`
    - :math:`2`

  + - :math:`255`
    - :math:`84`
    - N/A

It's important that the encoded output always begins with a valid code word
(i.e. the first byte is not a delimiter).
This provides the decoder with a known starting point, allowing it to correctly
decode the rest of the message.

Below are sample implementations of the COBS encoding and decoding algorithms
in Python:

.. literalinclude:: /../../examples/python/cobs.py
  :name: COBS Encode
  :pyobject: encode
  :caption: COBS encoding algorithm

.. literalinclude:: /../../examples/python/cobs.py
  :name: COBS Decode
  :pyobject: decode
  :caption: COBS decoding algorithm


Escaping and framing
********************

After encoding the data with COBS as described :ref:`above <COBS>`, the data
will contain no bytes with a value of ``0x00``, ``0x01``, or ``0x02``.

In SPIKE™ Prime, the values ``0x01`` and ``0x02`` are used as message delimiters.
``0x01`` signifies the start of a high-priority message, and ``0x02`` signifies
the end of a message (and implicitly the start or resumption of a low-priority message).

In addition to the delimiters ``0x01`` and ``0x02``, the value ``0x03`` must also
be replaced, as it carries special meaning in the SPIKE™ Prime protocol.
To ensure that the output contains no bytes with a value of ``0x03``, all bytes
are bitwise XORed with ``0x03``. This effectively shifts the byte values by 3,
turning ``0x03`` into ``0x00`` and vice versa, but because the COBS algorithm
already removed any ``0x00`` bytes, the result will contain no ``0x03`` bytes.

Finally, the message is framed by (optionally) prefixing it with ``0x01``,
and (always) suffixing it with ``0x02``. See example below:

.. literalinclude:: /../../examples/python/cobs.py
  :name: COBS Pack
  :pyobject: pack
  :caption: Encode, escape, frame


Deframing and unescaping
************************

As bytes are received, they should be buffered into their respective priority
queues until a complete message is received, as indicated by the presence of
``0x02``.

The table below shows how to interpret each delimiter depending on the state
of transmission:


.. list-table::
  :header-rows: 1
  :stub-columns: 1

  + - Delimiter
    - Message in progress
    - Interpretation
    - Action

  + - ``0x01``
    - None
    - Start of high-priority message
    - Start buffering into high-priority queue

  + - ``0x01``
    - High-priority
    - **Illegal state**
    - Sync error, clear queues and
      start buffering into high-priority queue

  + - ``0x01``
    - Low-priority
    - Start of high-priority message
    - Pause buffering of low-priority message and
      start buffering into high-priority queue

  + - ``0x02``
    - None
    - Start of low-priority message
    - Start buffering into low-priority queue

  + - ``0x02``
    - High-priority
    - End of high-priority message
    - Process high-priority message,
      empty high-priority queue and
      start buffering into low-priority queue

  + - ``0x02``
    - Low-priority
    - End of low-priority message
    - Process low-priority message and
      empty low-priority queue

When a message is completed, it can be deframed by removing any leading ``0x01``
and trailing ``0x02`` bytes. The remaining bytes can then be unescaped by
reversing the XOR operation and then COBS decoded as described :ref:`above <COBS>`.

Below is an example of how to deframe and unescape a message in Python:

.. literalinclude:: /../../examples/python/cobs.py
  :name: COBS Unpack
  :pyobject: unpack
  :caption: Deframe, unescape, decode
