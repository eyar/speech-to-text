from celery import Celery
import subprocess
app = Celery('tasks', broker='amqp://guest@rabbitmq//', backend='rpc://')

@app.task
def transcribe(filename):
    result = subprocess.run(["deepspeech","--model","../../deepspeech-0.9.3-models.pbmm","--scorer","../../deepspeech-0.9.3-models.scorer","--audio",filename], capture_output=True, text=True)
    return result.stdout