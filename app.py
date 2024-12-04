from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import numpy as np
import chardet

app = Flask(__name__)

CSV_DIR = "./data/csv_files/"
CSV_FILE_PATH_LAPTOP = './data/csv_files/laptop_full_short.csv'
CSV_FILE_PATH_MOBILE = './data/csv_files/mobiles_full.csv'
CSV_FILE_PATH_HEADPHONES = './data/csv_files/Headphones.csv'
CSV_FILE_PATH_TV = './data/csv_files/tv.csv'
CSV_FILE_PATH_SMART_WATCH = './data/csv_files/smartwatch.csv'
STATIC_FOLDER = './static/comparison'


def get_top_products(category, budget):
    file_path = os.path.join(CSV_DIR, f"{category}.csv") 
    try:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')  
    except FileNotFoundError:
        return None

    df_filtered = df[df['Selling Price'] <= budget]
    df_sorted = df_filtered.sort_values(by='Ratings', ascending=False)

    return df_sorted.head(5)

def create_comparison_charts(products, chart_type):
    MAX_LABEL_LENGTH = 15 

    product_names = [
        (product['Name'][:MAX_LABEL_LENGTH] + '...') if len(product['Name']) > MAX_LABEL_LENGTH else product['Name']
        for product in products
    ]
    selling_price = [product['Selling Price'] for product in products]
    mrp = [product['MRP'] for product in products]
    discount = [product['Discount'] for product in products]
    ratings = [product['Ratings'] for product in products]

    # BAR CHART
    if chart_type == 'Bar':
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=product_names, y=selling_price, name='Selling Price'))
        fig1.add_trace(go.Bar(x=product_names, y=mrp, name='MRP'))
        fig1.update_layout(title="Selling Price vs MRP", barmode='group', xaxis_title="Product Name", yaxis_title="Price")

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=product_names, y=discount, name='Discount'))
        fig2.add_trace(go.Bar(x=product_names, y=ratings, name='Ratings'))
        fig2.update_layout(title="Discount vs Ratings", barmode='group', xaxis_title="Product Name", yaxis_title="Values")

    # LINE CHART
    elif chart_type == 'Line':
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=product_names, y=selling_price, mode='lines+markers', name='Selling Price'))
        fig1.add_trace(go.Scatter(x=product_names, y=mrp, mode='lines+markers', name='MRP'))
        fig1.update_layout(title="Selling Price vs MRP", xaxis_title="Product Name", yaxis_title="Price")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=product_names, y=discount, mode='lines+markers', name='Discount'))
        fig2.add_trace(go.Scatter(x=product_names, y=ratings, mode='lines+markers', name='Ratings'))
        fig2.update_layout(title="Discount vs Ratings", xaxis_title="Product Name", yaxis_title="Values")

    # PIE CHART
    elif chart_type == 'Pie':
        fig1 = go.Figure()
        fig1.add_trace(go.Pie(labels=product_names, values=selling_price, name='Selling Price'))
        fig1.add_trace(go.Pie(labels=product_names, values=mrp, name='MRP'))
        fig1.update_layout(title="Selling Price vs MRP")

        fig2 = go.Figure()
        fig2.add_trace(go.Pie(labels=product_names, values=discount, name='Discount'))
        fig2.add_trace(go.Pie(labels=product_names, values=ratings, name='Ratings'))
        fig2.update_layout(title="Discount vs Ratings")

    # HEATMAP 
    elif chart_type == 'Heatmap':
        fig1 = go.Figure(data=go.Heatmap(
            z=[selling_price, mrp],
            x=product_names,
            colorscale='Viridis'
        ))
        fig1.update_layout(title="Selling Price vs MRP", xaxis_title="Product Name", yaxis_title="Price")

        fig2 = go.Figure(data=go.Heatmap(
            z=[discount, ratings],
            x=product_names,
            colorscale='Viridis'
        ))
        fig2.update_layout(title="Discount vs Ratings", xaxis_title="Product Name", yaxis_title="Values")

    return pio.to_html(fig1, full_html=False), pio.to_html(fig2, full_html=False)

def detect_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/laptop")
def laptop():
    try:
        encoding = detect_encoding(CSV_FILE_PATH_LAPTOP)
        df = pd.read_csv(CSV_FILE_PATH_LAPTOP, encoding=encoding)

        product_names = df['Name'].tolist()
    except Exception as e:
        product_names = []
        print(f"Error loading CSV file: {e}")
    return render_template('laptop.html', product_names=product_names)

