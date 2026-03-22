from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    app_description: str = 'Сервис для поддержки котиков'
    database_url: str = 'sqlite+aiosqlite:///./fast_api.db'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    secret: str = 'SECRET'
    yandex_disk_token: Optional[str] = None
    report_format: str = '%d.%m.%Y %H:%M:%S'

    model_config = SettingsConfigDict(env_file='.env')




settings = Settings()
