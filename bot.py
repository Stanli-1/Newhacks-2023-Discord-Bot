#this file receives and sends messages
import discord
import responses
import os

#triggers when a user sends a message
async def send_message(message, user_message, is_private):
   try:
       #sends message either into the main channel or a private message
       response = responses.handle_response(user_message)
       await message.author.send(response) if is_private else await message.channel.send(response)
  #if anything goes wrong
   except Exception as e:
       print(e)


def run_discord_bot():
    TOKEN = os.getenv("TOKEN")
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')

    @client.event
    async def on_message(message):
        #early return if the message sender is the bot
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        if user_message[0] =='?':
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)


    client.run(TOKEN)