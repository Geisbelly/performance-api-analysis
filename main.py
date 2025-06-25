from typing import Optional
from fastapi import FastAPI, HTTPException, Depends 
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os
import time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydatabase")

# Configuração do SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Dados (SQLAlchemy)
class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    descricao = Column(String)
    preco = Column(Float)

# Esquema Pydantic para validação de entrada/saída
class ItemBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    class Config:
        from_attributes = True # updated from orm_mode=True

# Criação da aplicação FastAPI
app = FastAPI()

# Função para obter a sessão do DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Evento de startup para criar tabelas
@app.on_event("startup")
def startup_event():
    # Tenta conectar ao banco de dados até que esteja disponível
    for _ in range(10): # Tenta 10 vezes
        try:
            Base.metadata.create_all(bind=engine)
            print("Tabelas criadas com sucesso ou já existentes.")
            break
        except Exception as e:
            print(f"Erro ao conectar ao DB ou criar tabelas: {e}. Tentando novamente em 5 segundos...")
            time.sleep(5)
    else:
        raise Exception("Não foi possível conectar ao banco de dados após várias tentativas.")


# Endpoints da API
@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate, db: SessionLocal = Depends(get_db)):
    db_item = ItemDB(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[Item])
def read_items(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db)):
    items = db.query(ItemDB).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: SessionLocal = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate, db: SessionLocal = Depends(get_db)):
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    for key, value in item.dict().items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: SessionLocal = Depends(get_db)):
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    db.delete(db_item)
    db.commit()
    return {"message": "Item excluído com sucesso!"}