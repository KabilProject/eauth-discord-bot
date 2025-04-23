import interactions
import hashlib
import requests
import json
import string
import random
import asyncio
from interactions import Embed, slash_command, SlashCommandOption, OptionType, SlashCommandChoice

# Required Configuration
BOT_TOKEN = "" # Your Discord bot token here
ADMIN_KEY = "" # Your Eauth admin key here
APP_SECRET = "" # Your Eauth application secret here
REQUIRED_ROLE_ID = ROLEIDHERE # Your Discord Role ID Here 

ERROR_INVALID_REQUEST = "Invalid API request format or parameters."
ERROR_MISCONFIG = "Server misconfiguration detected."
ERROR_NON_PREMIUM = "Feature is limited to premium users."
ERROR_UNAUTHORIZED = "Unauthorized request. Check your credentials."
ERROR_MISSING_ROLE = "You do not have the required role to use this command."

bot = interactions.Client(token=BOT_TOKEN)

def hash_sha512(input_string):
    return hashlib.sha512(input_string.encode('utf-8')).hexdigest()

def generate_auth_header(message, secret):
    return hash_sha512(secret + message)

def random_string(length=18):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def create_response_embed(title, description):
    embed = Embed(title=title, description=description)
    embed.set_footer(text="EAuth Discord License System | eauth.us.to")
    return embed

async def make_api_request(request_data):
    try:
        response = requests.post(
            'https://eauth.us.to/api/1.2/admin.php',
            headers={
                "Content-Type": "application/json",
                "User-Agent": generate_auth_header(request_data, APP_SECRET)
            },
            data=request_data,
            timeout=10
        )
        
        res = json.loads(response.text)
        message = res['message']
        auth_header = response.headers.get('Eauth')

        if message not in ['invalid_request', 'misconfiguration', 'nonpremium', 'unauthorized']:
            if auth_header != generate_auth_header(response.text, APP_SECRET):
                return {'message': "Verification failed"}
        
        return res
    except Exception as e:
        return {'message': f"API request failed: {str(e)}"}

async def verify_user_permissions(ctx):
    member_roles = [role.id for role in ctx.author.roles]
    if REQUIRED_ROLE_ID not in member_roles:
        await ctx.send(embed=create_response_embed("Access Denied", ERROR_MISSING_ROLE), ephemeral=True)
        return False
    return True

