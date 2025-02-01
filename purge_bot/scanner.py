import discord
from collections import Counter
from plan import Plan

from utils import send_message

async def get_message_counts(channel_or_thread, count):
    history = await channel_or_thread.history(limit=None).flatten()
    for message in history:
        if message.content:
            count[message.author] += 1


class Scanner:
    def __init__(self):
        pass

    async def scan(self, ctx: discord.ApplicationContext, plan_id: int) -> Plan:
        # await ctx.defer()

        count = Counter()

        guild: discord.Guild = ctx.guild

        for member in guild.members:
            count[member] = 0

        for channel in guild.text_channels:
            await send_message(ctx, f"Scanning channel: {channel}")
            await get_message_counts(channel, count)

            for thread in channel.threads:
                print(f"Thread: {thread} is_private={thread.is_private()=}")
                await send_message(ctx, f"Scanning thread: {thread}")
                await get_message_counts(thread, count)

            async for arch_thread in channel.archived_threads(private=False, limit=None):
                print(f"Archived thread: {arch_thread}")
                await send_message(ctx, f"Scanning thread: {arch_thread}")
                await get_message_counts(arch_thread, count)

            async for secret_thread in channel.archived_threads(private=True, limit=None):
                print(f"Archived secret thread: {secret_thread}")
                await send_message(ctx, f"Scanning thread: {secret_thread}")
                await get_message_counts(secret_thread, count)

        plan = Plan(plan_id)

        for member, message_count in count.items():
            if not message_count:
                plan.add(member)

        return plan
