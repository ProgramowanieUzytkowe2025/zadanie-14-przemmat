from pydantic import BaseModel

class CarBase(BaseModel):
    marka_model: str
    rok_produkcji: int
    czy_na_chodzie: bool

class CarCreate(CarBase):
    pass

class Car(CarBase):
    id: int

    class Config:
        from_attributes = True