#TODO Rework reddit command; allow users to provide subreddit.
#TODO Implement other entertaining APIs
#TODO Add support for non-US realms in get_char_profile() and get_char_media()
#TODO Make use of Repl.it db in some way

import discord
import os
import requests
import json
import random
import praw
import asyncio
from bot_vars import eightball_answers, command_list
from keep_alive import keep_alive
from PIL import Image
from io import BytesIO

client = discord.Client(activity=discord.Game(name='with Python'))

reddit = praw.Reddit(
    client_id = os.getenv('REDDIT_ID'),
    client_secret = os.getenv('REDDIT_SECRET'),
    username = os.getenv('REDDIT_USER'),
    password = os.getenv('REDDIT_PASS'),
    user_agent = os.getenv('REDDIT_USER_AGENT')
    )

subreddits = os.getenv('SUBREDDITS').split()

# Background task which runs every 5 minutes to update the Blizzard token. Would be nice to not have to use a global variable though.
async def bg_get_blizz_token():
    await client.wait_until_ready()
    while True:
        curl_data = {'grant_type': 'client_credentials'}
        get_token = requests.post('https://us.battle.net/oauth/token', data=curl_data, auth=(os.getenv('BLIZZARD_ID'), os.getenv('BLIZZARD_SECRET')))
        get_token_json = json.loads(get_token.text)
        global BLIZZARD_TOKEN
        BLIZZARD_TOKEN = get_token_json['access_token']
        await asyncio.sleep(300)
    
def get_quote():
    response = requests.get('https://zenquotes.io/api/random')
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote

def get_dadjoke():
    curl_headers = {'Accept': 'application/json'}
    response = requests.get('https://icanhazdadjoke.com/', headers=curl_headers)
    json_data = json.loads(response.text)
    dadjoke = json_data['joke']
    return dadjoke

def get_eightball():
    verdict = random.choice(eightball_answers)
    return verdict

def get_char_profile(REALM, CHARACTER, BLIZZARD_TOKEN):
    char_profile_request = requests.get(f'https://us.api.blizzard.com/profile/wow/character/{REALM}/{CHARACTER}?namespace=profile-us&locale=en_US&access_token={BLIZZARD_TOKEN}')
    if char_profile_request.status_code == 200:
        char_profile_json = json.loads(char_profile_request.text)
        char_profile = {
            'name': char_profile_json['name'],
            'active_spec': char_profile_json['active_spec']['name'],
            'character_class': char_profile_json['character_class']['name'],
            'equipped_item_level': char_profile_json['equipped_item_level'],
            'achievement_points': char_profile_json['achievement_points']
        }

        # Some characters do not have guilds
        try:
            char_profile['guild'] = char_profile_json['guild']['name']
        except KeyError:
            char_profile['guild'] = 'N/A'
        # Some characters do not have titles
        try:
            char_profile['active_title'] = char_profile_json['active_title']['display_string']
        except KeyError:
            char_profile['active_title'] = ''

        if char_profile['active_title'] != '':
            char_profile['full_name'] = char_profile['active_title'].replace('{name}', char_profile['name'])
        else:
            char_profile['full_name'] = char_profile['name']

        # Check spec and create a role variable to be used to build a proper Icy Veins URL
        tank_list = ['guardian', 'protection', 'blood', 'vengeance', 'brewmaster']
        healing_list = ['restoration', 'holy', 'discipline', 'mistweaver']
        if char_profile['active_spec'].lower() in tank_list:
            char_profile['role'] = 'tank'
        elif char_profile['active_spec'].lower() in healing_list:
            char_profile['role'] = 'healing'
        else:
            char_profile['role'] = 'dps'

        char_profile['armory_url'] = f"https://worldofwarcraft.com/en-us/character/us/{REALM}/{CHARACTER}"
        char_profile['bis_url'] = f"https://www.icy-veins.com/wow/{char_profile['active_spec'].lower()}-{char_profile['character_class'].lower().replace(' ', '-')}-pve-{char_profile['role']}-gear-best-in-slot"
    else:
        char_profile = 'failed'
    return char_profile

def get_char_media(REALM, CHARACTER, BLIZZARD_TOKEN):
    char_media_request = requests.get(f'https://us.api.blizzard.com/profile/wow/character/{REALM}/{CHARACTER}/character-media?namespace=profile-us&locale=en_US&access_token={BLIZZARD_TOKEN}')
    if char_media_request.status_code == 200:
        char_media_json = json.loads(char_media_request.text)
        char_media = {
            'portrait': char_media_json['assets'][1]['value'],
            'model': char_media_json['assets'][3]['value']
        }
    else:
        char_media = 'failed'
    return char_media

