from logging import basicConfig, getLogger, Logger


logger = getLogger("physical_agent")
basicConfig(level="DEBUG")

def get_logger(name:str)-> "Logger":
    return logger.getChild(name)
