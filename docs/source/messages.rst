.. |response status| replace:: :ref:`Response Status`.

.. index:: ! Messages

Messages
########

All messages start with a :term:`uint8 <int>` indicating the message type,
followed by zero or more fields specific to that message type.

Unless otherwise specified, all message fields are little-endian, and strings
are :term:`null-terminated <null-terminated string>`.

.. rubric:: Message type quick reference

.. message-quickref::

--------------------------------------------------------------------------------

.. _InfoRequest:

.. message:: InfoRequest
  :id: 0

.. _InfoResponse:

.. message:: InfoResponse
  :id: 1

  :uint8: RPC major version.
  :uint8: RPC minor version.
  :uint16: RPC build number.
  :uint8: Firmware major version.
  :uint8: Firmware minor version.
  :uint16: Firmware build number.
  :uint16: Maximum packet size in bytes.
  :uint16: Maximum message size in bytes.
  :uint16: Maximum chunk size in bytes.
  :uint16: :ref:`Product Group Device` type.

--------------------------------------------------------------------------------

.. message:: StartFirmwareUploadRequest
  :id: 10

  :uint8[20]: _`File SHA`.
  :uint32: :term:`CRC32` for the file.


.. message:: StartFirmwareUploadResponse
  :id: 11

  :uint8: |response status|
  :uint32: Number of bytes already uploaded for this `File SHA`_.
           Used to resume an interrupted upload.

--------------------------------------------------------------------------------

.. message:: StartFileUploadRequest
  :id: 12

  :string[32]: Name of the file as it will be stored on the hub.
  :uint8: :term:`Program slot` to store the file in.
  :uint32: :term:`CRC32` for the file.


.. message:: StartFileUploadResponse
  :id: 13

  :uint8: |response status|

--------------------------------------------------------------------------------

.. _TransferChunkRequest:

.. message:: TransferChunkRequest
  :id: 16

  :uint32: Running :term:`CRC32` for the transfer.
  :uint16: Chunk payload `size`.
  :uint8[`size`]: Chunk payload.


.. message:: TransferChunkResponse
  :id: 17

  :uint8: |response status|

--------------------------------------------------------------------------------

.. message:: BeginFirmwareUpdateRequest
  :id: 20

  :uint8[20]: `File SHA`_.
  :uint32: :term:`CRC32` for the file.


.. message:: BeginFirmwareUpdateResponse
  :id: 21

  :uint8: |response status|

--------------------------------------------------------------------------------

.. message:: SetHubNameRequest
  :id: 22

  :string[30]: New hub name.


.. message:: SetHubNameResponse
  :id: 23

  :uint8: |response status|

--------------------------------------------------------------------------------

.. message:: GetHubNameRequest
  :id: 24


.. message:: GetHubNameResponse
  :id: 25

  :string[30]: Hub name.

--------------------------------------------------------------------------------

.. message:: DeviceUuidRequest
  :id: 26


.. message:: DeviceUuidResponse
  :id: 27

  :uint8[16]: Device UUID.

--------------------------------------------------------------------------------

.. message:: ProgramFlowRequest
  :id: 30

  :uint8: :ref:`Program action`.
  :uint8: :term:`Program slot` to use.


.. message:: ProgramFlowResponse
  :id: 31

  :uint8: |response status|


.. message:: ProgramFlowNotification
  :id: 32

  :uint8: :ref:`Program action`.

--------------------------------------------------------------------------------

.. message:: ClearSlotRequest
  :id: 70

  :uint8: :term:`Program slot` to clear.


.. message:: ClearSlotResponse
  :id: 71

  :uint8: |response status|

--------------------------------------------------------------------------------

.. message:: ConsoleNotification
  :id: 33

  :string[256]: Console message.


.. message:: TunnelMessage
  :id: 50

  :uint16: Payload `size` in bytes.
  :uint8[`size`]: Payload data.

--------------------------------------------------------------------------------

.. message:: DeviceNotificationRequest
  :id: 40

  :uint16: Desired notification interval in milliseconds. (0 = disable)


.. message:: DeviceNotificationResponse
  :id: 41

  :uint8: |response status|


.. _DeviceNotification:

.. message:: DeviceNotification
  :id: 60

  :uint16: Payload `size` in bytes.
  :uint8[`size`]: Payload as an array of **device messages** (see below).

  .. rubric:: Device messages
    :class: indent-remaining

  The DeviceNotification_ payload is a sequence of **device messages**.

  Like the standard messages, device messages start with a :term:`uint8 <int>`
  indicating how to interpret the rest of the message.


  .. message:: DeviceBattery
    :device-message:
    :id: 0

    :uint8: Battery level in percent.


  .. message:: DeviceImuValues
    :device-message:
    :id: 1

    :uint8: :ref:`Hub Face` pointing up.
    :uint8: :ref:`Hub Face` configured as **yaw face**.
    :int16: Yaw value in respect to the configured *yaw face*.
    :int16: Pitch value in respect to the configured *yaw face*.
    :int16: Roll value in respect to the configured *yaw face*.
    :int16: Accelerometer reading in X axis.
    :int16: Accelerometer reading in Y axis.
    :int16: Accelerometer reading in Z axis.
    :int16: Gyroscope reading in X axis.
    :int16: Gyroscope reading in Y axis.
    :int16: Gyroscope reading in Z axis.


  .. message:: Device5x5MatrixDisplay
    :device-message:
    :id: 2

    :uint8[25]: Pixel value for display.


  .. message:: DeviceMotor
    :device-message:
    :id: 10

    :uint8: :ref:`Hub Port` the motor is connected to.
    :uint8: :ref:`Motor device type`.
    :int16: Absolute position in degrees, in the range ``-180`` to ``179``.
    :int16: Power applied to the motor, in the range ``-10000`` to ``10000``.
    :int8: Speed of the motor, in the range ``-100`` to ``100``.
    :int32: Position of the motor, in the range ``-2147483648`` to ``2147483647``.


  .. message:: DeviceForceSensor
    :device-message:
    :id: 11

    :uint8: :ref:`Hub Port` the force sensor is connected to.
    :uint8: Measured value, in the range ``0`` to ``100``.
    :uint8: ``0x01`` if the sensor detects pressure, ``0x00`` otherwise.


  .. message:: DeviceColorSensor
    :device-message:
    :id: 12

    :uint8: :ref:`Hub Port` the color sensor is connected to.
    :int8: :ref:`Color` detected by the sensor.
    :uint16: Raw red value, in the range ``0`` to ``1023``.
    :uint16: Raw green value, in the range ``0`` to ``1023``.
    :uint16: Raw blue value, in the range ``0`` to ``1023``.


  .. message:: DeviceDistanceSensor
    :device-message:
    :id: 13

    :uint8: :ref:`Hub Port` the distance sensor is connected to.
    :int16: Measured distance in millimeters, in the range ``40`` to ``2000``.
             (``-1`` if no object is detected.)


  .. message:: Device3x3ColorMatrix
    :device-message:
    :id: 14

    :uint8: :ref:`Hub Port` the color matrix is connected to.
    :uint8[9]: Displayed pixel values. Each pixel is encoded with the brightness
               in the high nibble and the color in the low nibble.


