# models.py
from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class VintageCar(Base):
    __tablename__ = "zabytkowe_samochody"

    id = Column(Integer, primary_key=True, index=True)
    # ZMIANA PONIŻEJ: Dodano (255) do String
    marka_model = Column(String(255), index=True)  
    rok_produkcji = Column(Integer)
    czy_na_chodzie = Column(Boolean)