import asyncio
from mautrix.types import PresenceState, UserID
from maubot import Plugin, MessageEvent
from maubot.handlers import command

class StatusPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_statuses = {}  # Store statuses per user: {user_id: status}

    async def manage_refresher(self, user_id: UserID):
        """Re-apply a user's status every 60 seconds."""
        while True:
            if user_id in self._user_statuses:
                status = self._user_statuses[user_id]
                try:
                    # Requires bot to have power-level >= 50 (admin) in the user's server
                    await self.client.set_presence(
                        state=PresenceState.ONLINE,
                        status_msg=status,
                        user_id=user_id  # <-- Key change: Set status for the user, not the bot
                    )
                except Exception as e:
                    self.log.error(f"Failed to update status for {user_id}: {e}")
            await asyncio.sleep(60)

    @command.new(
        name="setstatus",
        help="Set your presence status message"
    )
    @command.argument("status", pass_raw=True)
    async def cmd_setstatus(self, evt: MessageEvent, status: str):
        status = status.strip()
        if not status:
            await evt.reply("❗️ Please provide a status: `!setstatus Working from home`")
            return

        user_id = evt.sender  # The user who sent the command
        self._user_statuses[user_id] = status  # Store their status

        try:
            # Attempt to set the user's status immediately
            await self.client.set_presence(
                state=PresenceState.ONLINE,
                status_msg=status,
                user_id=user_id  # <-- Set for the user, not the bot
            )
            await evt.reply(f'✅ Your status was set to: "{status}"')
        except Exception as e:
            await evt.reply(f"❌ Failed to set your status (do I have permissions?): {e}")
            return

        # Start/update the refresher task for this user
        if hasattr(self, f"_refresh_task_{user_id}"):
            getattr(self, f"_refresh_task_{user_id}").cancel()
        
        task = asyncio.create_task(self.manage_refresher(user_id))
        setattr(self, f"_refresh_task_{user_id}", task)  # Track per-user tasks