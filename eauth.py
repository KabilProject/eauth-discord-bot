import interactions
import hashlib
import requests
import json
import string
import random

# Required configuration
bot_token = ""  # Your Discord bot token here
admin_key = "" # Your Eauth admin key here
application_secret = "" # Your application secret here

# Advanced configuration
invalid_request_message = "Invalid request!"
misconfiguration_message = "There is a misconfiguration. Ensure that you have correctly configured the Discord bot source code."
nonpremium_message = "The owner's subscription has been expired. Please upgrade @ https://eauth.us.to/#pricing"
unauthorized_message = "You are not allowed to do that!"

bot = interactions.Client(token=bot_token)

def compute_sha512(input_string):
    sha512 = hashlib.sha512()
    sha512.update(input_string.encode('utf-8'))
    return sha512.hexdigest()

def generate_Eauth_header(message, app_secret):
    auth_token = app_secret + message
    return compute_sha512(auth_token)

characters = string.ascii_uppercase + string.ascii_lowercase + string.digits

def generate_random_string(length=18):
    return ''.join(random.choices(characters, k=length))

# Send post request to Eauth
def run_request(request_data):
    response = requests.post('https://eauth.us.to/api/1.2/admin.php',
                             headers={"Content-Type": "application/json", "User-Agent": generate_Eauth_header(request_data, application_secret)},
                             data=request_data)
    
    res = json.loads(response.text)
    message = res['message']

    # Read signature
    Eauth_header = response.headers.get('Eauth')
    if (message != 'invalid_request' and message != 'misconfiguration' and message != 'nonpremium' and message != 'unauthorized'):
        if (Eauth_header != generate_Eauth_header(response.text, application_secret)):
            data = {'message': ":joy:"}
            return json.dumps(data)
    else:
        
        if message != 'invalid_request':
            data = {
        'message': invalid_request_message
        }
        elif message != 'misconfiguration':
            data = {
        'message': misconfiguration_message
        }
        elif message != 'nonpremium':
            data = {
        'message': nonpremium_message
        }
        elif message != 'unauthorized':
            data = {
        'message': unauthorized_message
        }
        return json.dumps(data)
    
    print("\n[!] New outcoming request:\n\n"+ response.text + "\n\n")
    return response.text

@bot.command(
  name="userid",
  description="Displays the user ID",
)
async def userid(ctx: interactions.CommandContext):
  await ctx.send(f"User ID: `{ctx.author.id}`")
  
