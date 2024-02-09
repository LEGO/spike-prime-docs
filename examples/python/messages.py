from __future__ import annotations
from abc import ABC
import struct


class BaseMessage(ABC):
    @property
    def ID(cls) -> int:
        raise NotImplementedError

    def serialize(self) -> bytes:
        raise NotImplementedError

    @staticmethod
    def deserialize(data: bytes) -> BaseMessage:
        raise NotImplementedError

    def __str__(self) -> str:
        props = vars(self)
        plist = ", ".join(f"{k}={v}" for k, v in props.items())
        return f"{self.__class__.__name__}({plist})"


def StatusResponse(name: str, id: int):
    class BaseStatusResponse(BaseMessage):
        ID = id

        def __init__(self, success: bool):
            self.success = success

        @staticmethod
        def deserialize(data: bytes):
            id, status = struct.unpack("<BB", data)
            return BaseStatusResponse(status == 0x00)

    BaseStatusResponse.__name__ = name
    return BaseStatusResponse


class InfoRequest(BaseMessage):
    ID = 0x00

    def serialize(self):
        return b"\0"


class InfoResponse(BaseMessage):
    ID = 0x01

    def __init__(
        self,
        rpc_major: int,
        rpc_minor: int,
        rpc_build: int,
        firmware_major: int,
        firmware_minor: int,
        firmware_build: int,
        max_packet_size: int,
        max_message_size: int,
        max_chunk_size: int,
        product_group_device: int,
    ):
        self.rpc_major = rpc_major
        self.rpc_minor = rpc_minor
        self.rpc_build = rpc_build
        self.firmware_major = firmware_major
        self.firmware_minor = firmware_minor
        self.firmware_build = firmware_build
        self.max_packet_size = max_packet_size
        self.max_message_size = max_message_size
        self.max_chunk_size = max_chunk_size
        self.product_group_device = product_group_device

    @staticmethod
    def deserialize(data: bytes) -> InfoResponse:
        (
            id,
            rpc_major,
            rpc_minor,
            rpc_build,
            firmware_major,
            firmware_minor,
            firmware_build,
            max_packet_size,
            max_message_size,
            max_chunk_size,
            product_group_device,
        ) = struct.unpack("<BBBHBBHHHHH", data)
        return InfoResponse(
            rpc_major,
            rpc_minor,
            rpc_build,
            firmware_major,
            firmware_minor,
            firmware_build,
            max_packet_size,
            max_message_size,
            max_chunk_size,
            product_group_device,
        )


class ClearSlotRequest(BaseMessage):
    ID = 0x46

    def __init__(self, slot: int):
        self.slot = slot

    def serialize(self):
        return struct.pack("<BB", self.ID, self.slot)


ClearSlotResponse = StatusResponse("ClearSlotResponse", 0x47)


class StartFileUploadRequest(BaseMessage):
    ID = 0x0C

    def __init__(self, file_name: str, slot: int, crc: int):
        self.file_name = file_name
        self.slot = slot
        self.crc = crc

    def serialize(self):
        encoded_name = self.file_name.encode("utf8")
        if len(encoded_name) > 31:
            raise ValueError(
                f"UTF-8 encoded file name too long: {len(encoded_name)} +1 >= 32"
            )
        fmt = f"<B{len(encoded_name)+1}sBI"
        return struct.pack(fmt, self.ID, encoded_name, self.slot, self.crc)


StartFileUploadResponse = StatusResponse("StartFileUploadResponse", 0x0D)


class TransferChunkRequest(BaseMessage):
    ID = 0x10

    def __init__(self, running_crc: int, chunk: bytes):
        self.running_crc = running_crc
        self.size = len(chunk)
        self.payload = chunk

    def serialize(self):
        fmt = f"<BIH{self.size}s"
        return struct.pack(fmt, self.ID, self.running_crc, self.size, self.payload)


TransferChunkResponse = StatusResponse("TransferChunkResponse", 0x11)


class ProgramFlowRequest(BaseMessage):
    ID = 0x1E

    def __init__(self, stop: bool, slot: int):
        self.stop = stop
        self.slot = slot

    def serialize(self):
        return struct.pack("<BBB", self.ID, self.stop, self.slot)


ProgramFlowResponse = StatusResponse("ProgramFlowResponse", 0x1F)


class ProgramFlowNotification(BaseMessage):
    ID = 0x20

    def __init__(self, stop: bool):
        self.stop = stop

    @staticmethod
    def deserialize(data: bytes) -> ProgramFlowNotification:
        id, stop = struct.unpack("<BB", data)
        return ProgramFlowNotification(bool(stop))


class ConsoleNotification(BaseMessage):
    ID = 0x21

    def __init__(self, text: str):
        self.text = text

    @staticmethod
    def deserialize(data: bytes) -> ConsoleNotification:
        text_bytes = data[1:].rstrip(b"\0")
        return ConsoleNotification(text_bytes.decode("utf8"))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.text!r})"


class DeviceNotificationRequest(BaseMessage):
    ID = 0x28

    def __init__(self, interval_ms: int):
        self.interval_ms = interval_ms

    def serialize(self):
        return struct.pack("<BH", self.ID, self.interval_ms)


DeviceNotificationResponse = StatusResponse("DeviceNotificationResponse", 0x29)

DEVICE_MESSAGE_MAP = {
    0x00: ("Battery", "<BB"),
    0x01: ("IMU", "<BBBhhhhhhhhh"),
    0x02: ("5x5", "<B25B"),
    0x0A: ("Motor", "<BBBhhbi"),
    0x0B: ("Force", "<BBBB"),
    0x0C: ("Color", "<BBbHHH"),
    0x0D: ("Distance", "<BBh"),
    0x0E: ("3x3", "<BB9B"),
}


class DeviceNotification(BaseMessage):
    ID = 0x3C

    def __init__(self, size: int, payload: bytes):
        self.size = size
        self._payload = payload
        self.messages = []
        data = payload[:]
        while data:
            id = data[0]
            if id in DEVICE_MESSAGE_MAP:
                name, fmt = DEVICE_MESSAGE_MAP[id]
                size = struct.calcsize(fmt)
                values = struct.unpack(fmt, data[:size])
                self.messages.append((name, values))
                data = data[size:]
            else:
                print(f"Unknown message: {id}")
                break

    @staticmethod
    def deserialize(data: bytes) -> DeviceNotification:
        id, size = struct.unpack("<BH", data[:3])
        if len(data) != size + 3:
            print(f"Unexpected size: {len(data)} != {size} + 3")
        return DeviceNotification(size, data[3:])

    def __str__(self) -> str:
        updated = list(map(lambda x: x[0], self.messages))
        return f"{self.__class__.__name__}({updated})"


KNOWN_MESSAGES = {
    M.ID: M
    for M in (
        InfoRequest,
        InfoResponse,
        ClearSlotRequest,
        ClearSlotResponse,
        StartFileUploadRequest,
        StartFileUploadResponse,
        TransferChunkRequest,
        TransferChunkResponse,
        ProgramFlowRequest,
        ProgramFlowResponse,
        ProgramFlowNotification,
        ConsoleNotification,
        DeviceNotificationRequest,
        DeviceNotificationResponse,
        DeviceNotification,
    )
}


def deserialize(data: bytes):
    message_type = data[0]
    if message_type in KNOWN_MESSAGES:
        return KNOWN_MESSAGES[message_type].deserialize(data)
    raise ValueError(f"Unknown message: {data.hex(' ')}")
