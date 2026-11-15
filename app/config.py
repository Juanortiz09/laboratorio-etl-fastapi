import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # MongoDB (Staging / NoSQL)
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "laboratorio_etl_db")
    MONGO_COLLECTION: str = os.getenv("MONGO_COLLECTION", "productos_raw")

    # MySQL (Analítica / SQL)
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "laboratorio_etl_sql")

    # API Externa
    DUMMYJSON_URL: str = os.getenv("DUMMYJSON_URL", "https://dummyjson.com/products")

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )


settings = Settings()