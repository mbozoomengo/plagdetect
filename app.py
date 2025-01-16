import streamlit as st
import pandas as pd
import nltk
nltk.download('punkt')
from sklearn.metrics.pairwise import cosine_similarity
import os
import asyncio

# Configure NLTK data path
os.environ['NLTK_DATA'] = 'C:/Users/MBOZOO/AppData/Roaming/nltk_data'

# Import database-related functions
from main import (
    clear_database, create_tables, delete_file, get_all_files,
    get_pivot_similarity, get_sentences, get_similarity,
    get_text_from_file, insert_file, translate_text
)

def empty_database_button():
    """Renders a checkbox and button to clear the database."""
    confirmation = st.checkbox("Confirmer la suppression de tous les fichiers", value=False)
    if confirmation:
        if st.button("Vider la base de données"):
            if clear_database():
                st.success("La base de données a été vidée avec succès.")
                st.rerun()
            else:
                st.error("Une erreur est survenue lors du vidage de la base de données.")
    else:
        st.warning("Veuillez cocher la case pour confirmer la suppression.")

# Configure Streamlit page avec un logo personnalisé
st.set_page_config(
    page_title='PlagDetect',
    layout="wide",
    page_icon="logo.png"  # Utilisation du fichier logo comme icône de l'application
)

# Sidebar Menu
menu = ["Accueil", "Vérifier les Similitudes", "Consulter les Documents", "À propos"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Accueil":
    # Ajouter le logo en haut de la page
    st.image("logo.png", width=150)  # Affichez le logo en haut de la page d'accueil

    # Titre principal
    st.title("🏠 Bienvenue dans **PlagDetect**")
    st.write("""
    **PlagDetect** est une application puissante et intuitive conçue pour détecter et analyser les similarités entre plusieurs documents, facilitant ainsi la détection de plagiat.
    """)

    # Ajout d'une ligne de séparation
    st.markdown("---")

    # Section des fonctionnalités principales
    st.header("✨ Fonctionnalités principales")
    st.markdown("""
    - **📄 Évaluez à quel point un document est "inspiré" d'un autre avec un pourcentage de similarité.**
    - **📂 Analyse de plusieurs fichiers**
    - **🖥️ Une interface conviviale pour le téléchargement et l'analyse des documents.**
    - **📑 Support multi-formats (.docx, .pdf, .txt).**
    - **🌍 Comparaison multilingue.**
    """)

    # Ajout d'une section Call-to-Action
    st.markdown("---")
    st.subheader("📌 **Prêt à commencer ?**")
    st.write("Sélectionnez une option dans le menu à gauche pour démarrer votre analyse.")


elif choice == "Vérifier les Similitudes":
    st.title(':mag: PlagDetect - Vérification des Similitudes')
    st.write("Vérifiez les similitudes entre les fichiers téléchargés.")

    # File upload in the sidebar
    st.sidebar.title(":file_folder: Importer les fichiers à comparer")
    st.sidebar.write("Téléchargez des fichiers pivots et cibles pour vérifier les similitudes entre eux.")

    pivot_files = st.sidebar.file_uploader("Fichier(s) pivot(s) (.docx, .pdf, .txt)", type=["docx", "pdf", "txt"], accept_multiple_files=True, key="pivot")
    target_files = st.sidebar.file_uploader("Fichier(s) cible(s) (.docx, .pdf, .txt)", type=["docx", "pdf", "txt"], accept_multiple_files=True, key="target")

    # Traitement des fichiers téléchargés
    pivot_texts, pivot_filenames = [], []
    for pivot_file in pivot_files:
        if pivot_file:
            text = get_text_from_file(pivot_file)
            # Traduction en anglais
            text = asyncio.run(translate_text(text, target_lang='en'))
            pivot_texts.append(text)
            pivot_filenames.append(pivot_file.name)
            insert_file(pivot_file.name, text)

    target_texts, target_filenames = [], []
    for target_file in target_files:
        if target_file:
            text = get_text_from_file(target_file)
            # Traduction en anglais
            text = asyncio.run(translate_text(text, target_lang='en'))
            target_texts.append(text)
            target_filenames.append(target_file.name)
            insert_file(target_file.name, text)

    if st.button('Vérifier les similitudes entre les fichiers'):
        if not pivot_texts or not target_texts:
            st.error("Aucun fichier trouvé pour la recherche de similitudes.")
            st.stop()

        similarities = get_pivot_similarity(pivot_texts, target_texts, pivot_filenames, target_filenames)
        df = pd.DataFrame(similarities, columns=['Fichier Pivot', 'Fichier Cible', 'Similarité (%)'])
        df = df.sort_values(by=['Similarité (%)'], ascending=False)
        st.dataframe(df)

elif choice == "Consulter les Documents":
    st.title(":open_file_folder: Consulter les Documents Enregistrés")
    files = get_all_files()
    if files:
        df = pd.DataFrame(files, columns=["ID", "Nom du Fichier", "Contenu"])
        st.dataframe(df)

        selected_id = st.number_input("Entrez l'ID du fichier à gérer", min_value=1, step=1)

        if st.button("Afficher le Contenu"):
            selected_file = next((file for file in files if file[0] == selected_id), None)
            if selected_file:
                st.subheader(f"Contenu du fichier : {selected_file[1]}")
                st.text_area("Contenu", selected_file[2], height=300)
            else:
                st.error("Fichier introuvable.")

        if st.button("Supprimer le fichier"):
            delete_file(selected_id)
            st.success(f"Le fichier {selected_id} a été supprimé avec succès.")
            st.rerun()

        empty_database_button()

    else:
        st.info("Aucun fichier trouvé dans la base de données.")

elif choice == "À propos":
    st.title("📝 À propos")
    st.write("""
        ### Notre Équipe :
        **PlagDetect** est développé par une équipe d'Ingénieurs en Informatique et Systèmes d'Informations.

        ### Membres de l'équipe :
        - **MBOZO'O William**
        - **TAKU Aurélien**
        - **TOMBI Medhi**

        **Merci d'avoir choisi PlagDetect !**
    """)
    st.write("© 2025 PlagDetect. Tous droits réservés.")


if __name__ == "__main__":
    create_tables()
