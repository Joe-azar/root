import subprocess
import time
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import signal
import sys
import logging

# Initialiser les logs
logging.basicConfig(filename="service_logs.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# Liste des services à lancer
services = [
    {"name": "Information Extraction Service", "script": "uvicorn services.information_extraction_service:app --reload --port 8001"},
    {"name": "Solvency Check Service", "script": "uvicorn services.solvency_check_service:app --reload --port 8002"},
    {"name": "Property Evaluation Service", "script": "uvicorn services.property_evaluation_service:app --reload --port 8003"},
    {"name": "Approval Decision Service", "script": "uvicorn services.approval_decision_service:app --reload --port 8004"},
    {"name": "Composite Loan Evaluation Service", "script": "uvicorn web_composite_service:app --reload --port 8000"},
    {"name": "Watchdog Trigger", "script": "python watchdog_trigger.py"}
]

processes = []

def launch_service(service):
    try:
        # Vérifier si le service est déjà lancé
        process = subprocess.Popen(service["script"], shell=True)
        processes.append(process)
        logging.info(f"{service['name']} lancé avec succès.")
    except Exception as e:
        logging.error(f"Erreur lors du lancement de {service['name']}: {str(e)}")

def stop_services():
    print("\nArrêt des services...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
        print(f"Service {process.args[1]} arrêté.")
    print("Tous les services sont arrêtés.")
    sys.exit(0)

def signal_handler(sig, frame):
    stop_services()

def submit_request():
    nom = entry_nom.get()
    adresse = entry_adresse.get()
    email = entry_email.get()
    telephone = entry_telephone.get()
    montant = entry_montant.get()
    duree = entry_duree.get()
    description = entry_description.get()
    revenu = entry_revenu.get()
    depenses = entry_depenses.get()

    if not all([nom, adresse, email, telephone, montant, duree, description, revenu, depenses]):
        messagebox.showwarning("Erreur", "Tous les champs doivent être remplis.")
        return

    # Formatage du contenu du fichier avec les informations fournies
    loan_request = (
        f"Nom du Client: {nom}\n"
        f"Adresse: {adresse}\n"
        f"Email: {email}\n"
        f"Numéro de Téléphone: {telephone}\n"
        f"Montant du Prêt Demandé: {montant} EUR\n"
        f"Durée du Prêt: {duree} ans\n"
        f"Description de la Propriété: {description}\n"
        f"Revenu Mensuel: {revenu} EUR\n"
        f"Dépenses Mensuelles: {depenses} EUR\n"
    )

    data_directory = "data"
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    request_filename = os.path.join(data_directory, f"loan_request_{nom.replace(' ', '_')}.txt")
    
    # Écriture du contenu formaté dans le fichier
    with open(request_filename, "w", encoding="utf-8") as f:
        f.write(loan_request)

    logging.info("Demande de prêt soumise avec succès.")
    messagebox.showinfo("Succès", "Votre demande de prêt a été soumise avec succès.")

def submit_file():
    file_path = filedialog.askopenfilename(title="Sélectionnez un fichier de demande",
                                           filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")))

    if file_path:
        data_directory = "data"
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)

        try:
            shutil.copy(file_path, data_directory)
            logging.info(f"Fichier {file_path} déposé avec succès.")
            messagebox.showinfo("Succès", "Le fichier a été déposé avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors de la copie du fichier: {str(e)}")
            messagebox.showerror("Erreur", f"Impossible de copier le fichier: {str(e)}")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    print("Lancement de tous les services...")

    for service in services:
        launch_service(service)
        time.sleep(1)

    print("Tous les services sont en cours d'exécution.")

    root = tk.Tk()
    root.title("Soumission de Demande de Prêt Immobilier")

    fields = [
        ("Nom du Client:", "entry_nom"),
        ("Adresse:", "entry_adresse"),
        ("Email:", "entry_email"),
        ("Numéro de Téléphone:", "entry_telephone"),
        ("Montant du Prêt Demandé (EUR):", "entry_montant"),
        ("Durée du Prêt (années):", "entry_duree"),
        ("Description de la Propriété:", "entry_description"),
        ("Revenu Mensuel (EUR):", "entry_revenu"),
        ("Dépenses Mensuelles (EUR):", "entry_depenses")
    ]

    for label_text, variable_name in fields:
        frame = tk.Frame(root)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", padx=5, pady=5)
        globals()[variable_name] = entry

    submit_button = tk.Button(root, text="Soumettre une nouvelle demande", command=submit_request)
    submit_button.pack(pady=10)

    submit_file_button = tk.Button(root, text="Déposer un fichier de demande", command=submit_file)
    submit_file_button.pack(pady=10)

    root.mainloop()

    stop_services()
