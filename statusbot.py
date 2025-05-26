import asyncio
from mautrix.types import PresenceState
from maubot import Plugin, MessageEvent
from maubot.handlers import command

class StatusPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        # Forward all args (config, client, instance, etc.) to the base Plugin
        super().__init__(*args, **kwargs)
        self._refresh_task = None
        self._current_status = None

    async def manage_refresher(self):
        """Background task to re-apply presence every 60s."""
        while True:
            await self.client.set_presence(PresenceState.ONLINE, status=self._current_status)
            await asyncio.sleep(60)

    @command.new(name="setstatus", help="Set your presence status message")
    async def cmd_setstatus(self, evt: MessageEvent, status: str):
        # 1) Apply immediately
        self._current_status = status
        await self.client.set_presence(PresenceState.ONLINE, status=status)
        await evt.reply(f"Status set to: “{status}”")

        # 2) (Re)start refresher
        if self._refresh_task:
            self._refresh_task.cancel()
        self._refresh_task = asyncio.create_task(self.manage_refresher())
