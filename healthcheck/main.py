import os
from flask import Flask, request, render_template
from flask_mail import Mail, Message
from dotenv import load_dotenv
from uuid import uuid4
import time
import threading
from flask_apscheduler import APScheduler

load_dotenv()

app = Flask(__name__)
scheduler = APScheduler()

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# { "job@instance": {"confirmed": False, "timestamp": ...} }
state = {}

# { "fid": "job@instance" }
confirm_map = {}

mail = Mail(app)
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

def send_email_alert(job, instance, summary, link):
    msg = Message(subject=f"[ALERT] {job} is DOWN",
                  recipients=[ADMIN_EMAIL])
    msg.html = render_template("email_template.html", job=job, instance=instance, summary=summary, link=link)
    mail.send(msg)

@app.route('/')
def index():
    return "✅ Confirm Service Running"

@app.route('/alert', methods=['POST'])
def receive_alert():
    data = request.json
    for alert in data.get('alerts', []):
        job = alert['labels'].get('job')
        instance = alert['labels'].get('instance')
        summary = alert['annotations'].get('summary', 'No summary')
        if not job or not instance:
            continue  # skip if missing labels

        key = f"{job}@{instance}"

        # Skip if already confirmed
        if key in state and state[key]['confirmed']:
            print(f"[SKIPPED] Alert {key} already confirmed.")
            continue

        # Update or create alert state
        state[key] = {
            "confirmed": False,
            "timestamp": time.time()
        }

        # Create unique confirm link
        fid = uuid4().hex
        confirm_map[fid] = key
        confirm_link = f"http://127.0.0.1:8001/confirm/{fid}"
        with app.app_context():
            send_email_alert(job, instance, summary, confirm_link)

    return "OK"

@app.route('/confirm/<fid>')
def confirm(fid):
    key = confirm_map.get(fid)
    if key and key in state:
        state[key]['confirmed'] = True
        print(f"[CONFIRMED] Alert {key} confirmed via {fid}")
        return f"✅ Confirmed alert for {key}"
    return "❌ Invalid or expired link", 404

def cleanup():
    now = time.time()
    for key in list(state.keys()):
        data = state[key]
        if not data['confirmed'] and now - data['timestamp'] > 300:
            print(f"[RE-ALERT] {key} has not been confirmed after 5 minutes.")
            fid = uuid4().hex
            confirm_map[fid] = key
            state[key]['timestamp'] = now
            confirm_link = f"http://127.0.0.1:8001/confirm/{fid}"
            job, instance = key.split("@")
            with app.app_context():
                send_email_alert(job, instance, "Service is still down", confirm_link)
        elif data['confirmed']:
            del state[key]

if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    
    scheduler.add_job(id='cleanup_job', func=cleanup, trigger='interval', seconds=30)
    app.run(host='0.0.0.0', port=8001)