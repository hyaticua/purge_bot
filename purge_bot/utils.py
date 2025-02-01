import discord
import sys

async def send_message(ctx: discord.ApplicationContext, content: str):
    try:
        await ctx.send(content)
    except discord.Forbidden:
        sys.stderr.write(f"Failed to send message in {ctx.guild.name}#{ctx.channel.name}: {content}\n")