@bot.command(
  name="online",
  description="Getting list of current online users"
)
async def online(ctx: interactions.CommandContext):
    data = {
        'type': 'online',
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    await ctx.send(data['message'])
    
@bot.command(
  name="keys_list",
  description="Getting list of all keys"
)
async def keys_list(ctx: interactions.CommandContext):
    data = {
        'type': 'keys_list',
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    await ctx.send(data['message'])

@bot.command(
  name="getvar",
  description="Getting value of a server-sided variable",
  options=[
    interactions.Option(
      name="varname",
      description="Your Variable Name",
      type=interactions.OptionType.STRING,
      required=True,
    ),
  ],
)
async def getvar(ctx: interactions.CommandContext, varname: str):
    data = {
        'type': 'getvar',
        'varname': varname,
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    await ctx.send(data['message'])


@bot.command(
  name="genkey",
  description="Generate a new key",
  options=[
    interactions.Option(
      name="length",
      description="Length of the key (9 ~ 16)",
      type=interactions.OptionType.STRING,
      required=True,
    ),
    interactions.Option(
      name="rank",
      description="Rank given to the key",
      type=interactions.OptionType.STRING,
      required=True,
    ),
    interactions.Option(
      name="expire",
      description="Expire duration of the key",
      type=interactions.OptionType.STRING,
      required=True,
    ),
    interactions.Option(
      name="prefix",
      description="Prefix of the key",
      type=interactions.OptionType.STRING,
      required=False,  # Set required to False to make it optional
    ),
  ],
)
async def genkey(ctx: interactions.CommandContext, rank: str, expire: str,
                 length: str, prefix: str = ""):  # Set prefix to an empty string as default value
    data = {
        'type': 'genkey',
        'rank': rank,
        'expire': expire,
        'length': length,
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    await ctx.send(data['message'])

@bot.command(
  name="delkey",
  description="Delete a key",
  options=[
    interactions.Option(
      name="key",
      description="The key you wish to delete",
      type=interactions.OptionType.STRING,
      required=True,
    ),
  ],
)
async def delkey(ctx: interactions.CommandContext, key: str):
    data = {
        'type': 'delkey',
        'key': key,
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    await ctx.send(data['message'])


@bot.command(
  name="delvar",
  description="Delete a variable",
  options=[
    interactions.Option(
      name="varname",
      description="The variable you wish to delete",
      type=interactions.OptionType.STRING,
      required=True,
    ),
  ],
)
async def delvar(ctx: interactions.CommandContext, varname: str):
    data = {
        'type': 'delvar',
        'varname': varname,
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    await ctx.send(data['message'])


@bot.command(
  name="addvar",
  description="Add a variable",
  options=[
    interactions.Option(
      name="varname",
      description="A name your want",
      type=interactions.OptionType.STRING,
      required=True,
    ),
    interactions.Option(
      name="varvalue",
      description="A value your want",
      type=interactions.OptionType.STRING,
      required=True,
    ),
  ],
)
async def addvar(ctx: interactions.CommandContext, varname: str, varvalue: str):
    data = {
        'type': 'addvar',
        'varname': varname,
        'varvalue': varvalue,
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    await ctx.send(data['message'])


@bot.command(
  name="adduser",
  description="Add a new user account",
  options=[
    interactions.Option(
      name="username",
      description="A name given to the user",
      type=interactions.OptionType.STRING,
      required=True,
    ),
    interactions.Option(
      name="password",
      description="Password for the user account",
      type=interactions.OptionType.STRING,
      required=True,
    ),
    interactions.Option(
      name="rank",
      description="Rank given to the user",
      type=interactions.OptionType.STRING,
      required=True,
    ),
    interactions.Option(
      name="expire",
      description="Expire duration of the user account",
      type=interactions.OptionType.STRING,
      required=True,
    ),
  ],
)
async def adduser(ctx: interactions.CommandContext, username: str,
                  password: str, rank: str, expire: str):
    data = {
        'type': 'adduser',
        'username': username,
        'password': password,
        'rank': rank,
        'expire': expire,
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    await ctx.send(data['message'])


@bot.command(
  name="deluser",
  description="Delete a user",
  options=[
    interactions.Option(
      name="username",
      description="The user you wish to delete",
      type=interactions.OptionType.STRING,
      required=True,
    ),
  ],
)
async def deluser(ctx: interactions.CommandContext, username: str):
    data = {
        'type': 'deluser',
        'username': username,
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    await ctx.send(data['message'])


@bot.command(
  name="keydata",
  description="Obtain the properties of a key",
  options=[
    interactions.Option(
      name="key",
      description="Your Key",
      type=interactions.OptionType.STRING,
      required=True,
    ),
  ],
)
async def keydata(ctx: interactions.CommandContext, key: str):
    data = {
        'type': 'keydata',
        'key': key,
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    message = data['message']
    if (message == "success"):
        message = "- Key: " + key + "\n- Rank: " + data['rank'] + "\n- Create Date: " + data['create_date'] + "\n- Expire Date: " + data['expire_date'] + "\n- Used: " + data['used'] + "\n- Used date: " + data['used_date']
    await ctx.send(message)


@bot.command(
  name="userdata",
  description="Obtain the properties of a user based on its name",
  options=[
    interactions.Option(
      name="username",
      description="Name of the account",
      type=interactions.OptionType.STRING,
      required=True,
    ),
  ],
)
async def userdata(ctx: interactions.CommandContext, username: str):
    data = {
        'type': 'userdata',
        'username': username,
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    message = data['message']
    if (message == "success"):
        message = "- Username: " + username + "\n- Rank: " + data['rank'] + "\n- Create Date: " + data['create_date'] + "\n- Last Login Date: " + data['last_login_date'] + "\n- Expire Date: " + data['expire_date'] + "\n- HWID: " + data['hwid']
    await ctx.send(message)


@bot.command(
  name="resethwid",
  description="Reassigning the hardware ID for a user account to default",
  options=[
    interactions.Option(
      name="username",
      description="The user you wish to reset",
      type=interactions.OptionType.STRING,
      required=True,
    ),
  ],
)
async def resethwid(ctx: interactions.CommandContext, username: str):
    data = {
        'type': 'resethwid',
        'username': username,
        'admin_key': admin_key,
        'discord_user_id': str(ctx.author.id),
        'pair': generate_random_string()
    }

    json_string = run_request(json.dumps(data))
    data = json.loads(json_string)
    await ctx.send(data['message'])

bot.start() # Launch the bot
