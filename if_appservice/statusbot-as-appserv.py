import asyncio
from mautrix.types import PresenceState, UserID
from maubot import Plugin, MessageEvent
from maubot.handlers import command

class StatusAppService(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_statuses = {}
        self.refresh_tasks = {}

    async def _refresh_presence(self, user_id: UserID):
        """Maintain presence state for a user"""
        while True:
            try:
                await self.client.set_presence(
                    presence=PresenceState.ONLINE,
                    status_msg=self.user_statuses.get(user_id, ""),
                    user_id=user_id
                )
            except Exception as e:
                self.log.error(f"Presence refresh failed for {user_id}: {e}")
            await asyncio.sleep(60)

    @command.new(
        name="setstatus",
        help="Set your Matrix presence status",
        require_admin=False
    )
    @command.argument("status", pass_raw=True)
    async def set_status(self, evt: MessageEvent, status: str):
        user_id = evt.sender
        status = status.strip()
        
        if not status:
            return await evt.reply("Please provide a status message")
        
        # Update stored status
        self.user_statuses[user_id] = status
        
        try:
            # Immediate presence update
            await self.client.set_presence(
                presence=PresenceState.ONLINE,
                status_msg=status,
                user_id=user_id
            )
            await evt.reply(f"✅ Presence updated: {status}")
        except Exception as e:
            await evt.reply(f"❌ Failed to update presence: {str(e)}")
            return

        # Manage background task
        if user_id in self.refresh_tasks:
            self.refresh_tasks[user_id].cancel()
        self.refresh_tasks[user_id] = asyncio.create_task(
            self._refresh_presence(user_id)
        )

    async def stop(self):
        """Cleanup on plugin unload"""
        for task in self.refresh_tasks.values():
            task.cancel()
        await asyncio.gather(*self.refresh_tasks.values(), return_exceptions=True)