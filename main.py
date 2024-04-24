import dota2api
import discord
import sqlite3
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from numdeclination import NumDeclination

api_key = 'D9C572EBE4B884D5711B330DECFC6888'
api = dota2api.Initialise(api_key, raw_mode=True)

id_player = 1100907863
count_games = 20


def get_hero_id(name_hero):
    heroes = api.get_heroes()
    for hero in heroes['heroes']:
        if name_hero == hero['localized_name']:
            return hero['id']

def check_steam_id(id):
    try:
        api.get_match_history(id)
    except dota2api.src.exceptions.APIError:
        return False
    return True

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
    eeds1 = []
    aboba = None
    for s in eeds:
        print(s[0], s[1], interaction.user.id)
        if int(s[0]) == int(interaction.user.id):
            aboba = s[1]
    print(aboba)

def get_hero_name(id_hero):
    heroes = api.get_heroes()
    for hero in heroes['heroes']:
        if id_hero == hero['id']:
            return hero['localized_name']


def get_gero_url(id_hero):
    heroes = api.get_heroes()
    for hero in heroes['heroes']:
        if id_hero == hero['id']:
            return hero['url_large_portrait']


def get_win_rate(count_games, id_player, game_type='all'):
    # выводит процент побед за последние n игр
    # all - все виды игр
    # 0 - анранкет
    # 7 ранкет
    # 8 solo mid 1 vs 1
    win = 0
    games = api.get_match_history(id_player)['matches'][:count_games]
    for game in games:
        if game_type == 'all':
            match_id = game['match_id']
            game_details = api.get_match_details(match_id)
            for player in game_details['players']:
                if id_player == player['account_id']:
                    if player['team_number'] == 0 and game_details['radiant_win']:
                        win += 1
                    elif player['team_number'] == 1 and not game_details['radiant_win']:
                        win += 1
        else:
            if game_type == game['lobby_type']:
                match_id = game['match_id']
                game_details = api.get_match_details(match_id)
                for player in game_details['players']:
                    if id_player == player['account_id']:
                        if player['team_number'] == 0 and game_details['radiant_win']:
                            win += 1
                        elif player['team_number'] == 1 and not game_details['radiant_win']:
                            win += 1
    return f"{win / count_games * 100} %"


def get_pick_rate(count_games, id_player):  # выводит пикрейт героев за поледние n игр
    games = api.get_match_history(id_player)['matches'][:count_games]
    pick_dict = {}
    for game in games:
        match_id = game['match_id']
        game_details = api.get_match_details(match_id)
        for player in game_details['players']:
            if id_player == player['account_id']:
                try:
                    pick_dict[get_gero_url(player['hero_id'])] += 1
                except KeyError:
                    pick_dict[get_gero_url(player['hero_id'])] = 1
    result = Image.new('RGB', (1075, 625), 'black')
    n_x, n_y = 0, 0
    font = ImageFont.truetype("arial.ttf", size=24)
    draw = ImageDraw.Draw(result)
    for key, value in pick_dict.items():
        responce = requests.get(key, stream=True).raw
        image = Image.open(responce)
        result.paste(image, (5 + 210 * n_x, 5 + 150 * n_y))
        nd = NumDeclination()
        text = nd.declinate(value, ['игра', 'игры', 'игр']).word
        draw.text((5 + 210 * n_x + 92, 120 + 150 * n_y), f"{value} {text}", font=font)
        n_x += 1
        if n_x == 5:
            n_x = 0
            n_y += 1
    if n_y != 5:
        n_y += 1
        result = result.crop((0, 0, 1075, n_y * 150 + 5))
    result.save('result.png')


def get_ability_upgrades(id_player):  # выводит раскачку скилов за последню игру
    match_id = api.get_match_history(id_player)['matches'][0]['match_id']
    game_details = api.get_match_details(match_id)
    skills_list = []
    for player in game_details['players']:
        if id_player == player['account_id']:
            abilityes = player['ability_upgrades']
            break
    with open('jsons/abilities.json') as file:
        data = json.load(file)
        for ability in abilityes:
            skills_list.append(
                {'name': [skill['name'] for skill in data['abilities'] if skill['id'] == str(ability['ability'])],
                 'time': f"{ability['time'] // 60}:{ability['time'] % 60}"})
    return skills_list


def get_player_items(list_id):
    with open('jsons/items.json') as items:
        data = json.load(items)
    list_items = []
    for item in data['items']:
        if item['id'] in list_id:
            list_items.append(item['name'])
    return list_items


def get_match_info(match_id, player_id=False):
    if player_id:
        match_id = api.get_match_history(id)['matches'][0]['match_id']
    game_details = api.get_match_details(match_id)
    info = []
    for player in game_details['players']:
        list_id = [player['item_0'], player['item_1'], player['item_2'], player['item_3'],
                   player['item_4'], player['item_5']]
        list_items = get_player_items(list_id)
        info.append({'hero': get_hero_name(player['hero_id']), 'kills': player['kills'], 'deaths': player['deaths'],
                     'assists': player['assists'], 'game_items': list_items})
    return info
