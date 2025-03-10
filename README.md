# Retards_SNCF

La motivation de ce projet est la vengeance. Mon train est annulé, sans me prévenir avec SNCF Connect, alors que je le mets bien dans "Vos itinérances". Mais la fonction est down depuis 3 mois, là ça marche mais pour une raison inconnue il veut me faire partir à 15h alors qu'il y a un train à 9h40. Je ne sais pas quel algorithme peut être aussi mauvais. Tout ça en m'envoyant des notifications de pubs pour aller à Rouen, sans m'aider à prendre le train que je veux prendre. Pire UX.

Du coup, aidé de mon fidèle compère Claude 3.7, je vais taper sur leur API à 8h20 tous les jours de semaine
pour demander si mon train est annulé, et envoyer la réponse sur mon téléphone, par Telegram, pour ne pas me taper du vélo et attendre des heures à la gare parce qu'un chauffeur a décidé de pas se lever (j'abuse : c'est sûrement pas de sa faute. Référez-vous à la première phrase.)

Il vous faut un jeton d'accès à l'API SNCF : 

Ils l'envoient par mail quand on leur donne ici : https://numerique.sncf.com/

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


...
9h40 est arrivé, je continuerai ce projet aux prochains retards.

## 10 Mars 2025, encore un train **annulé**

10h27 pour le prochain, avec une partie en autocar.

L'API SNCF me propose des solutions, du coup ça ne me dit pas que mon train spécifique est annulé.
Il faut que j'arrive à filtrer par CE TRAIN, CETTE HORAIRE précisémment. Pour n'importe quel, changement, notification. Parce que leur API est optimisée pour toujours "essayer de trouver quelque chose", donc c'est à moi de filtrer sinon il va me mettre des trajets qui arrivent à Libourne (à 10km de ma destination) par exemple.
