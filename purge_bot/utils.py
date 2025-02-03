import discord
import sys

async def send_message(ctx: discord.ApplicationContext, content: str):
    try:
        # if ctx.response.is_done():
        #     await ctx.followup.send(content)
        # else:
        #     await ctx.send(content)
        await ctx.send(content)
    except discord.Forbidden:
        sys.stderr.write(f"Failed to send message in {ctx.guild.name}#{ctx.channel.name}: {content}\n")