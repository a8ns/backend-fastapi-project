from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # API settings
    project_name: str = os.environ.get("PROJECT_NAME", "Shop & Product API")
    api_v1_str: str = os.environ.get("API_V1_STR", "/api/v1")
    
    # Testing toggle
    testing: bool = os.environ.get("TESTING", "false").lower() == "true"
    
    # Database settings
    postgres_server: str = os.environ.get("POSTGRES_SERVER", "localhost")
    postgres_port: str = os.environ.get("POSTGRES_PORT", "5432")
    postgres_user: str = os.environ.get("POSTGRES_USER", "postgres")
    postgres_password: str = os.environ.get("POSTGRES_PASSWORD", "postgres")
    postgres_db: str = os.environ.get("POSTGRES_DB", "shop_product_db")
    
    # Test database settings
    postgres_test_server: str = os.environ.get("POSTGRES_TEST_SERVER", "db-postgres-test")
    postgres_test_port: str = os.environ.get("POSTGRES_TEST_PORT", "5432")
    postgres_test_user: str = os.environ.get("POSTGRES_TEST_USER", "postgres")
    postgres_test_password: str = os.environ.get("POSTGRES_TEST_PASSWORD", "postgres")
    postgres_test_db: str = os.environ.get("POSTGRES_TEST_DB", "user_data")
    
    # Connection string - initialize it properly as an attribute
    database_url = os.environ.get("DATABASE_URL")
    
    # LLM Settings
    default_llm_provider: str = os.environ.get("DEFAULT_LLM_PROVIDER", "openai")
    openai_api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")
    default_llm_model: str = os.environ.get("DEFAULT_LLM_MODEL", "gpt-4-turbo")
    anthropic_api_key: Optional[str] = os.environ.get("ANTHROPIC_API_KEY")
    default_claude_model: str = os.environ.get("DEFAULT_CLAUDE_MODEL", "claude-3-opus-20240229")
    
    # CORS settings
    cors_origins: str = os.environ.get("CORS_ORIGINS", "*")
    
    def get_database_url(self) -> str:
        """Get database URL based on testing flag"""
        if self.testing:
            return f"postgresql+asyncpg://{self.postgres_test_user}:{self.postgres_test_password}@{self.postgres_test_server}:{self.postgres_test_port}/{self.postgres_test_db}"
        else:
            return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"


# Create settings instance
settings = Settings()
# Initialize database_url if not set from environment
settings.database_url = settings.database_url or settings.get_database_url()