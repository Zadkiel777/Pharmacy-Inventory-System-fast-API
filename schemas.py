from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# --- Categories ---
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
class CategoryCreate(CategoryBase):
    pass
# NEW: Schema for partial updates
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

# --- Medicines ---
class MedicineBase(BaseModel):
    name: str
    price: float
    stock_qty: int
    reorder_level: Optional[int] = 10
    expiry_date: date
    category_id: int
class MedicineCreate(MedicineBase):
    pass
# NEW: Schema for partial updates
class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock_qty: Optional[int] = None
    reorder_level: Optional[int] = None
    expiry_date: Optional[date] = None
    category_id: Optional[int] = None
class Medicine(MedicineBase):
    id: int
    class Config:
        from_attributes = True

# --- Suppliers ---
class SupplierBase(BaseModel):
    company_name: str
    contact_person: Optional[str] = None
    contact: str
class SupplierCreate(SupplierBase):
    pass
# NEW: Schema for partial updates
class SupplierUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact: Optional[str] = None
class Supplier(SupplierBase):
    id: int
    class Config:
        from_attributes = True

# --- Purchases ---
class PurchaseItemBase(BaseModel):
    medicine_id: int
    quantity: int
    cost_price: float
    expiry_date: date
class PurchaseItemCreate(PurchaseItemBase):
    pass
class PurchaseItem(PurchaseItemBase):
    id: int
    purchase_id: int
    class Config:
        from_attributes = True

class PurchaseBase(BaseModel):
    supplier_id: int
    total_amount: float
class PurchaseCreate(PurchaseBase):
    items: List[PurchaseItemCreate] 
class Purchase(PurchaseBase):
    id: int
    purchase_date: datetime
    items: List[PurchaseItem] = []
    class Config:
        from_attributes = True

# --- Sales ---
class SaleItemBase(BaseModel):
    medicine_id: int
    quantity: int
    subtotal: float
class SaleItemCreate(SaleItemBase):
    pass
class SaleItem(SaleItemBase):
    id: int
    sale_id: int
    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    cashier_name: str
    total_amount: float
class SaleCreate(SaleBase):
    items: List[SaleItemCreate]
class Sale(SaleBase):
    id: int
    sale_date: datetime
    items: List[SaleItem] = []
    class Config:
        from_attributes = True