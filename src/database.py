"""Handles the SQLite database connection, table management, and data operations."""

import os
import sqlite3
import logging
from sqlite3 import Connection
import pandas as pd
from typing import Optional
from translator import TranslatorModule
from classifier import Classifier

class Database:
    """
    Database class for handling connection to an SQLite database, performing
    table management, and executing operations such as populating translations,
    classification, and exporting data.
    """

    def __init__(self, db_file: str):
        """Initialize the Database class with the SQLite database file."""
        self.db_file = db_file
        self.conn: Optional[Connection] = None

    def connect(self) -> Connection:
        """
        Create a database connection to the SQLite database specified by db_file.
        If the database already exists, it deletes the old one and creates a new one.
        
        Returns:
            sqlite3.Connection: The connection object to the SQLite database.
        """
        try:
            # Ensure the 'data/' directory exists
            if not os.path.exists('data'):
                os.makedirs('data')

            # Set the database path inside the 'data/' directory
            db_path = os.path.join('data', self.db_file)

            # If the database file exists, remove it to create a new one
            if os.path.exists(db_path):
                os.remove(db_path)
                logging.info(f"Existing database {db_path} deleted.")

            # Create a new connection
            self.conn = sqlite3.connect(db_path)
            logging.info(f"SQLite DB connected: {db_path}")
            return self.conn
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def create_table(self) -> None:
        """
        Create a table for fast food nutrition data if it doesn't exist.
        The table stores restaurant items and their nutritional information.
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS fastfood (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant TEXT,
            item TEXT,
            calories INTEGER,
            cal_fat INTEGER,
            total_fat INTEGER,
            sat_fat REAL,
            trans_fat REAL,
            cholesterol INTEGER,
            sodium INTEGER,
            total_carb INTEGER,
            fiber REAL,
            sugar REAL,
            protein REAL,
            vit_a REAL,
            vit_c REAL,
            calcium REAL,
            salad TEXT,
            item_gr TEXT,
            category TEXT
        );
        """
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(create_table_sql)
                logging.info("Table created successfully.")
            except sqlite3.Error as e:
                logging.error(f"Error creating table: {e}")
                raise
        else:
            logging.error("No database connection established, connection failed.")

    def destroy_database(self) -> None:
        """
        Destroy the current SQLite database by deleting the database file.
        Useful for cleanup or resetting the database.
        """
        db_path = os.path.join('data', self.db_file)
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                logging.info(f"Database {db_path} deleted successfully.")
            else:
                logging.warning(f"Database {db_path} does not exist.")
        except Exception as e:
            logging.error(f"Error deleting database: {e}")
            raise

    def populate_item_gr_column(self, translator: TranslatorModule) -> None:
        """
        Populates the 'item_gr' column in the fastfood table by translating
        item names into Greek using the TranslatorModule.
        
        Args:
            translator (TranslatorModule): The translation module to translate item names.
        """
        # Calculate the chunk size based on available memory
        chunk_size = translator.calculate_chunk_size()
        logging.info(f"Processing translations in chunks of size {chunk_size}...")

        # Fetch data from the SQLite database in chunks and translate
        for chunk in pd.read_sql_query("SELECT * FROM fastfood;", self.conn, chunksize=chunk_size):
            chunk['item_gr'] = chunk['item'].apply(translator.translate_item)

            # Update the translated items back to the database
            for index, row in chunk.iterrows():
                self.conn.execute("UPDATE fastfood SET item_gr = ? WHERE id = ?", (row['item_gr'], row['id']))

            # Commit changes after processing each chunk
            self.conn.commit()

        logging.info("Translations added successfully to the 'item_gr' column.")

    def classify_items_and_add_category(self, classifier: Classifier) -> None:
        """
        Classify food items as 'Main', 'Side', or 'Dessert' and add the category to the database.
        
        Args:
            classifier (Classifier): The classifier used to categorize food items.
        """
        # Fetch the classified dataframe from the classifier
        classified_df = classifier.classify_items()

        # Add the 'category' column back into the fastfood table
        for index, row in classified_df.iterrows():
            self.conn.execute("UPDATE fastfood SET category = ? WHERE id = ?", (row['category'], row['id']))
        
        self.conn.commit()
        logging.info("Classification added successfully to the 'category' column.")

    def export_classification_to_csv(self, csv_filename: str = "data/food_categories.csv") -> None:
        """
        Export the item names and their corresponding classifications to a CSV file.
        
        Args:
            csv_filename (str): Path to the CSV file where the classification is exported.
        """
        # Check if the file exists and delete it
        if os.path.exists(csv_filename):
            os.remove(csv_filename)
            logging.info(f"Existing file {csv_filename} has been deleted.")
        
        # Fetch data
        query = "SELECT item, item_gr, category FROM fastfood;"
        df = pd.read_sql_query(query, self.conn)

        # Save to CSV
        df.to_csv(csv_filename, index=False)
        logging.info(f"Classification results successfully exported to {csv_filename}.")

    def get_nutrition_stats(self) -> pd.DataFrame:
        """
        Retrieve average, minimum, and maximum calorie counts, and rank restaurants by average carbohydrates.
        
        Returns:
            pd.DataFrame: DataFrame with nutrition statistics grouped by restaurant.
        """
        query = """
        SELECT 
            restaurant,
            AVG(calories) AS avg_calories,
            MIN(calories) AS min_calories,
            MAX(calories) AS max_calories,
            AVG(total_carb) AS avg_carbohydrates
        FROM fastfood
        GROUP BY restaurant
        ORDER BY avg_carbohydrates DESC;
        """
        try:
            return pd.read_sql_query(query, self.conn)
        except sqlite3.Error as e:
            logging.error(f"Error querying nutrition stats: {e}")
            raise
