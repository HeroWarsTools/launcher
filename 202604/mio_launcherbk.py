import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import subprocess
import os
import json

# Configurazione estetica
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DATA_FILE = "launcher_data.json"
IMG_FOLDER = "IMG"

# Assicuriamoci che la cartella immagini esista
if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

# Font raddoppiati o aumentati
FS_MENU = 30     # Font gigante per Modifica/Elimina
FS_SMALL = 18 
FS_MEDIUM = 21
FS_LARGE = 36

class ProgramDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, initial_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x600")
        self.result = None
        self.grab_set()
        self.focus_set()

        self.columnconfigure(0, weight=1)

        # CAMPI INPUT
        ctk.CTkLabel(self, text="Nome:", font=("Roboto", FS_SMALL)).pack(pady=(20, 0))
        self.entry_nome = ctk.CTkEntry(self, width=350, font=("Roboto", FS_SMALL))
        self.entry_nome.pack(pady=5)

        ctk.CTkLabel(self, text="Posizione:", font=("Roboto", FS_SMALL)).pack(pady=(10, 0))
        self.entry_pos = ctk.CTkEntry(self, width=350, font=("Roboto", FS_SMALL))
        self.entry_pos.pack(pady=5)

        ctk.CTkLabel(self, text="Percorso Programma:", font=("Roboto", FS_SMALL)).pack(pady=(10, 0))
        self.entry_path = ctk.CTkEntry(self, width=350, font=("Roboto", FS_SMALL))
        self.entry_path.pack(pady=5)
        ctk.CTkButton(self, text="Sfoglia EXE", command=self.sfoglia_exe).pack(pady=2)

        ctk.CTkLabel(self, text="Immagine (PNG/ICO):", font=("Roboto", FS_SMALL)).pack(pady=(10, 0))
        self.entry_img = ctk.CTkEntry(self, width=350, font=("Roboto", FS_SMALL))
        self.entry_img.pack(pady=5)
        ctk.CTkButton(self, text="Sfoglia Immagine", command=self.sfoglia_img).pack(pady=2)

        if initial_data:
            self.entry_nome.insert(0, initial_data.get('nome', ''))
            self.entry_pos.insert(0, str(initial_data.get('pos', '')))
            self.entry_path.insert(0, initial_data.get('path', ''))
            self.entry_img.insert(0, initial_data.get('img', ''))

        self.btn_salva = ctk.CTkButton(self, text="SALVA", fg_color="green", command=self.salva, font=("Roboto", FS_MEDIUM))
        self.btn_salva.pack(pady=40)

    def sfoglia_exe(self):
        p = filedialog.askopenfilename()
        if p: self.entry_path.delete(0, "end"); self.entry_path.insert(0, p)

    def sfoglia_img(self):
        p = filedialog.askopenfilename(filetypes=[("Immagini", "*.png *.ico *.jpg")])
        if p: self.entry_img.delete(0, "end"); self.entry_img.insert(0, p)

    def salva(self):
        self.result = {
            "nome": self.entry_nome.get(),
            "pos": int(self.entry_pos.get()) if self.entry_pos.get().isdigit() else None,
            "path": self.entry_path.get(),
            "img": self.entry_img.get()
        }
        self.destroy()

class CustomContextMenu(ctk.CTkToplevel):
    """ Finestra popup per emulare un menu con font giganti """
    def __init__(self, parent, x, y, app_info, callback_mod, callback_del):
        super().__init__(parent)
        self.overrideredirect(True) # Toglie i bordi della finestra
        self.geometry(f"+{x}+{y}")
        self.configure(fg_color="#1a1a1a")
        self.grab_set()

        # Bottone Modifica
        ctk.CTkButton(self, text="📝 MODIFICA", font=("Roboto", FS_MENU), 
                      anchor="w", fg_color="transparent", hover_color="#333333",
                      command=lambda: [callback_mod(app_info), self.destroy()]).pack(fill="x", padx=10, pady=5)
        
        # Bottone Elimina
        ctk.CTkButton(self, text="🗑️ ELIMINA", font=("Roboto", FS_MENU), 
                      anchor="w", fg_color="transparent", hover_color="#662222", text_color="#FF5555",
                      command=lambda: [callback_del(app_info), self.destroy()]).pack(fill="x", padx=10, pady=5)

        # Chiudi se si clicca fuori
        self.bind("<FocusOut>", lambda e: self.destroy())

class AppLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.dati = self.carica_dati()
        
        # Ripristino dimensioni
        geo = self.dati["settings"].get("geometry", "900x700")
        self.geometry(geo)
        self.title("Launcher Pro V3")

        # Evento per salvare le dimensioni quando si chiude
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.lbl_titolo = ctk.CTkLabel(self.header, text=self.dati["settings"]["titolo"], font=("Roboto", FS_LARGE, "bold"))
        self.lbl_titolo.pack(side="left")
        
        ctk.CTkButton(self.header, text="📝", width=40, command=self.rinomina_titolo).pack(side="left", padx=10)
        ctk.CTkButton(self.header, text="+ Aggiungi", font=("Roboto", FS_MEDIUM), command=self.aggiungi_nuovo).pack(side="right")

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="colonna")

        self.aggiorna_griglia()

    def carica_dati(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f: return json.load(f)
        return {"settings": {"titolo": "Launcher", "geometry": "900x700"}, "apps": []}

    def salva_dati(self):
        with open(DATA_FILE, "w") as f: json.dump(self.dati, f, indent=4)

    def on_closing(self):
        # Salva le dimensioni e la posizione correnti
        self.dati["settings"]["geometry"] = self.geometry()
        self.salva_dati()
        self.destroy()

    def rinomina_titolo(self):
        n = ctk.CTkInputDialog(text="Titolo:", title="Edit").get_input()
        if n: self.dati["settings"]["titolo"] = n; self.lbl_titolo.configure(text=n); self.salva_dati()

    def aggiorna_griglia(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        
        for app_info in self.dati["apps"]:
            idx = app_info["pos"] - 1
            riga, col = idx // 3, idx % 3

            cell = ctk.CTkFrame(self.scrollable_frame, fg_color="#2B2B2B", corner_radius=15)
            cell.grid(row=riga, column=col, padx=10, pady=10, sticky="nsew")
            
            # Caricamento immagine se presente
            img_ctk = None
            if app_info.get("img") and os.path.exists(app_info["img"]):
                try:
                    pil_img = Image.open(app_info["img"])
                    # Ridimensionamento mantenendo proporzioni
                    w, h = pil_img.size
                    new_h = 150
                    new_w = int((new_h / h) * w)
                    img_ctk = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))
                except: pass

            # Bottone con eventuale immagine
            btn = ctk.CTkButton(cell, text=app_info["nome"], font=("Roboto", FS_MEDIUM), 
                                image=img_ctk, compound="top", # Immagine sopra il testo
                                fg_color="transparent", hover_color="#3d3d3d",
                                command=lambda p=app_info["path"]: subprocess.Popen(p))
            btn.pack(expand=True, fill="both", padx=10, pady=10)
            
            # Numerino
            ctk.CTkLabel(cell, text=str(app_info["pos"]), font=("Roboto", 14), text_color="gray").place(x=10, y=5)

            # Bind tasto destro per Menu Gigante
            btn.bind("<Button-3>", lambda e, a=app_info: CustomContextMenu(self, e.x_root, e.y_root, a, self.modifica_app, self.elimina_app))

    def aggiungi_nuovo(self):
        d = ProgramDialog(self, "Aggiungi")
        self.wait_window(d)
        if d.result:
            if d.result["pos"] is None: d.result["pos"] = len(self.dati["apps"]) + 1
            self.dati["apps"].append(d.result)
            self.dati["apps"].sort(key=lambda x: x["pos"])
            self.salva_dati(); self.aggiorna_griglia()

    def modifica_app(self, app_info):
        d = ProgramDialog(self, "Modifica", initial_data=app_info)
        self.wait_window(d)
        if d.result:
            app_info.update(d.result)
            self.dati["apps"].sort(key=lambda x: x["pos"])
            self.salva_dati(); self.aggiorna_griglia()

    def elimina_app(self, app_info):
        if messagebox.askyesno("Elimina", f"Eliminare {app_info['nome']}?"):
            self.dati["apps"].remove(app_info); self.salva_dati(); self.aggiorna_griglia()

if __name__ == "__main__":
    app = AppLauncher()
    app.mainloop()
