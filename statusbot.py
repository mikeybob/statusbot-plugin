import asyncio
from mautrix.types import PresenceState
from maubot import Plugin, MessageEvent
from maubot.handlers import command

class StatusPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._refresh_task = None
        self._current_status = None

    async def manage_refresher(self):
        """Re-apply your status every 60 seconds."""
        while True:
            await self.client.set_presence(PresenceState.ONLINE, status=self._current_status)
            await asyncio.sleep(60)

    @command.new(
        name="setstatus",
        help="Set your presence status message",
        params=["status:text"]
    )
    async def cmd_setstatus(self, evt: MessageEvent, status: str):
        if not status.strip():
            await evt.reply("❗️ Please provide a status: `!setstatus Working from home`")
            return

        # 1) Apply immediately
        self._current_status = status
        await self.client.set_presence(PresenceState.ONLINE, status=status)
        # **Fixed quote syntax here**--use single quotes around the f-string’s embedded quotes
        await evt.reply(f'Status set to: "{status}"')

        # 2) (Re)start the background refresher
        if self._refresh_task:
            self._refresh_task.cancel()
        self._refresh_task = asyncio.create_task(self.manage_refresher())