from prometheus_metrics import monitor_model_inference, track_model_accuracy, track_model_loss, monitor_model_tokens

@track_model_accuracy()
@track_model_loss()
@monitor_model_inference()
def process(message):
    print(message)
    pass