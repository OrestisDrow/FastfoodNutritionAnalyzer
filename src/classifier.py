from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sqlite3 import Connection

class Classifier:
    """
    Classifier class responsible for classifying food items into categories such as 'Main', 'Side', and 'Dessert'.
    Uses KMeans clustering algorithm on selected nutritional features to group items.
    """
    
    def __init__(self, conn: Connection, n_clusters: int = 3):
        """
        Initialize the classifier with the database connection and clustering settings.

        Args:
            conn (Connection): Database connection.
            n_clusters (int): Number of clusters for KMeans (default is 3 for 'Main', 'Side', 'Dessert').
        """
        self.conn = conn
        self.n_clusters = n_clusters
        # Features used for clustering
        self.features = ['calories', 'total_fat', 'sugar', 'total_carb', 'protein', 'calcium', 'fiber']
        # Mapping KMeans clusters to food categories
        self.category_mapping = {0: 'Side', 1: 'Dessert', 2: 'Main'}

    def classify_items(self) -> pd.DataFrame:
        """
        Classify food items into categories ('Main', 'Side', 'Dessert') using KMeans clustering.
        
        1. Retrieves food data from the database.
        2. Preprocesses and scales the selected nutritional features.
        3. Performs KMeans clustering and maps the clusters to human-readable categories.
        4. Adds the classification back to the DataFrame and returns it.

        Returns:
            pd.DataFrame: The DataFrame with the added 'category' column containing the classification.
        """
        # Fetch the data from the database
        df = pd.read_sql_query("SELECT * FROM fastfood;", self.conn)
        
        # Select only the features used for clustering
        feature_df = df[self.features].copy()

        # Ensure the features are numeric (convert non-numeric data to NaN and drop rows with NaN values)
        feature_df = feature_df.apply(pd.to_numeric, errors='coerce')
        feature_df = feature_df.dropna()

        # Normalize the features using StandardScaler
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_df)

        # Perform KMeans clustering on the scaled data
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=0)
        feature_df['category'] = kmeans.fit_predict(scaled_features)

        # Map the cluster numbers to the corresponding food categories
        feature_df['category'] = feature_df['category'].map(self.category_mapping)

        # Add the 'category' column back into the original DataFrame
        df = df.loc[feature_df.index]  # Only keep rows with valid numeric data
        df['category'] = feature_df['category']

        return df
