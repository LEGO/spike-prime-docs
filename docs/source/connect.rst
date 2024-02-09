Setting up the connection
#########################


BLE capabilities of the hub
***************************

The LEGO® SPIKE™ Prime Hub exposes a BLE GATT service containing two
characteristics: one for receiving data (:dfn:`RX`),
and one for transmitting data (:dfn:`TX`).

The table below shows the UUIDs for the service and characteristics.

.. list-table::
  :header-rows: 1
  :stub-columns: 1
  :widths: 1 5
  :class: first-col-right

  * - Item
    - UUID
  * - Service
    - :samp:`0000FD02-000{0}-1000-8000-00805F9B34FB`
  * - RX
    - :samp:`0000FD02-000{1}-1000-8000-00805F9B34FB`
  * - TX
    - :samp:`0000FD02-000{2}-1000-8000-00805F9B34FB`

.. note::
  "Receiving" and "transmitting" are from the perspective of the hub.

The hub includes the service UUID in the advertisement data,
so that it can be used to filter scan results.

To send data to the hub, perform a **write-without-response**
operation on the hub's RX characteristic.

Any data from the hub will be delivered as a notification on the TX
characteristic.

.. hint:: Make sure to enable notifications on the TX characteristic.


Handshake and negotiation
*************************

Upon connecting, the client should always initiate communication
by sending an :ref:`InfoRequest <InfoRequest>` to the hub.
The hub will respond with an :ref:`InfoResponse <InfoResponse>`,
detailing the capabilities of the hub.

Of particular interest are the maximum sizes for packets and chunks:

:Max. packet size:
  The largest amount of data that can be written to the RX characteristic
  in a single operation.

:Max. chunk size:
  The maximum number of bytes allowed in the payload of a
  :ref:`TransferChunkRequest <TransferChunkRequest>`.

The examples below show how these limits may be applied in Python:

.. literalinclude:: /../../examples/python/app.py
  :caption: Honoring the maximum packet size
  :dedent:
  :start-at: async def send_message
  :end-at: await client.write

.. literalinclude:: /../../examples/python/app.py
  :caption: Using the maximum chunk size
  :dedent:
  :start-at: running_crc = 0
  :end-before: if not chunk_response.success
