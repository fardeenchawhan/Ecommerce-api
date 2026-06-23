from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.utils.db import Base

class Usermodel(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True,index=True)
    name:Mapped[str]=mapped_column(String(100),nullable=False)
    username:Mapped[str]=mapped_column(String(100),nullable=False,unique=True,index=True)
    email:Mapped[str]=mapped_column(String(150),nullable=False,unique=True,index=True)
    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    cart_item=relationship("CartItemModel",back_populates="users",cascade="all, delete")
    orders=relationship("orderModel",back_populates="users",cascade="all, delete")

