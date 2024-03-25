import pandera as pa
from pandera.typing import DataFrame, Series

email_regex = r"[^@]+@[^@]+\.[^@]+"

class ProdutoSchema(pa.SchemaModel):
    """
    Esquema para representar dados de produtos.

    Attributes:
        id_produto (pandas.Series[int]): Série contendo IDs de produtos.
        nome (pandas.Series[str]): Série contendo nomes de produtos.
        quantidade (pandas.Series[int]): Série contendo quantidades de produtos (deve ser maior ou igual a 0).
        preco (pandas.Series[float]): Série contendo preços de produtos (deve ser maior ou igual a 0).
        categoria (pandas.Series[str]): Série contendo categorias de produtos.
        email (Series[str]): E-mail associado ao produto, deve seguir o formato padrão de e-mails.
    """
    id_produto: Series[int]
    nome: Series[str]
    quantidade: Series[int] = pa.Field(ge=0)
    preco: Series[float] = pa.Field(ge=0)
    categoria: Series[str]
    email: Series[str] = pa.Field(regex=email_regex)

    class Config:
        coerce = True
        # strict = True


class ProdutoSchemaKPI(ProdutoSchema):
    valor_total_estoque: Series[float] = pa.Field(ge=0)
    categoria_normalizada: Series[str]  # Assume-se que a categoria será uma string, não precisa de check específico além de ser uma string
    disponibilidade: Series[bool]  # Disponibilidade é um booleano, então não precisa de check específico