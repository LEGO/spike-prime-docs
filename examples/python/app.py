"""
This is a simple example script showing how to

    * Connect to a SPIKE™ Prime hub over BLE
    * Subscribe to device notifications
    * Transfer and start a new program

The script is heavily simplified and not suitable for production use.

----------------------------------------------------------------------

After prompting for confirmation to continue, the script will simply connect to
the first device it finds advertising the SPIKE™ Prime service UUID, and proceed
with the following steps:

    1. Request information about the device (e.g. max chunk size for file transfers)
    2. Subscribe to device notifications (e.g. state of IMU, display, sensors, motors, etc.)
    3. Clear the program in a specific slot
    4. Request transfer of a new program file to the slot
    5. Transfer the program in chunks
    6. Start the program

If the script detects an unexpected response, it will print an error message and exit.
Otherwise it will continue to run until the connection is lost or stopped by the user.
(You can stop the script by pressing Ctrl+C in the terminal.)

While the script is running, it will print information about the messages it sends and receives.
"""

import sys
from typing import cast, TypeVar

TMessage = TypeVar("TMessage", bound="BaseMessage")

import cobs
from messages import *
from crc import crc

import asyncio
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData


SCAN_TIMEOUT = 10.0
"""How long to scan for devices before giving up (in seconds)"""

SERVICE = "0000fd02-0000-1000-8000-00805f9b34fb"
"""The SPIKE™ Prime BLE service UUID"""

RX_CHAR = "0000fd02-0001-1000-8000-00805f9b34fb"
"""The UUID the hub will receive data on"""

TX_CHAR = "0000fd02-0002-1000-8000-00805f9b34fb"
"""The UUID the hub will transmit data on"""

DEVICE_NOTIFICATION_INTERVAL_MS = 5000
"""The interval in milliseconds between device notifications"""

EXAMPLE_SLOT = 0
"""The slot to upload the example program to"""

EXAMPLE_PROGRAM = """import runloop
from hub import light_matrix
print("Console message from hub.")
async def main():
    await light_matrix.write("Hello, world!")
runloop.run(main())""".encode(
    "utf8"
)
"""The utf8-encoded example program to upload to the hub"""

answer = input(
    f"This example will override the program in slot {EXAMPLE_SLOT} of the first hub found. Do you want to continue? [Y/n] "
)
if answer.strip().lower().startswith("n"):
    print("Aborted by user.")
    sys.exit(0)

stop_event = asyncio.Event()

async def main():

    def match_service_uuid(device: BLEDevice, adv: AdvertisementData) -> bool:
        return SERVICE.lower() in adv.service_uuids

    print(f"\nScanning for {SCAN_TIMEOUT} seconds, please wait...")
    device = await BleakScanner.find_device_by_filter(
        filterfunc=match_service_uuid, timeout=SCAN_TIMEOUT
    )

    if device is None:
        print(
            "No hubs detected. Ensure that a hub is within range, turned on, and awaiting connection."
        )
        sys.exit(1)

    device = cast(BLEDevice, device)
    print(f"Hub detected! {device}")

    def on_disconnect(client: BleakClient) -> None:
        print("Connection lost.")
        stop_event.set()

    print("Connecting...")
    async with BleakClient(device, disconnected_callback=on_disconnect) as client:
        print("Connected!\n")

        service = client.services.get_service(SERVICE)
        rx_char = service.get_characteristic(RX_CHAR)
        tx_char = service.get_characteristic(TX_CHAR)

        # simple response tracking
        pending_response: tuple[int, asyncio.Future] = (-1, asyncio.Future())

        # callback for when data is received from the hub
        def on_data(_: BleakGATTCharacteristic, data: bytearray) -> None:
            if data[-1] != 0x02:
                # packet is not a complete message
                # for simplicity, this example does not implement buffering
                # and is therefore unable to handle fragmented messages
                un_xor = bytes(map(lambda x: x ^ 3, data))  # un-XOR for debugging
                print(f"Received incomplete message:\n {un_xor}")
                return

            data = cobs.unpack(data)
            try:
                message = deserialize(data)
                print(f"Received: {message}")
                if message.ID == pending_response[0]:
                    pending_response[1].set_result(message)
                if isinstance(message, DeviceNotification):
                    # sort and print the messages in the notification
                    updates = list(message.messages)
                    updates.sort(key=lambda x: x[1])
                    lines = [f" - {x[0]:<10}: {x[1]}" for x in updates]
                    print("\n".join(lines))

            except ValueError as e:
                print(f"Error: {e}")

        # enable notifications on the hub's TX characteristic
        await client.start_notify(tx_char, on_data)

        # to be initialized
        info_response: InfoResponse = None

        # serialize and pack a message, then send it to the hub
        async def send_message(message: BaseMessage) -> None:
            print(f"Sending: {message}")
            payload = message.serialize()
            frame = cobs.pack(payload)

            # use the max_packet_size from the info response if available
            # otherwise, assume the frame is small enough to send in one packet
            packet_size = info_response.max_packet_size if info_response else len(frame)

            # send the frame in packets of packet_size
            for i in range(0, len(frame), packet_size):
                packet = frame[i : i + packet_size]
                await client.write_gatt_char(rx_char, packet, response=False)

        # send a message and wait for a response of a specific type
        async def send_request(
            message: BaseMessage, response_type: type[TMessage]
        ) -> TMessage:
            nonlocal pending_response
            pending_response = (response_type.ID, asyncio.Future())
            await send_message(message)
            return await pending_response[1]

        # first message should always be an info request
        # as the response contains important information about the hub
        # and how to communicate with it
        info_response = await send_request(InfoRequest(), InfoResponse)

        # enable device notifications
        notification_response = await send_request(
            DeviceNotificationRequest(DEVICE_NOTIFICATION_INTERVAL_MS),
            DeviceNotificationResponse,
        )
        if not notification_response.success:
            print("Error: failed to enable notifications")
            sys.exit(1)

        # clear the program in the example slot
        clear_response = await send_request(
            ClearSlotRequest(EXAMPLE_SLOT), ClearSlotResponse
        )
        if not clear_response.success:
            print(
                "ClearSlotRequest was not acknowledged. This could mean the slot was already empty, proceeding..."
            )

        # start a new file upload
        program_crc = crc(EXAMPLE_PROGRAM)
        start_upload_response = await send_request(
            StartFileUploadRequest("program.py", EXAMPLE_SLOT, program_crc),
            StartFileUploadResponse,
        )
        if not start_upload_response.success:
            print("Error: start file upload was not acknowledged")
            sys.exit(1)

        # transfer the program in chunks
        running_crc = 0
        for i in range(0, len(EXAMPLE_PROGRAM), info_response.max_chunk_size):
            chunk = EXAMPLE_PROGRAM[i : i + info_response.max_chunk_size]
            running_crc = crc(chunk, running_crc)
            chunk_response = await send_request(
                TransferChunkRequest(running_crc, chunk), TransferChunkResponse
            )
            if not chunk_response.success:
                print(f"Error: failed to transfer chunk {i}")
                sys.exit(1)

        # start the program
        start_program_response = await send_request(
            ProgramFlowRequest(stop=False, slot=EXAMPLE_SLOT), ProgramFlowResponse
        )
        if not start_program_response.success:
            print("Error: failed to start program")
            sys.exit(1)

        # wait for the user to stop the script or disconnect the hub
        await stop_event.wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user.")
        stop_event.set()
