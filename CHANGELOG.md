# Changelog

## [1.2.0] - 2026-03-10

### Ajouté
- Reconnexion propre quand le token expire
  - Tentative de refresh token automatique
  - Fallback sur authentification complète si refresh échoue
  - Retry unique de la requête après reconnexion
- Exposition étendue des données station
  - Capteurs dynamiques créés pour les champs API non mappés
  - Capteur diagnostic "Raw Data" par station avec payload complet en attributs

### Changé
- Gestion de session API plus robuste pour éviter les erreurs prolongées après expiration

## [1.1.0] - 2026-01-28

### Ajouté
- 🔋 **Support complet de la batterie**
  - Puissance batterie en temps réel
  - État de charge (SOC)
  - Statut (charge/décharge)
  - Charge/décharge journalière et totale
  - Capacité et puissance nominales
- 📊 **Production étendue**
  - Production journalière, mensuelle et annuelle
  - Valeur de génération en temps réel
- ⚡ **Consommation**
  - Puissance d'utilisation en temps réel
- 🔧 **Système**
  - Type de système d'alimentation
  - Attributs étendus sur tous les capteurs

### Corrigé
- Structure de données alignée avec l'API
- Gestion correcte des timestamps
- Configuration simplifiée

## [1.0.0] - 2026-01-28

### Ajouté
- Première version de l'intégration TSUN Monitoring
- Support de l'authentification OAuth2
- Récupération des données de stations
- Capteurs pour la puissance de génération
- Capteurs pour l'énergie totale produite
- Capteurs pour la capacité installée
- Capteur du statut réseau
- Configuration via l'interface utilisateur (Config Flow)
- Support HACS
- Documentation complète