@slash_command(name="online", description="View currently online users")
async def cmd_online(ctx):
    if not await verify_user_permissions(ctx):
        return
    
    request_data = {
        'type': 'online',
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    if isinstance(response['message'], str):
        await ctx.send(embed=create_response_embed("🟢 Online Users", response['message']))
    else:
        await ctx.send(embed=create_response_embed("🟢 Online Users", json.dumps(response['message'], indent=2)))

@slash_command(name="keys_list", description="List all license keys")
async def cmd_keys_list(ctx):
    if not await verify_user_permissions(ctx):
        return
    
    request_data = {
        'type': 'keys_list',
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    if isinstance(response['message'], str):
        await ctx.send(embed=create_response_embed("🔑 License Keys", response['message']))
    else:
        await ctx.send(embed=create_response_embed("🔑 License Keys", json.dumps(response['message'], indent=2)))

@slash_command(
    name="genkey",
    description="Generate license key",
    options=[
        SlashCommandOption(
            name="length",
            description="Key length (9-16)",
            type=OptionType.STRING,
            required=True
        ),
        SlashCommandOption(
            name="rank",
            description="Access rank",
            type=OptionType.STRING,
            required=True
        ),
        SlashCommandOption(
            name="expire",
            description="Expiration period",
            type=OptionType.STRING,
            required=True,
            choices=[
                SlashCommandChoice(name="Day", value="Day"),
                SlashCommandChoice(name="Week", value="Week"),
                SlashCommandChoice(name="Month", value="Month"),
                SlashCommandChoice(name="Year", value="Year"),
                SlashCommandChoice(name="Lifetime", value="Lifetime")
            ]
        ),
        SlashCommandOption(
            name="duration",
            description="Duration",
            type=OptionType.INTEGER,
            required=True
        ),
        SlashCommandOption(
            name="prefix",
            description="Custom prefix",
            type=OptionType.STRING,
            required=False
        )
    ]
)
async def cmd_genkey(ctx, length: str, rank: str, expire: str, duration: int, prefix: str = ""):
    if not await verify_user_permissions(ctx):
        return
    
    if duration < 0:
        await ctx.send(embed=create_response_embed("⚠️ Error", "Duration must be a positive number"), ephemeral=True)
        return
    
    if expire == "Lifetime":
        expire = "Lifetime"
    else:
        expire = f"{duration} {expire}"
    
    request_data = {
        'type': 'genkey',
        'length': length,
        'rank': rank,
        'expire': expire,
        'prefix': prefix,
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    await ctx.send(embed=create_response_embed("🔐 Key Generated", response['message']))

@slash_command(
    name="delkey",
    description="Delete license key",
    options=[
        SlashCommandOption(
            name="key",
            description="Key to delete",
            type=OptionType.STRING,
            required=True
        )
    ]
)
async def cmd_delkey(ctx, key: str):
    if not await verify_user_permissions(ctx):
        return
    
    request_data = {
        'type': 'delkey',
        'key': key,
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    await ctx.send(embed=create_response_embed("❌ Key Deleted", response['message']))

@slash_command(
    name="keydata",
    description="Get key information",
    options=[
        SlashCommandOption(
            name="key",
            description="Key to inspect",
            type=OptionType.STRING,
            required=True
        )
    ]
)
async def cmd_keydata(ctx, key: str):
    if not await verify_user_permissions(ctx):
        return
    
    request_data = {
        'type': 'keydata',
        'key': key,
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    
    if response.get('message') == "success":
        details = (
            f"- Key: {key}\n"
            f"- Rank: {response.get('rank', 'N/A')}\n"
            f"- Duration: {response.get('expire_date', 'N/A')}\n"
            f"- Create Date: {response.get('create_date', 'N/A')}\n"
            f"- Used: {response.get('used', 'N/A')}\n"
            f"- Used date: {response.get('used_date', 'N/A')}"
        )
        await ctx.send(embed=create_response_embed("🔍 Key Details", details))
    else:
        await ctx.send(embed=create_response_embed("⚠️ Error", response.get('message', 'Unknown error')))

@slash_command(
    name="adduser",
    description="Create new user",
    options=[
        SlashCommandOption(
            name="username",
            description="Account username",
            type=OptionType.STRING,
            required=True
        ),
        SlashCommandOption(
            name="password",
            description="Account password",
            type=OptionType.STRING,
            required=True
        ),
        SlashCommandOption(
            name="rank",
            description="Access rank",
            type=OptionType.STRING,
            required=True
        ),
        SlashCommandOption(
            name="expire",
            description="Expiration period",
            type=OptionType.STRING,
            required=True
        )
    ]
)
async def cmd_adduser(ctx, username: str, password: str, rank: str, expire: str):
    if not await verify_user_permissions(ctx):
        return
    
    request_data = {
        'type': 'adduser',
        'username': username,
        'password': password,
        'rank': rank,
        'expire': expire,
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    await ctx.send(embed=create_response_embed("👤 User Created", response['message']))

@slash_command(
    name="deluser",
    description="Delete user",
    options=[
        SlashCommandOption(
            name="username",
            description="Account to delete",
            type=OptionType.STRING,
            required=True
        )
    ]
)
async def cmd_deluser(ctx, username: str):
    if not await verify_user_permissions(ctx):
        return
    
    request_data = {
        'type': 'deluser',
        'username': username,
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    await ctx.send(embed=create_response_embed("🗑️ User Deleted", response['message']))

@slash_command(
    name="userdata",
    description="Get user details",
    options=[
        SlashCommandOption(
            name="username",
            description="Account to inspect",
            type=OptionType.STRING,
            required=True
        )
    ]
)
async def cmd_userdata(ctx, username: str):
    if not await verify_user_permissions(ctx):
        return
    
    request_data = {
        'type': 'userdata',
        'username': username,
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    
    if response.get('message') == "success":
        details = (
            f"- Username: {username}\n"
            f"- Rank: {response.get('rank', 'N/A')}\n"
            f"- Create Date: {response.get('create_date', 'N/A')}\n"
            f"- Last Login Date: {response.get('last_login_date', 'N/A')}\n"
            f"- Duration: {response.get('expire_date', 'N/A')}\n"
            f"- HWID: {response.get('hwid', 'N/A')}"
        )
        await ctx.send(embed=create_response_embed("🔍 User Details", details))
    else:
        await ctx.send(embed=create_response_embed("⚠️ Error", response.get('message', 'Unknown error')))

@slash_command(
    name="resethwid",
    description="Reset user HWID",
    options=[
        SlashCommandOption(
            name="username",
            description="Account to reset",
            type=OptionType.STRING,
            required=True
        )
    ]
)
async def cmd_resethwid(ctx, username: str):
    if not await verify_user_permissions(ctx):
        return
    
    request_data = {
        'type': 'resethwid',
        'username': username,
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    await ctx.send(embed=create_response_embed("🔄 HWID Reset", response['message']))

@slash_command(
    name="sendkey",
    description="Send key via DM",
    options=[
        SlashCommandOption(
            name="key",
            description="Key to send",
            type=OptionType.STRING,
            required=True
        ),
        SlashCommandOption(
            name="user",
            description="Recipient",
            type=OptionType.USER,
            required=True
        )
    ]
)
async def cmd_sendkey(ctx, key: str, user: interactions.User):
    if not await verify_user_permissions(ctx):
        return
    
    key_check = {
        'type': 'keydata',
        'key': key,
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(key_check))
    
    if response.get('message') != "success":
        await ctx.send(embed=create_response_embed("⚠️ Error", "Invalid key or not found"))
        return
    
    embed = create_response_embed(
        "🎁 License Key Received",
        f"Here's your license key:\n\n- `{key}`\n- Rank: `{response.get('rank', 'N/A')}`\n- Duration: `{response.get('expire_date', 'N/A')}`"
    )
    
    try:
        await user.send(embed=embed)
        await ctx.send(embed=create_response_embed("✅ Success", f"Key successfully sent to {user.mention}"))
    except:
        await ctx.send(embed=create_response_embed("❌ Failed", "Couldn't DM the user. They may have DMs disabled."))

@slash_command(
    name="banuser",
    description="Ban user HWID/IP",
    options=[
        SlashCommandOption(
            name="username",
            description="User to ban",
            type=OptionType.STRING,
            required=True
        )
    ]
)
async def cmd_banuser(ctx, username: str):
    if not await verify_user_permissions(ctx):
        return
    
    request_data = {
        'type': 'banuser',
        'username': username,
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    await ctx.send(embed=create_response_embed("🔨 User Banned", response['message']))

@slash_command(
    name="banid",
    description="Ban a HWID/IP from accessing your app",
    options=[
        SlashCommandOption(
            name="identifier",
            description="The HWID/IP you wish to ban",
            type=OptionType.STRING,
            required=True,
        ),
    ],
)
async def cmd_banid(ctx, identifier: str):
    if not await verify_user_permissions(ctx):
        return
    
    request_data = {
        'type': 'banid',
        'id': identifier,
        'admin_key': ADMIN_KEY,
        'discord_user_id': str(ctx.author.id),
        'pair': random_string()
    }
    
    response = await make_api_request(json.dumps(request_data))
    await ctx.send(embed=create_response_embed("🔨 ID Banned", response['message']))


if __name__ == "__main__":
    bot.start()
