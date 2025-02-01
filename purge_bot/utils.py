import discord

async def send_message(ctx: discord.ApplicationContext, content: str):
    try:
        await ctx.send(content)
    except discord.Forbidden:
        pass