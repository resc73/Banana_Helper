import asyncio
from discord import app_commands
from discord.ext import commands
import logging
import os
from main import *

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = False
intents.message_content = False

bot = commands.Bot(command_prefix='/+', intents=intents)

connection = sqlite3.connect('users.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS id (
    discordid TEXT,
    steamid   INTEGER
);
''')
cursor.execute('SELECT * FROM id')
eedoss = cursor.fetchall()


@bot.event
async def on_ready():
    print('ready')
    try:
        synced = await bot.tree.sync()
        await bot.tree.sync()
        print(f'succes, {len(synced)} commands avaible')
    except Exception as e:
        print(e)


@bot.tree.command(name='winrate', description='Вы узнаете свой винрейт на дистанции из определенного количества игр')
@app_commands.describe(amount='количество игр')
@app_commands.choices(gamemode=[
    discord.app_commands.Choice(value='all', name='все режимы'),
    discord.app_commands.Choice(value='0', name='не соревновательный'),
    discord.app_commands.Choice(value='5', name='командный подбор'),
    discord.app_commands.Choice(value='6', name='соло подбор'),
    discord.app_commands.Choice(value='7', name='соревновательный подбор'),
])
async def wr(interaction: discord.Interaction, amount: int, gamemode: discord.app_commands.Choice[str]):
    try:
        id = get_id(interaction)
        await interaction.response.defer(thinking=True, ephemeral=False)
        await asyncio.sleep(10)
        await interaction.followup.send(str(get_win_rate(amount, id, gamemode.value)))
    except Exception as iasf:
        await interaction.response.send_message(f'{iasf}')


@bot.tree.command(name='sync', description='sync')
async def deferr(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=False)
    await asyncio.sleep(9)
    await bot.tree.sync()


@bot.tree.command(name='pickrate', description='ваши герои за n игр')
@app_commands.describe(amount='количество игр')
async def pr(interaction: discord.Interaction, amount: int):
    try:
        id = get_id(interaction)
        await interaction.response.defer(thinking=True, ephemeral=False)
        await asyncio.sleep(10)
        get_pick_rate(amount, id)
        nd = NumDeclination()
        await interaction.followup.send(
            f'Вот каких героев ты пикал за последние {amount} {nd.declinate(amount, ["игра", "игры", "игр"]).word}',
            file=discord.File('result.png'))
        os.remove('result.png')
    except Exception as iasf:
        await interaction.response.send_message(f'{iasf}')


@bot.tree.command(name='abilities', description='раскачка за последнию игру')
async def gau(interaction: discord.Interaction):
    try:
        await interaction.response.defer(thinking=True, ephemeral=False)
        await asyncio.sleep(10)
        id = get_id(interaction)
        abils = get_ability_upgrades(id)
        p = ''
        for s in abils:
            y = list(s.values())
            y[0].append('талант')
            p = p + f'{str(y[0][0])}: {y[1]}\n'
        await interaction.followup.send(p)
    except Exception as iasf:
        await interaction.response.send_message(f'{iasf}')


@bot.tree.command(name='регистрация')
@app_commands.describe(id='ваш steam id')
async def sid(interaction: discord.Interaction, id: int):
    if check_steam_id(id):
        await interaction.response.defer(thinking=True, ephemeral=True)
        await asyncio.sleep(3)
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS id (
            discordid TEXT,
            steamid   INTEGER
        );
        ''')
        cursor.execute('SELECT * FROM id')
        eeds = cursor.fetchall()
        eeds1 = []
        for s in eeds:
            eeds1.append(s[0])
        print(eeds1)
        if str(interaction.user.id) not in eeds1:
            cursor.execute('INSERT INTO id (discordid, steamid) VALUES(?, ?)',
                           (interaction.user.id, id))
            print('created')
        cursor.execute('UPDATE id SET steamid = ? WHERE discordid = ?',
                       (id, interaction.user.id))
        print(eeds, id, interaction.user.id)
        connection.commit()
        connection.close()
        if str(interaction.user.id) not in eeds1:
            await interaction.followup.send('ваш айди записан в базу данных')
        if str(interaction.user.id) in eeds1:
            await interaction.followup.send('ваши данные обновлены')
    else:
        await interaction.response.defer(thinking=True, ephemeral=False)
        await asyncio.sleep(0)
        await interaction.followup.send('такого айди нет!')


@bot.tree.command(name='match-info', description=' статистика за матч')
async def gmi(interaction: discord.Interaction):
    try:
        await interaction.response.defer(thinking=True, ephemeral=False)
        await asyncio.sleep(10)
        id = get_id(interaction)
        info = get_match_info(id)
        d = ''
        for s in info:
            t = list(s.values())
            g = ''
            if 'empty' in t[4]:
                t[4].remove('empty')
            for s in t[4]:
                if g == '':
                    g = g + s
                else:
                    g = g + ' / ' + s
            d = d + f'------------------------\n{t[0]}\n{t[1]}/{t[2]}/{t[3]}\n{g}\n'
        await interaction.followup.send(d)
    except Exception as iasf:
        await interaction.response.send_message(f'{iasf}')


def get_id(interaction: discord.Interaction):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS id (
        discordid TEXT,
        steamid   INTEGER
    );
    ''')
    cursor.execute('SELECT * FROM id')
    eeds = cursor.fetchall()
    connection.commit()
    connection.close()
    aboba = None
    for s in eeds:
        print(s[0], s[1], interaction.user.id)
        if int(s[0]) == int(interaction.user.id):
            aboba = s[1]
    print(aboba)
    return aboba


TOKEN = "SECRET"

bot.run(TOKEN)
