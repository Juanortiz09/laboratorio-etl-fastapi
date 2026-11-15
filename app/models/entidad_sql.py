from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from app.database import Base


class ProductMaster(Base):
    __tablename__ = "productos_master"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, default="N/A")
    brand = Column(String(100), nullable=False, default="N/A")
    price = Column(Float, nullable=True)
    discount_percentage = Column(Float, nullable=True)
    rating = Column(Float, nullable=True)
    stock = Column(Integer, nullable=True)
    width = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=True)
    es_stock_alto = Column(Boolean, nullable=False, default=False)