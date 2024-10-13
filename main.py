from flask import Flask, Response, request
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

def scrape_conjugation(verb):
    url = f"https://conjugaison.lemonde.fr/conjugaison/search?verb={verb}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP
        soup = BeautifulSoup(response.content, 'html.parser')

        conjugation_data = f"✅{verb}\n"

        # Extraire les informations sur le groupe du verbe
        verb_info = soup.find('div', class_='vtfc-verbs-details')
        if verb_info:
            conjugation_data += f"❤️{verb_info.text.strip()}\n"

        # Extraire les modes de conjugaison
        modes = soup.find_all('div', class_='vtfc-verbs-mode')
        for mode in modes:
            mode_name = mode.text.strip()
            conjugation_data += f"\n❤️{mode_name}\n"

            # Extraire les temps pour chaque mode
            tenses = mode.find_next_siblings('div')[0].find_all('div', class_='vtfc-verbs-conjugated')
            for tense in tenses:
                tense_name = tense.find('span', class_='vtfc-verbs-tense').text.strip()
                conjugation_data += f"👉{tense_name}\n"

                # Extraire les conjugaisons
                conjugations = tense.find_all('li')
                for conjugation in conjugations:
                    conjugation_data += f"{conjugation.text.strip()}\n"

        return conjugation_data.strip()
    except requests.RequestException as e:
        # Gérer les erreurs de requête
        return f"Erreur lors de la récupération des données : {str(e)}"
    except Exception as e:
        # Gérer les autres erreurs
        return f"Une erreur inattendue s'est produite : {str(e)}"

@app.route('/conjugaison')
def conjugate():
    verb = request.args.get('verbe', '')
    if not verb:
        return Response(json.dumps({"error": "Aucun verbe fourni"}, ensure_ascii=False), 
                        status=400, 
                        content_type="application/json; charset=utf-8")

    conjugation = scrape_conjugation(verb)
    return Response(json.dumps({"response": conjugation}, ensure_ascii=False), 
                    content_type="application/json; charset=utf-8")

@app.errorhandler(404)
def not_found(error):
    return Response(json.dumps({"error": "Route non trouvée"}, ensure_ascii=False), 
                    status=404, 
                    content_type="application/json; charset=utf-8")

@app.errorhandler(500)
def internal_error(error):
    return Response(json.dumps({"error": "Erreur interne du serveur"}, ensure_ascii=False), 
                    status=500, 
                    content_type="application/json; charset=utf-8")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