@app.route('/generate-graphs', methods=['POST'])
def generate_graphs():
    data = request.json
    selected_products = data.get('products')

    if not selected_products or len(selected_products) != 4:
        return jsonify({'message': 'Please select exactly 4 products'}), 400

    try:
        encoding = detect_encoding(CSV_FILE_PATH_LAPTOP)
        df = pd.read_csv(CSV_FILE_PATH_LAPTOP, encoding=encoding)
    except Exception as e:
        return jsonify({'message': f'Error loading CSV file: {e}'}), 500

    filtered_data = df[df['Name'].isin(selected_products)]

    if filtered_data.empty:
        return jsonify({'message': 'No data available for the selected products'}), 404

    attributes = ["Selling Price", "MRP", "Ratings", "Reviews"]
    graph_paths = []

    for attribute in attributes:
        if attribute not in filtered_data.columns:
            continue

        fig = go.Figure()

        for _, row in filtered_data.iterrows():
            truncated_label = row['Name'][:10] + "..." if len(row['Name']) > 10 else row['Name']
            full_label = row['Name']

            fig.add_trace(go.Bar(
                x=[truncated_label],
                y=[row[attribute]],
                name=truncated_label,
                text=f"{full_label}<br>{attribute}: {row[attribute]}",
                hoverinfo="text",
                textposition='auto'
            ))

        fig.update_layout(
            title=f"{attribute} Comparison of Selected Products",
            xaxis_title="Product Name",
            yaxis_title=attribute,
            barmode='group',
            template="plotly_dark"
        )

        graph_filename = f"{attribute.replace(' ', '_')}_comparison_headphones.html"
        graph_path = os.path.join(STATIC_FOLDER, graph_filename)
        fig.write_html(graph_path)
        graph_paths.append(f"static/comparison/{graph_filename}")

    return jsonify({
        'message': 'Graphs generated successfully',
        'graph_paths': graph_paths
    }), 200


@app.route("/smart_watch")
def smart_watch():
    try:
        encoding = detect_encoding(CSV_FILE_PATH_SMART_WATCH)
        df = pd.read_csv(CSV_FILE_PATH_SMART_WATCH, encoding=encoding)

        product_names = df['Name'].tolist()
    except Exception as e:
        product_names = []
        print(f"Error loading CSV file: {e}")
    return render_template('smart_watch.html', product_names=product_names)

@app.route('/generate-graphs1', methods=['POST'])
def generate_graphs1():
    data = request.json
    selected_products = data.get('products')

    if not selected_products or len(selected_products) != 4:
        return jsonify({'message': 'Please select exactly 4 products'}), 400

    try:
        encoding = detect_encoding(CSV_FILE_PATH_SMART_WATCH)
        df = pd.read_csv(CSV_FILE_PATH_SMART_WATCH, encoding=encoding)
    except Exception as e:
        return jsonify({'message': f'Error loading CSV file: {e}'}), 500

    filtered_data = df[df['Name'].isin(selected_products)]

    if filtered_data.empty:
        return jsonify({'message': 'No data available for the selected products'}), 404

    attributes = ["Selling Price", "MRP", "Ratings", "Reviews"]
    graph_paths = []

    for attribute in attributes:
        if attribute not in filtered_data.columns:
            continue

        fig = go.Figure()

        for _, row in filtered_data.iterrows():
            truncated_label = row['Name'][:10] + "..." if len(row['Name']) > 10 else row['Name']
            full_label = row['Name']

            fig.add_trace(go.Bar(
                x=[truncated_label],
                y=[row[attribute]],
                name=truncated_label,
                text=f"{full_label}<br>{attribute}: {row[attribute]}",
                hoverinfo="text",
                textposition='auto'
            ))

        fig.update_layout(
            title=f"{attribute} Comparison of Selected Products",
            xaxis_title="Product Name",
            yaxis_title=attribute,
            barmode='group',
            template="plotly_dark"
        )

        graph_filename = f"{attribute.replace(' ', '_')}_comparison_headphones.html"
        graph_path = os.path.join(STATIC_FOLDER, graph_filename)
        fig.write_html(graph_path)
        graph_paths.append(f"static/comparison/{graph_filename}")

    return jsonify({
        'message': 'Graphs generated successfully',
        'graph_paths': graph_paths
    }), 200


