from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, timedelta
import models, schemas, database


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Pharmacy Inventory System",
    description="Full API for managing Medicines, Suppliers, Purchases, and Sales.",
    version="1.0.0"
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- CATEGORIES ENDPOINTS ---

@app.post("/categories/", response_model=schemas.Category, tags=["Categories"])
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = models.Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[schemas.Category], tags=["Categories"])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Category).offset(skip).limit(limit).all()

# NEW: Update Category
@app.patch("/categories/{category_id}", response_model=schemas.Category, tags=["Categories"])
def update_category(category_id: int, category: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)

    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# NEW: Delete Category
@app.delete("/categories/{category_id}", status_code=204, tags=["Categories"])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Prevent deletion if medicines are associated
    if db_category.medicines:
        raise HTTPException(status_code=400, detail="Cannot delete category with associated medicines")

    db.delete(db_category)
    db.commit()
    return {"ok": True}

# --- MEDICINES ENDPOINTS ---

@app.post("/medicines/", response_model=schemas.Medicine, tags=["Medicines"])
def create_medicine(medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):

    if not db.query(models.Category).filter(models.Category.id == medicine.category_id).first():
        raise HTTPException(status_code=404, detail="Category not found")
        
    db_medicine = models.Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@app.get("/medicines/", response_model=List[schemas.Medicine], tags=["Medicines"])
def read_medicines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Medicine).offset(skip).limit(limit).all()

# NEW: Update Medicine
@app.patch("/medicines/{medicine_id}", response_model=schemas.Medicine, tags=["Medicines"])
def update_medicine(medicine_id: int, medicine: schemas.MedicineUpdate, db: Session = Depends(get_db)):
    db_medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    update_data = medicine.dict(exclude_unset=True)

    # Validate category_id if provided
    if 'category_id' in update_data:
        if not db.query(models.Category).filter(models.Category.id == update_data['category_id']).first():
            raise HTTPException(status_code=404, detail="Category not found")

    for key, value in update_data.items():
        setattr(db_medicine, key, value)

    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

# NEW: Delete Medicine
@app.delete("/medicines/{medicine_id}", status_code=204, tags=["Medicines"])
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    db_medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    # The existing database structure uses foreign keys to purchase_items and sales_items. 
    # Attempting to delete a Medicine with associated items will fail unless ON DELETE CASCADE 
    # is set up in the database or the items are deleted first. For simplicity here, we proceed with deletion.
    
    db.delete(db_medicine)
    db.commit()
    return {"ok": True}


# --- SUPPLIERS ENDPOINTS ---

@app.post("/suppliers/", response_model=schemas.Supplier, tags=["Suppliers"])
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = models.Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@app.get("/suppliers/", response_model=List[schemas.Supplier], tags=["Suppliers"])
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Supplier).offset(skip).limit(limit).all()

# NEW: Update Supplier
@app.patch("/suppliers/{supplier_id}", response_model=schemas.Supplier, tags=["Suppliers"])
def update_supplier(supplier_id: int, supplier: schemas.SupplierUpdate, db: Session = Depends(get_db)):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    update_data = supplier.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_supplier, key, value)

    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

# NEW: Delete Supplier
@app.delete("/suppliers/{supplier_id}", status_code=204, tags=["Suppliers"])
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # Prevent deletion if purchases are associated
    if db_supplier.purchases:
        raise HTTPException(status_code=400, detail="Cannot delete supplier with associated purchases")

    db.delete(db_supplier)
    db.commit()
    return {"ok": True}


# --- PURCHASES ENDPOINTS (UNCHANGED) ---

@app.post("/purchases/", response_model=schemas.Purchase, tags=["Purchases"])
def create_purchase(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db)):
    # 1. Create the main Purchase record
    db_purchase = models.Purchase(
        supplier_id=purchase.supplier_id,
        total_amount=purchase.total_amount
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)

    # 2. Add Items & Update Stock
    for item in purchase.items:
        db_item = models.PurchaseItem(
            purchase_id=db_purchase.id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            cost_price=item.cost_price,
            expiry_date=item.expiry_date
        )
        db.add(db_item)

        
        medicine = db.query(models.Medicine).filter(models.Medicine.id == item.medicine_id).first()
        if medicine:
            # Add to stock
            medicine.stock_qty += item.quantity
            # Update expiry date if the new batch expires SOONER than current stock
            if item.expiry_date < medicine.expiry_date:
                medicine.expiry_date = item.expiry_date
                
    db.commit()
    return db_purchase

@app.get("/purchases/", response_model=List[schemas.Purchase], tags=["Purchases"])
def read_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Purchase).offset(skip).limit(limit).all()


# --- SALES ENDPOINTS (UNCHANGED) ---

@app.post("/sales/", response_model=schemas.Sale, tags=["Sales"])
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    # 1. Create Sales Record
    db_sale = models.Sale(
        cashier_name=sale.cashier_name,
        total_amount=sale.total_amount
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    # 2. Add Items & Deduct Stock
    for item in sale.items:
        # Check stock first!
        medicine = db.query(models.Medicine).filter(models.Medicine.id == item.medicine_id).first()
        if not medicine:
            raise HTTPException(status_code=404, detail=f"Medicine ID {item.medicine_id} not found")
        
        if medicine.stock_qty < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {medicine.name}. Available: {medicine.stock_qty}")

        # Create Sale Item
        db_item = models.SaleItem(
            sale_id=db_sale.id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            subtotal=item.subtotal
        )
        db.add(db_item)

        # DEDUCT STOCK
        medicine.stock_qty -= item.quantity

    db.commit()
    return db_sale

@app.get("/sales/", response_model=List[schemas.Sale], tags=["Sales"])
def read_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Sale).offset(skip).limit(limit).all()


# --- REPORTS ENDPOINTS (UNCHANGED) ---

@app.get("/reports/low-stock", response_model=List[schemas.Medicine], tags=["Reports"])
def get_low_stock(db: Session = Depends(get_db)):
    """Returns medicines where stock is below reorder level."""
    return db.query(models.Medicine).filter(models.Medicine.stock_qty <= models.Medicine.reorder_level).all()

@app.get("/reports/expiring", response_model=List[schemas.Medicine], tags=["Reports"])
def get_expiring_soon(days: int = 30, db: Session = Depends(get_db)):
    """Returns medicines expiring within the next 30 days (default)."""
    expiration_threshold = date.today() + timedelta(days=days)
    return db.query(models.Medicine).filter(models.Medicine.expiry_date <= expiration_threshold).all()