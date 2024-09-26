"""This module is responsible for:
   - Fetching data from the SQLite database in chunks.
   - Checking available RAM to handle large datasets efficiently.
   - Translating food item names, using a curated dictionary first and Google Translate as a fallback.
"""

import pandas as pd
import psutil
from googletrans import Translator
import sqlite3

class TranslatorModule:
    """
    TranslatorModule class that manages translations of food items.
    It first checks a curated CSV dictionary for translations and falls back to Google Translate if not found.
    """

    def __init__(self, connection: sqlite3.Connection, translation_csv: str, memory_fraction: float = 0.5):
        """
        Initialize the TranslatorModule with a SQLite connection and load the translation dictionary.
        
        Args:
            connection (sqlite3.Connection): Database connection.
            translation_csv (str): Path to the curated translation CSV file.
            memory_fraction (float): Fraction of available memory to allocate for chunk processing.
        """
        self.conn = connection
        self.memory_fraction = memory_fraction
        self.translator = Translator()
        
        # Load the curated translations from the CSV
        self.dict_translations = self.load_translation_dict(translation_csv)

    def load_translation_dict(self, csv_path: str) -> dict:
        """
        Load translations from the given CSV file into a dictionary.

        Args:
            csv_path (str): Path to the translation CSV file.

        Returns:
            dict: Dictionary with item names as keys and their Greek translations as values.
        """
        df = pd.read_csv(csv_path)
        return pd.Series(df['item_gr'].values, index=df['item']).to_dict()

    def get_available_memory(self) -> float:
        """
        Check and return the available system memory in GB.

        Returns:
            float: Available system memory in GB.
        """
        available_memory_bytes = psutil.virtual_memory().available
        return available_memory_bytes / (1024 ** 3)  # Convert bytes to GB

    def calculate_chunk_size(self) -> int:
        """
        Calculate the chunk size for reading data from the database based on available memory.

        Returns:
            int: Number of rows to process in a single chunk.
        """
        available_memory_gb = self.get_available_memory()
        # Use half of the available memory by default (adjustable via memory_fraction)
        allocated_memory_gb = self.memory_fraction * available_memory_gb
        
        # Estimate the memory usage of one row of data
        one_row_memory_usage_bytes = pd.read_sql_query("SELECT * FROM fastfood LIMIT 1;", self.conn).memory_usage(deep=True).sum()
        one_row_memory_usage_gb = one_row_memory_usage_bytes / (1024 ** 3)  # Convert bytes to GB
        
        # Calculate chunk size based on available memory and estimated memory usage per row
        chunk_size = int(allocated_memory_gb / one_row_memory_usage_gb)
        return max(chunk_size, 1)  # Ensure chunk_size is at least 1

    def google_translate_word_by_word(self, item: str, target_language: str = 'el') -> str:
        """
        Translate a food item word by word using Google Translate.

        Args:
            item (str): Food item name to translate.
            target_language (str): Target language for translation (default is 'el' for Greek).

        Returns:
            str: Translated food item name.
        """
        words = item.split()  # Split the item name into individual words
        translated_words = [
            self.translator.translate(word, dest=target_language).text for word in words
        ]
        return ' '.join(translated_words)  # Reassemble the translated words

    def translate_item(self, item: str) -> str:
        """
        Translate a food item name. First, it checks the curated dictionary for translation.
        If not found, it falls back to Google Translate.

        Args:
            item (str): The food item name to translate.

        Returns:
            str: Translated food item name (Greek by default).
        """
        # Check if the item is in the curated dictionary
        if item in self.dict_translations:
            return self.dict_translations[item]
        else:
            # Fallback to Google Translate word-by-word translation
            return self.google_translate_word_by_word(item)
