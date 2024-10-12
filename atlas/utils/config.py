import os
from pydantic import Field
from pydantic_settings import BaseSettings
from neomodel import config as neomodel_config

class Settings(BaseSettings):
    ATLAS_UPDATE_INTERVAL: int = Field(default=60, env='ATLAS_UPDATE_INTERVAL')
    OPENAI_API_KEY: str = Field(..., env='OPENAI_API_KEY')
    OPENAI_API_BASE_URL: str = 'https://api.openai.com/v1'
    OPENAI_MODEL: str = 'gpt-4'

    # Neo4j settings
    NEO4J_USERNAME: str = Field(default='neo4j', env='NEO4J_USERNAME')
    NEO4J_PASSWORD: str = Field(..., env='NEO4J_PASSWORD')
    NEO4J_HOST: str = Field(default='localhost', env='NEO4J_HOST')
    NEO4J_PORT: int = Field(default=7687, env='NEO4J_PORT')

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        env_file_encoding = 'utf-8'

    @property
    def neo4j_database_url(self):
        return f"bolt://{self.NEO4J_USERNAME}:{self.NEO4J_PASSWORD}@{self.NEO4J_HOST}:{self.NEO4J_PORT}"

# Initialize settings
config = Settings()

# Configure neomodel
neomodel_config.DATABASE_URL = config.neo4j_database_url

print(f"Neo4j Database URL: {config.neo4j_database_url}")  # For debugging
