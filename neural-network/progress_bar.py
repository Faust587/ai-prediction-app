from tensorflow.keras.callbacks import Callback

class VisualProgressBar(Callback):
    def __init__(self, total_epochs, bar_width=30):
        self.total_epochs = total_epochs
        self.bar_width = bar_width

    def on_epoch_end(self, epoch, logs=None):
        percent = (epoch + 1) / self.total_epochs
        filled_len = int(self.bar_width * percent)
        bar = '=' * filled_len + '>' + ' ' * (self.bar_width - filled_len - 1)
        acc = logs.get('accuracy', 0)
        val_acc = logs.get('val_accuracy', 0)
        print(f"\r[{bar}] {int(percent * 100)}% — Epoch {epoch + 1}/{self.total_epochs} | acc={acc:.4f} | val_acc={val_acc:.4f}") 