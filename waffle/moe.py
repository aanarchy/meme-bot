from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

import discord
from discord.ext import commands


def setup(bot):
    """Set up the cog."""
    bot.add_cog(Moe(bot))


class Moe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.transport = AIOHTTPTransport(url="https://graphql.anilist.co")

    async def query_anime(self):
        pass

    @commands.group(name="moe", invoke_without_command=True)
    @commands.guild_only()
    async def moe(self, ctx, id):
        """
        Group for Anime-related commands.
        """

        client = Client(transport=self.transport, fetch_schema_from_transport=True)
        params = {"id": id}
        query = gql(
            """
            query ($id: ID){
              hero {
                id
                name
                friends {
                  name
                }
              }
            }
            """
        )

        async with client as session:
            result = await session.execute(query, variable_values=params)

        await ctx.send(result)
