# fsbot/cogs/activity.py
from __future__ import annotations

import time
import logging

import discord
from discord.ext import commands

from fsbot.cogs.router import ensure_player_run_channel

log = logging.getLogger("futuresky")


def _now() -> float:
    return time.time()


class ActivityCog(commands.Cog):
    """
    Run-channel discipline + activity tracking.

    - Run channels are commands-only (messages must start with '!')
    - Non-command messages in run channels are deleted
    - A short warning is posted IN-CHANNEL every time a non-command message is deleted
      (warning auto-deletes after a short delay to keep the channel clean)
    - Activity timestamp bumps on typing + command usage in run channel

    IMPORTANT:
    - We do NOT create channels from passive listeners.
    - We identify run channels via stored run_channel_id on the character record.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # In-memory is fine (world resets on restart is acceptable)
        if not hasattr(self.bot.state, "last_activity_at"):
            self.bot.state.last_activity_at = {}  # user_id -> float epoch seconds

    # ---------- Helpers ----------
    def bump_activity(self, user_id: str) -> None:
        self.bot.state.last_activity_at[user_id] = _now()

    def _get_char_name(self, user_id: str) -> str:
        """
        Best-effort char name for this user from storage.
        Used only for debug command / channel ensure.
        """
        try:
            s = self.bot.storage
            if user_id in s.characters:
                return str(s.characters[user_id].get("name") or "player")
        except Exception:
            pass
        return "player"

    def _get_run_channel_id(self, user_id: str) -> int | None:
        """
        Non-invasive: read run_channel_id from storage if present.
        """
        try:
            s = self.bot.storage
            if user_id not in s.characters:
                return None
            run_id = s.characters[user_id].get("run_channel_id")
            if run_id:
                return int(run_id)
        except Exception:
            return None
        return None

    def _is_users_run_channel(self, channel: discord.abc.GuildChannel | discord.abc.Messageable, user_id: str) -> bool:
        """
        True iff this channel is the user's stored run channel.
        (No ctx required; safe for on_typing/on_message.)
        """
        cid = getattr(channel, "id", None)
        if cid is None:
            return False

        run_id = self._get_run_channel_id(user_id)
        return bool(run_id and int(run_id) == int(cid))

    async def _warn_in_channel(self, channel: discord.abc.Messageable) -> None:
        """
        Post a short warning in the run channel after deleting a non-command message.
        Warns EVERY time. Auto-deletes the warning to keep the channel readable.
        """
        try:
            warn_msg = await channel.send(
                "🧭 Run channels are commands-only. Use `!help` — RP: `!say` `!pose` `!think` `!whisper`."
            )
            try:
                await warn_msg.delete(delay=8)
            except Exception:
                pass
        except Exception:
            pass

    # ---------- Debug / diagnosis ----------
    @commands.command(name="runwhere")
    @commands.is_owner()
    async def runwhere(self, ctx: commands.Context):
        """
        Owner-only: show the channel you're in vs stored run_channel_id,
        and also resolves/ensures the run channel using router ensure (ctx+char_name).
        """
        user_id = str(ctx.author.id)

        stored_run_id = self._get_run_channel_id(user_id)
        here_id = getattr(ctx.channel, "id", None)

        char_name = self._get_char_name(user_id)

        # Use the real router function properly (ctx + user_id + char_name)
        ensured = None
        try:
            ensured = await ensure_player_run_channel(self.bot, ctx, user_id, char_name)
        except Exception as e:
            log.info(f"[activity] runwhere: ensure_player_run_channel failed: {type(e).__name__}: {e}")

        ensured_id = getattr(ensured, "id", None)

        await ctx.send(
            "🧭 **runwhere**\n"
            f"- you are in: <#{here_id}>\n"
            f"- stored run_channel_id: `{stored_run_id}`\n"
            f"- ensured run channel: <#{ensured_id}>\n"
            f"- match(stored): `{bool(stored_run_id and here_id == stored_run_id)}`\n"
            f"- match(ensured): `{bool(ensured_id and here_id == ensured_id)}`"
        )

    @runwhere.error
    async def runwhere_error(self, ctx: commands.Context, error: commands.CommandError):
        # Prevent noisy stack traces when non-owner tries to run diagnostics
        if isinstance(error, commands.NotOwner):
            await ctx.send("⛔ This diagnostic is owner-only.")
            return
        raise error

    # ---------- Activity signals ----------
    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        if getattr(user, "bot", False):
            return

        user_id = str(user.id)
        try:
            if self._is_users_run_channel(channel, user_id):
                self.bump_activity(user_id)
        except Exception:
            return

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        # Bump activity when a command is recognized in the user's run channel
        user_id = str(ctx.author.id)
        try:
            if self._is_users_run_channel(ctx.channel, user_id):
                self.bump_activity(user_id)
        except Exception:
            return

    # ---------- Commands-only enforcement ----------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # IMPORTANT: do NOT call bot.process_commands here (bot already does)
        if message.author.bot:
            return

        user_id = str(message.author.id)

        try:
            # Only enforce inside the author's own run channel (by stored run_channel_id)
            if not self._is_users_run_channel(message.channel, user_id):
                return

            # Any message in run channel counts as activity (even if we delete it)
            self.bump_activity(user_id)

            # Allow commands only
            content = (message.content or "").lstrip()
            if not content.startswith("!"):
                deleted_ok = False
                try:
                    await message.delete()
                    deleted_ok = True
                except Exception as e:
                    # This will happen unless the bot has Manage Messages in that channel/category.
                    log.info(
                        "[activity] Could not delete non-command message in run channel "
                        f"(chan_id={getattr(message.channel,'id',None)}) "
                        f"user={message.author} err={type(e).__name__}: {e}"
                    )

                # Warn in-channel regardless (even if deletion failed) so player understands the rule.
                # If deletion failed, the original message will remain, but at least the rule is surfaced.
                await self._warn_in_channel(message.channel)

                # Optional: if deletion failed, avoid repeated warnings spamming too hard by returning early.
                # But user requested warn every time, so we keep it as-is.

        except Exception as e:
            log.debug(f"[activity] on_message exception: {type(e).__name__}: {e}")
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(ActivityCog(bot))
