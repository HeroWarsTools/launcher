import customtkinter as ctk
from tkinter import filedialog
import subprocess
import os

# Configurazione estetica (Tema e Colore)
ctk.set_appearance_mode("dark")  # Modi: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temi: "blue" (standard), "green", "dark-blue"

class AppLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurazione finestra principale
        self.title("Il Mio Launcher Moderno")
        self.geometry("500x300")

        # Variabile per memorizzare il percorso del file selezionato
        self.percorso_programma = ""

        # --- Interfaccia Utente (UI) ---
        
        self.label_titolo = ctk.CTkLabel(self, text="Launcher Programmi", font=("Roboto", 24))
        self.label_titolo.pack(pady=20)

        # Visualizzerà il percorso del file scelto
        self.label_percorso = ctk.CTkLabel(self, text="Nessun programma selezionato", wraplength=400)
        self.label_percorso.pack(pady=10)

        # Bottone "Esplora"
        self.btn_esplora = ctk.CTkButton(self, text="Esplora Risorse", command=self.seleziona_file)
        self.btn_esplora.pack(pady=10)

        # Bottone "Avvia"
        self.btn_avvia = ctk.CTkButton(self, text="AVVIA", command=self.avvia_programma, 
                                       fg_color="green", hover_color="darkgreen")
        self.btn_avvia.pack(pady=20)

    # --- Funzioni Logiche ---

    def seleziona_file(self):
        # Apre la finestra di dialogo del sistema operativo
        file_selezionato = filedialog.askopenfilename(
            title="Seleziona un programma",
            filetypes=[("Eseguibili", "*.exe"), ("Tutti i file", "*.*")]
        )
        
        if file_selezionato:
            self.percorso_programma = file_selezionato
            self.label_percorso.configure(text=f"Pronto per avviare:\n{os.path.basename(file_selezionato)}")

    def avvia_programma(self):
        if self.percorso_programma:
            try:
                # Avvia il processo in modo indipendente
                subprocess.Popen(self.percorso_programma)
            except Exception as e:
                self.label_percorso.configure(text=f"Errore: {e}")
        else:
            self.label_percorso.configure(text="Seleziona prima un file!")

# Avvio dell'applicazione
if __name__ == "__main__":
    app = AppLauncher()
    app.mainloop()