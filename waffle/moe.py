import asyncio

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
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)

    async def query_anime(self, page=1, per_page=100):
        query = gql(
            """
            query ($page: Int, $perPage: Int) {
                Page (page: $page, perPage: $perPage) {
                    pageInfo {
                        total
                        currentPage
                        lastPage
                        hasNextPage
                        perPage
                    }
                    media (sort: POPULARITY_DESC) {
                        id
                        title {
                            romaji
                            english
                            native
                        }
                        synonyms
                    }
                }
            }
            """
        )
        async with self.client as session:
            return await session.execute(
                query,
                variable_values={
                    "page": page,
                    "per_page": per_page,
                },
            )

    @commands.group(name="moe", invoke_without_command=True)
    @commands.guild_only()
    async def moe(self, ctx, page=1, per_page=100):
        """
        Group for Anime-related commands.
        """
        print(await self.query_anime(page=page, per_page=per_page))
