import pandera as pa
from pandera.typing import DataFrame, Series


class ProdutoSchema(pa.SchemaModel):
    """
    Esquema para representar dados de produtos.

    Attributes:
        id_produto (pandas.Series[int]): Série contendo IDs de produtos.
        nome (pandas.Series[str]): Série contendo nomes de produtos.
        quantidade (pandas.Series[int]): Série contendo quantidades de produtos (deve ser maior ou igual a 0).
        preco (pandas.Series[float]): Série contendo preços de produtos (deve ser maior ou igual a 0).
        categoria (pandas.Series[str]): Série contendo categorias de produtos.
    """
    id_produto: Series[int]
    nome: Series[str]
    quantidade: Series[int] = pa.Field(ge=0)
    preco: Series[float] = pa.Field(ge=0)
    categoria: Series[str]

    class Config:
        coerce = True
        # strict = True
