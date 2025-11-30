import tensorflow as tf
import platform

def check_gpu_availability():
    """
    Check if GPU is available and print system information.
    """
    print("System Information:")
    print(f"Python version: {platform.python_version()}")
    print(f"TensorFlow version: {tf.__version__}")
    print(f"Platform: {platform.platform()}")
    
    # Check for Metal device
    metal_devices = tf.config.list_physical_devices('GPU')
    if metal_devices:
        print("\nMetal GPU is available!")
        print("Available devices:")
        for device in metal_devices:
            print(f"  - {device}")
        
        # Configure memory growth
        try:
            for device in metal_devices:
                tf.config.experimental.set_memory_growth(device, True)
            print("\nMemory growth enabled for all GPU devices")
        except RuntimeError as e:
            print(f"\nError configuring GPU memory growth: {e}")
    else:
        print("\nNo Metal GPU devices found. Running on CPU.")
    
    return len(metal_devices) > 0 