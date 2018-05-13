"""
Run this file with python3.5+ in order to log in to Pyrogram with a Telegram user account
interactively, creating a Pyrogram "session" file (json) in the process.
It will try to log into the provided account like every regular Telegram client does,
and you will be prompted for the login code.

Once the session is generated, you will be able to run the integration tests.

The configuration can be found in tests/bots.py and may be set via environment variables:
  - API_ID=12345
  - API_HASH=abcdefghijklmnopqrstuvwxyz123456
  - PHONE_NUMBER=+49123456789

Read here about how to obtain the values for API_ID and API_HASH:
    https://docs.pyrogram.ml/start/ProjectSetup#api-keys

It is okay to use the provided defaults for API_ID and API_HASH, but you should use your own
(or a spare) Telegram account's PHONE_NUMBER.

Feel free to contact @JosXa on Telegram if you encounter problems.
"""
import os
import sys

from tests.bots import get_bot, get_userbot
from tests.integration import USERBOT_SESSION_ENV_VAR

try:
    from tgintegration import InteractionClient
except ImportError:
    print("You need to install the TgIntegration library to run tests:")
    print("$ pip install -r requirements-dev.txt")
    sys.exit(1)

output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'session_min_base64.txt')

if __name__ == '__main__':
    userbot_info = get_userbot()
    bot_info = get_bot()
    peer_username = bot_info['username']

    # Create a TgIntegration client (based on Pyrogram)
    client = InteractionClient(
        session_name="my_account",
        api_id=userbot_info['api_id'],
        api_hash=userbot_info['api_hash']
    )
    print("Starting client...")
    client.start()

    # Send an initial message to the bot to register it as a known peer
    print("Sending initial message to peer")
    try:
        client.send_message(peer_username, "Hi, I'll be your testing buddy for today.")
    except Exception as e:
        print("Could not contact {}. Please write a message to this peer manually and run the "
              "script again.\nException is: {}".format(peer_username, e))
        sys.exit(1)

    # Export the minified and base64-encoded session to be used in environment variables
    b64_string = client.export_minimal_session_b64(
        output_file,
        include_peers=[peer_username]
    ).strip()

    print('Initialized successfully.\n\n'
          'Now please set the {} test environment variable '
          'to the following:\n{}'.format(USERBOT_SESSION_ENV_VAR, b64_string))
    print('\nThis value was also written to\n{}'.format(output_file))
    print("\nIf you're using PyCharm, copy the key to clipboard and set the "
          "{} environment variable here:".format(USERBOT_SESSION_ENV_VAR))
    print("Run| Edit Configurations| Defaults| Python tests| py.test")
    client.stop()
