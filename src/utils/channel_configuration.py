from typing import Final
from src.utils.byte_builder import ByteBuilder
from src.utils.channel_point import ChannelPoint


class MidLevelChannelConfiguration():

    isActive: bool = False
    ramp: int = 0
    periodInMs: int = 0
    points: list[ChannelPoint] = []


    def getData(self) -> bytes:
        if len(self.points) > 16:
            raise ValueError(f"Mid level update maximum of 16 points allowed {len(self.points)}")
        if self.ramp < 0 or self.ramp > 15:
            raise ValueError(f"Mid level update ramp must be between 0..15 {self.ramp}")
        if self.periodInMs < 0 or self.periodInMs > 32767 * 4:
            raise ValueError(f"Mid level update period must be between 0..131071 {self.periodInMs}")
        
        bb = ByteBuilder()
        bb.setToPosition(self.ramp, 0, 4)
        bb.setToPosition(len(self.points), 4, 4)
        bb.setToPosition(0 if self.periodInMs <= 32767 else 1, 8, 1)
        bb.setToPosition(self.periodInMs, 9, 15)
        bb.swap(1, 2)
        for x in self.points:
            bb.extendBytes(x.getData())
        return bb.getBytes()
