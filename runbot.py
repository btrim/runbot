#!/usr/bin/env python3

import requests
import json
import datetime
import argparse

from time import sleep
from discord_webhook import DiscordWebhook, DiscordEmbed
from types import SimpleNamespace as Namespace


   

def get_runs(url):
    r = requests.get(url)
    runs = json.loads(r.text, object_hook=lambda d: Namespace(**d))

    runs.data.reverse()
    return runs.data






def get_users(run):
    users_str = ''
    users = []
    for u in run.players.data:
      #  r = requests.get(u.uri)
      #  ux = json.loads(r.text, object_hook=lambda d: Namespace(**d))
        if users_str == '':
            users_str = u.names.international
        else:
            users_str = users_str + ", " + u.names.international

        users.append(u)

    return (users_str, users)

def get_game(run):
    return (run.game.data.names.international, run.game.data)

def get_category(run):
    return (run.category.data.name, run.category.data)

def generate_webhooks(webhook_url, webhook_name, runs):
    for run in runs:
        (users_str, users) = get_users(run)
        (game_name, game) = get_game(run)
        (cat_name, category) = get_category(run)
        has_rt = run.times.realtime is not None
        tm = str(datetime.timedelta(seconds=run.times.primary_t))
        has_igt = run.times.ingame is not None and run.times.ingame != run.times.primary
        igt = str(datetime.timedelta(seconds=run.times.ingame_t))
        url = run.weblink
        print ('{}: {} - {} - {} \n {}'.format(users,game,category,tm,url))

        webhook = DiscordWebhook(url=webhook_url, username=webhook_name)
        cover_art = getattr(game.assets, 'cover-small').uri
        embed = DiscordEmbed(title='Game', description=game_name)
        embed.set_thumbnail(url=cover_art)
        for user in users:
            embed.add_embed_field(name='Runner', value=user.names.international)
        embed.set_author(name='View on speedrun.com',url=run.weblink)
        embed.set_timestamp(run.submitted)
        embed.add_embed_field(name='Category', value=cat_name, url=category.weblink)
        embed.add_embed_field(name='Time', value=tm, url=run.weblink)
        if has_igt:
            embed.add_embed_field(name='In-game Time', value=igt, url=run.weblink)
        embed.set_footer(text='Submitted ')
        webhook.add_embed(embed)
        sleep(5)
        webhook.execute()

def print_runs(runs):
    for run in runs:
        print('{} - {} - {}'.format(run.game.data.names.international,run.players, run.category.data.name))

def read_runfile(filename):
    with open(filename) as json_file:
        old_runs = json.load(json_file)
        return old_runs

def read_config(filename):
    with open(filename) as json_file:
        return json.load(json_file)

def write_runfile(old_runs, filename):
    with open(filename, 'w') as json_file:
        json.dump(old_runs, json_file)

def get_games(series):
    r = requests.get('https://www.speedrun.com/api/v1/series/{}/games'.format(series))
    ux = json.loads(r.text, object_hook=lambda d: Namespace(**d))
    return ux.data



def main():
    parser = argparse.ArgumentParser(description='Update a discord channel with runs from speedrun.com',fromfile_prefix_chars='@')
    parser.add_argument('--config', dest='config', help='Path to json configuration file')


    args = parser.parse_args()
    if args.config is None:
        parser.print_help()
        exit(1)



    config = read_config(args.config)

    webhook_url = config['webhook']
    webhook_name = config['name']
    api_url = 'https://www.speedrun.com/api/v1/runs?embed=game,category,players&'+'&'.join(config['params'])

    print(webhook_url + '\n')
    print(webhook_name + '\n')
    print(api_url + '\n')

    series = None
    try:
        series = config['series']
    except KeyError:
        pass

    raw_runs = []
    if series is not None and series is not "":
        games = get_games(series) # /series/{series}/games
        for game in games:
            raw_runs.extend(get_runs(api_url+'&game='+game.id))
            sleep(5)
    else:
        raw_runs.extend(get_runs(api_url))

    old_runs = []
    try:
        old_runs.extend(read_runfile(config['runfile']))
    except:
        pass

    
    runs = list(filter(lambda r: r.id not in old_runs, raw_runs))

    print_runs(runs)
    #generate_webhooks(webhook_url, webhook_name, runs)

    old_runs.extend(run.id for run in runs)

    write_runfile(old_runs, config['runfile'])
 

if __name__ == "__main__":
    main()