@app.route("/headphones")
def headphones():
    try:
        encoding = detect_encoding(CSV_FILE_PATH_HEADPHONES)
        df = pd.read_csv(CSV_FILE_PATH_HEADPHONES, encoding=encoding)

        product_names = df['Name'].tolist()
    except Exception as e:
        product_names = []
        print(f"Error loading CSV file: {e}")
    return render_template('headphones.html', product_names=product_names)


@app.route('/generate-graphs3', methods=['POST'])
def generate_graphs3():
    data = request.json
    selected_products = data.get('products')

    if not selected_products or len(selected_products) != 4:
        return jsonify({'message': 'Please select exactly 4 products'}), 400

    try:
        encoding = detect_encoding(CSV_FILE_PATH_HEADPHONES)
        df = pd.read_csv(CSV_FILE_PATH_HEADPHONES, encoding=encoding)
    except Exception as e:
        return jsonify({'message': f'Error loading CSV file: {e}'}), 500

    filtered_data = df[df['Name'].isin(selected_products)]

    if filtered_data.empty:
        return jsonify({'message': 'No data available for the selected products'}), 404

    attributes = ["Selling Price", "MRP"]
    graph_paths = []

    for attribute in attributes:
        if attribute not in filtered_data.columns:
            continue

        fig = go.Figure()

        for _, row in filtered_data.iterrows():
            truncated_label = row['Name'][:10] + "..." if len(row['Name']) > 10 else row['Name']
            full_label = row['Name']

            fig.add_trace(go.Bar(
                x=[truncated_label],
                y=[row[attribute]],
                name=truncated_label,
                text=f"{full_label}<br>{attribute}: {row[attribute]}",
                hoverinfo="text",
                textposition='auto'
            ))

        fig.update_layout(
            title=f"{attribute} Comparison of Selected Products",
            xaxis_title="Product Name",
            yaxis_title=attribute,
            barmode='group',
            template="plotly_dark"
        )

        graph_filename = f"{attribute.replace(' ', '_')}_comparison_headphones.html"
        graph_path = os.path.join(STATIC_FOLDER, graph_filename)
        fig.write_html(graph_path)
        graph_paths.append(f"static/comparison/{graph_filename}")

    return jsonify({
        'message': 'Graphs generated successfully',
        'graph_paths': graph_paths
    }), 200


@app.route("/mobiles")
def mobiles():
    try:
        encoding = detect_encoding(CSV_FILE_PATH_MOBILE)
        df = pd.read_csv(CSV_FILE_PATH_MOBILE, encoding=encoding)

        product_names = df['Name'].tolist()
    except Exception as e:
        product_names = []
        print(f"Error loading CSV file: {e}")
    return render_template('mobiles.html', product_names=product_names)

@app.route('/generate-graphs4', methods=['POST'])
def generate_graphs4():
    data = request.json
    selected_products = data.get('products')

    if not selected_products or len(selected_products) != 4:
        return jsonify({'message': 'Please select exactly 4 products'}), 400

    try:
        encoding = detect_encoding(CSV_FILE_PATH_MOBILE)
        df = pd.read_csv(CSV_FILE_PATH_MOBILE, encoding=encoding)
    except Exception as e:
        return jsonify({'message': f'Error loading CSV file: {e}'}), 500

    filtered_data = df[df['Name'].isin(selected_products)]

    if filtered_data.empty:
        return jsonify({'message': 'No data available for the selected products'}), 404

    attributes = ["Selling Price", "MRP", "Ratings", "Reviews"]
    graph_paths = []

    for attribute in attributes:
        if attribute not in filtered_data.columns:
            continue

        fig = go.Figure()

        for _, row in filtered_data.iterrows():
            truncated_label = row['Name'][:10] + "..." if len(row['Name']) > 10 else row['Name']
            full_label = row['Name']

            fig.add_trace(go.Bar(
                x=[truncated_label],
                y=[row[attribute]],
                name=truncated_label,
                text=f"{full_label}<br>{attribute}: {row[attribute]}",
                hoverinfo="text",
                textposition='auto'
            ))

        fig.update_layout(
            title=f"{attribute} Comparison of Selected Products",
            xaxis_title="Product Name",
            yaxis_title=attribute,
            barmode='group',
            template="plotly_dark"
        )

        graph_filename = f"{attribute.replace(' ', '_')}_comparison_headphones.html"
        graph_path = os.path.join(STATIC_FOLDER, graph_filename)
        fig.write_html(graph_path)
        graph_paths.append(f"static/comparison/{graph_filename}")

    return jsonify({
        'message': 'Graphs generated successfully',
        'graph_paths': graph_paths
    }), 200


