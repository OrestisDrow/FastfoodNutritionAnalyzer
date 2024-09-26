import sys
import os
import pandas as pd
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_loader import DataLoader

@pytest.fixture
def data_loader():
    """Fixture to initialize DataLoader."""
    return DataLoader(connection=None)

def test_clean_item_name(data_loader):
    """Test the clean_item_name method."""
    assert data_loader.clean_item_name('Chicken Sandwich®') == 'Chicken Sandwich'
    assert data_loader.clean_item_name('"Chicken"') == 'Chicken'
    assert data_loader.clean_item_name("6\" Sandwich") == '6" Sandwich'
    assert data_loader.clean_item_name('Spicy Chicken® Sandwich *') == 'Spicy Chicken Sandwich'

def test_drop_nulls(data_loader):
    """Test the drop_nulls method."""
    df = pd.DataFrame({
        'item': ['Chicken Sandwich', None, 'Burger'],
        'calories': [500, 600, None]
    })
    cleaned_df = data_loader.drop_nulls(df)
    assert cleaned_df.shape[0] == 1  # Only one row should remain
    assert cleaned_df['item'].iloc[0] == 'Chicken Sandwich'

def test_calculate_chunk_size(data_loader, monkeypatch):
    """Test the calculate_chunk_size method."""
    # Mock available memory and CSV size
    monkeypatch.setattr(data_loader, 'get_available_memory', lambda: 10)  # 10 GB available
    # Simulate a CSV of 100 MB
    test_csv_file = 'data/test.csv'
    pd.DataFrame({'item': ['A', 'B', 'C']}).to_csv(test_csv_file, index=False)

    chunk_size = data_loader.calculate_chunk_size(test_csv_file, memory_fraction=0.5)
    assert chunk_size > 0

    # Clean up test CSV file
    os.remove(test_csv_file)
