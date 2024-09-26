import pandas as pd
from sqlite3 import Connection
import psutil
import re
import logging

class DataLoader:
    """
    DataLoader class responsible for loading CSV data into the database, performing
    chunked data loading based on system memory, and cleaning item names.
    """

    def __init__(self, connection: Connection):
        """Initialize the DataLoader with a database connection."""
        self.connection = connection

    def get_available_memory(self) -> float:
        """
        Return available system memory in GB.

        Returns:
            float: Available memory in GB.
        """
        available_memory_bytes = psutil.virtual_memory().available
        available_memory_gb = available_memory_bytes / (1024 ** 3)  # Convert bytes to GB
        return available_memory_gb

    def calculate_chunk_size(self, csv_file: str, memory_fraction: float = 0.5) -> int:
        """
        Calculate the chunk size for reading the CSV based on available RAM.
        By default, we'll use half of the available memory, though this can be adjusted
        via the memory_fraction argument.

        Args:
            csv_file (str): Path to the CSV file.
            memory_fraction (float): Fraction of available memory to use (default is 0.5).
        
        Returns:
            int: The chunk size (number of rows) to use when reading the CSV in chunks.
        """
        # Get available memory in GB
        available_memory_gb = self.get_available_memory()

        # Calculate the size of the CSV file in GB
        csv_size_bytes = pd.read_csv(csv_file, nrows=1).memory_usage(deep=True).sum() * pd.read_csv(csv_file).shape[0]
        csv_size_gb = csv_size_bytes / (1024 ** 3)  # Convert bytes to GB

        # Determine chunk size based on available memory and the memory fraction
        if csv_size_gb < available_memory_gb:
            logging.info(f"Whole CSV can fit into memory: {csv_size_gb:.2f} GB < {available_memory_gb:.2f} GB available.")
            chunk_size = pd.read_csv(csv_file).shape[0]  # Load everything at once
        else:
            logging.info(f"Not enough memory for full CSV, loading in chunks using {memory_fraction * available_memory_gb:.2f} GB.")
            chunk_size = int((memory_fraction * available_memory_gb) * (1024 ** 3) /
                             (pd.read_csv(csv_file, nrows=1).memory_usage(deep=True).sum()))

        return chunk_size

    def clean_item_name(self, item_name: str) -> str:
        """
        Clean the item name by removing unnecessary characters while keeping meaningful ones like 6".

        Args:
            item_name (str): The raw item name to be cleaned.
        
        Returns:
            str: The cleaned item name.
        """
        # Remove leading/trailing quotation marks but preserve internal quotes (e.g., 6")
        if item_name.startswith('"'):
            item_name = item_name[1:].strip()
        
        # Remove trailing quotes if they are not part of a number + inches pattern (e.g., 6")
        if item_name.endswith('"') and not re.search(r'\d+"$', item_name):
            item_name = item_name[:-1].strip()

        # Remove unwanted characters: trademark symbol (®), asterisk (*), and commas
        item_name = item_name.replace('®', '').replace('*', '').replace(',', '').strip()

        # Normalize spaces after character removal
        item_name = re.sub(r'\s+', ' ', item_name).strip()

        return item_name

    def drop_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop rows with any null values from the DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame.
        
        Returns:
            pd.DataFrame: A new DataFrame with rows containing null values removed.
        """
        df_cleaned = df.dropna()  # Drop rows with any NaN values
        return df_cleaned

    def _insert_chunk(self, chunk: pd.DataFrame) -> None:
        """
        Insert a chunk of data into the SQLite fastfood table.

        Args:
            chunk (pd.DataFrame): The chunk of data to be inserted.
        """
        try:
            chunk.to_sql('fastfood', self.connection, if_exists='append', index=False)
        except Exception as e:
            logging.error(f"Error inserting chunk into database: {e}")
            raise

    def load_csv_to_db(self, csv_file: str, memory_fraction: float = 0.5) -> None:
        """
        Load the CSV data into the fastfood table using chunked reading based on available memory.

        Args:
            csv_file (str): Path to the CSV file to be loaded.
            memory_fraction (float): Fraction of available memory to use for chunking (default is 0.5).
        """
        try:
            # Calculate the appropriate chunk size based on memory
            chunk_size = self.calculate_chunk_size(csv_file, memory_fraction)
            logging.info(f"Loading data in chunks of {chunk_size} rows.")
            
            # Read and process the CSV in chunks
            for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
                # Clean item names and drop rows with null values
                chunk['item'] = chunk['item'].apply(self.clean_item_name)
                chunk_cleaned = self.drop_nulls(chunk)
                self._insert_chunk(chunk_cleaned)
            
            logging.info(f"Data from {csv_file} inserted successfully in chunks.")
        except Exception as e:
            logging.error(f"Error loading data from CSV: {e}")
            raise
