import requests
import datetime
import logging
import time
import os
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("sncf_api_notifier")

# Chargement des variables d'environnement
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SNCF_API_KEY = os.getenv("SNCF_API_KEY")
DEPARTURE_STATION_CODE = os.getenv("DEPARTURE_STATION_CODE")     # Ex: stop_area:SNCF:87271007 (Bordeaux)
INTERMEDIATE_STATION_CODE = os.getenv("INTERMEDIATE_STATION_CODE") # Ex: stop_area:SNCF:87584102 (Saint-Émilion)
TRAIN_TIME = "08:40"  # Heure du train à surveiller
LINE_CODE = os.getenv("LINE_CODE", "")  # Si connu, code de la ligne (ex: line:SNCF:TER-33:)


print("TELEGRAM_BOT_TOKEN : ", SNCF_API_KEY)
# URL de base de l'API SNCF
SNCF_API_BASE_URL = "https://api.sncf.com/v1/coverage/sncf/"

def send_telegram_message(message):
    """Envoie un message via Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logger.info(f"Message envoyé avec succès: {message}")
            return True
        else:
            logger.error(f"Échec d'envoi du message: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message: {str(e)}")
        return False

def format_time(timestamp):
    """Formate un timestamp en heure lisible"""
    try:
        date_obj = datetime.datetime.strptime(timestamp, "%Y%m%dT%H%M%S")
        return date_obj.strftime("%H:%M")
    except:
        return "??:??"

def find_journey_details(departure_datetime):
    """
    Recherche les détails d'un parcours spécifique
    Utilise l'API journeys pour trouver un train passant par l'arrêt intermédiaire
    """
    journeys_url = f"{SNCF_API_BASE_URL}journeys"
    
    # Format de la date pour l'API: YYYYMMDDThhmmss
    formatted_datetime = departure_datetime.strftime("%Y%m%dT%H%M%S")
    
    params = {
        "from": DEPARTURE_STATION_CODE,
        "to": INTERMEDIATE_STATION_CODE,
        "datetime": formatted_datetime,
        "datetime_represents": "departure",
        "data_freshness": "realtime",
        "count": 4,  # Nombre de résultats à récupérer
        "disable_geojson": True
    }
    
    if LINE_CODE:
        params["allowed_id[]"] = LINE_CODE
    
    logger.info(f"Recherche de trajets: {journeys_url} avec params={params}")
    
    try:
        response = requests.get(journeys_url, auth=(SNCF_API_KEY, ''), params=params)
        
        if response.status_code != 200:
            logger.error(f"Erreur API: {response.status_code} - {response.text}")
            return None
        
        journeys = response.json().get('journeys', [])

        print("journeys")
        print(journeys)
        
        if not journeys:
            logger.warning(f"Aucun trajet trouvé pour {formatted_datetime}")
            return None
        
        # Trouver le trajet qui correspond à l'heure de départ souhaitée
        target_journey = None
        
        for journey in journeys:
            sections = journey.get('sections', [])
            
            for section in sections:
                if section.get('type') == 'public_transport':
                    # Vérifier l'heure de départ
                    departure_dt = section.get('departure_date_time', '')
                    departure_time = format_time(departure_dt)

                    print("is public transport")
                    print(section)
                    
                    # Vérifier le numéro de train si fourni
                    display_info = section.get('display_informations', {})
                    headsign = display_info.get('headsign', '')

                    print("departure_time")
                    print(departure_time)
                    
                    if departure_time == TRAIN_TIME:
                        return section
        
        # Si on n'a pas trouvé de correspondance exacte, prendre le premier résultat
        if journeys and not target_journey:
            for journey in journeys:
                sections = journey.get('sections', [])
                
                for section in sections:
                    if section.get('type') == 'public_transport':
                        return section
        
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche du trajet: {str(e)}")
        return None

def check_train_status():
    """Vérifie le statut du train et envoie une notification"""
    try:
        # Obtenir la date pour aujourd'hui
        today = datetime.datetime.now()
        
        # Construire l'heure de départ cible
        hour, minute = map(int, TRAIN_TIME.split(':'))
        target_datetime = datetime.datetime(
            today.year, today.month, today.day, hour, minute
        )

        print("target_datetime ", target_datetime)
        
        # Trouver le trajet correspondant
        journey_section = find_journey_details(target_datetime)
        
        if not journey_section:
            msg = f"❓ Impossible de trouver des informations sur le train de {TRAIN_TIME}"
            logger.warning(msg)
            send_telegram_message(msg)
            return
        
        # Extraire les informations
        display_info = journey_section.get('display_informations', {})
        train_name = display_info.get('commercial_mode', 'Train')
        train_number = display_info.get('headsign', '') or display_info.get('trip_short_name', 'Inconnu')
        direction = display_info.get('direction', 'destination inconnue')
        
        # Horaires prévus et réels
        base_departure = journey_section.get('base_departure_date_time', '')
        departure = journey_section.get('departure_date_time', '')

        print("departure")
        print(departure)
        print("journey_section")
        print(journey_section)
        
        # Information sur les perturbations
        disruptions = journey_section.get('display_informations', {}).get('links', [])
        disruption_status = None
        
        for link in disruptions:
            if link.get('rel') == 'disruptions':
                disruption_status = link.get('type')
        
        # Convertir les timestamps en objets datetime
        try:
            base_dt = datetime.datetime.strptime(base_departure, "%Y%m%dT%H%M%S")
            actual_dt = datetime.datetime.strptime(departure, "%Y%m%dT%H%M%S")
            
            delay_seconds = (actual_dt - base_dt).total_seconds()
            delay_minutes = int(delay_seconds / 60)
            
            # Vérifier les perturbations
            is_cancelled = False
            
            if disruption_status == 'NO_SERVICE':
                is_cancelled = True
            
            # Préparer la notification
            train_info = f"{train_name} {train_number} de {TRAIN_TIME} vers {direction}"
            
            if is_cancelled:
                send_telegram_message(f"❌ ALERTE: {train_info} ANNULÉ! 😱")
                logger.warning(f"Train {train_number} annulé")
            elif delay_minutes > 5:  # Considérer un retard à partir de 5 minutes
                send_telegram_message(f"⚠️ ALERTE: {train_info} en RETARD de {delay_minutes} minutes! ⏰")
                logger.warning(f"Train {train_number} en retard de {delay_minutes} minutes")
            else:
                # Train à l'heure ou retard négligeable
                send_telegram_message(f"✅ {train_info} validé! Bon voyage! 🚄")
                logger.info(f"Train {train_number} validé")
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des horaires: {str(e)}")
            status_message = f"ℹ️ Statut du train {train_name} {train_number} ({TRAIN_TIME}) non disponible précisément."
            send_telegram_message(status_message)
            
    except Exception as e:
        error_msg = f"Erreur lors de la vérification du statut du train: {str(e)}"
        logger.error(error_msg)
        send_telegram_message(f"⚠️ {error_msg}")

def main():
    """Fonction principale"""
    logger.info("Vérification du statut du train SNCF")
    check_train_status()

if __name__ == "__main__":
    main()