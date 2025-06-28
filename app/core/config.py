import secrets
from typing import Any, Dict, List, Optional, Union
import os

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 分钟 * 24 小时 * 8 天 = 8 天
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # BACKEND_CORS_ORIGINS用于设置允许跨域请求的源
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "雨林作业管理系统"
    
    # 数据库配置
    DATABASE_TYPE: str = "sqlite"  # 'sqlite' 或 'mysql'
    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "yulin123"
    MYSQL_DB: str = "llm0321_work"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        # 根据数据库类型选择连接字符串
        if values.get('DATABASE_TYPE') == 'sqlite':
            # 使用SQLite数据库
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'homework_system.db')
            return f"sqlite:///{db_path}"
        else:
            # 使用MySQL数据库
            return f"mysql+pymysql://{values.get('MYSQL_USER')}:{values.get('MYSQL_PASSWORD')}@{values.get('MYSQL_SERVER')}/{values.get('MYSQL_DB')}"

    # 文件存储配置
    STORAGE_TYPE: str = "local"  # 'local', 's3', 'aliyun'
    LOCAL_STORAGE_PATH: str = "uploads"
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: Optional[str] = None
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 