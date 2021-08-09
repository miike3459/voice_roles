# Made by miike3459

import asyncio
import discord
import time
import os

from configparser import ConfigParser
from dotenv import load_dotenv

load_dotenv(override=True)

print("Voice Roles 1.0 by miike3459\n----------------------------")

"""
tracked_members = {
    discord.Member: {
         "total_seconds": int,
         "voice_state": {
             "in_voice": bool,
             "join_time": Optional[int]
         }
    },
    ...
}
"""
tracked_members = {}

"""
tracked_member_timers = {
    discord.Member: int
}
"""
tracked_member_timers = {}

client = discord.Client(
    intents=discord.Intents(voice_states=True, members=True, guilds=True))

config = ConfigParser()
config.read("app.ini")
config = config["Configuration"]

VOICE_CHANNEL = int(config["voice_channel"])
ROLE = int(config["role"])
GUILD = int(config["guild"])
EXCLUDED_USERS = None if not config["exclude_users"] else \
    list(map(int, config["exclude_users"].split(",")))
SECOND_THRESHOLD = int(config["minutes_in_voice"]) * 60
DEFAULT_MEMBER_DATA = {
    "total_seconds": 0,
    "voice_state": {
        "in_voice": False,
        "join_time": None
    }
}

print("Configuration loaded.")


def get_time() -> int:
    return int(time.time())


async def check_voice_times():
    while True:
        current_time = get_time()
        for member, voice_time in tracked_member_timers.copy().items():
            if current_time > voice_time:
                print(f"| REWARD: {member} was given {ROLE}.")
                tracked_member_timers.pop(member)
                await member.add_roles(
                    ROLE, reason="Voice activity reward")
        await asyncio.sleep(5)


@client.event
async def on_voice_state_update(member, before, after):
    if not client.is_ready() or member.bot or member.id in EXCLUDED_USERS:
        return

    if not before.channel and after.channel:
        if after.channel != VOICE_CHANNEL:
            return

        print(f"| {member} connected to voice.")
        member_data = tracked_members.get(member, DEFAULT_MEMBER_DATA.copy())
        seconds_elapsed = member_data["total_seconds"]
        if seconds_elapsed > SECOND_THRESHOLD:
            return

        member_data["voice_state"]["in_voice"] = True
        member_data["voice_state"]["join_time"] = get_time() # noqa
        tracked_members[member] = member_data
        tracked_member_timers[member] = \
            get_time() + (SECOND_THRESHOLD - seconds_elapsed)

    elif before.channel and not after.channel:
        if before.channel.id != VOICE_CHANNEL:
            return

        member_data = tracked_members.get(member)
        if member_data is None:
            print(f"| ERROR: Failed to track voice activity for {member}.")
            return

        print(f"| {member} disconnected from voice.")
        if member_data["total_seconds"] > SECOND_THRESHOLD:
            return

        new_elapsed_time = \
            get_time() - member_data["voice_state"]["join_time"]
        member_data["voice_state"]["in_voice"] = False
        member_data["total_seconds"] += new_elapsed_time
        member_data["voice_state"]["join_time"] = None
        tracked_members[member] = member_data
        tracked_member_timers.pop(member)


@client.event
async def on_ready():
    print(f"Connected to Discord. ({client.user})\n")
    global ROLE, VOICE_CHANNEL
    guild = client.get_guild(GUILD)
    ROLE = guild.get_role(ROLE)
    VOICE_CHANNEL = guild.get_channel(VOICE_CHANNEL)

    voice_members = [
        m for m in VOICE_CHANNEL.members if m.id not in EXCLUDED_USERS]
    for member in voice_members:
        tracked_members[member] = DEFAULT_MEMBER_DATA.copy()
        tracked_member_timers[member] = get_time() + SECOND_THRESHOLD

    print(f"| Started tracking {len(voice_members)} users in voice.")
    asyncio.ensure_future(check_voice_times())


client.run(os.getenv("TOKEN"))
