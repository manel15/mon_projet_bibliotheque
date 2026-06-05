import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import requests

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class InterfaceBibliotheque(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestion de Bibliothèque & Assistant IA")
        self.geometry("1100x650")

        # Configuration des URLs du serveur Flask (Port 8000)
        self.backend_url = "http://127.0.0.1:8000/livres"
        self.chatbot_url = "http://127.0.0.1:8000/chatbot"

        # --- SYSTÈME DE GRILLE APPLI ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ========================================================
        # BARRE LATÉRALE DE NAVIGATION (À GAUCHE)
        # ========================================================
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BiblioTech", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=30)

        self.mode_label = ctk.CTkLabel(self.sidebar_frame, text="Thème graphique :", anchor="w")
        self.mode_label.grid(row=5, column=0, padx=20, pady=(350, 0))
        self.mode_option = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light"], command=self.change_theme)
        self.mode_option.grid(row=6, column=0, padx=20, pady=(10, 20))

        # ========================================================
        # ZONE DE TRAVAIL PRINCIPALE (À DROITE)
        # ========================================================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # ---- 1. Formulaire de saisie des livres ----
        self.form_frame = ctk.CTkScrollableFrame(self.main_frame, height=140, label_text="Informations du Livre")
        self.form_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.form_frame.grid_columnconfigure((0,1,2,3,4,5), weight=1)

        self.entry_titre = ctk.CTkEntry(self.form_frame, placeholder_text="Titre")
        self.entry_titre.grid(row=0, column=0, padx=5, pady=5)
        self.entry_auteur = ctk.CTkEntry(self.form_frame, placeholder_text="Auteur")
        self.entry_auteur.grid(row=0, column=1, padx=5, pady=5)
        self.entry_categorie = ctk.CTkComboBox(self.form_frame, values=["Roman", "Science-Fiction", "Fantastique", "Romantic", "Droit", "Informatique", "Science", "Théâtre", "Policier"])
        self.entry_categorie.grid(row=0, column=2, padx=5, pady=5)
        self.entry_annee = ctk.CTkEntry(self.form_frame, placeholder_text="Année")
        self.entry_annee.grid(row=0, column=3, padx=5, pady=5)
        self.entry_quantite = ctk.CTkEntry(self.form_frame, placeholder_text="Quantité")
        self.entry_quantite.grid(row=0, column=4, padx=5, pady=5)
        
        self.entry_statut = ctk.CTkComboBox(self.form_frame, values=["Disponible", "Emprunté"])
        self.entry_statut.grid(row=0, column=5, padx=5, pady=5)

        # ---- 2. Les Boutons CRUD ----
        self.actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.actions_frame.grid(row=1, column=0, sticky="ew", pady=5)

        self.btn_ajouter = ctk.CTkButton(self.actions_frame, text="➕ Ajouter", command=self.action_ajouter, font=ctk.CTkFont(weight="bold"))
        self.btn_ajouter.grid(row=0, column=0, padx=5)
        self.btn_modifier = ctk.CTkButton(self.actions_frame, text="✏️ Modifier", command=self.action_modifier, fg_color="orange", hover_color="#b87100")
        self.btn_modifier.grid(row=0, column=1, padx=5)
        self.btn_supprimer = ctk.CTkButton(self.actions_frame, text="🗑️ Supprimer", command=self.action_supprimer, fg_color="red", hover_color="#8a0000")
        self.btn_supprimer.grid(row=0, column=2, padx=5)

        # ---- 3. Le Tableau (Treeview stylisé) ----
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=28, fieldbackground="#2a2d2e", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#1f538d", foreground="white", relief="flat")

        self.tree = ttk.Treeview(self.main_frame, columns=("id", "titre", "auteur", "categorie", "annee", "quantite", "statut"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("titre", text="Titre")
        self.tree.heading("auteur", text="Auteur")
        self.tree.heading("categorie", text="Catégorie")
        self.tree.heading("annee", text="Année")
        self.tree.heading("quantite", text="Qté")
        self.tree.heading("statut", text="Statut")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("quantite", width=50, anchor="center")
        
        self.scrollbar = ctk.CTkScrollbar(self.main_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.grid(row=2, column=0, sticky="nsew", padx=(5, 0), pady=10)
        self.scrollbar.grid(row=2, column=1, sticky="ns", padx=(0, 5), pady=10)
        
        self.tree.bind("<Double-1>", self.charger_selection)

        # ---- 4. Zone du Chatbot IA (En Bas) ----
        self.chat_title = ctk.CTkLabel(self.main_frame, text="💬 Assistant Virtuel IA (Gemini)", font=ctk.CTkFont(weight="bold"))
        self.chat_title.grid(row=3, column=0, sticky="w", padx=5, pady=(10, 2))

        self.chat_frame = ctk.CTkFrame(self.main_frame)
        self.chat_frame.grid(row=4, column=0, sticky="ew", pady=(0, 0))
        
        self.entry_question = ctk.CTkEntry(self.chat_frame, placeholder_text="Posez une question sur vos livres (ex: Quels sont les romans disponibles ?)...", width=650)
        self.entry_question.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.btn_chat = ctk.CTkButton(self.chat_frame, text="Poser la question", command=self.action_chat)
        self.btn_chat.grid(row=0, column=1, padx=10, pady=10)
        
        self.lbl_reponse = ctk.CTkLabel(self.chat_frame, text="En attente de votre question...", text_color="gray", wraplength=800, justify="left")
        self.lbl_reponse.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        self.charger_livres()

    # ========================================================
    # LOGIQUE DES ACTIONS
    # ========================================================
    
    def action_ajouter(self):
        payload = {
            "titre": self.entry_titre.get(),
            "auteur": self.entry_auteur.get(),
            "categorie": self.entry_categorie.get(),
            "annee": self.entry_annee.get(),
            "quantite": self.entry_quantite.get(),
            "statut": self.entry_statut.get()
        }
        if not payload["titre"] or not payload["auteur"]:
            messagebox.showwarning("Erreur Saisie", "Le titre et l'auteur sont obligatoires.")
            return
        try:
            res = requests.post(self.backend_url, json=payload)
            if res.status_code == 200:
                messagebox.showinfo("Succès", "Livre inséré avec succès.")
                self.charger_livres()
                self.vider_champs()
        except Exception as e:
            messagebox.showerror("Erreur Connexion", f"Impossible de joindre le serveur backend : {e}")

    def action_modifier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un livre dans le tableau.")
            return
        
        # 🟢 CORRECTION : On récupère le VRAI ID de la BDD stocké dans les valeurs cachées du Treeview
        livre_id = self.tree.item(selected[0])['tags'][0]
        
        payload = {
            "titre": self.entry_titre.get(),
            "auteur": self.entry_auteur.get(),
            "categorie": self.entry_categorie.get(),
            "annee": self.entry_annee.get(),
            "quantite": self.entry_quantite.get(),
            "statut": self.entry_statut.get()
        }
        try:
            res = requests.put(f"{self.backend_url}/{livre_id}", json=payload)
            if res.status_code == 200:
                messagebox.showinfo("Succès", "Livre mis à jour.")
                self.charger_livres()
                self.vider_champs()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def action_supprimer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Sélection", "Sélectionnez une ligne à supprimer.")
            return
        
        # 🟢 CORRECTION : On récupère le VRAI ID via les tags
        livre_id = self.tree.item(selected[0])['tags'][0]
        
        if messagebox.askyesno("Confirmation", "Supprimer définitivement ce livre ?"):
            try:
                res = requests.delete(f"{self.backend_url}/{livre_id}")
                if res.status_code == 200:
                    messagebox.showinfo("Succès", "Livre supprimé.")
                    self.charger_livres()
                    self.vider_champs()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def action_chat(self):
        question = self.entry_question.get()
        if not question:
            return
        
        self.lbl_reponse.configure(text="L'IA réfléchit...", text_color="yellow")
        
        try:
            res = requests.post(self.chatbot_url, json={"question": question})
            if res.status_code == 200:
                reponse_serveur = res.json().get("reponse", "")
                
                # 🟢 CORRECTION DIAGNOSTIC : Si le serveur transmet l'erreur d'authentification de la clé
                if "Erreur" in reponse_serveur or "Google Gemini" in reponse_serveur:
                    self.lbl_reponse.configure(text=reponse_serveur, text_color="red")
                else:
                    self.lbl_reponse.configure(text=reponse_serveur, text_color="white")
            else:
                self.lbl_reponse.configure(text=f"Erreur Serveur ({res.status_code})", text_color="red")
        except Exception as e:
            self.lbl_reponse.configure(text=f"Erreur de connexion : {str(e)}", text_color="red")

    def charger_livres(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            res = requests.get(self.backend_url)
            if res.status_code == 200:
                compteur_visuel = 1
                for l in res.json():
                    # 🟢 CORRECTION : On affiche le compteur visuel (1, 2, 3...) MAIS on cache le vrai l["id"] dans l'argument `tags`
                    self.tree.insert("", "end", values=(compteur_visuel, l["titre"], l["auteur"], l["categorie"], l["annee"], l["quantite"], l["statut"]), tags=(l["id"],))
                    compteur_visuel += 1
        except Exception as e:
            print(f"Serveur non démarré : {e}")

    def charger_selection(self, event):
        selected = self.tree.selection()
        if selected:
            v = self.tree.item(selected)['values']
            self.vider_champs()
            self.entry_titre.insert(0, v[1])
            self.entry_auteur.insert(0, v[2])
            self.entry_categorie.set(v[3])  # 🟢 CORRECTION : .set() au lieu de .insert() pour un ComboBox
            self.entry_annee.insert(0, v[4])
            self.entry_quantite.insert(0, v[5])
            self.entry_statut.set(v[6])

    def vider_champs(self):
        self.entry_titre.delete(0, tk.END)
        self.entry_auteur.delete(0, tk.END)
        self.entry_categorie.set("Roman")
        self.entry_annee.delete(0, tk.END)
        self.entry_quantite.delete(0, tk.END)

    def change_theme(self, mode: str):
        ctk.set_appearance_mode(mode)

if __name__ == "__main__":
    app = InterfaceBibliotheque()
    app.mainloop()