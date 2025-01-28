import discord
import os
import asyncio

from collections import Counter
from scanner import Scanner
from plan import id_generator, Plan
from discord import default_permissions

import json
from datetime import datetime

discord_api_key = os.environ.get("DISCORD_API_KEY")

intents = discord.Intents().default()
intents.members = True

bot = discord.Bot(intents=intents)
scanner = Scanner()

current_scans = {}
plans: dict[int, Plan] = {}
plan_id_gen = id_generator()


def dump_plan(plan: Plan, guild_id: int):
    obj = {
        "plan_id": plan.plan_id,
        "guild_id": guild_id,
        "to_purge": [member.id for member in plan.to_purge]
    }
    time = datetime.now().strftime("%Y-%m-%d.%H:%M:%S")
    path = f"plans/{guild_id}-{plan.plan_id}.{time}.json"
    with open(path, "w") as f:
        json.dump(obj, f)


async def add_role(ctx: discord.ApplicationContext, member: discord.Member):
    guild: discord.Guild = ctx.guild
    role = discord.utils.get(guild.roles, name="Purged")

    await member.add_roles(role)
    await ctx.send(f"Added {role} to {member}")


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

def on_scan_finished(ctx: discord.ApplicationContext, plan: Plan):
    plans[plan.plan_id] = plan
    current_scans.pop(plan.plan_id)
    bot.loop.create_task(notify_user_on_scan_finished(ctx, plan))

async def notify_user_on_scan_finished(ctx: discord.ApplicationContext, plan: Plan):
    await ctx.send(f"Scan complete! {len(plan.to_purge)} members found to purge. plan ID {plan.plan_id}")

@bot.slash_command()
@default_permissions(manage_messages=True)
async def scan(ctx: discord.ApplicationContext):
    if ctx.guild.id in current_scans.values():
        await ctx.respond("Sorry, I'm already scanning this server.")
        return
    
    plan_id = next(plan_id_gen)
    current_scans[plan_id] = ctx.guild.id

    await ctx.respond(f"Okay! Scanning now... your plan ID is {plan_id}")
    task = bot.loop.create_task(scanner.scan(ctx, plan_id))
    task.add_done_callback(lambda plan: on_scan_finished(ctx, plan.result()))

@bot.slash_command()
@default_permissions(manage_messages=True)
async def list(ctx: discord.ApplicationContext, plan_id: int):
    plan = plans.get(plan_id)
    if not plan:
        await ctx.respond(f"Sorry, I couldn't find a plan with ID {plan_id}")
    
    to_purge = [member.name for member in plan.to_purge]
    msg = f"Plan {plan_id} has {len(plan.to_purge)} members to purge:\n"
    msg += "\n".join(to_purge)
    await ctx.respond(msg)

@bot.slash_command()
@default_permissions(manage_messages=True)
async def execute(ctx: discord.ApplicationContext, plan_id: int):
    await ctx.defer()
    plan = plans.get(plan_id)
    if not plan:
        await ctx.respond(f"Sorry, I couldn't find a plan with ID {plan_id}")
    
    for member in plan.to_purge:
        await add_role(ctx, member)

    dump_plan(plan, ctx.guild.id)
    plans.pop(plan_id)

    await ctx.followup.send(f"Done! {len(plan.to_purge)} members have been purged.")


def run():
    bot.run(discord_api_key)


if __name__ == "__main__":
    run()