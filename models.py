from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# --- CATEGORIES ---
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    medicines = relationship("Medicine", back_populates="category")

# --- MEDICINES ---
class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_qty = Column(Integer, nullable=False)
    reorder_level = Column(Integer, default=10)
    expiry_date = Column(Date, nullable=False)

    category = relationship("Category", back_populates="medicines")
    purchase_items = relationship("PurchaseItem", back_populates="medicine")
    sale_items = relationship("SaleItem", back_populates="medicine")

# --- SUPPLIERS ---
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(100), nullable=True)
    contact = Column(String(20), nullable=False)

    purchases = relationship("Purchase", back_populates="supplier")

# --- PURCHASES ---
class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    purchase_date = Column(DateTime, default=func.now())
    total_amount = Column(DECIMAL(10, 2), nullable=False)

    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase")

class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    cost_price = Column(DECIMAL(10, 2), nullable=False)
    expiry_date = Column(Date, nullable=False)

    purchase = relationship("Purchase", back_populates="items")
    medicine = relationship("Medicine", back_populates="purchase_items")

# --- SALES ---
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    cashier_name = Column(String(100), nullable=False)
    sale_date = Column(DateTime, default=func.now())
    total_amount = Column(DECIMAL(10, 2), nullable=False)

    items = relationship("SaleItem", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sales_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)

    sale = relationship("Sale", back_populates="items")
    medicine = relationship("Medicine", back_populates="sale_items")