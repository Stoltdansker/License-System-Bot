import discord
from discord.ext import commands
import json
import logging
import os

# Replace with your actual bot token
TOKEN = 'YOUR-BOT-TOKEN-HERE'

# Set up bot intents
intents = discord.Intents.default()
intents.members = True  
intents.guilds = True  
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables for channel and role IDs
log_channel_id = None  
admin_role_id = None  

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define config folder path and constants
CONFIG_FOLDER = 'config'
LICENSES_FILE = 'licenses.json'  # Constant for the licenses file

def load_config():
    """Load admin role ID from admins.json."""
    global admin_role_id
    try:
        with open(os.path.join(CONFIG_FOLDER, 'admins.json'), 'r') as file:
            data = json.load(file)
            admin_role_id = data['admin_role_id']
    except FileNotFoundError:
        logger.error("Admins file not found. Please create 'admins.json' with the required data.")

# Load configuration on startup
load_config()

def load_json(file_name):
    """Load JSON data from a file and return it."""
    try:
        with open(os.path.join(CONFIG_FOLDER, file_name), 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.warning(f"File {file_name} not found, returning empty data.")
        return {}

def save_json(file_name, data):
    """Save data to a JSON file."""
    with open(os.path.join(CONFIG_FOLDER, file_name), 'w') as file:
        json.dump(data, file, indent=4)

# Load used keys and log channel data
used_keys = set(load_json('used_keys.json').get('keys', []))
log_channel_id = load_json('log_channel.json').get('channel_id')

async def log_action(action_type: str, details: str, user: discord.User):
    """Log actions in the log channel and console."""
    log_message = f"{action_type} | {details} | Action performed by: {user.name}"
    logger.info(log_message)  # Log to console

    if log_channel_id is not None:
        channel = bot.get_channel(log_channel_id)
        if channel:
            embed = discord.Embed(
                title=f"Log: {action_type}",
                description=details,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Action performed by: {user.name}")
            await channel.send(embed=embed)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    logger.info(f'Logged in as {bot.user}')

@bot.slash_command(name="clear", description="Clear a specified number of messages.")
async def clear(interaction: discord.Interaction, amount: int):
    """Clear messages in the channel, requires admin role."""
    if admin_role_id is None or not any(role.id == int(admin_role_id) for role in interaction.user.roles):
        await interaction.response.send_message("You do not have permission to clear the chat.")
        return

    if amount < 1:
        await interaction.response.send_message("You must delete at least one message.", ephemeral=True)
        return

    deleted = await interaction.channel.purge(limit=amount + 1)  # +1 to include the command message
    await interaction.response.send_message(f'Deleted {len(deleted) - 1} messages.', ephemeral=True)

@bot.slash_command(name="setup_log_channel", description="Set the log channel for the bot.")
async def setup_log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    """Set the log channel for logging actions."""
    global log_channel_id
    log_channel_id = channel.id
    save_json('log_channel.json', {"channel_id": log_channel_id})
    await interaction.response.send_message(f'Log channel set to {channel.mention}.')

@bot.slash_command(name="add_license", description="Add a new license key with a role ID.")
async def add_license(interaction: discord.Interaction, key: str, role_id: str):
    """Add a new license key, requires admin role."""
    if admin_role_id is None or not any(role.id == int(admin_role_id) for role in interaction.user.roles):
        await interaction.response.send_message("You do not have permission to add a license.")
        return
    
    keys = load_json(LICENSES_FILE).get('keys', [])
    
    # Check if the key already exists
    if any(item['key'] == key for item in keys):
        await interaction.response.send_message(f'License key {key} already exists.')
        return
    
    # Create a new license entry and save it
    new_license = {"key": key, "role_id": role_id}
    keys.append(new_license)
    save_json(LICENSES_FILE, {"keys": keys})

    # Log the action
    await log_action("License Added", f"License key {key} added with role ID {role_id}.", interaction.user)
    await interaction.response.send_message(f'License key {key} added with role ID {role_id}.')

@bot.slash_command(name="remove_license", description="Remove an existing license key.")
async def remove_license(interaction: discord.Interaction, key: str):
    """Remove an existing license key, requires admin role."""
    if admin_role_id is None or not any(role.id == int(admin_role_id) for role in interaction.user.roles):
        await interaction.response.send_message("You do not have permission to remove a license.")
        return

    keys = load_json(LICENSES_FILE).get('keys', [])
    if any(item['key'] == key for item in keys):
        keys = [item for item in keys if item['key'] != key]  # Remove the key
        save_json(LICENSES_FILE, {"keys": keys})
        
        # Log the action
        await log_action("License Removed", f"License key {key} removed.", interaction.user)
        await interaction.response.send_message(f'License key {key} removed.')
    else:
        await interaction.response.send_message(f'License key {key} does not exist.')

@bot.slash_command(name="redeem", description="Redeem a valid license key.")
async def redeem(interaction: discord.Interaction, key: str):
    """Redeem a valid license key and assign the corresponding role."""
    keys = load_json(LICENSES_FILE).get('keys', [])
    license_data = next((item for item in keys if item['key'] == key), None)
    
    if license_data:
        if key not in used_keys:
            used_keys.add(key)
            save_json('used_keys.json', {"keys": list(used_keys)})

            # Get the role ID associated with the license
            role_id = int(license_data["role_id"])
            role = interaction.guild.get_role(role_id)

            if role:
                # Assign the role to the user
                await interaction.user.add_roles(role)
                
                # Log the action
                await log_action("License Redeemed", f"License key {key} redeemed. Role ID {role_id} assigned.", interaction.user)

                # Create an embed for the redeem message
                embed = discord.Embed(
                    title="License Redeemed!",
                    description=f'You have successfully redeemed the license key **{key}** and been given the role: <@&{role_id}>.',
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f'License key {key} redeemed, but the role with ID {role_id} does not exist.')
        else:
            await interaction.response.send_message(f'License key {key} has already been redeemed.')
    else:
        await interaction.response.send_message(f'License key {key} does not exist.')

# Run the bot
bot.run(TOKEN)