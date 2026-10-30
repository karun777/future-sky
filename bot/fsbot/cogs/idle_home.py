"""One checked walking action per heartbeat; human input takes priority."""
import time
import logging
from copy import copy, deepcopy
import discord
from discord.ext import commands
from fsbot.idle_home import KEY, record, configure, touch, due, blocked, next_step, note
from fsbot.cogs.router import RunRoutedContext, send_to_player_run_channel_if_any

class QuietHomeContext(RunRoutedContext):
    async def send(self, content=None, **kwargs):
        return None

class IdleHomeCog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.now=time.time
        self.contexts={}
        self.seen_messages={}
        self.suspended=set()
        self.active=set()

    async def cog_load(self):
        self.bot.events.subscribe("heartbeat.advanced",self.on_heartbeat)

    async def cog_unload(self):
        self.bot.events.unsubscribe("heartbeat.advanced",self.on_heartbeat)

    def commit(self,uid,updated):
        storage=self.bot.storage
        original=storage.characters[uid]
        if updated==original:return
        storage.characters[uid]=updated
        try:storage.save_characters()
        except Exception:
            storage.characters[uid]=original
            self.suspended.add(uid)
            raise

    def observe(self,uid,message=None):
        uid=str(uid)
        if message is not None:
            self.contexts[uid]=message
            if self.seen_messages.get(uid)==str(message.id):return
            self.seen_messages[uid]=str(message.id)
        ch=self.bot.storage.characters.get(uid)
        if not isinstance(ch,dict):return
        try:
            self.commit(uid,touch(ch,self.now(),message))
            self.suspended.discard(uid)
        except Exception:
            self.suspended.add(uid)
            logging.getLogger("futuresky.idle_home").exception("Idle activity save failed")

    def allow_step(self,ctx):
        uid=str(ctx.author.id)
        ch=self.bot.storage.characters.get(uid)
        if uid in self.suspended or not isinstance(ch,dict):return False
        s=record(ch)
        return bool(s and s["generation"]==ctx._idle_generation
                    and s["home"]==ctx._idle_home and due(ch,self.now()) and not blocked(ch))

    async def bot_check(self,ctx):
        if getattr(ctx,"_automatic_action",False):
            return self.allow_step(ctx)
        if not getattr(ctx,"_sequence_child",False):
            self.observe(str(ctx.author.id),ctx.message)
        return True

    @commands.Cog.listener()
    async def on_message(self,message):
        if getattr(message.author,"bot",False):return
        uid=str(message.author.id)
        ch=self.bot.storage.characters.get(uid)
        if isinstance(ch,dict) and str(ch.get("run_channel_id"))==str(message.channel.id):
            self.observe(uid,message)

    @commands.Cog.listener()
    async def on_typing(self,channel,user,when):
        if getattr(user,"bot",False):return
        uid=str(user.id)
        ch=self.bot.storage.characters.get(uid)
        if isinstance(ch,dict) and str(ch.get("run_channel_id"))==str(channel.id):
            self.observe(uid)

    async def source_message(self,uid,ch):
        s=record(ch)
        cached=self.contexts.get(uid)
        if cached:return cached
        channel=self.bot.get_channel(int(s.get("channel_id") or 0))
        if channel is None or str(ch.get("run_channel_id"))!=str(getattr(channel,"id",None)):
            return None
        try:message=await channel.fetch_message(int(s.get("message_id") or 0))
        except Exception:return None
        if str(message.author.id)!=uid or getattr(message.author,"bot",False):return None
        self.contexts[uid]=message
        return message

    async def deliver(self,uid):
        ch=self.bot.storage.characters[uid];s=record(ch)
        text=s.get("pending_notice")
        if not text:return
        delivered=False
        for guild in self.bot.guilds:
            if await send_to_player_run_channel_if_any(self.bot,guild,uid,text,
                    allowed_mentions=discord.AllowedMentions.none()):
                delivered=True;break
        if delivered:
            # Work from latest record; a player's input may have arrived while sending.
            from copy import deepcopy
            updated=deepcopy(self.bot.storage.characters[uid])
            updated["extra"][KEY].pop("pending_notice",None)
            self.commit(uid,updated)

    async def tick(self,uid):
        if uid in self.active or uid in self.suspended:return
        self.active.add(uid)
        try:
            ch=self.bot.storage.characters.get(uid)
            if not isinstance(ch,dict):return
            s=record(ch)
            if not s or not s["enabled"]:return
            await self.deliver(uid)
            ch=self.bot.storage.characters[uid];s=record(ch)
            if not due(ch,self.now()) or s.get("status")=="home":return
            runner=self.bot.get_cog("SequenceCog")
            if runner and uid in runner.running:return
            if blocked(ch):
                self.commit(uid,note(ch,"blocked"))
                return
            home=s["home"]
            if ch.get("current_room")==home:
                self.commit(uid,note(ch,"home"))
                return
            try:direction=next_step(self.bot.storage.rooms,ch.get("current_room"),home)
            except ValueError:
                # Delivery clears pending_notice, but must not rearm the warning.
                # Persist the episode key so a restart also remains quiet.
                episode = [s["generation"], ch.get("current_room"), home]
                if s.get("status") != "blocked" or s.get("route_block_notice") != episode:
                    updated = deepcopy(note(ch, "blocked",
                        "Your usual way home is unavailable. You stay where you are."))
                    updated["extra"][KEY]["route_block_notice"] = episode
                    self.commit(uid, updated)
                return
            generation=s["generation"]
            message=await self.source_message(uid,ch)
            if message is None:return
            # Source lookup can yield: re-check the latest durable activity before invocation.
            ch=self.bot.storage.characters[uid];s=record(ch)
            if s["generation"]!=generation or not due(ch,self.now()):return
            synthetic=copy(message);synthetic.content="!go "+direction
            ctx=await self.bot.get_context(synthetic,cls=QuietHomeContext)
            ctx._automatic_action=True
            ctx._idle_generation=generation
            ctx._idle_home=home
            ctx.sequence_result=None
            if ctx.command is None:return
            try:
                if not await self.bot.can_run(ctx,call_once=True):return
                await ctx.command.invoke(ctx)
            except commands.CommandError:
                return
            ch=self.bot.storage.characters[uid];s=record(ch)
            if s["generation"]!=generation:return
            if ctx.sequence_result!="success":
                self.commit(uid,note(ch,"blocked"))
                return
            if ch.get("current_room")==s["home"]:
                title=self.bot.storage.rooms.get(s["home"],{}).get("title",s["home"])
                self.commit(uid,note(ch,"home",f"While your attention wandered, you made your way home to **{title}**."))
                await self.deliver(uid)
            else:self.commit(uid,note(ch,"walking"))
        finally:self.active.discard(uid)

    async def on_heartbeat(self,event):
        for uid,ch in list(self.bot.storage.characters.items()):
            try:
                if isinstance(ch,dict) and (ch.get("extra") or {}).get(KEY):
                    await self.tick(str(uid))
            except Exception:
                logging.getLogger("futuresky.idle_home").exception("Idle return failed for %s",uid)

    @commands.command(name="idlehome")
    async def idlehome(self,ctx,*,action="status"):
        uid=str(ctx.author.id)
        ch=self.bot.storage.characters.get(uid)
        if not isinstance(ch,dict):
            await ctx.send("Create a character first.");return
        words=action.casefold().split()
        try:
            s=record(ch)
            if words and words[0]=="on" and len(words)<=2:
                seconds=int(words[1]) if len(words)==2 else 1800
                self.commit(uid,configure(ch,self.now(),idle_seconds=seconds,message=ctx.message))
                self.contexts[uid]=ctx.message
                self.suspended.discard(uid)
                await ctx.send(f"Idle return enabled after **{seconds} real seconds** without input. Typing or a command interrupts it. Home: **{record(self.bot.storage.characters[uid])['home']}**.")
            elif words==["off"]:
                if s:self.commit(uid,configure(ch,self.now(),enabled=False,idle_seconds=s["idle_seconds"]))
                await ctx.send("Idle return disabled.")
            elif len(words)==2 and words[0]=="home":
                if words[1] not in self.bot.storage.rooms:raise ValueError("That home room does not exist.")
                self.commit(uid,configure(ch,self.now(),enabled=s["enabled"] if s else False,
                    idle_seconds=s["idle_seconds"] if s else 1800,message=ctx.message,home=words[1]))
                await ctx.send(f"Your home is now **{words[1]}**.")
            elif words==["status"]:
                await self.deliver(uid)
                s=record(self.bot.storage.characters[uid])
                await ctx.send("Idle return is off. Enable with `!idlehome on`." if not s else
                    f"Idle return: **{'on' if s['enabled'] else 'off'}**; home **{s['home']}**; threshold **{s['idle_seconds']} real seconds**; state **{s.get('status','armed')}**.")
            else:await ctx.send("Use `!idlehome on [seconds]`, `!idlehome off`, `!idlehome home <room_id>` or `!idlehome status`.")
        except (ValueError,TypeError,KeyError,AttributeError):
            await ctx.send("Idle-home settings unavailable. Use a valid room and 60–86400 real seconds.")
        except Exception:
            await ctx.send("Idle-home settings could not be saved. Please try again.")

async def setup(bot):
    await bot.add_cog(IdleHomeCog(bot))
