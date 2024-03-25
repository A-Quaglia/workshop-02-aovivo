import json
import os
from pathlib import Path

import duckdb
import pandas as pd
import pandera as pa
import schema
from dotenv import load_dotenv
from sqlalchemy import create_engine

from schema import ProdutoSchema, ProdutoSchemaKPI

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

    Attributes:
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


@pa.check_input(ProdutoSchemaKPI)
def load_to_duckdb(df: pd.DataFrame, table_name: str, db_file: str = 'my_duckdb.db'):
    """
    Carrega o DataFrame no DuckDB, criando ou substituindo a tabela especificada.

    Attributes:
        df: DataFrame do Pandas para ser carregado no DuckDB.
        table_name: Nome da tabela no DuckDB onde os dados serão inseridos.
        db_file: Caminho para o arquivo DuckDB. Se não existir, será criado.
    """
    # Conectar ao DuckDB. Se o arquivo não existir, ele será criado.
    con = duckdb.connect(database=db_file, read_only=False)
    
    # Registrar o DataFrame como uma tabela temporária
    con.register('df_temp', df)
    
    # Utilizar SQL para inserir os dados da tabela temporária em uma tabela permanente
    # Se a tabela já existir, substitui.
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df_temp")
    
    # Fechar a conexão
    con.close()


if __name__ == "__main__":
    query = "SELECT * FROM produtos_bronze_email"
    df_crm = extrair_do_sql(query=query)

    df_crm_kpi = transformar(df_crm)

    with open("inferred_schema.json", "w") as file:
         file.write(df_crm_kpi.to_json())

    load_to_duckdb(df=df_crm_kpi, table_name="table_kpi")