from discord.ext import commands
from source.db import Session
from source.config import COMMAND_PREFIX, ROLE_PERM
from source.models.set import Set


def clear_boost(session):
    sets = session.query(Set).all()
    print(sets)
    for s in sets:
        print('before: ' + str(s.boosted))
        s.boosted = False
        s.name = 'TESTING'
        print('after: ' + str(s.boosted))


class EditSets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases= ['addset'])
    @commands.has_role(ROLE_PERM)
    async def AddSet(self, ctx, prefix, name):
        command = f"```{COMMAND_PREFIX}addset [set id] [set name]```"
        session = Session()

        if len(prefix) > 3:
            await ctx.send(f'SET: id must be 3 characters or less.\n' + command)

        session.add(Set(prefix=prefix.upper(), name=name, total_cards=0, boosted=False))
        await ctx.send(f'**{prefix.upper()}: {name}** has been created.')
        session.commit()


    @commands.command(aliases= ['removeset'])
    @commands.has_role(ROLE_PERM)
    async def RemoveSet(self, ctx, prefix):
        command = f"```{COMMAND_PREFIX}removeset [set id]```"
        session = Session()

        q_set = session.query(Set).filter(Set.prefix == prefix.upper()).one_or_none()
        if q_set is None:
            await ctx.send(f'SET: **{prefix}** does not exist.\n' + command)
            return

        if q_set.total_cards > 0:
            await ctx.send(f'Removing this set must be done manually, as it will delete {q_set.total_cards} cards.')
            return

        session.delete(q_set)
        session.commit()
        await ctx.send(f'**{q_set.prefix}: {q_set.name}** has been deleted.')


    @commands.command()
    @commands.has_role(ROLE_PERM)
    async def boost(self, ctx, prefix):
        command = f"```{COMMAND_PREFIX}boost [set id]```"
        session = Session()

        if prefix.upper() == 'CANCEL':
            clear_boost(session)
            session.commit()
            await ctx.send('All set boosts canceled, normal drop rates resumed.')
            return

        q_set = session.query(Set).filter(Set.prefix == prefix.upper()).one_or_none()
        if q_set is None:
            await ctx.send(f'SET: **{prefix}** does not exist.\n' + command)
            return

        clear_boost(session)
        q_set.boosted = True
        session.commit()
        await ctx.send(f'**{q_set.prefix}: {q_set.name}** is now boosted.  Each pull will now have a 50% chance '
                       f'of being from this set.')

def setup(bot):
    bot.add_cog(EditSets(bot))



