# Lexique des sentiments

Un outil pour trouver le mot juste quand on cherche à nommer un sentiment. On part d'un mot qui vient à l'esprit, on regarde les mots de sens voisin, on lit leurs fiches, puis on se recentre sur l'un d'eux, et ainsi de suite. Ce n'est pas un test ni un diagnostic : on arrive avec un mot, on repart avec un mot plus précis.

**Utiliser l'outil en ligne : https://gogumpe.github.io/lexique_des_sentiments/**

Il fonctionne aussi sans connexion : téléchargez `index.html` et ouvrez-le dans un navigateur. Le fichier contient tout (données, polices).

## Ce que contient le lexique

330 mots français des sentiments, répartis en huit familles et leurs sous-familles. Chaque mot a une fiche rédigée pour l'outil : définition (avec un lien vers l'entrée du CNRTL), ce qui déclenche le sentiment, ce qu'on ressent dans le corps, ce vers quoi il pousse, et les nuances avec les mots proches.

## Lire la roue

Le ou les mots choisis sont au centre (jusqu'à cinq) ; autour, leurs plus proches voisins de sens.

- **Distance au centre** : plus un mot est près, plus son sens est proche. C'est la lecture principale.
- **Direction** : à droite, un sentiment plus agréable que le centre ; à gauche, moins agréable ; en haut, plus agité ; en bas, plus calme.
- **Vue 3D** : ajoute un troisième axe, le sentiment de contrôle (vers l'avant, un état plus maîtrisé à agrément égal). On fait tourner la roue à la souris ou au doigt ; la taille et l'opacité des mots indiquent la profondeur. Un mot qui paraît proche du centre peut en réalité être loin devant ou derrière : tourner la vue permet de le voir.

Un clic sur un mot le place seul au centre ; un appui long (ou Maj + clic) l'ajoute aux mots déjà au centre. Les filtres par famille et par système de Panksepp s'appliquent à la liste et aux voisins.

## Méthode

- **Proximité de sens** : chaque fiche est transformée en vecteur par le modèle BAAI/bge-m3, à partir du texte `mot : définition déclencheurs corps pousse` (les nuances ne sont pas prises en compte). La proximité est la similarité cosinus. Avec plusieurs mots au centre, on prend la moyenne normalisée de leurs vecteurs.
- **Valence** (agréable / désagréable) : moyenne du NRC VAD et d'EMONORM (ramené à la même échelle en divisant par 0,8) quand les deux diffèrent de moins de 0,375 ; sinon, arbitrage manuel. Valeur posée à la main pour « hâte » (+0,40, au sens d'« avoir hâte ») ; désaccord sur « ivresse » tranché en faveur du NRC (sens figuré).
- **Activation** (calme / agité) : NRC VAD seul ; deux mots utilisent d'autres termes anglais.
- **Contrôle** (subir / maîtriser) : NRC VAD seul, faute de norme française. 22 mots utilisent une forme anglaise qui décrit l'état vécu (`terrified` plutôt que `terror`), 3 sont arbitrés à la main (mépris et dédain +0,30, pitié −0,20). C'est la valeur affichée dans les fiches.
- **Contrôle relatif** (axe de la vue 3D) : le contrôle brut est très lié à la valence (corrélation 0,75). On retire donc la part prévisible par la valence (régression linéaire, recalculée à chaque construction), puis on multiplie par 1,6 pour donner aux écarts la même ampleur que sur les autres axes. Les 9 mots de la sous-famille Sérénité ont un plancher à 0 (le NRC confond calme et faiblesse). Les petits écarts (moins de 0,3 environ) entre mots d'une même sous-famille relèvent du bruit de mesure.
- **Systèmes de Panksepp** : les sept systèmes émotionnels de base décrits par Jaak Panksepp (Seeking, Rage, Fear, Lust, Care, Panic/Grief, Play), auxquels l'outil ajoute Spirituality. Chaque mot est rattaché à zéro, un ou plusieurs systèmes, comme central ou simplement présent.

## Organisation du dossier

| Dossier ou fichier | Contenu |
|---|---|
| `index.html` | L'outil complet, en un seul fichier (produit par `scripts/assemble.py`) |
| `src/app.html` | Interface : HTML, CSS et JavaScript |
| `src/fonts/` | Polices Gloria Hallelujah et Comfortaa (licence OFL) |
| `data/vdata.js` | Données : familles et sous-familles, fiches, valeurs affectives, vecteurs (1024 dimensions) |
| `data/E_bge.npy` | Mêmes vecteurs au format numpy |
| `fiches/` | Les 330 fiches (`fiches.py`, `fiches_lot1.py` … `fiches_lot7.py`), la liste des mots par famille (`vivier.py`), l'arborescence et les systèmes de Panksepp (`taxo.py`, `pk_old.json`), les corrections du contrôle et de l'activation (`controle.py`, `activation.py`) |
| `scripts/` | Scripts de construction |
| `export/fiches-sentiments.csv` | Toutes les fiches et leurs valeurs en tableur |

## Reconstruire

Il faut Python 3 avec `numpy` ; pour les vecteurs, aussi `sentence-transformers` et `torch` (la version CPU suffit). Le modèle BAAI/bge-m3 (environ 2,3 Go) se télécharge au premier lancement.

Les normes d'origine (NRC VAD, EMONORM) ne sont pas fournies dans ce dépôt, en raison de leurs licences. Il faut se les procurer auprès de leurs auteurs et les placer dans un dossier `normes/` pour relancer les deux premiers scripts.

1. `python scripts/combine_valence.py` : recalcule la valence.
2. `python scripts/build.py` : calcule les vecteurs et écrit `data/vdata.js` (quelques minutes sur CPU ; `--sans-vecteurs` réutilise les vecteurs existants).
3. `python scripts/export_csv.py` : met à jour le tableur.
4. `python scripts/assemble.py` : produit `index.html`.

Pour modifier seulement l'interface : éditer `src/app.html`, puis lancer l'étape 4.

## Sources

- NRC VAD Lexicon v2.1 (Mohammad, 2025), usage de recherche non commercial.
- EMONORM (Gobin et al., 2017 ; métanorme de Leveau et al., 2012).
- Modèle BAAI/bge-m3.
- Définitions rédigées pour l'outil, avec liens vers le CNRTL.

## Licence

CC BY-NC 4.0 (attribution, pas d'utilisation commerciale) : voir `LICENSE`. Les polices restent sous licence OFL et les valeurs issues du NRC sous les conditions du NRC.
