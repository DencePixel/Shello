import asyncio
import yaml

def load_yaml_file():
    with open("config.yaml", 'r') as yaml_file:
        return yaml.safe_load(yaml_file)

def Load_yaml():
    data = load_yaml_file()
    return data

def initalize_yaml(self):
    """
    Initialize our yaml config
    """
    self.config = Load_yaml()
    self.mongo_uri = self.config["mongodb"]["uri"]
    
    if self.config["mongodb"]["uri"] is None:
        raise Exception("No mongo URI found")

if __name__ == '__main__':
    asyncio.run(Load_yaml())
