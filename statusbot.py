import asyncio
from mautrix.types import PresenceState
from maubot import Plugin, MessageEvent
from maubot.handlers import command

class StatusPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._refresh_task = None
        self._current_status = None
        self.log.debug("StatusBot plugin initialized")

    async def stop(self):
        """Clean up when plugin is stopped"""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
        await super().stop()

    async def manage_refresher(self):
        """Re-apply your status every 60 seconds."""
        while True:
            try:
                await self.client.set_presence(PresenceState.ONLINE, status=self._current_status)
                self.log.debug(f"Refreshed status: {self._current_status}")
            except Exception as e:
                self.log.exception("Failed to refresh status")
            await asyncio.sleep(60)

    @command.new(
        name="setstatus",
        help="Set your presence status message",
        params=["status:text"]
    )
    async def cmd_setstatus(self, evt: MessageEvent, status: str):
        status = status.strip()
        if not status:
            await evt.reply("❗️ Please provide a status: `!setstatus Working from home`")
            return
            
        if len(status) > 100:
            await evt.reply("❗️ Status message too long (max 100 characters)")
            return

        self._current_status = status
        try:
            await self.client.set_presence(PresenceState.ONLINE, status=status)
            await evt.reply(f'Status set to: "{status}"')
        except Exception as e:
            await evt.reply(f"❌ Failed to set status: {str(e)}")
            return

        if self._refresh_task:
            self._refresh_task.cancel()
        self._refresh_task = asyncio.create_task(self.manage_refresher())
        self.log.info(f"Status updated by {evt.sender}: {status}")