import vk
import dotenv
import os

dotenv.load_dotenv()
TOKEN = os.environ['TOKEN']
GROUP_ID = os.environ['GROUP_ID']
APP_ID=

session = vk.AuthSession(scope='wall', app_id=, access_token=TOKEN)
vk_api = vk.API(session, v='5.103')