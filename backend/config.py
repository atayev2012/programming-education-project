from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """
    Base configuration class.
    """

    # Database configuration
    USER = os.getenv('DB_USERNAME')
    PASSWORD = os.getenv('PASSWORD')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    DATABASE = os.getenv('DATABASE')

    # JWT token configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
    JWT_EXPIRATION_TIME = int(os.getenv('JWT_EXPIRATION_TIME'))
    JWT_REFRESH_EXPIRATION_TIME = int(os.getenv('JWT_REFRESH_EXPIRATION_TIME'))

    # For email verification
    EMAIL_VERIFICATION_SECRET_KEY = os.getenv('EMAIL_VERIFICATION_SECRET_KEY')
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    EMAIL = os.getenv("EMAIL")
    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
    EMAIL_SMTP_SERVER_PORT = int(os.getenv("EMAIL_SMTP_SERVER_PORT"))

    # Web App Domain name for urls
    WEB_APP_DOMAIN = os.getenv('WEP_APP_DOMAIN')

    def get_db_url(self):
        """
        Construct the database URL from the configuration.
        """
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"


config = Config()

if __name__ == "__main__":
    print("Database Configuration:")
    print(f"USER: {config.USER}")
    print(f"PASSWORD: {config.PASSWORD}")
    print(f"HOST: {config.HOST}")
    print(f"PORT: {config.PORT}")
    print(f"DATABASE: {config.DATABASE}")

    print("\nJWT Configuration:")
    print(f"JWT_SECRET_KEY: {config.JWT_SECRET_KEY}")
    print(f"JWT_ALGORITHM: {config.JWT_ALGORITHM}")
    print(f"JWT_EXPIRATION_TIME: {config.JWT_EXPIRATION_TIME}")
    print(f"JWT_REFRESH_EXPIRATION_TIME: {config.JWT_REFRESH_EXPIRATION_TIME}")
    print(f"EMAIL_VERIFICATION_SECRET_KEY: {config.EMAIL_VERIFICATION_SECRET_KEY}")