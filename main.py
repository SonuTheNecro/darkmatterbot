# Imports

import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, utils
from discord.ext import commands
from responses import get_response
import json
import requests


# Load Token

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ROLE_ID = os.getenv('ROLE_ID')
GUILD_ID = os.getenv('GUILD_ID')
ROLE_NAME = os.getenv('ROLE_NAME')

# Bot Setup (Setup Intents) 

intents = Intents.default()
intents.message_content = True
intents.members = True
client = Client(intents=intents)
#pulls data from CR-API to find a username from clan
def pull_data(user_message):
    clan_urls = [
        "https://api.clashroyale.com/v1/clans/%23LCJ9LU2/members",
        "https://api.clashroyale.com/v1/clans/%23R09V89RP/members",
        f"https://api.clashroyale.com/v1/clans/%23G00VV29L/members"
    ]
    for url in clan_urls:
        r = requests.get(url, headers={"Accept": "application/json", "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjQxMDA1ZjhlLTRmM2YtNDQ2MS05MGFjLTZlNGZkZDAyMjE5MiIsImlhdCI6MTcxMDU1NTI0OCwic3ViIjoiZGV2ZWxvcGVyLzk5NTY0ZTIyLTlkZDgtMDkzOS0yOGVmLTJlNGNlMGU4YmNmZCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIyNC4xMy40NC43Il0sInR5cGUiOiJjbGllbnQifV19.b2icLc0w7GY5NEwEbDn6qzsCP0kBykdNm2FHRI1rojaBh0OSEZMz1e0yMwldqg4Ng7Kw2vwDv6xhv9VMc7DNBQ"}, params={"limit": 50})
        data = r.json()
        all_names = [item['name'].lower() for item in data['items']]
        
        for name in all_names:
            if name.lower() == user_message.lower():
                return name
    
    return ""
#send message
async def send_message(message, user_message) -> None:
    #If its empty
    if not user_message: 
        return
    #If its private
    if str(message.channel).startswith("Direct Message"):
        is_private = True
        userName = pull_data(user_message)
        if userName == "": return
        lock = False
        check = False
        fileStream = open('members.txt', 'r')
        memberlist = fileStream.readlines()
        fileStream.close()
        for line in memberlist:
            check_line = line.strip().split(':')
            if(userName == check_line[0] and str(message.author).lower() == check_line[1]):
                print(f"{userName} has been given a role!")
                await give_role(GUILD_ID,ROLE_NAME,message.author.id)
                await message.author.send("You are already in our system. Role has been given!")
                check = True
                break

            if(userName == check_line[0] and str(message.author).lower() != check_line[1]):
                print(userName)
                print(check_line[0])
                print(str(message.author).lower())
                print(check_line[1])
                print("You are already registered under a different username")
                await message.author.send("This Clash Royale Account is under a different discord account. Please give another account in the DLM family!")
                lock = True  
        if check == False and lock == False:
            fileStream.close()
            fileStream = open('members.txt', 'a')
            fileStream.write(f"{userName}:{str(message.author).lower()}\n")
            fileStream.close()
            await give_role(GUILD_ID,ROLE_NAME,message.author.id)
            await message.author.send("You have been added to the list! Welcome to Dark Matter discord server!")
                
        

    
    # try to stop errors
    try:
        response = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# startup for bot

@client.event
async def on_ready() -> None:
    print(f'{client.user} has joined the Arena')

@client.event
async def on_member_join(member):
    print(str(member))
    await member.send('Welcome to Dark Matter! Please DM me your username to be allowed in the Discord Server!')


@client.event
async def on_message(message) -> None:
    # Bot doesn't reply to itself
    if message.author == client.user:
        return
    #Log
    username = str(message.author)
    user_message = message.content
    channel = str(message.channel)
    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)

async def give_role(guild_id: int, role_name: str, user_id: int):
    guild = client.get_guild(int(guild_id))
    if not guild:
        print("Guild not found.")
        return
    
    role = utils.get(guild.roles, name=role_name)
    if not role:
        print("Role not found.")
        return
    member = guild.get_member(user_id)
    if not member:
        print("User not found in the specified server.")
        return

    await member.add_roles(role)
    print(f"Added {role_name} role to {member.display_name} in {guild.name}.")

def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()