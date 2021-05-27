from discord.ext.commands.errors import CommandInvokeError, CommandNotFound
import requests,os,json,discord, marklib
from discord.ext import commands, tasks
from bs4 import BeautifulSoup as scraper
LAST_UPDATED = 0.0
REFRESH_TIME = 5
info={}

FEEDURL='https://feeds.feedburner.com/ndtvnews-latest'

def newsembed(data):
    embed = discord.Embed(title='R.O.C.E News', color=0x03f8fc)
    embed.set_image(url=data[4])
    embed.add_field(name=data[0], value=data[3], inline=False)
    embed.add_field(name='Sources:', value='[Read More]({})'.format(data[1]))
    embed.set_footer(text=data[2])
    return embed

def invite_embed():
    embed = discord.Embed(title='R.O.C.E Invite',
                          url='https://discord.com/api/oauth2/authorize?client_id=847457384078114857&permissions=60480&scope=bot',
                          description='Invite R.O.C.E on your server.')
    return embed

def source_embed():
    source_code = 'https://github.com/0x0is1/R.O.C.E-MarkIII'
    embed = discord.Embed(title='R.O.C.E Source code',
                          url=source_code,
                          description='Get R.O.C.E Source Code.')
    return embed

def register_text_channel(channel_id, status, regkey):
    global info
    activation_info = json.load(open('info.json', 'r'))
    if regkey == 'reg':
        activation_info[str(channel_id)] = str(status)
    if regkey == 'dereg':
        activation_info.pop(str(channel_id))
    
    with open('info.json', 'w') as filename:
        json.dump(activation_info, filename)
    info = json.load(open('info.json', 'r'))

def help_embed():
    embed = discord.Embed(title="Rational Operative Communication Entity", color=0x03f8fc)
    embed.add_field(
        name="Description:", value="This bot is designed for NEWS distribution over discord servers.", inline=False)
    embed.add_field(
        name="**Commands:**\n", value="`enable` : Command used for enabling news bot in this channel. \n `disable` : Command used for disabling news bot in this channel.", inline=False)
    embed.add_field(
        name="Invite: ", value="You can get invite link by typing `invite`")
    embed.add_field(
        name="Source: ", value="You can get source code by typing `source`")
    embed.add_field(
        name="Credits: ", value="You can get credits info by typing `credits`")
    return embed

def set_status_res_emb(status):
    embed = discord.Embed(color=0x03f8fc)
    embed.add_field(name='Status',
                    value='`{}`'.format(status), inline=False)
    return embed

bot = commands.Bot(command_prefix='!!')
bot.remove_command('help')

@bot.command(name="help", description="Returns all commands available")
async def help(ctx):
    embed = help_embed()
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    global info
    info = json.load(open('info.json', 'r'))
    print('Bot status: Online.')
    main_fun.start()

@tasks.loop(seconds=REFRESH_TIME)
async def main_fun():
    global LAST_UPDATED
    global info
    response=requests.get(FEEDURL)
    soup=scraper(response.content, 'html.parser')
    items=soup.find_all('item')
    channel_ids = list(info.keys())    
    data = marklib.newsgen(list(reversed(items)), LAST_UPDATED)
    for channel_id in channel_ids:
        status=info[channel_id]
        if status == 'ON':
            for i in data[0]:
                if not None in i:
                    embed = newsembed(i)
                    channel_obj = bot.get_channel(int(channel_id))
                    await channel_obj.send(embed=embed)
    LAST_UPDATED = data[1]

@bot.command()
async def deregister(ctx):
    channel_id = ctx.message.channel.id
    channels = json.load(open('info.json', 'r'))[0]
    channel_ids = list(channels.keys())
    if str(channel_id) in channel_ids:
        register_text_channel(str(channel_id), '', 'dereg')
        embed = discord.Embed(color=0x03f8fc)
        embed.add_field(name='Info: ',
                        value='This channel is no more subscribed for R.O.C.E \n Use `enable` or `disable` commands to resubscribe.', inline=False)
        await ctx.send(embed=embed)


@bot.command()
async def source(ctx):
    embed = source_embed()
    await ctx.send(embed=embed)

@bot.command()
async def invite(ctx):
    embed = invite_embed()
    await ctx.send(embed=embed)

@bot.command()
async def credits(ctx):
    embed = discord.Embed(
        title="R.O.C.E: \n Rational Operative Communication Entity", color=0x03f8fc)
    embed.add_field(name='Developed by ', value='0x0is1', inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send('Pong! `{}ms`'.format(round(bot.latency * 1000)))

@bot.command()
async def enable(ctx):
    channel_id = ctx.message.channel.id
    register_text_channel(channel_id, 'ON', 'reg')
    await ctx.message.add_reaction('✅')

@bot.command()
async def disable(ctx):
    channel_id = ctx.message.channel.id
    register_text_channel(channel_id, 'OFF', 'reg')
    await ctx.message.add_reaction('✅')

@deregister.error
async def enable_error(ctx, error):
    await ctx.send('`Access Denied.` \n Channel is not registered previously. \n use `enable` or `disable` command to register.')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send('`Unknown command` \n Please use right command to operate. `help` for commands details.')
    if isinstance(error, CommandInvokeError):
        return

token=os.environ.get('EXPERIMENTAL_BOT_TOKEN')
bot.run(token)
