import asyncio
import yaml
import logging
import os


import asyncio
import yaml
import logging
import os

def load_yaml_file():
    try:
        with open("config.yaml", 'r') as yaml_file:
            result = yaml.safe_load(yaml_file)
            if result is None:
                raise logging.CRITICAL("The config file is setup incorrectly")
    except FileNotFoundError:
        logging.warning("Inserting default config file")
        template_content = f"""
mongodb:
  uri: {os.getenv("MONGO_URI")}

collections:
  payment:
    database: 'PaymentLinkSystem'
    collection: 'Payment Config'

  design:
    database: 'DesignSystem'
    config_collection: 'Design Config'
    log_collection: 'Designs'
    feedback_config: 'FeedbackConfig'
    feedback_records: 'Feedback'
    active_designs_collection: 'Active'
    quota_collection: 'Quota'
    refund_collection: 'Refunds'

  welcome:
    database: 'WelcomeSystem'
    collection: 'Welcome Config'

  suggestion:
    database: 'Suggestions'
    config: 'Suggestions Config'  

  Roblox:
    database: 'Roblox'
    accounts_collection: 'accounts'

  Customization:
    database: 'Customization'
    config_collection: 'Customization Config'
  
  Alerts:
    database: 'Alerts'
    config: 'Config'  
    logs: 'Alert Logs'
"""
        yaml_config_file = open("config.yaml", "a")
        yaml_config_file.write(template_content)
        result = yaml.safe_load(template_content)
        logging.info("I have succesfully inserted base data into Config.yaml")

    return result
            

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
