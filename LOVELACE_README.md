# 📝 Note importante sur les noms d'entités

Dans tous les exemples de cartes, remplacez `{station}` par le nom de votre station en minuscules et sans espaces.


## Comment trouver vos noms d'entités ?

Dans Home Assistant :
1. Allez dans **Paramètres** → **Appareils et services**
2. Cliquez sur votre intégration **TSUN Monitoring**
3. Vous verrez toutes vos entités avec leurs noms exacts

## Remplacer automatiquement dans les exemples

Faites un rechercher-remplacer dans votre éditeur :
- Cherchez : `{station}`
- Remplacez par le nom de votre station en minuscules

## Nouveau capteur pour les graphiques journée

L'intégration expose maintenant un capteur dédié :
- `sensor.{station}_day_graph`

Ce capteur contient les attributs suivants, utiles pour `apexcharts-card` :
- `power_points`
- `weather_points`
- `day_summary`
- `segment_day`

Autres blocs ajoutés après analyse HAR (dans le capteur Raw Data et Day Graph) :
- `station_status_count`
- `station_manage`
- `station_energy_saved`
- `station_current_flow`
- `station_scene`
- `station_alerts`

## Vue complète type application TSUN

Le fichier [lovelace-cards-examples.yaml](c:/Users/v3ryf/OneDrive/Documents/www/tsun-ha/lovelace-cards-examples.yaml) contient maintenant une section :
- `📱 VUE COMPLÈTE TYPE APP TSUN`

Pré-requis :
- `apexcharts-card` installé via HACS
