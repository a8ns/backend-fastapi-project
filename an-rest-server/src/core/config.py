from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # API settings
    project_name: str = os.environ.get("PROJECT_NAME", "Shop & Product API")
    api_v1_str: str = os.environ.get("API_V1_STR", "/api/v1")
    rest_server_api_key: str = os.environ.get("X-API-KEY") 
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
    postgres_test_db: str = os.environ.get("POSTGRES_TEST_DB", "shop_product_db_test")
    
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
    
    # Search settings
    vector_search_enabled: bool = os.environ.get("VECTOR_SEARCH_ENABLED", "false").lower() == "true"
    default_search_method: str = os.environ.get("DEFAULT_SEARCH_METHOD", "text")
    embedding_model: str = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dimensions: int = int(os.environ.get("EMBEDDING_DIMENSIONS", "1536"))
    hybrid_search_text_weight: float = float(os.environ.get("HYBRID_SEARCH_TEXT_WEIGHT", "0.4"))
    hybrid_search_vector_weight: float = float(os.environ.get("HYBRID_SEARCH_VECTOR_WEIGHT", "0.6"))
    
    # Search rate limiting
    search_rate_limit_per_minute: int = int(os.environ.get("SEARCH_RATE_LIMIT_PER_MINUTE", "60"))
    embedding_batch_size: int = int(os.environ.get("EMBEDDING_BATCH_SIZE", "50"))
    max_search_results: int = int(os.environ.get("MAX_SEARCH_RESULTS", "100"))
    
    def get_database_url(self) -> str:
        """Get database URL based on testing flag"""
        if self.testing:
            return f"postgresql+asyncpg://{self.postgres_test_user}:{self.postgres_test_password}@{self.postgres_test_server}:{self.postgres_test_port}/{self.postgres_test_db}"
        else:
            return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins string into a list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def initialize(self):
        """Initialize derived settings after loading environment variables"""
        # Initialize database_url if not set from environment
        self.database_url = self.database_url or self.get_database_url()
        
        # Ensure vector weights sum to 1.0
        total_weight = self.hybrid_search_text_weight + self.hybrid_search_vector_weight
        if total_weight != 1.0:
            # Normalize weights
            self.hybrid_search_text_weight /= total_weight
            self.hybrid_search_vector_weight /= total_weight

# Create settings instance
settings = Settings()

# Initialize settings
settings.initialize()