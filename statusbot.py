import asyncio
from mautrix.types import PresenceState
from maubot import Plugin, MessageEvent
from maubot.handlers import command
import yaml
from pathlib import Path

class StatusPlugin(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._refresh_task = None
        self._current_status = None
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        """Load plugin metadata from maubot.yaml"""
        try:
            mbp_path = Path(__file__).parent / "maubot.yaml"
            with mbp_path.open() as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.log.warning(f"Failed to load metadata: {e}")
            return {"version": "unknown", "author": "unknown"}

    @command.new(
        name="setstatus",
        help="Status management commands",
        require_subcommand=True
    )
    async def setstatus(self, evt: MessageEvent):
        """Base command handler (will only show help)"""
        pass

    @setstatus.subcommand(
        name="set",
        help="Set your status message",
    )
    @command.argument("message", pass_raw=True)
    async def set_status(self, evt: MessageEvent, message: str):
        """Original status-setting functionality"""
        message = message.strip()
        if not message:
            await evt.reply("❗ Please provide a status message")
            return

        self._current_status = message
        await self.client.set_presence(PresenceState.ONLINE, status=message)
        await evt.reply(f'Status set to: "{message}"')

        if self._refresh_task:
            self._refresh_task.cancel()
        self._refresh_task = asyncio.create_task(self.manage_refresher())

    @setstatus.subcommand(
        name="version",
        help="Show plugin version information"
    )
    async def show_version(self, evt: MessageEvent):
        """Version subcommand handler"""
        await evt.reply(
            f"🔄 StatusBot\n"
            f"• Version: {self.metadata.get('version', 'unknown')}\n"
            f"• Author: {self.metadata.get('author', 'unknown')}\n"
            f"• License: {self.metadata.get('license', 'unknown')}"
        )

    async def manage_refresher(self):
        """Background status refresher"""
        while True:
            await self.client.set_presence(PresenceState.ONLINE, status=self._current_status)
            await asyncio.sleep(60)