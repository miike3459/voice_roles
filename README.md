# voice_roles

A Discord bot to reward voice activity with roles. This project does not use 
storage and is made to run continuously during events such as listen-in stages.

## Installation

Clone this repository. Configure the application by editing the values found in `app.ini`. Set the `TOKEN` environment variable with your bot's token (either through console or a `.env` file). You can then run the bot with `python3 main.py`.

## Requirements

- `discord.py`
- `python-dotenv`

Please make sure you give the bot the "Manage Roles" permission to avoid nasty errors.