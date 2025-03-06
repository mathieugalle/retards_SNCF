

# 

La motivation de ce projet est la vengeance contre la SNCF qui m'annule mon putain de train sans me prévenir avec leur putain d'application de merde alors que je le mets bien dans "Vos itinérances". Mais la fonction est down depuis 3 mois, là ça marche mais pour une raison inconnue il veut me faire partir à 15h alors qu'il y a un train à 9h40.

Du coup, aidé de mon fidèle compère Claude 3.7, je vais taper sur leur API à 8h20 tous les jours de semaine
pour demander si mon train est annulé, et envoyer la réponse sur mon téléphone, par Telegram, pour ne pas me taper du vélo et attendre des heures à la gare parce qu'un putain de chauffeur a décidé de pas se lever (j'abuse : c'est sûrement pas de sa faute. Référez-vous à la première phrase.)


Il vous faut un jeton d'accès à l'API SNCF : 

Ils l'envoie par mail quand on leur donne ici : https://numerique.sncf.com/

Pour trouver les adresses des gares au format "stop_area" (il y en a besoin ensuite pour chopper les trains), il faut ensuite taper sur :

https://api.sncf.com/v1/coverage/sncf/places?q=nom_de_la_gare

(il faut copier la clé API dans "nom d'utilisateur" et laisser "mot de passe" vide : super chelou)

https://api.sncf.com/v1/coverage/sncf/places?q=nom_de_la_gare

Par exemple, https://api.sncf.com/v1/coverage/sncf/places?q=bordeaux
je trouve : 
{
    "id": "**stop_area:SNCF:87581009**",
    "name": "Bordeaux Saint-Jean (Bordeaux)",
    "quality": 70,
    ...
}
De même, 
{
    "id": "**stop_area:SNCF:87584102**",
    "name": "Saint-Émilion (Saint-Émilion)",
    "quality": 89,
    "stop_area": {
    "id": "stop_area:SNCF:87584102",
    ...
    }
}

Ensuite, pour obtenir si mon putain de train est annulé, il faut faire : 

https://api.sncf.com/v1/coverage/sncf/stop_areas/stop_area:SNCF:87581009/departures

Et je pense 