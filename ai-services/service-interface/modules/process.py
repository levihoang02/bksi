import random
import time

# Simulate AI inference processing
def process(message):
    time.sleep(random.uniform(0.1, 0.5))

    # Simulate generating results
    result = {
        "prediction": random.choice(["cat", "dog", "bird"]),
        "confidence": random.uniform(0.5, 1.0)
    }

    # Simulate model accuracy and loss
    accuracy = random.uniform(0.85, 0.95)
    loss = random.uniform(0.1, 0.3)

    return result, {"accuracy": accuracy, "loss": loss}
