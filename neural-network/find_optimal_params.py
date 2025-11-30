import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from model_trainer import train_model
from sequence_processor import load_sequences
import itertools
from datetime import datetime
import os
import tensorflow as tf
import multiprocessing
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

# Налаштування для використання всіх ядер CPU
physical_devices = tf.config.list_physical_devices('CPU')
try:
    tf.config.threading.set_inter_op_parallelism_threads(multiprocessing.cpu_count())
    tf.config.threading.set_intra_op_parallelism_threads(multiprocessing.cpu_count())
    for device in physical_devices:
        tf.config.experimental.set_memory_growth(device, True)
except:
    pass

# Налаштування для GPU
physical_devices = tf.config.list_physical_devices('GPU')
try:
    for device in physical_devices:
        tf.config.experimental.set_memory_growth(device, True)
except:
    pass

# Налаштування для паралельного виконання
tf.config.optimizer.set_jit(True)  # XLA оптимізація

def run_experiment(args):
    data_path, epochs, window_size, batch_size, lstm_units, i, results_dir = args
    try:
        # Генеруємо послідовності для конкретного розміру вікна
        pre_generated_data = load_sequences(data_path, window_size)
        
        model, history, accuracy = train_model(
            n_days=60,
            data_path=data_path,
            epochs=epochs,
            window_size=window_size,
            batch_size=batch_size,
            lstm_units=lstm_units,
            show_plot=False,
            save_model=False,
            pre_generated_data=pre_generated_data
        )
        if history is not None:
            # Зберігаємо графік
            plt.figure(figsize=(10, 6))
            plt.plot(history.history['accuracy'], label='Train Accuracy')
            plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
            plt.title(f'Model Accuracy (epochs={epochs}, window={window_size}, batch={batch_size}, units={lstm_units})')
            plt.xlabel('Epoch')
            plt.ylabel('Accuracy')
            plt.legend()
            plt.grid(True)
            plt.savefig(f"{results_dir}/plot_{i+1}.png")
            plt.close()
            return {
                'epochs': epochs,
                'window_size': window_size,
                'batch_size': batch_size,
                'lstm_units': lstm_units,
                'final_accuracy': accuracy,
                'best_val_accuracy': max(history.history['val_accuracy']),
                'best_epoch': np.argmax(history.history['val_accuracy']) + 1,
            }
    except Exception as e:
        print(f"Помилка при тестуванні параметрів: {str(e)}")
    return None

