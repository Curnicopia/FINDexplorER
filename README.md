# 🔍 FINDexplorER — v0.2 FR

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
| ****`Ctrl` + `Flèche Bas ↓`** | Ouvrir le dossier sélectionné ou lancer le fichier avec le programme Windows par défaut |
| ****`Ctrl` + `Flèche Haut ↑`** | Remonter au dossier supérieur |
| **`Retour Arrière ⌫`** | Remonter au dossier parent (Dossier supérieur) |
| **`Ctrl` + `X`** | Couper l'élément sélectionné |
| **`Ctrl` + `C`** | Copier l'élément sélectionné |
| **`Ctrl` + `V`** | Coller les éléments du presse-papier dans le dossier courant |
| **`Suppr`** | Supprimer définitivement l'élément sélectionné (avec confirmation) |
| **`F2`** | Renommer l'élément sélectionné |
| **`Échap`** | Masquer l'application (réduction instantanée dans la zone de notification) |
| **`Ctrl` + `D`** | Revenir à la racine de l'ordinateur
| **`Ctrl` + `H`** | Aller directement au dossier personnel |

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
   
# 🔍 FINDexplorER — v0.2 EN

A fast and lightweight alternative to Windows Explorer, optimized for keyboard navigation.

FINDexplorER is an ultra-fast file manager built with Python and CustomTkinter. Inspired by the Windows 11 design language, it offers a smooth interface and instant access to your files through a global shortcut and navigation designed entirely around the keyboard.

⌨️ Keyboard Shortcuts
The application is designed to be driven without ever leaving the keyboard.

| Shortcut | Action |
| :--- | :--- |
| **`Ctrl` + `Espace`** | **Global Shortcut :** Afficher / Show / Hide FINDexplorER from any application |
| **`Arrow Down ↓`** | Move down in the list (automatically loads more if the folder is large) |
| **`Arrow Up ↑`** | Move up in the list |
| **`Entrée ↵`** | Open the selected folder or launch the file with the default Windows program |
| **Ctrl` + `Arrow Down ↓`** | Open the selected folder or launch the file with the default Windows program) |
| **Ctrl` + `Arrow Up ↑`** | Go back to the parent folder |
| **`Retour Arrière ⌫`** | Go up to the parent folder |
| **`Ctrl` + `X`** | Cut the selected item |
| **`Ctrl` + `C`** | Copy the selected item |
| **`Ctrl` + `V`** | Paste clipboard items into the current folder |
| **`Suppr`** | Permanently delete the selected item (with confirmation) |
| **`F2`** | Rename the selected item |
| **`Échap`** | Hide the application (instantly minimizes to the notification area) |
| **`Ctrl` + `D`** | Return to the computer root
| **`Ctrl` + `H`** | Go directly to the home folder |

⚖️ Legal Notice & License
This program is free software, made available under the terms of the MIT License.
General Terms (MIT License)
Copyright (c) 2026 Geo
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

Disclaimer
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

🛠️ Build Instructions (For Developers)
If you wish to modify the code and compile your own standalone executable:

Make sure you have Python 3.12 installed.
Simply run the provided automation script:

   ```bash
   build.bat
