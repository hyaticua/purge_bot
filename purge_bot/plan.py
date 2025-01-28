import discord


def id_generator(start = 0):
    id = start
    while True:
        id += 1
        yield id

class Plan:
    def __init__(self, plan_id: int):
        self.plan_id = plan_id
        self.to_purge = []

    def add(self, member: discord.Member):
        self.to_purge.append(member)