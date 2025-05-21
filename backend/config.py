from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """
    Base configuration class.
    """

    # Database configuration
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    DATABASE = os.getenv('DATABASE')

config = Config()