import requests
from bs4 import BeautifulSoup
import os
import urllib.parse

# URL de la page de recherche BOAMP
url = "https://www.boamp.fr/pages/recherche/?disjunctive.type_marche&disjunctive.descripteur_code&disjunctive.dc&disjunctive.code_departement&disjunctive.type_avis&disjunctive.famille&sort=dateparution&refine.type_marche=TRAVAUX&refine.dc=365&refine.dc=366&refine.code_departement=34&q.timerange.dateparution=dateparution:%5B2024-08-01%20TO%202024-12-01%5D&q.timerange.datelimitereponse=datelimitereponse:%5B2024-08-01%20TO%202024-12-01%5D&q.filtre_etat=(NOT%20%23null(datelimitereponse)%20AND%20datelimitereponse%3E%3D%222024-10-01%22)%20OR%20(%23null(datelimitereponse)%20AND%20datefindiffusion%3E%3D%222024-10-01%22)#resultarea"

# Dossier où sauvegarder les fichiers PDF
output_dir = "pdf_boamp"
os.makedirs(output_dir, exist_ok=True)

# En-têtes HTTP pour simuler une requête légitime
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}

# Fonction pour télécharger un fichier PDF
def download_pdf(pdf_url, output_dir):
    try:
        pdf_response = requests.get(pdf_url, headers=headers)
        pdf_filename = os.path.join(output_dir, pdf_url.split("/")[-1])
        with open(pdf_filename, "wb") as f:
            f.write(pdf_response.content)
        print(f"Téléchargé : {pdf_filename}")
    except Exception as e:
        print(f"Erreur lors du téléchargement {pdf_url}: {e}")

# Faire la requête HTTP pour obtenir le contenu HTML
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "lxml")

# Trouver les éléments contenant les liens vers les PDFs
# Modifier les selecteurs CSS en fonction de la structure réelle de la page

for article in soup.find_all("article", class_="item"):  # Assurez-vous que l'élément correspondant est bien un article
    pdf_link = article.find("a", href=True)  # Trouver le lien PDF
    
    if pdf_link and pdf_link['href'].endswith(".pdf"):
        pdf_url = urllib.parse.urljoin(url, pdf_link['href'])  # URL absolue du PDF
        download_pdf(pdf_url, output_dir)
    else:
        print("PDF non trouvé pour cet article.")

print("Téléchargement terminé.")
