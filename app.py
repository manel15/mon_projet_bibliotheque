import os
import sqlite3
from flask import Flask, request, jsonify
# 🟢 On utilise le nouveau package officiel de Google
from google import genai

app = Flask(__name__)

# Configuration de la base de données
DB_NAME = "bibliotheque.db"

def init_db():
    """Crée la base de données et insère des livres de test si elle est vide."""
    print("Initialisation de la base de données...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Création propre de la table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            auteur TEXT,
            categorie TEXT,
            annee TEXT,
            quantite TEXT,
            statut TEXT
        )
    ''')
    conn.commit()
    
    # Insertion de livres de test si la table est vide
    cursor.execute("SELECT COUNT(*) FROM livres")
    if cursor.fetchone()[0] == 0:
        livres_test = [
            ("Le Petit Prince", "Antoine de Saint-Exupéry", "Roman", "1943", "5", "Disponible"),
            ("Les Misérables", "Victor Hugo", "Roman", "1862", "2", "Disponible"),
            ("1984", "George Orwell", "Science-Fiction", "1949", "0", "Emprunté"),
            ("Le Code civil", "Collectif", "Droit", "1804", "1", "Disponible")
        ]
        cursor.executemany("INSERT INTO livres (titre, auteur, categorie, annee, quantite, statut) VALUES (?, ?, ?, ?, ?, ?)", livres_test)
        conn.commit()
    conn.close()
    print("Base de données prête !")


# --- CONFIGURATION GEMINI AI INITIALE (CORRIGÉE) ---
# 🔑 ATTENTION : Ta clé doit obligatoirement commencer par "AIzaSy..." générée sur Google AI Studio
GOOGLE_API_KEY = "AQ.Ab8RN6KuVMm9EM8WXeUR36iuzNY0t8Rp3ToIQU1wXdKSxiP69Q" 

try:
    # Initialisation du client avec la nouvelle syntaxe officielle
    client = genai.Client(api_key="AQ.Ab8RN6KuVMm9EM8WXeUR36iuzNY0t8Rp3ToIQU1wXdKSxiP69Q")
    print("-> [OK] Nouveau client Gemini initié avec succès ! ✅")
except Exception as e:
    print(f"-> [ERREUR] Échec de l'initialisation Gemini : {e}")

def interroger_gemini(prompt, contexte_db):
    try:
        # On passe la question en minuscules pour faciliter la recherche
        question = prompt.lower()
        
        # Connexion locale pour analyser les livres disponibles
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        if "disponible" in question or "quels sont les romans" in question or "recommand" in question:
            cursor.execute("SELECT titre, auteur FROM livres WHERE statut = 'Disponible'")
            livres = cursor.fetchall()
            conn.close()
            if livres:
                liste = ", ".join([f"'{l[0]}' de {l[1]}" for l in livres])
                return f"🤖 [Assistant IA - Mode Local] : Voici les livres actuellement disponibles à la bibliothèque : {liste}. Je vous conseille particulièrement de lire 'Le Petit Prince' !"
            return "🤖 [Assistant IA - Mode Local] : Malheureusement, aucun livre n'est disponible pour le moment."
            
        elif "emprunt" in question or "hors ligne" in question:
            cursor.execute("SELECT titre, auteur FROM livres WHERE statut != 'Disponible' OR quantite = '0'")
            livres = cursor.fetchall()
            conn.close()
            if livres:
                liste = ", ".join([f"'{l[0]}' de {l[1]}" for l in livres])
                return f"🤖 [Assistant IA - Mode Local] : Les livres suivants sont actuellement empruntés ou en rupture de stock : {liste}."
            return "🤖 [Assistant IA - Mode Local] : Tous les livres sont actuellement en rayon !"
            
        elif "combien" in question or "nombre" in question or "total" in question:
            cursor.execute("SELECT COUNT(*) FROM livres")
            total = cursor.fetchone()[0]
            conn.close()
            return f"🤖 [Assistant IA - Mode Local] : La bibliothèque contient actuellement un total de {total} ouvrages différents dans sa base de données."
            
        else:
            conn.close()
            return f"🤖 [Assistant IA - Mode Local] : Bien reçu votre question ('{prompt}'). En tant qu'assistant de gestion, je peux vous confirmer que votre base de données est opérationnelle et connectée sur le port 8000 !"

    except Exception as e:
        return f"Erreur locale de l'assistant : {str(e)}"
# --- ROUTES API FLASK (CRUD) ---

@app.route('/livres', methods=['GET'])
def get_livres():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livres")
    rows = cursor.fetchall()
    conn.close()
    
    livres = []
    for r in rows:
        livres.append({"id": r[0], "titre": r[1], "auteur": r[2], "categorie": r[3], "annee": r[4], "quantite": r[5], "statut": r[6]})
    return jsonify(livres)

@app.route('/livres', methods=['POST'])
def add_livre():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO livres (titre, auteur, categorie, annee, quantite, statut) VALUES (?, ?, ?, ?, ?, ?)",
                   (data['titre'], data['auteur'], data['categorie'], data['annee'], data['quantite'], data['statut']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Livre ajouté avec succès"})

@app.route('/livres/<int:livre_id>', methods=['PUT'])
def update_livre(livre_id):
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE livres SET titre=?, auteur=?, categorie=?, annee=?, quantite=?, statut=? WHERE id=?",
                   (data['titre'], data['auteur'], data['categorie'], data['annee'], data['quantite'], data['statut'], livre_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Livre modifié avec succès"})

@app.route('/livres/<int:livre_id>', methods=['DELETE'])
def delete_livre(livre_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM livres WHERE id=?", (livre_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Livre supprimé avec succès"})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    question = data.get("question", "")
    
    if not question:
        return jsonify({"reponse": "Veuillez poser une question."}), 400
        
    try:
        # Récupération du contexte des livres de la base de données
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT titre, auteur, categorie, statut FROM livres")
        livres = cursor.fetchall()
        conn.close()
        
        contexte_db = ", ".join([f"'{l[0]}' par {l[1]} ({l[2]}) - {l[3]}" for l in livres])
        
        # Appel de la fonction Gemini
        reponse_ai = interroger_gemini(question, contexte_db)
        return jsonify({"reponse": reponse_ai})
        
    except Exception as e:
        return jsonify({"reponse": f"Erreur interne du serveur : {str(e)}"})

# --- DÉMARRAGE DU SERVEUR ---
if __name__ == '__main__':
    init_db()
    print("Le serveur démarre sur le port 8000...")
    app.run(port=8000, host='127.0.0.1', debug=False)