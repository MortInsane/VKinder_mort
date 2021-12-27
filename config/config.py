from environs import Env

env = Env()
env.read_env()

VK_GROUP_TOKEN = env.str("VK_GROUP_TOKEN")
VK_USER_TOKEN = env.str("VK_USER_TOKEN")
VK_VERSION = env.float("VK_VERSION")

POSTGRES_DB = env.str("POSTGRES_DB")
POSTGRES_USER = env.str("POSTGRES_USER")
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
IP = env.str("IP")
PORT = env.str("PORT")

POSTGRES_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{IP}:{PORT}/{POSTGRES_DB}"
