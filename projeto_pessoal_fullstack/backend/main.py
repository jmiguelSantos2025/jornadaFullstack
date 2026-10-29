from fastapi import FastAPI, Depends, HTTPException, Depends
from sqlalchemy import  create_engine,select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, Session
from uuid import uuid4, UUID as UUIDType
from sqlalchemy import String, UUID
from pydantic import BaseModel, Field
from http import HTTPStatus
from fastapi.middleware.cors import CORSMiddleware


engine = create_engine("sqlite:///livros.db")
session = sessionmaker(engine)
def get_db():
    db = session()

    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass

class Livro(Base):
    __tablename__= "Livros"
    id: Mapped[UUIDType] = mapped_column(UUID, primary_key=True, default=uuid4)
    titulo: Mapped[str] = mapped_column(String[400])
    autor: Mapped[str] = mapped_column(String[150], nullable=True)




class LivrosEntrada(BaseModel):
    titulo: str = Field(min_length=1)
    autor: str = Field(min_length=1)


class LivrosSaida(LivrosEntrada):
    id: UUIDType


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(engine)

#Rotas

livros = {}
@app.post("/adicionarlivros")
def adicionar_livros(livro:LivrosEntrada ,db:Session = Depends(get_db)) -> LivrosSaida:
    l = Livro(**livro.model_dump())

    db.add(l)
    db.commit()

    return LivrosSaida(id=l.id, titulo=l.titulo, autor=l.autor)

@app.get("/listarlivros")
def listar_livros(db: Session = Depends(get_db)):
    listar = select(Livro)
    livrosListados = db.execute(listar).scalars().all()

    return [{ "ID": livro.id , "TITULO": livro.titulo, "AUTOR":livro.autor} for livro in livrosListados]


@app.put("/atualizarlivros")
def atualizar_livros(id_autor: UUIDType, livros: LivrosEntrada,db: Session = Depends(get_db)) -> LivrosSaida:
    listar_livros_por_id = select(Livro).where(Livro.id == id_autor)
    lista_livros = db.execute(listar_livros_por_id).scalar_one_or_none()

    if not lista_livros:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Livro não encontrado")


    lista_livros.autor = livros.autor
    lista_livros.titulo = livros.titulo

    db.commit()

    return LivrosSaida(id=lista_livros.id, titulo=lista_livros.titulo, autor=lista_livros.autor)

@app.delete("/deletarlivros")
def deletar_livros( id_livro: UUIDType,db: Session = Depends(get_db)):
    listar_livros = select(Livro).where(Livro.id ==  id_livro)
    listagem_livros = db.execute(listar_livros).scalar_one_or_none()
    if not listagem_livros:    
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Livro não encontrado")
    db.delete(listagem_livros)
    db.commit()
    return{
        "Gasto deletado com sucesso!"
    }

    

