# Discord License System Bot

## Overview

This Discord bot is designed to manage license keys and provide administrative utilities such as message clearing and logging actions in a designated channel. It utilizes the Discord API through the `discord.py` library, offering a robust interface for server management.

## Features

- **License Key Management**: Add, remove, and redeem license keys associated with specific roles.
- **Message Clearing**: Admins can clear messages in a channel with a specified command.
- **Action Logging**: Logs actions performed by users in a designated log channel.
- **Dynamic Configuration**: Loads configuration settings from JSON files, allowing for easy modifications.

## Requirements

- Python 3.8 or higher
- `discord.py` library (v2.x recommended)
- JSON files for configuration (`admins.json`, `used_keys.json`, `log_channel.json`, `licenses.json`)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Stoltdansker/License-System-Bot.git
   cd your-bot-repo

2. **Install requirements:**
   ```bash
   pip install discord.py
   pip install logging
   
3. **Create Configuration Files:**
   ```bash
   {
    "admin_role_id": "YOUR-ADMIN-ROLE-ID"
   }

   {
    "keys": [
        {
            "key": "KEY-HERE",
            "role_id": "ROLE-ID-HERE"
        },
        {
            "key": "KEY-HERE",
            "role_id": "ROLE-ID-HERE"
        },
        {
            "key": "KEY-HERE",
            "role_id": "ROLE-ID-HERE"
        }
    ]
   }

- **Anything else can be set in the server**



## Commands

- **/clear**: Clear a specified number of messages (admin only).
- **/setup_log_channel**: Set the log channel for the bot (admin only).
- **/add_license**: Add a new license key with a role ID (admin only).
- **/remove_license**: Remove an existing license key (admin only).
- **/redeem**: Redeem a valid license key and assign the corresponding role.

## Logging

The bot logs actions to the console and sends messages to a specified log channel. Ensure you set the log channel using the `/setup_log_channel` command after starting the bot.

## Running the Bot

To run the bot, simply execute the following command in your terminal:
```bash
python bot.py
```

## Contributing

Contributions are welcome! Please feel free to fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For any issues or questions, please open an issue in the GitHub repository. 
