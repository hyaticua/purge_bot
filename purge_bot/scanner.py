import discord
from collections import Counter
from plan import Plan
import sys

from utils import send_message

async def get_message_counts(channel_or_thread, count):
    try:
        history = await channel_or_thread.history(limit=None).flatten()
        for message in history:
            if message.content:
                count[message.author] += 1
    except discord.Forbidden:
        sys.stderr.write(f"Failed to access {channel_or_thread} history\n")
        return False
    return True


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
            has_access = await get_message_counts(channel, count)

            if not has_access:
                continue
            
            for thread in channel.threads:
                try:
                    print(f"Thread: {thread} is_private={thread.is_private()=}")
                    await send_message(ctx, f"Scanning thread: {thread}")
                    await get_message_counts(thread, count)
                except discord.Forbidden:
                    sys.stderr.write(f"Failed to access {thread} history\n")

            async for arch_thread in channel.archived_threads(private=False, limit=None):
                try:
                    print(f"Archived thread: {arch_thread}")
                    await send_message(ctx, f"Scanning thread: {arch_thread}")
                    await get_message_counts(arch_thread, count)
                except discord.Forbidden:
                    sys.stderr.write(f"Failed to access {arch_thread} history\n")


            async for secret_thread in channel.archived_threads(private=True, limit=None):
                try:
                    print(f"Archived secret thread: {secret_thread}")
                    await send_message(ctx, f"Scanning thread: {secret_thread}")
                    await get_message_counts(secret_thread, count)
                except discord.Forbidden:
                    sys.stderr.write(f"Failed to access {secret_thread} history\n")
                
        plan = Plan(plan_id)

        for member, message_count in count.items():
            if not message_count:
                plan.add(member)

        print("Scan complete!")

        return plan
