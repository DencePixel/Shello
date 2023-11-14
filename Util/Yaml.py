import asyncio
import yaml

async def load_yaml_file():
    with open("config.yaml", 'r') as yaml_file:
        return yaml.safe_load(yaml_file)

async def Load_yaml():
    data = await load_yaml_file()
    return data

async def initalize_yaml(self):
    """
    Initialize our yaml config
    """
    self.config = await Load_yaml()
    self.mongo_uri = self.config["mongodb"]["uri"]

if __name__ == '__main__':
    asyncio.run(Load_yaml())