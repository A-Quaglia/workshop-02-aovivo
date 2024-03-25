import json
import os
from pathlib import Path

import pandas as pd
import pandera as pa
import schema
from dotenv import load_dotenv
from sqlalchemy import create_engine

from .schema import ProdutoSchema, ProdutoSchemaKPI

# from schema import ProdutoSchema, ProductSchemaKPI

def load_settings():
    """Carrega as configurações a partir de variáveis de ambiente."""
    dotenv_path = Path.cwd() / '.env'
    load_dotenv(dotenv_path=dotenv_path)

    settings = {
        "db_host": os.getenv("POSTGRES_HOST"),
        "db_user": os.getenv("POSTGRES_USER"),
        "db_pass": os.getenv("POSTGRES_PASSWORD"),
        "db_name": os.getenv("POSTGRES_DB"),
        "db_port": os.getenv("POSTGRES_PORT"),
    }
    return settings

@pa.check_output(ProdutoSchema)
def extrair_do_sql(query: str) -> pd.DataFrame:
    settings = load_settings()

    # Criar a string de conexão com base nas configurações
    connection_string = f"postgresql://{settings['db_user']}:{settings['db_pass']}@{settings['db_host']}:{settings['db_port']}/{settings['db_name']}"

    # Criar engine de conexão
    engine = create_engine(connection_string)

    with engine.connect() as conn, conn.begin():
            df_crm = pd.read_sql(query, conn)

    return df_crm

@pa.check_input(ProdutoSchema)
@pa.check_output(ProdutoSchemaKPI)
def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma os dados do DataFrame aplicando cálculos e normalizações.

    Args:
        df: DataFrame do Pandas contendo os dados originais.

    Returns:
        DataFrame do Pandas após a aplicação das transformações.
    """
    # Calcular valor_total_estoque
    df['valor_total_estoque'] = df['quantidade'] * df['preco']
    
    # Normalizar categoria para maiúsculas
    df['categoria_normalizada'] = df['categoria'].str.lower()
    
    # Determinar disponibilidade (True se quantidade > 0)
    df['disponibilidade'] = df['quantidade'] > 0
    
    return df



if __name__ == "__main__":
    query = "SELECT * FROM produtos_bronze LIMIT 10"
    df_crm = extrair_do_sql(query=query)

      # schema_crm = pa.infer_schema(df_crm)

    # with open("schema_crm.py", "w", encoding='utf-8') as arquivo:
    #      arquivo.write(schema_crm.to_script())

    print(df_crm)