def get_and_crop_img(img_url):
    img_response = requests.get(img_url)
    img = Image.open(BytesIO(img_response.content))
    final_img = img.crop(img.getbbox())  
    return final_img

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    print("We are currently in the following guilds (servers):")
    for guild in client.guilds:
        print(f"{guild.name} - {guild.id}")
    # How to leave a guild (server):
    # await client.get_guild(id_integer).leave()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user = message.author.display_name
    msg = message.content.lower()

    # Commands
    if msg.startswith('m!commands') or msg.startswith('m!help'):
        await message.channel.send(command_list)

    # Inspirational quote
    elif msg.startswith('m!inspire'):
        quote = get_quote()
        await message.channel.send(f"{user}: {quote}")

    # Random dad joke
    elif msg.startswith('m!dadjoke'):
        dadjoke = get_dadjoke()
        await message.channel.send(dadjoke)

    # Dirty 8-ball (to be retired)
    elif msg.startswith('m!8ball'):
        verdict = get_eightball()
        await message.channel.send(f"{user}: {verdict}")

    # WoW character model
    elif msg.startswith('m!wowchar'):
        wowchar_arg = msg.split('m!wowchar ', 1)[1]
        realm_char_query = wowchar_arg.split('/')
        REALM = realm_char_query[0].replace('\'', '').replace(' ', '-')
        CHARACTER = realm_char_query[1]
        char_media = get_char_media(REALM, CHARACTER, BLIZZARD_TOKEN)
        if char_media != 'failed':
            await message.channel.send("Processing...")
            final_img = get_and_crop_img(char_media['model'])
            with BytesIO() as image_binary:
                final_img.save(image_binary, 'PNG')
                image_binary.seek(0)
                await message.channel.send(file=discord.File(fp=image_binary, filename=f'{CHARACTER}.png'))
        else:
            await message.channel.send("There was no response from the server. Check your spelling and/or visit https://account.blizzard.com/privacy and ensure that \"Share my game data with community developers\" is enabled under \"Game Data and Profile Privacy\".")

    # WoW character armory and Icy Veins best-in-slot link
    elif msg.startswith('m!armory'):
        armory_arg = msg.split('m!armory ', 1)[1]
        realm_char_query = armory_arg.split('/')
        REALM = realm_char_query[0].replace('\'', '').replace(' ', '-')
        CHARACTER = realm_char_query[1]
        char_profile = get_char_profile(REALM, CHARACTER, BLIZZARD_TOKEN)
        char_media = get_char_media(REALM, CHARACTER, BLIZZARD_TOKEN)

        if char_profile != 'failed':
            char_embed = discord.Embed(title=char_profile['full_name'], type='rich', color=0x992d22, url=char_profile['armory_url'])
            char_embed.add_field(name="Guild", value=char_profile['guild'], inline=False)
            char_embed.add_field(name="Character", value=f"{char_profile['active_spec']} {char_profile['character_class']}", inline=False)
            char_embed.add_field(name="Item Level (Equipped)", value=char_profile['equipped_item_level'], inline=False)
            char_embed.add_field(name="Best In Slot (PvE)", value=f"[Icy-Veins]({char_profile['bis_url']})", inline=False)
            char_embed.add_field(name="Achievement Points", value=char_profile['achievement_points'], inline=False)
        if char_media != 'failed':
            char_embed.set_image(url=char_media['portrait'])
            await message.channel.send(embed=char_embed)
        else:
            await message.channel.send("There was no response from the server. Check your spelling and/or visit https://account.blizzard.com/privacy and ensure that \"Share my game data with community developers\" is enabled under \"Game Data and Profile Privacy\".")
 
    # Link to free games updates
    elif msg.startswith('m!freegames'):
        await message.channel.send('https://gamesfree.today/')

    # Easter eggs
    if 'i love mike' in msg:
        await message.channel.send('https://i.imgur.com/mgVUmum.png')

    elif 'i hate mike' in msg:
        await message.channel.send('https://i.imgur.com/mgVUmum.png')

    elif 'whataburger' in msg:
        await message.channel.send("Freddy's is better.")

    elif 'mike hates us' in msg:
        await message.channel.send("No he doesn't.")
        
    elif 'mike loves us' in msg:
        await message.channel.send("Yes he does.")

    # Fetch specific message ID in DM with user who uses the command
    # Then delete message
    # This needs fiddling
    # if msg.startswith('m!dmpurge'):
    #     if message.author.dm_channel:
    #         the_message = await message.channel.fetch_message(802068665188089876)
    #         await the_message.delete()

keep_alive()
client.loop.create_task(bg_get_blizz_token())
client.run(os.getenv('DISCORD_TOKEN'))