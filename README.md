# TSUN Monitoring - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Intégration Home Assistant pour les onduleurs solaires TSUN via l'API Talent Monitoring.

## 📋 Fonctionnalités

Cette intégration vous permet de monitorer vos stations solaires TSUN directement dans Home Assistant :

- ⚡ **Puissance de génération en temps réel** (W)
- 📊 **Production totale d'énergie** (kWh)
- 🔌 **Capacité installée** (kW)
- 🌐 **Statut du réseau**
- 📍 **Informations de localisation**
- ⏰ **Dernière mise à jour**

## 🚀 Installation

### Via HACS (Recommandé)

#### Étape 1 : Ajouter le repository custom

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur **Integrations**
3. Cliquez sur les **3 points** (⋮) en haut à droite
4. Sélectionnez **Custom repositories**
5. Dans le champ "Repository", collez : `https://github.com/v3ryf/tsun-ha`
6. Dans "Category", sélectionnez **Integration**
7. Cliquez sur **Add**

#### Étape 2 : Installer l'intégration

1. Cliquez sur le bouton **+ Add Integration** en bas à droite
2. Recherchez **"TSUN Monitoring"**
3. Cliquez dessus et sélectionnez **Download**
4. Redémarrez Home Assistant

### Installation Manuelle

1. Téléchargez le dossier `custom_components/tsun_monitoring`
2. Copiez-le dans le dossier `custom_components` de votre configuration Home Assistant
3. Redémarrez Home Assistant

## ⚙️ Configuration

1. Allez dans **Configuration** → **Intégrations**
2. Cliquez sur le bouton **+ Ajouter une intégration**
3. Recherchez **TSUN Monitoring**
4. Entrez vos identifiants :
   - **Nom d'utilisateur** : Votre email utilisé pour l'application TSUN
   - **Mot de passe** : Votre mot de passe hashé (celui utilisé dans l'API)

> **Note** : Le mot de passe doit être celui utilisé par l'application mobile TSUN (version hashée).

## 📊 Capteurs créés

Pour chaque station, l'intégration créera les capteurs suivants :

### 🌞 Production Solaire

| Capteur | Description | Unité |
|---------|-------------|-------|
| `sensor.{station}_generation_power` | Puissance générée actuellement | W |
| `sensor.{station}_generation_total` | Énergie totale produite | kWh |
| `sensor.{station}_generation_value_daily` | Production journalière | kWh |
| `sensor.{station}_generation_month` | Production mensuelle | kWh |
| `sensor.{station}_generation_year` | Production annuelle | kWh |

### 🔋 Batterie

| Capteur | Description | Unité |
|---------|-------------|-------|
| `sensor.{station}_battery_power` | Puissance batterie (+ charge / - décharge) | W |
| `sensor.{station}_battery_soc` | État de charge | % |
| `sensor.{station}_battery_status` | Statut (CHARGE/DISCHARGE) | - |
| `sensor.{station}_battery_charge_today` | Charge aujourd'hui | kWh |
| `sensor.{station}_battery_discharge_today` | Décharge aujourd'hui | kWh |
| `sensor.{station}_battery_charge_total` | Charge totale | kWh |
| `sensor.{station}_battery_discharge_total` | Décharge totale | kWh |
| `sensor.{station}_battery_rated_power` | Puissance nominale | kW |
| `sensor.{station}_battery_rated_capacity` | Capacité nominale | kWh |

### ⚡ Consommation

| Capteur | Description | Unité |
|---------|-------------|-------|
| `sensor.{station}_use_power` | Consommation actuelle | W |

### ⚙️ Système

| Capteur | Description | Unité |
|---------|-------------|-------|
| `sensor.{station}_installed_capacity` | Capacité installée | kW |
| `sensor.{station}_network_status` | État de la connexion | - |
| `sensor.{station}_power_system_type` | Type de système | - |

### Attributs supplémentaires

Chaque capteur inclut des attributs additionnels :
- `location` : Adresse de la station
- `power_type` : Type de puissance (ex: "PV")
- `power_system_type` : Type de système (ex: "GEN_GRID_USE_BTR")
- `geography_type` : Type géographique (ex: "HOUSE_ROOF")
- `operation_type` : Type d'opération
- `operating` : État opérationnel (true/false)
- `last_update` : Timestamp de la dernière mise à jour
- `last_update_formatted` : Date formatée de la dernière mise à jour

## 🔄 Fréquence de mise à jour

Les données sont mises à jour toutes les **5 minutes** par défaut.

## 📝 Exemple d'utilisation

### Card Lovelace simple

```yaml
type: entities
title: Ma Station TSUN
entities:
  - entity: sensor.billon_generation_power
    name: Puissance actuelle
  - entity: sensor.billon_generation_total
    name: Production totale
  - entity: sensor.billon_network_status
    name: Statut
```

### Card avec graphique d'énergie

```yaml
type: energy-date-selection
title: Production Solaire
entities:
  - entity: sensor.billon_generation_total
```

## 🐛 Dépannage

### Erreur d'authentification

Si vous rencontrez des erreurs d'authentification :
1. Vérifiez que vos identifiants sont corrects
2. Assurez-vous d'utiliser le mot de passe hashé de l'API
3. Consultez les logs Home Assistant pour plus de détails

### Les données ne se mettent pas à jour

- Vérifiez votre connexion Internet
- Vérifiez que l'API TSUN est accessible
- Consultez les logs pour d'éventuelles erreurs

## 🔍 Logs

Pour activer les logs de débogage, ajoutez à votre `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.tsun_monitoring: debug
```

## 👨‍💻 Développement

Cette intégration utilise :
- L'API Talent Monitoring de TSUN
- Authentication OAuth2
- Polling toutes les 5 minutes

## 📄 Licence

MIT License

## 🙏 Remerciements

Merci à la communauté Home Assistant et HACS !

---

**Note** : Cette intégration n'est pas officielle et n'est pas affiliée à TSUN ou Talent Monitoring.
