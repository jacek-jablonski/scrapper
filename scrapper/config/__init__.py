# for bigger projects with multiple environments I would use something like https://github.com/rochacbruno/dynaconf
import os


APP_HOST = os.environ.get("APP_HOST", default="0.0.0.0")
APP_PORT = int(os.environ.get("APP_PORT", default=8080))

MONGO_HOST = os.environ.get("MONGO_HOST", default="mongo")
MONGO_PORT = int(os.environ.get("MONGO_PORT", default=27017))

CLIENT_HTTP_TIMEOUT = int(os.environ.get("CLIENT_HTTP_TIMEOUT", default=60))