@app.route("/tv")
def tv():
    try:
        encoding = detect_encoding(CSV_FILE_PATH_TV)
        df = pd.read_csv(CSV_FILE_PATH_TV, encoding=encoding)

        product_names = df['Name'].tolist()
    except Exception as e:
        product_names = []
        print(f"Error loading CSV file: {e}")
    return render_template('tv.html', product_names=product_names)

@app.route('/generate-graphs2', methods=['POST'])
def generate_graphs2():
    data = request.json
    selected_products = data.get('products')

    if not selected_products or len(selected_products) != 4:
        return jsonify({'message': 'Please select exactly 4 products'}), 400

    try:
        encoding = detect_encoding(CSV_FILE_PATH_TV)
        df = pd.read_csv(CSV_FILE_PATH_TV, encoding=encoding)
    except Exception as e:
        return jsonify({'message': f'Error loading CSV file: {e}'}), 500

    filtered_data = df[df['Name'].isin(selected_products)]

    if filtered_data.empty:
        return jsonify({'message': 'No data available for the selected products'}), 404

    attributes = ["Selling Price", "MRP", "Ratings", "Reviews"]
    graph_paths = []

    for attribute in attributes:
        if attribute not in filtered_data.columns:
            continue

        fig = go.Figure()

        for _, row in filtered_data.iterrows():
            truncated_label = row['Name'][:10] + "..." if len(row['Name']) > 10 else row['Name']
            full_label = row['Name']

            fig.add_trace(go.Bar(
                x=[truncated_label],
                y=[row[attribute]],
                name=truncated_label,
                text=f"{full_label}<br>{attribute}: {row[attribute]}",
                hoverinfo="text",
                textposition='auto'
            ))

        fig.update_layout(
            title=f"{attribute} Comparison of Selected Products",
            xaxis_title="Product Name",
            yaxis_title=attribute,
            barmode='group',
            template="plotly_dark"
        )

        graph_filename = f"{attribute.replace(' ', '_')}_comparison_headphones.html"
        graph_path = os.path.join(STATIC_FOLDER, graph_filename)
        fig.write_html(graph_path)
        graph_paths.append(f"static/comparison/{graph_filename}")

    return jsonify({
        'message': 'Graphs generated successfully',
        'graph_paths': graph_paths
    }), 200


@app.route("/searching")
def searching():
    return render_template("searching.html")

@app.route("/budget_searching", methods=['GET','POST'])
def budget_searching():
    csv_files1 = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
    return render_template("budget_searching.html", csv_files1 = csv_files1)

@app.route('/result', methods=['POST'])
def result():
    category = request.form['category']
    budget = float(request.form['budget'])
    chart_type = request.form['chart_type']

    products = get_top_products(category, budget)

    if products is None or products.empty:
        return render_template('result.html', message="No products found within the budget")

    products_dict = products.to_dict(orient='records')

    chart1, chart2 = create_comparison_charts(products_dict, chart_type)

    return render_template('result.html', products=products_dict, chart1=chart1, chart2=chart2)

@app.route("/analysis")
def analysis():
    csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
    return render_template("analysis.html", csv_files=csv_files)

@app.route("/visualize", methods=["POST"])
def visualize():
    selected_file = request.form["file"]
    x_column = request.form["x_axis"]
    y_column = request.form["y_axis"]
    graph_type = request.form["graph_type"]

    file_path = os.path.join(CSV_DIR, selected_file)

    try:
        encoding = detect_encoding(file_path)
        df = pd.read_csv(file_path, encoding=encoding)
    except Exception as e:
        return f"Error loading file: {e}"

    if graph_type == "bar":
        fig = px.bar(df, x=x_column, y=y_column)
    elif graph_type == "line":
        fig = px.line(df, x=x_column, y=y_column)
    elif graph_type == "pie":
        fig = px.pie(df, x=x_column, y=y_column)
    else:
        return "Invalid graph type!"

    graph_html = pio.to_html(fig, full_html=False)
    return render_template("graph.html", graph_html=graph_html)

if __name__ == "__main__":
    app.run(debug=True)
