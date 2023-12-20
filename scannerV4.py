import os
import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

# Chemin du dossier racine à analyser
#root_folder = "C:/Users/mstzk/Pictures/scanner/test" C:\Users\mstzk\Pictures\air+quality
root_folder ="C:/Users/mstzk/Pictures/air+quality"

# Chemin de la base de données SQLite
db_path = "file_info.db"

# Fonction pour créer la table dans la base de données
def create_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            path TEXT,
            folder TEXT,
            extension TEXT,
            size INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Fonction pour insérer des informations dans la base de données
def insert_into_db(filename, path, folder, extension, size):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO documents (filename, path, folder, extension, size) VALUES (?, ?, ?, ?, ?)",
                   (filename, path, folder, extension, size))
    conn.commit()
    conn.close()

def explore_folder(folder_path):
    # Creattion du dossier 'organized' 
    organized_folder = os.path.join(root_folder, "organized")
    os.makedirs(organized_folder, exist_ok=True)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Affiche le type d'entrée (DOSSIER ou FICHIER)
            print("FICHIER:", file_path)

            # Catégorisation par extension
            _, file_extension = os.path.splitext(file)
            file_extension = file_extension.lower()

            # Création des dossiers pour chaque extension dans le dossier 'organized'
            extension_folder = os.path.join(organized_folder, file_extension[1:])
            os.makedirs(extension_folder, exist_ok=True)

            # Déplacement du fichier dans le bon dossier avec gestion des conflits
            new_file_path = os.path.join(extension_folder, file)
            counter = 1
            while os.path.exists(new_file_path):
                base, ext = os.path.splitext(file)
                new_file_path = os.path.join(extension_folder, f"{base}_{counter}{ext}")
                counter += 1

            os.rename(file_path, new_file_path)

            # Obtention des informations sur le fichier
            size = os.path.getsize(new_file_path) // 1024  # Taille en Ko
            folder_name = os.path.basename(os.path.dirname(new_file_path))

            # Insertion des informations dans la base de données
            insert_into_db(file, new_file_path, folder_name, file_extension, size)



# Exécute la fonction pour créer la table dans la base de données
create_table()

# Exécute la fonction pour explorer le dossier racine
explore_folder(root_folder)

# Interface web avec Flask pour consulter la base de données
@app.route('/')
def display_files():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents")
    rows = cursor.fetchall()
    conn.close()
    return render_template('index.html', documents=rows)

if __name__ == '__main__':
    app.run(debug=True)
