
import requests


USER_KEY = 'unm6h553h251f8upmssx5p5rbem881'
APP_TOKEN = 'ac4b78642pz97vcifowhe4bmorpz6w'
def send_pushover_notification(message):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        'token': APP_TOKEN,
        'user': USER_KEY,
        'message': message
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Notification sent successfully")
    else:
        print(f"Failed to send notification: {response.text}")
# Example usage
send_pushover_notification("This is a test notification from my Python script.\n Check new push capabilities of Heroku Git")
