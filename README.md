# FastfoodNutritionAnalyzer

# FastfoodNutritionAnalyzer

## Setup Instructions

### 1. Prerequisites

- Docker installed on your system. (Recommended for isolated environment, ease of setup, and automation)
- Python 3.11+ (if running locally without Docker).
- Required Python packages listed in `requirements.txt`.

### 2. Running the Application with Docker (Recommended)

#### **Steps (Same for Windows, Linux, and macOS)**:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/OrestisDrow/FastfoodNutritionAnalyzer
    cd FastfoodNutritionAnalyzer
    ```

2. **Build and run the Docker container**:
    ```bash
    docker-compose build
    docker-compose up
    ```

   - This will:
      - Create a new SQLite database with the fast food nutritional data.
      - Add Greek translations of the items and classify them into `Main`, `Side`, or `Dessert`.
      - Start a Dash server to visualize the data.

3. **Access the application**:
    Open your web browser and navigate to `http://localhost:80` to view the visualizations. The visualizations/plots are interactive, feel free to explore the visual drill-downs.

### 3. Running the Application Locally (Without Docker)

#### **For Linux/macOS**:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/OrestisDrow/FastfoodNutritionAnalyzer
    cd FastfoodNutritionAnalyzer
    ```

2. **Set up a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the main script**:
    ```bash
    python src/main.py
    ```

5. **Access the Dash web application**:
    Open your web browser and navigate to `http://localhost:80`.

#### **For Windows**:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/OrestisDrow/FastfoodNutritionAnalyzer
    cd FastfoodNutritionAnalyzer
    ```

2. **Set up a virtual environment**:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the main script**:
    ```bash
    python src\main.py
    ```

5. **Access the Dash web application**:
    Open your web browser and navigate to `http://localhost:80`.

### 4. Running Unit Tests

To run the tests, use the following command:
```bash
pytest
```

This will run the unit tests located in the `tests/` directory. The project includes a few tests to demonstrate basic unit testing.

## Project Components

### 1. `data_loader.py`
Handles the loading and cleaning of fast food nutrition data from a CSV file into the SQLite database. It includes functionality to handle large datasets by calculating chunk sizes based on available memory.

### 2. `translator.py`
Translates food item names from English to Greek using a curated dictionary. If a translation is not found in the dictionary, it uses Google Translate as a fallback. Handles large datasets by processing data in memory-efficient chunks.

### 3. `classifier.py`
Uses KMeans clustering to categorize food items into `Main`, `Side`, or `Dessert`. The classification is based on several nutritional features, such as calories, total fat, sugar, carbohydrates, etc. It is NOT based on names, since names can be misleading, for example 4 chicken nuggets can be a side dish whereas 20 would be considered a meal, thus nutritional content might be a better indicator

### 4. `figuremaker.py`
Generates visualizations for nutritional data, including:
- **Max Calorie Item** per top 5 restaurants (scatter plot).
- **Average Carbohydrates** per top 5 restaurants (donut chart).
- **Calorie Breakdown** (treemap and sunburst charts).
- **PCA (Principal Component Analysis) of Food Categories** based on nutritional content, used for visualizing the category clusters.

### 5. `main.py`
The main entry point of the application that orchestrates:
- Database initialization.
- Data loading and cleaning.
- Item translation.
- Classification into categories.
- Visualization using Dash and plotly.

## Classification Approach and Decision Making

### Why KMeans for Unsupervised Classification

#### Unsupervised Learning Fit:
- Since the task did not involve manually labeling the data, **KMeans** allowed the data to reveal its natural groupings. 
- By clustering into three distinct groups, we could later interpret these clusters as "Main," "Side," and "Dessert" based on their average nutritional characteristics.

#### Feature Selection:
- The clustering was performed using relevant features like **calories, protein, fat, carbohydrates, sugar, fiber, and calcium**. These features provide the KMeans algorithm with enough detail to distinguish between different types of food items.

#### Post-Clustering Interpretation:
- After KMeans assigned each item to one of the three clusters, I calculated the average nutritional values for each cluster to interpret their meaning. 
- The clusters were then mapped to **"Main," "Side," and "Dessert"** categories based on characteristics like high calories and protein for Main, high sugar and carbs for Dessert, and moderate calories for Side.

#### Visualization:
- To confirm that the clusters were distinct, I used **PCA (Principal Component Analysis)** to reduce the data to two dimensions and plotted the items with their cluster assignments. This visual representation helped verify that the clusters made sense.

#### Evaluation:
- While there isn’t a formal accuracy evaluation for unsupervised learning, I used **cluster inertia** and **visual inspection** via PCA to ensure that the clusters formed coherent groups.

#### Why KMeans Works for This Task:
- **Centroid-based clustering**, such as KMeans, groups items by minimizing the within-cluster variance. Since the nutritional content for "Main," "Side," and "Dessert" items is naturally different, KMeans found meaningful clusters, which were later mapped to the food categories.

---

### How I Named the Clusters

Once the clusters were formed, I examined the **cluster centroids** (the average nutritional values for each cluster) to label them as "Main," "Side," and "Dessert." Below is a breakdown of the centroids:

#### Cluster 1: Side
- **Calories**: Low
- **Protein**: Low
- **Fat**: Low
- **Carbs**: Low to Moderate
- Interpretation: This cluster represents smaller portion items with lower energy content, typically sides like fries, salads, or small portions.

#### Cluster 2: Main
- **Calories**: Moderate to High
- **Protein**: Moderate
- **Fat**: Moderate
- **Carbs**: Moderate
- Interpretation: This cluster contains items with a higher caloric value and more balanced nutrients, making it a good fit for main dishes like sandwiches or burgers.

#### Cluster 3: Dessert
- **Calories**: High
- **Sugar**: Very High
- **Carbs**: High
- Interpretation: Items in this cluster are typically high in sugar and carbohydrates, which are characteristic of desserts like cookies, cakes, or sweet drinks.

By mapping these centroids to the categories, I ensured that each cluster was appropriately labeled, and the final classification results were exported to a CSV.

---

### Conclusion:
The use of **KMeans** for this task enabled an unsupervised approach to grouping food items based on their nutritional content. The post-clustering interpretation ensured the clusters were meaningfully labeled as **"Main," "Side," and "Dessert"** based on average nutritional values and cluster characteristics. Using **PCA** for visualization further validated the cluster separation.

### Additional Notes

- The project follows clean coding principles, with attention to readability and maintainability. It includes docstrings, type hints, logging and an overall structured project layout in case you want to dive deeper into the code. I aimed it to be as production ready as possible compared to the time given to me. 

## Future Improvements

- Expand unit testing to cover more modules and edge cases.
- Improve error handling and robustness in the translation module.
- Add more visualizations for deeper insights into the nutritional data.
- Optimize the KMeans clustering model for better categorization.

## License

This project is licensed under the MIT License.