def create_advanced_visualizations(df_results, results_dir):
    """
    Створює розширені візуалізації результатів експерименту.
    
    Args:
        df_results (pd.DataFrame): DataFrame з результатами експерименту
        results_dir (str): Директорія для збереження графіків
    """
    # Налаштування стилю
    plt.style.use('seaborn')
    sns.set_palette("husl")
    
    # 1. 3D поверхня для візуалізації залежності точності від window_size та lstm_units
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Групуємо дані за window_size та lstm_units
    grouped = df_results.groupby(['window_size', 'lstm_units'])['best_val_accuracy'].mean().reset_index()
    
    # Створюємо сітку для 3D поверхні
    window_sizes = sorted(grouped['window_size'].unique())
    lstm_units = sorted(grouped['lstm_units'].unique())
    X, Y = np.meshgrid(window_sizes, lstm_units)
    Z = np.zeros_like(X)
    
    for i, window in enumerate(window_sizes):
        for j, units in enumerate(lstm_units):
            mask = (grouped['window_size'] == window) & (grouped['lstm_units'] == units)
            if mask.any():
                Z[j, i] = grouped.loc[mask, 'best_val_accuracy'].values[0]
    
    # Побудова 3D поверхні
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8)
    ax.set_xlabel('Window Size')
    ax.set_ylabel('LSTM Units')
    ax.set_zlabel('Validation Accuracy')
    ax.set_title('3D Surface Plot of Validation Accuracy')
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    plt.savefig(f"{results_dir}/3d_surface.png", bbox_inches='tight', dpi=300)
    plt.close()
    
    # 2. Теплова карта для візуалізації залежності точності від batch_size та epochs
    plt.figure(figsize=(12, 8))
    pivot_table = df_results.pivot_table(
        values='best_val_accuracy',
        index='batch_size',
        columns='epochs',
        aggfunc='mean'
    )
    sns.heatmap(pivot_table, annot=True, cmap='YlOrRd', fmt='.3f')
    plt.title('Heatmap of Validation Accuracy by Batch Size and Epochs')
    plt.savefig(f"{results_dir}/heatmap.png", bbox_inches='tight', dpi=300)
    plt.close()
    
    # 3. Боксплоти для розподілу точності по кожному параметру
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Distribution of Validation Accuracy by Parameter')
    
    sns.boxplot(x='window_size', y='best_val_accuracy', data=df_results, ax=axes[0,0])
    axes[0,0].set_title('Window Size')
    
    sns.boxplot(x='lstm_units', y='best_val_accuracy', data=df_results, ax=axes[0,1])
    axes[0,1].set_title('LSTM Units')
    
    sns.boxplot(x='batch_size', y='best_val_accuracy', data=df_results, ax=axes[1,0])
    axes[1,0].set_title('Batch Size')
    
    sns.boxplot(x='epochs', y='best_val_accuracy', data=df_results, ax=axes[1,1])
    axes[1,1].set_title('Epochs')
    
    plt.tight_layout()
    plt.savefig(f"{results_dir}/boxplots.png", bbox_inches='tight', dpi=300)
    plt.close()
    
    # 4. Лінійний графік з трендами для кожного параметра
    plt.figure(figsize=(15, 10))
    for param in ['window_size', 'lstm_units', 'batch_size', 'epochs']:
        grouped = df_results.groupby(param)['best_val_accuracy'].mean()
        plt.plot(grouped.index, grouped.values, marker='o', label=param)
    
    plt.xlabel('Parameter Value')
    plt.ylabel('Mean Validation Accuracy')
    plt.title('Trend of Validation Accuracy Across Parameters')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{results_dir}/trends.png", bbox_inches='tight', dpi=300)
    plt.close()

def experiment_with_parameters(data_path: str):
    """
    Експеримент з різними параметрами моделі.
    
    Args:
        data_path (str): Шлях до файлу з даними
    """
    params = {
        'epochs': [10, 20, 30, 40, 50],
        'window_size': [15, 30, 60, 120, 240],
        'batch_size': [16, 32, 64, 128],
        'lstm_units': [32, 64, 128, 256]
    }
    param_combinations = list(itertools.product(
        params['epochs'],
        params['window_size'],
        params['batch_size'],
        params['lstm_units']
    ))
    results_dir = f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(results_dir, exist_ok=True)

    # Формуємо аргументи для кожного процесу
    args_list = [
        (data_path, epochs, window_size, batch_size, lstm_units, i, results_dir)
        for i, (epochs, window_size, batch_size, lstm_units) in enumerate(param_combinations)
    ]

    # Використовуємо multiprocessing для паралельного запуску
    with multiprocessing.Pool(processes=2) as pool:
        results = list(pool.map(run_experiment, args_list))

    # Фільтруємо None
    results = [r for r in results if r is not None]

    if results:
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('best_val_accuracy', ascending=False)
        df_results.to_csv(f"{results_dir}/results.csv", index=False)
        print("\nНайкращі результати:")
        print(df_results.head().to_string())
        best_result = df_results.iloc[0]
        print("\nОптимальні параметри:")
        print(f"Epochs: {best_result['epochs']}")
        print(f"Window Size: {best_result['window_size']}")
        print(f"Batch Size: {best_result['batch_size']}")
        print(f"LSTM Units: {best_result['lstm_units']}")
        print(f"Best Validation Accuracy: {best_result['best_val_accuracy']:.4f}")

        # Створюємо розширені візуалізації
        create_advanced_visualizations(df_results, results_dir)
        
        return best_result
    else:
        print("Не вдалося отримати жодного результату")
        return None

if __name__ == "__main__":
    # Шлях до файлу з даними
    data_path = "data/BTCUSD_Daily_OHLC.csv"
    
    # Запуск експерименту
    best_params = experiment_with_parameters(data_path) 