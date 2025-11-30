import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Mock data
np.random.seed(42)
data = {
    'epochs': np.random.choice([10, 20, 30, 40, 50], 100),
    'window_size': np.random.choice([15, 30, 60, 120, 240], 100),
    'batch_size': np.random.choice([16, 32, 64, 128], 100),
    'lstm_units': np.random.choice([32, 64, 128, 256], 100),
    'best_val_accuracy': np.random.rand(100) * 0.57  # Scale to max 0.57
}

df_results = pd.DataFrame(data)

def create_interesting_visualizations(df_results):
    sns.set_theme(style="whitegrid")
    
    # 1. Pair Plot
    sns.pairplot(df_results, hue='epochs', palette='husl')
    plt.suptitle('Pair Plot of Parameters and Accuracy', y=1.02)
    plt.show()
    
    # 2. Violin Plot
    plt.figure(figsize=(12, 8))
    sns.violinplot(x='window_size', y='best_val_accuracy', data=df_results, palette='muted')
    plt.title('Violin Plot of Validation Accuracy by Window Size')
    plt.show()
    
    # 3. Facet Grid
    g = sns.FacetGrid(df_results, col='batch_size', hue='lstm_units', palette='coolwarm', col_wrap=2, height=4)
    g.map(sns.scatterplot, 'epochs', 'best_val_accuracy', alpha=0.7)
    g.add_legend()
    plt.suptitle('Facet Grid of Accuracy by Batch Size and LSTM Units', y=1.02)
    plt.show()
    
    # 4. Swarm Plot
    plt.figure(figsize=(12, 8))
    sns.swarmplot(x='lstm_units', y='best_val_accuracy', data=df_results, palette='deep')
    plt.title('Swarm Plot of Validation Accuracy by LSTM Units')
    plt.show()

# Call the function to create visualizations
create_interesting_visualizations(df_results)