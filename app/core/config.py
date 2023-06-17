"""
A module for config in the app-core package.
"""
import base64
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional, Union

from pydantic import (
    AnyHttpUrl,
    AnyUrl,
    BaseSettings,
    EmailStr,
    MongoDsn,
    RedisDsn,
    root_validator,
    validator,
)


def get_image_b64(image_path: str) -> str:
    """
    Converts an image to base64 format
    :param image_path: Path to the image file
    :type image_path: str
    :return: The image file in base64 format
    :rtype: str
    """
    return base64.b64encode(Path(image_path).read_bytes()).decode("utf")


img_b64: str = get_image_b64("./app/assets/static/images/project.png")
users_b64: str = get_image_b64("./app/assets/static/images/users.png")
auth_b64: str = get_image_b64("./app/assets/static/images/auth.png")


class MySQLDsn(AnyUrl):
    """
    MySQL DSN class inherited from Pydantic AnyURL.
    """
    allowed_schemes: set[str] = {"mysql+aiomysql"}


class Settings(BaseSettings):
    """
    Settings class based on Pydantic Base Settings
    """
    API_V1_STR: str = "/api/v1"
    ALGORITHM: str = "HS256"
    SERVER_NAME: str = "Telegram bot"
    PROJECT_NAME: str = "telegram-bot"
    VERSION: str = "1.0"
    ENCODING: str = "UTF-8"
    OPENAPI_FILE_PATH: str = "/openapi.json"
    TOKEN_URL: str = "api/v1/auth/login"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    FILE_DATE_FORMAT: str = "%d-%b-%Y-%H-%M-%S"
    IMAGES_PATH: str = "/./app/assets/static/images"
    IMAGES_DIRECTORY: str = "./app/assets/static/images"
    TIMESTAMP_PRECISION: int = 2
    EMAIL_TEMPLATES_DIR: str = "app/assets/templates"
    LOG_FORMAT: str = "[%(name)s][%(asctime)s][%(levelname)s][%(module)s]" \
                      "[%(funcName)s][%(lineno)d]: %(message)s"
    TELEPHONE_REGEX: str = "\\(\\?\\+[0-9]{1,3}\\)? ?-?[0-9]{1,3} ?-?[0-9]" \
                           "{3,5}?-?[0-9]{4}( ?-?[0-9]{3})? ?(\\w{1,10}\\s?" \
                           "\\d{1,6})?"
    PASSWORD_REGEX: str = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?" \
                          "[#?!@$%^&*-]).{8,14}$"
    SUB_REGEX: str = "username:(?!0)\\d+"
    DB_EMAIL_CONSTRAINT: str = "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\" \
                               ".[A-Z|a-z]{2,}$'"
    DB_TELEPHONE_CONSTRAINT: str = "phone_number ~* '^\\+[0-9]{1,15}$'"

    DESCRIPTION: str = f"""**FastAPI**, **SQLAlchemy**, **Beanie** and 
    **Redis**  helps you do awesome stuff. 🚀
    \n\n<img src="data:image/png;base64,{img_b64}"/>"""
    LICENSE_INFO: dict[str, str] = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"}
    TAGS_METADATA: list[dict[str, str]] = [
        {
            "name": "users",
            "description": f"""Operations with users, such as register, get,
             update and delete.\n\n<img src="data:image/png;base64,
             {users_b64}" width="300" height="200"/>"""
        },
        {
            "name": "auth",
            "description": f"""The authentication logic is here as well as
             password recovery and reset.
             \n\n<img src="data:image/png;base64,{auth_b64}" width="150" 
             height="150"/>"""}]

    SECRET_KEY: str
    SERVER_HOST: AnyHttpUrl
    ACCESS_TOKEN_EXPIRE_MINUTES: float
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    AUDIENCE: Optional[str] = None

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
            cls, v: Union[str, list[str]]
    ) -> Union[list[str], str]:
        """
        Assemble a list of allowed CORS origins.
        :param v: Provided CORS origins, either a string or a list of strings
        :type v: Union[str, list[str]]
        :return: List of Backend CORS origins to be accepted
        :rtype: Union[list[str], str]
        """
        # pylint: disable=unused-argument,no-self-argument,invalid-name
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, list):
            return v
        raise ValueError(v)

    @validator("AUDIENCE", pre=True)
    def assemble_audience(
            cls, v: Optional[str], values: dict[str, Any]) -> str:
        """
        Combine server host and API_V1_STR to create the audience string.
        :param v: The value of audience attribute
        :type v: Optional[str]
        :param values: The values to assemble the audience string
        :type values: dict[str, Any]
        :return: The AUDIENCE attribute
        :rtype: str
        """
        # pylint: disable=unused-argument,no-self-argument,invalid-name
        return f"{values['SERVER_HOST']}{values['API_V1_STR']}/auth/login"

    MYSQL_SERVER: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    MYSQL_PORT: int
    SQLALCHEMY_DATABASE_URI: Optional[MySQLDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_mysql_connection(
            cls, v: Optional[str], values: dict[str, Any]
    ) -> str:
        """
        Assemble the database connection as URI string
        :param v: Variables to consider
        :type v: str
        :param values: Variables names and its values
        :type values: dict[str, Any]
        :return: SQLAlchemy URI
        :rtype: str
        """
        # pylint: disable=unused-argument,no-self-argument,invalid-name
        if isinstance(v, str):
            return v
        return str(MySQLDsn.build(
            scheme="mysql+aiomysql",
            user=values.get("MYSQL_USER"),
            password=values.get("MYSQL_PASSWORD"),
            host=values.get("MYSQL_SERVER"),
            port=str(values.get("MYSQL_PORT")),
            path=f"/{values.get('MYSQL_DB')}" or ""
        ))

    SMTP_TLS: bool
    SMTP_PORT: int
    SMTP_HOST: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    MAIL_SUBJECT: str
    MAIL_TIMEOUT: float

    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int

    SUPERUSER_EMAIL: EmailStr
    SUPERUSER_FIRST_NAME: str
    SUPERUSER_PASSWORD: str

    REDIS_HOST: str
    REDIS_USERNAME: str
    REDIS_PASSWORD: str
    REDIS_PORT: int
    AIOREDIS_DATABASE_URI: Optional[RedisDsn] = None

    @validator("AIOREDIS_DATABASE_URI", pre=True)
    def assemble_redis_connection(
            cls, v: Optional[str], values: dict[str, Any]
    ) -> str:
        """
        Assemble the cache database connection as URI string
        :param v: Variables to consider
        :type v: str
        :param values: Variables names and its values
        :type values: dict[str, Any]
        :return: Redis URI
        :rtype: str
        """
        # pylint: disable=unused-argument,no-self-argument,invalid-name
        if isinstance(v, str):
            return v
        return str(RedisDsn.build(
            scheme="redis",
            user=values.get("REDIS_USERNAME"),
            password=values.get("REDIS_PASSWORD"),
            host=values.get("REDIS_HOST"),
            port=str(values.get("REDIS_PORT"))
        ))

    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str
    MONGODB_SERVER: str
    MONGODB_PORT: int
    MONGODB_DB: str
    BEANIE_DATABASE_URI: Optional[MongoDsn] = None

    @validator("BEANIE_DATABASE_URI", pre=True)
    def assemble_mongodb_connection(
            cls, v: Optional[str], values: dict[str, Any]
    ) -> str:
        """
        Assemble the MongoDB connection as URI string
        :param v: Variables to consider
        :type v: str
        :param values: Variables names and its values
        :type values: dict[str, Any]
        :return: MongoDB URI
        :rtype: str
        """
        if isinstance(v, str):
            return v
        return str(MongoDsn.build(
            scheme="mongodb",
            user=values.get("MONGODB_USERNAME"),
            password=values.get("MONGODB_PASSWORD"),
            host=values.get("MONGODB_SERVER"),
            port=str(values.get("MONGODB_PORT")),
            path=f"/{values.get('MONGODB_DB') or ''}"
        ))

    CONTACT_NAME: Optional[str]
    CONTACT_URL: Optional[AnyHttpUrl]
    CONTACT_EMAIL: Optional[EmailStr]
    CONTACT: dict[str, Any]

    @root_validator(pre=True)
    def assemble_contact(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Assemble contact information
        :param values: Values of the environment variables
        :type values: dict[str, Any]
        :return: The contact attribute
        :rtype: dict[str, Any]
        """
        # pylint: disable=unused-argument,no-self-argument
        contact: dict[str, Any] = {}
        if values.get("CONTACT_NAME"):
            contact["name"] = values["CONTACT_NAME"]
        if values.get("CONTACT_URL"):
            contact["url"] = values["CONTACT_URL"]
        if values.get("CONTACT_EMAIL"):
            contact["email"] = values["CONTACT_EMAIL"]
        values["CONTACT"] = contact
        return {k: v for k, v in values.items() if
                k not in ("CONTACT_NAME", "CONTACT_URL", "CONTACT_EMAIL")}

    class Config:
        """
        Config class for Settings
        """
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"
        case_sensitive = True


settings: Settings = Settings()


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings cached
    :return: settings object
    :rtype: Settings
    """
    return Settings()
