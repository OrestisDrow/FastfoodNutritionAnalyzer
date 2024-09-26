import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

class FigureMaker:
    """
    FigureMaker class responsible for generating various visualizations
    using data from the fastfood database.
    """

    def __init__(self, conn):
        """Initialize the FigureMaker with a database connection."""
        self.conn = conn
        self.top_5_restaurants = ['Subway', 'Mcdonalds', 'Sonic', 'Taco Bell', 'Arbys']

    def get_max_calorie_items_fig(self):
        """
        Generate a scatter plot showing the max calorie items per restaurant.

        Returns:
            plotly.graph_objs._figure.Figure: The scatter plot figure.
        """
        query = f"""
        SELECT restaurant, item, item_gr, MAX(calories) as max_calories, AVG(total_carb) as avg_carbohydrates
        FROM fastfood
        WHERE restaurant IN ({','.join([f"'{r}'" for r in self.top_5_restaurants])})
        GROUP BY restaurant
        ORDER BY max_calories DESC;
        """
        df = pd.read_sql_query(query, self.conn)
        df['label'] = df['item'] + '<br>' + df['item_gr']

        fig = px.scatter(df, x='restaurant', y='max_calories', size='max_calories',
                         color='avg_carbohydrates', hover_name='label', size_max=60)

        # Remove the title from the figure itself
        fig.update_layout(showlegend=False, title=None)

        return fig

    def get_avg_carbohydrates_donut_fig(self):
        """
        Generate a donut chart of average carbohydrates by restaurant.

        Returns:
            plotly.graph_objs._figure.Figure: The donut chart figure.
        """
        query = f"""
        SELECT restaurant, AVG(total_carb) as avg_carbohydrates
        FROM fastfood
        WHERE restaurant IN ({','.join([f"'{r}'" for r in self.top_5_restaurants])})
        GROUP BY restaurant
        ORDER BY avg_carbohydrates DESC;
        """
        df = pd.read_sql_query(query, self.conn)

        fig = px.pie(df, values='avg_carbohydrates', names='restaurant', hole=0.4)
        
        # Remove the title from the figure itself
        fig.update_layout(title=None)

        return fig

    def get_calorie_treemap_fig(self):
        """
        Generate a treemap of the top 5 calorie items per restaurant.

        Returns:
            plotly.graph_objs._figure.Figure: The treemap figure.
        """
        query = f"""
        SELECT restaurant, item, item_gr, max_calories FROM (
            SELECT restaurant, item, item_gr, MAX(calories) as max_calories,
                ROW_NUMBER() OVER (PARTITION BY restaurant ORDER BY MAX(calories) DESC) as rank
            FROM fastfood
            WHERE restaurant IN ({','.join([f"'{r}'" for r in self.top_5_restaurants])})
            GROUP BY restaurant, item
        ) WHERE rank <= 5
        ORDER BY restaurant, max_calories DESC;
        """
        df = pd.read_sql_query(query, self.conn)
        df['label'] = df['item'] + '<br>' + df['item_gr'] + '<br>' + 'Calories: ' + df['max_calories'].astype(str)

        fig = px.treemap(df, path=['restaurant', 'label'], values='max_calories',
                         height=1500, width=1200)

        # Center-align the text and remove the figure title
        fig.update_traces(texttemplate="<b>%{label}</b>", textposition="middle center", textfont_size=20)
        fig.update_layout(title=None)

        return fig

    def get_calorie_sunburst_fig(self):
        """
        Generate a sunburst plot of the top 5 calorie items per restaurant.

        Returns:
            plotly.graph_objs._figure.Figure: The sunburst plot figure.
        """
        query = f"""
        SELECT restaurant, item, item_gr, max_calories FROM (
            SELECT restaurant, item, item_gr, MAX(calories) as max_calories,
                ROW_NUMBER() OVER (PARTITION BY restaurant ORDER BY MAX(calories) DESC) as rank
            FROM fastfood
            WHERE restaurant IN ({','.join([f"'{r}'" for r in self.top_5_restaurants])})
            GROUP BY restaurant, item
        ) WHERE rank <= 5
        ORDER BY restaurant, max_calories DESC;
        """
        df = pd.read_sql_query(query, self.conn)
        df['label'] = df['item'] + '<br>' + df['item_gr']

        fig = px.sunburst(df, path=['restaurant', 'label'], values='max_calories', height=1200, width=1200)

        # Remove title from the figure itself
        fig.update_traces(textinfo="label+percent entry", textfont_size=16)
        fig.update_layout(title=None)

        return fig

    def get_pca_clusters_fig(self):
        """
        Generates the PCA plot for visualizing KMeans clusters.

        Returns:
            plotly.graph_objs._figure.Figure: The PCA scatter plot.
        """
        query = "SELECT item, item_gr, calories, total_fat, sugar, total_carb, protein, calcium, fiber, category FROM fastfood;"
        df = pd.read_sql_query(query, self.conn)

        # Normalize the features before PCA
        features = ['calories', 'total_fat', 'sugar', 'total_carb', 'protein', 'calcium', 'fiber']
        feature_df = df[features]
        category_df = df['category']

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_df)

        # Perform PCA
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(scaled_features)
        vis_df = pd.DataFrame(pca_result, columns=['PC1', 'PC2'])
        vis_df['category'] = category_df
        vis_df['item'] = df['item']
        vis_df['item_gr'] = df['item_gr']

        # Combine English and Greek names for hover
        vis_df['label'] = vis_df['item'] + ' | ' + vis_df['item_gr']

        # Create the plot
        fig = px.scatter(vis_df, x='PC1', y='PC2', color='category',
                         labels={'PC1': 'Principal Component 1', 'PC2': 'Principal Component 2'},
                         hover_name='label',  # Show English and Greek names on hover
                         template="plotly_white",
                         height=800)  # Increase plot height

        # Remove the title from the figure
        fig.update_layout(title=None)

        return fig
