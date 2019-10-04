# runbot
A discord bot which polls speedrun.com for runs and posts them via discord webhooks.

This program is meant to be run periodically (via cron for example)

There are two files used.  One is a configuration file in JSON.

The other file (specified in the config) stores the state for the bot of runs it's already published.

You will need to create a discord webhook for the channel you want the program to post to.

There are likely numerous ways to achieve this goal, this happens to be how I did it.  Feel free to adapt it to your liking.

Requires python 3.4+

Dependencies: discord_webhook and requests.
