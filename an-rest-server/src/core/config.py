from pydantic_settings import BaseSettings
from typing import Optional
class Settings(BaseSettings):
    # API settings
    project_name: str = "Shop & Product API"
    api_v1_str: str = "/api/v1"
    
    # Testing toggle
    testing: bool = False
    
    # Production DB settings
    postgres_server: str
    postgres_port: str = "5432"
    postgres_user: str
    postgres_password: str
    postgres_db: str
    
    # Test DB settings
    postgres_test_server: str = "db-postgres-test"
    postgres_test_port: str = "5432"
    postgres_test_user: str = "postgres"
    postgres_test_password: str = "postgres"
    postgres_test_db: str = "user_data"
    # Connection string that gets built based on the above values
    database_url: Optional[str] = None
    
    # LLM settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_database_url(self) -> str:
        """Build the database URL from components or use override"""
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

# Initialize settings
settings = Settings()
settings.database_url = settings.database_url or settings.get_database_url()