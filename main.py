import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv 
""" using the dotenv library to load the .env file we can also use decouple library as both of these
provide more features for managing different configurations compared to the os library. """

# Load environment variables from .env file
load_dotenv()

intents = discord.Intents.default()  # Intents specify specific events and data that we want our bot to have access to
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def helpme(ctx):
    embed = discord.Embed(
        title="Bot Commands",
        color=discord.Color.blue(),
        description="Here are the available bot commands:"
    )

    embed.add_field(name="Pomodoro Timer", value="!startpomodoro - Start a Pomodoro timer\n!timeleft - Time to carry on work\n!pausepomodoro - Pause the Pomodoro timer\n!resetpomodoro - Reset the Pomodoro timer", inline=False)

    embed.add_field(name="Goals", value="!setgoal [name] [description] - Set a new goal\n!listgoals - List your goals\n!updategoal [name] [new description] - Update a goal\n!deletegoal [name] - Delete a goal", inline=False)

    embed.add_field(name="Greeting", value="The bot will greet new members automatically.", inline=False)

    await ctx.send(embed=embed)

# Define Pomodoro timer variables
work_time = 25 * 60  # 25 minutes (in seconds)
break_time = 5 * 60  # 5 minutes (in seconds)
pomodoro_active = False
timer_task = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Variable to store the time the Pomodoro started
pomodoro_start_time = None

@bot.command()
async def startpomodoro(ctx):
    global pomodoro_active, timer_task, pomodoro_start_time

    if not pomodoro_active:
        pomodoro_active = True
        pomodoro_start_time = ctx.message.created_at
        await ctx.send("Pomodoro timer started! Work for 25 minutes.")
        timer_task = asyncio.create_task(run_pomodoro(ctx))
    else:
        await ctx.send("A Pomodoro session is already in progress.")

@bot.command()
async def timeleft(ctx):
    global pomodoro_active, pomodoro_start_time, work_time

    if pomodoro_active:
        current_time = ctx.message.created_at
        elapsed_time = (current_time - pomodoro_start_time).total_seconds()
        remaining_time = max(work_time - elapsed_time, 0)

        minutes, seconds = divmod(int(remaining_time), 60)
        await ctx.send(f"{minutes} mins left. Keep it up!")
    else:
        await ctx.send("No active Pomodoro session.")


@bot.command()
async def pausepomodoro(ctx):
    global pomodoro_active, timer_task

    if pomodoro_active:
        pomodoro_active = False
        timer_task.cancel()
        await ctx.send("Pomodoro timer paused.")
    else:
        await ctx.send("There is no active Pomodoro session to pause.")

@bot.command()
async def resetpomodoro(ctx):
    global pomodoro_active, timer_task

    if pomodoro_active:
        pomodoro_active = False
        timer_task.cancel()
    await ctx.send("Pomodoro timer reset.")
    
async def run_pomodoro(ctx):
    await asyncio.sleep(work_time)
    if pomodoro_active:
        await ctx.send("Great job! Time for a 5-minute break.")
        await asyncio.sleep(break_time)
        if pomodoro_active:
            await ctx.send("Break's over! Start another Pomodoro or use !pausepomodoro to pause the timer.")
            pomodoro_active = False

# Dictionary to store user-specific goals
user_goals = {}

@bot.command()
async def setgoal(ctx, goal_name, goal_description):
    user_id = ctx.author.id

    if user_id not in user_goals:
        user_goals[user_id] = {}

    user_goals[user_id][goal_name] = goal_description
    await ctx.send(f'Goal "{goal_name}" set: {goal_description}')

@bot.command()
async def listgoals(ctx):
    user_id = ctx.author.id

    if user_id in user_goals:
        goals = user_goals[user_id]
        if not goals:
            await ctx.send('You have no goals set.')
        else:
            goal_list = "\n".join([f"**{goal_name}**: {goal_description}" for goal_name, goal_description in goals.items()])
            await ctx.send(f'Your goals:\n{goal_list}')
    else:
        await ctx.send('You have no goals set.')

@bot.command()
async def updategoal(ctx, goal_name, updated_description):
    user_id = ctx.author.id

    if user_id in user_goals and goal_name in user_goals[user_id]:
        user_goals[user_id][goal_name] = updated_description
        await ctx.send(f'Goal "{goal_name}" updated: {updated_description}')
    else:
        await ctx.send(f'Goal "{goal_name}" not found.')

@bot.command()
async def deletegoal(ctx, goal_name):
    user_id = ctx.author.id

    if user_id in user_goals and goal_name in user_goals[user_id]:
        del user_goals[user_id][goal_name]
        await ctx.send(f'Goal "{goal_name}" deleted.')
    else:
        await ctx.send(f'Goal "{goal_name}" not found.')

@bot.event
async def on_member_join(member):
    # Customize the welcome message as desired
    welcome_message = f"Welcome to the server, {member.mention}! Feel free to introduce yourself and enjoy your stay."

    # Send the welcome message to a specific channel (replace 'welcome_channel_id' with the actual channel ID)
    welcome_channel_id = 1234567890
    welcome_channel = member.guild.get_channel(welcome_channel_id)

    if welcome_channel:
        await welcome_channel.send(welcome_message)

bot.run(os.getenv('TOKEN'))