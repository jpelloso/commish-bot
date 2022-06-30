import json
import time
import logging

# Disable yahoo oauth logger
logging.disable(logging.DEBUG)

class GuildsDatastore():

    def __init__(self, datastore):
        self.datastore = datastore
        self.refreshDatastore()

    def getGuildDetails(self, guild_id):
        return self.guilds[str(guild_id)]

    def refreshDatastore(self):
        with open(self.datastore, 'r') as f:
            self.guilds = json.load(f)
            f.close()
        self.last_refresh_timestamp = time.time()