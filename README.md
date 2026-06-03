                                                                                                    
# 🔍 FINDexplorER — v0.2

**Alternative rapide et légère à l'Explorateur Windows, optimisée pour la navigation au clavier.**

FINDexplorER est un gestionnaire de fichiers ultra-rapide conçu avec Python et CustomTkinter. Inspiré du design de Windows 11, il propose une interface fluide et un accès instantané à vos fichiers grâce à un raccourci global et une navigation entièrement pensée pour le clavier.

---

## ⌨️ Raccourcis Clavier

L'application a été conçue pour être pilotée sans jamais lâcher le clavier.

| Raccourci | Action |
| :--- | :--- |
| **`Ctrl` + `Espace`** | **Raccourci Global :** Afficher / Masquer FINDexplorER depuis n'importe quelle application |
| **`Flèche Bas ↓`** | Descendre dans la liste (charge la suite automatiquement si le dossier est grand) |
| **`Flèche Haut ↑`** | Monter dans la liste |
| **`Entrée ↵`** | Ouvrir le dossier sélectionné ou lancer le fichier avec le programme Windows par défaut |
| **`Retour Arrière ⌫`** | Remonter au dossier parent (Dossier supérieur) |
| **`Ctrl` + `X`** | Couper l'élément sélectionné |
| **`Ctrl` + `C`** | Copier l'élément sélectionné |
| **`Ctrl` + `V`** | Coller les éléments du presse-papier dans le dossier courant |
| **`Suppr`** | Supprimer définitivement l'élément sélectionné (avec confirmation) |
| **`F2`** | Renommer l'élément sélectionné |
| **`Échap`** | Masquer l'application (réduction instantanée dans la zone de notification) |
| **`Ctrl` + `D`** | Revenir à la racine de l'ordinateur
| **`Ctrl` + `H`** | Aller directement au dossier personnel |
 |

---

## ⚖️ Mentions Légales & Licence

Ce programme est un logiciel libre, mis à disposition sous les termes de la **Licence MIT**.

### Conditions Générales (Licence MIT)
Copyright (c) 2026 Geo

L'autorisation est accordée par la présente, à titre gratuit, à toute personne obtenant une copie de ce logiciel et des fichiers de documentation associés (le "Logiciel"), d'exploiter le Software sans restriction, y compris, mais sans s'y limiter, les droits d'utiliser, de copier, de modifier, de fusionner, de publier, de distribuer, de sous-licencier et/ou de vendre des copies du Logiciel, et de permettre aux personnes auxquelles le Logiciel est fourni de le faire, sous réserve des conditions suivantes :

* L'avis de copyright ci-dessus et la présente autorisation doivent être inclus dans toutes les copies ou portions substantielles du Logiciel.

### Exclusion de Responsabilité (Disclaimer)
LE LOGICIEL EST FOURNI "EN L'ÉTAT", SANS GARANTIE D'AUCUNE SORTIE, EXPRESSE OU IMPLICITE, Y COMPRIS MAIS SANS S'Y LIMITER, LES GARANTIES DE QUALITÉ MARCHANDE, D'ADÉQUATION À UN USAGE PARTICULIER ET DE NON-CONTREFAÇON. 

EN AUCUN CAS LES AUTEURS OU TITULAIRES DU DROIT D'AUTEUR NE POURRONT ÊTRE TENUS POUR RESPONSABLES DE TOUTE RÉCLAMATION, DOMMAGE OU AUTRE RESPONSABILITÉ, QUE CE SOIT DANS LE CADRE D'UN CONTRAT, D'UN DÉLIT OU AUTRE, DÉCOULANT DE, LIÉ À OU EN RELATION AVEC LE LOGICIEL OU L'UTILISATION OU D'AUTRES RAPPORTS AVEC LE LOGICIEL.

---

## 🛠️ Compilation (Pour les développeurs)

Si vous souhaitez modifier le code et compiler votre propre exécutable standalone :
1. Assurez-vous d'avoir Python 3.12 installé.
2. Lancez simplement le script d'automatisation fourni :
   ```bash
   build.bat
