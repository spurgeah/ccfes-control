import asyncio
from protocol import Protocol


class DeviceGeneral:

    async def getDeviceId(self) -> str | None:
        ack = await Protocol.sendPacket(p, 0, self.connection, self.factory)
        if ack:
            return ack.DeviceId
        
        return None
    

    async def getVersion() -> str:
        
        await asyncio.sleep(1)
        print('hello')