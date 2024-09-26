from database import Database
from data_loader import DataLoader
from translator import TranslatorModule
from figuremaker import FigureMaker
from classifier import Classifier
import dash
from dash import dcc, html
import logging

def main():
    """
    Main function to orchestrate the fast food nutrition analysis process.
    This function:
    1. Initializes and sets up the SQLite database.
    2. Loads and processes the CSV data into the database.
    3. Translates the item names into Greek.
    4. Classifies the food items based on their nutritional information.
    5. Exports the classification to a CSV file.
    6. Visualizes the data using Dash web app with various charts.
    """
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize and connect to the database
    logging.info("Initializing database connection...")
    db = Database(db_file="fastfood_nutrition.db")
    conn = db.connect()

    # Create the necessary table and load the CSV data
    logging.info("Creating table and loading CSV data into the database...")
    db.create_table()
    loader = DataLoader(connection=conn)
    loader.load_csv_to_db(csv_file="data/fastfood.csv", memory_fraction=0.5)
    logging.info("CSV data loaded successfully.")
    
    # Translate item names into Greek
    logging.info("Translating food item names into Greek...")
    translator = TranslatorModule(connection=conn, translation_csv="data/curated_translations.csv")
    db.populate_item_gr_column(translator=translator)
    logging.info("Translation completed successfully.")

    # Initialize the classifier and classify items
    logging.info("Classifying food items into categories (Main, Side, Dessert)...")
    classifier = Classifier(conn=conn)
    db.classify_items_and_add_category(classifier=classifier)
    db.export_classification_to_csv()
    logging.info("Classification completed and exported to 'food_categories.csv'.")

    # Create the figures using FigureMaker
    logging.info("Generating visualizations...")
    figure_maker = FigureMaker(conn=conn)
    max_calorie_fig = figure_maker.get_max_calorie_items_fig()
    avg_carbohydrates_fig = figure_maker.get_avg_carbohydrates_donut_fig()
    calorie_treemap_fig = figure_maker.get_calorie_treemap_fig()
    sunburst_calorie_fig = figure_maker.get_calorie_sunburst_fig()
    pca_fig = figure_maker.get_pca_clusters_fig()
    food_categories_table = figure_maker.get_food_categories_table()
    logging.info("Visualizations generated successfully.")

    # Setup the Dash app for visualization
    logging.info("Starting Dash web application for visualizations...")
    app = dash.Dash(__name__)

    # CSS Styling for the page layout
    app.layout = html.Div(style={'textAlign': 'center'}, children=[
        html.H1(children='Fast Food Nutrition Analysis'),

        html.Div([
            html.H2(children='Max Calorie Item per Top 5 Restaurants'),
            dcc.Graph(id='calorie-bubble-graph', figure=max_calorie_fig),
        ], style={'textAlign': 'center'}),

        html.Div([
            html.H2(children='Top 5 Restaurants by Average Carbohydrates'),
            dcc.Graph(id='carbohydrate-donut-graph', figure=avg_carbohydrates_fig),
        ], style={'textAlign': 'center'}),

        html.Div([
            html.H2(children='Calorie Breakdown (Treemap top 5 items)'),
            dcc.Graph(id='calorie-treemap-graph', figure=calorie_treemap_fig),
        ], style={'textAlign': 'center', 'display': 'inline-block'}),

        html.Div([
            html.H2(children='Calorie Breakdown (Sunburst top 5 items)'),
            dcc.Graph(id='sunburst-calorie-graph', figure=sunburst_calorie_fig),
        ], style={'textAlign': 'center', 'display': 'inline-block'}),

        html.Div([
            html.H2(children='PCA of Food Categories'),
            dcc.Graph(id='pca-cluster-graph', figure=pca_fig),
        ], style={'textAlign': 'center'}),

        html.Div([
            html.H2(children='Food Categories Table'),
            food_categories_table,  # Include the new table here
        ], style={'textAlign': 'center'}),
    ])

    # Run the Dash app on port 80
    app.run_server(host="0.0.0.0", port=80)

    # Close the database connection
    logging.info("Closing database connection...")
    conn.close()
    logging.info("Database connection closed. Program finished successfully.")


if __name__ == "__main__":
    main()
