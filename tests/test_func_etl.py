import pandas as pd
import pytest
from app.etl import extrair_do_sql, transformar


# Define test data
@pytest.fixture
def sample_dataframe():
    data = {'id_produto': [1, 2, 3],
            'nome': ['A', 'B', 'C'],
            'quantidade': [10, 0, 5],
            'preco': [20, 30, 15],
            'categoria': ['Eletrônicos', 'Roupas', 'Eletrônicos'],
            'email': ['produtoA@example.com', 'produtoA@example.com', 'produtoA@example.com']}
    return pd.DataFrame(data)

# Test case 1: Test if 'valor_total_estoque' is calculated correctly
def test_valor_total_estoque(sample_dataframe):
    expected_values = [200, 0, 75]
    result_df = transformar(sample_dataframe)
    assert result_df['valor_total_estoque'].tolist() == expected_values

# Test case 2: Test if 'categoria_normalizada' is converted to lowercase
def test_categoria_normalizada(sample_dataframe):
    expected_values = ['eletrônicos', 'roupas', 'eletrônicos']
    result_df = transformar(sample_dataframe)
    assert result_df['categoria_normalizada'].tolist() == expected_values

# Test case 3: Test if 'disponibilidade' is determined correctly
def test_disponibilidade(sample_dataframe):
    expected_values = [True, False, True]
    result_df = transformar(sample_dataframe)
    assert result_df['disponibilidade'].tolist() == expected_values