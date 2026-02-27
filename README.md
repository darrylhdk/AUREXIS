<div align="center">

```
 █████╗ ██╗   ██╗██████╗ ███████╗██╗  ██╗██╗███████╗
██╔══██╗██║   ██║██╔══██╗██╔════╝╚██╗██╔╝██║██╔════╝
███████║██║   ██║██████╔╝█████╗   ╚███╔╝ ██║███████╗
██╔══██║██║   ██║██╔══██╗██╔══╝   ██╔██╗ ██║╚════██║
██║  ██║╚██████╔╝██║  ██║███████╗██╔╝ ██╗██║███████║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚══════╝
```

**Universal AI Agent OS** — Multi-LLM · Local · Extensible · Open Source

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey?style=flat-square)]()

</div>

---

## 🤖 C'est quoi AUREXIS ?

**AUREXIS** est un **OS d'agent IA** qui tourne entièrement sur ton PC — comme ChatGPT, mais **local, gratuit, et sous ton contrôle total.**

Tu peux lui brancher n'importe quel LLM (GPT-4, Claude, Mistral, ou un modèle local), connecter des outils via le protocole MCP, et lui parler depuis Telegram, Discord, WhatsApp ou via l'interface web.

> Aucun abonnement. Aucune donnée envoyée vers le cloud (sauf si tu utilises une API cloud). 100% chez toi.

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🧠 **Multi-LLM** | OpenAI, Claude, Mistral, Groq, Kimi, Phi-2 local, ou n'importe quelle API compatible OpenAI |
| 🔒 **100% Local** | Tourne sur ton PC, tes clés API sont chiffrées localement |
| 🔌 **MCP Compatible** | Connecte des outils externes (fichiers, GitHub, web, base de données...) |
| 🤖 **4 Modes Agent** | Assistant général, Cybersécurité, Business/Startup, Autonome (planifie + exécute) |
| 💬 **Interface Web** | UI style ChatGPT accessible sur `http://localhost:8000` |
| 📱 **Multi-connecteurs** | Telegram, Discord, WhatsApp, Facebook Messenger |
| ⚡ **Streaming** | Réponses en temps réel via WebSocket |
| 🎨 **Personnalisable** | Prompts système modifiables par LLM et par mode |

---

## ⚡ Installation en 1 commande

### Windows — PowerShell
```powershell
iwr -useb https://raw.githubusercontent.com/darrylhdk/aurexis/main/install_aurexis.ps1 | iex
```

### Windows — Double-clic
👉 Télécharge **[install_aurexis.bat](install_aurexis.bat)** et double-clique dessus.

### Mac / Linux
```bash
curl -fsSL https://raw.githubusercontent.com/darrylhdk/aurexis/main/install_aurexis.sh | bash
```

L'installateur fait **tout automatiquement** :
- ✅ Vérifie Python et Git
- ✅ Clone le projet
- ✅ Installe les dépendances
- ✅ Crée ton profil local
- ✅ Crée un raccourci sur le bureau
- ✅ Lance AUREXIS et ouvre le navigateur

---

## 🛠️ Installation manuelle

Si tu préfères tout faire toi-même :

```bash
# 1. Clone le projet
git clone https://github.com/darrylhdk/aurexis.git
cd aurexis

# 2. Installe les dépendances
pip install -r requirements.txt

# 3. Setup (une seule fois)
python install.py

# 4. Lance !
python main.py
```

Ouvre **http://localhost:8000** dans ton navigateur. C'est tout. 🎉

---

## 🚀 Démarrage rapide — 3 options

### Option A — Sans rien installer (Groq, gratuit)
1. Lance AUREXIS → `python main.py`
2. Va sur http://localhost:8000
3. Clique **API Keys** → entre ta clé Groq (gratuite sur [groq.com](https://groq.com))
4. Change le LLM → **Groq** dans le sidebar
5. Commence à discuter !

### Option B — Avec OpenAI
1. Récupère ta clé sur [platform.openai.com](https://platform.openai.com)
2. Dans l'UI → API Keys → colle ta clé OpenAI
3. LLM → **OpenAI GPT**

### Option C — 100% local (aucune clé, aucune connexion)
```bash
# Télécharge le modèle Phi-2 (~1.6 Go)
mkdir models
# Télécharge phi-2.Q4_K_M.gguf depuis :
# https://huggingface.co/TheBloke/phi-2-GGUF
# et place-le dans le dossier models/
```
Le LLM tourne entièrement sur ton CPU. Fonctionne sans internet.

---

## 🎮 Les 4 modes de l'agent

```
┌─────────────────┬──────────────────────────────────────────────────────┐
│ 🤖 Assistant    │ Mode par défaut. Répond à toutes tes questions.       │
│ 🔐 Cyber        │ Analyse de sécurité, OSINT, audit, vulnérabilités.    │
│ 📈 Business     │ Stratégie startup, GTM, pitch, analyse de marché.     │
│ 🚀 Autonome     │ Décompose une tâche complexe en étapes et l'exécute.  │
└─────────────────┴──────────────────────────────────────────────────────┘
```

---

## 🧠 LLMs supportés

| LLM | Clé API | Qualité | Vitesse |
|-----|---------|---------|---------|
| ⚡ **Phi-2 (local)** | ❌ Aucune | ★★★☆☆ | Dépend du PC |
| 🟢 **OpenAI GPT-4o** | ✅ Oui | ★★★★★ | Rapide |
| 🟣 **Anthropic Claude** | ✅ Oui | ★★★★★ | Rapide |
| 🔵 **Mistral** | ✅ Oui | ★★★★☆ | Rapide |
| ⚡ **Groq** | ✅ Gratuit | ★★★★☆ | Ultra rapide |
| 🌙 **Kimi** | ✅ Oui | ★★★★☆ | Rapide |
| ⚙️ **Custom API** | Optionnel | Variable | Variable |

---

## 🔌 Connecter des outils (MCP)

AUREXIS est compatible avec le protocole officiel [Model Context Protocol](https://github.com/modelcontextprotocol/servers).

Dans l'interface web → **Settings → MCP** → entre l'URL de ton serveur MCP.

Les outils sont découverts automatiquement. Exemples d'outils disponibles :

```
filesystem    → Lire/écrire des fichiers sur ton PC
brave_search  → Recherche web en temps réel
github        → Accès à tes repos GitHub
puppeteer     → Contrôle automatique d'un navigateur
postgres      → Requêtes sur ta base de données
slack         → Lire/envoyer des messages Slack
```

---

## 📱 Connecteurs messaging

| Connecteur | Comment activer |
|---|---|
| **Telegram** | Settings → Connectors → entre ton token @BotFather |
| **Discord** | Settings → Connectors → entre ton token de bot Discord |
| **WhatsApp** | Settings → Connectors → entre ton token Meta API |
| **Facebook** | Webhook auto configuré sur `/webhook/facebook` |

---

## 📁 Structure du projet

```
aurexis/
├── main.py              ← Point d'entrée
├── install.py           ← Setup wizard (1 fois)
├── server.py            ← Serveur FastAPI + WebSocket
│
├── core/
│   ├── orchestrator.py  ← Coordinateur central
│   ├── planner.py       ← Planificateur autonome
│   ├── memory.py        ← Historique conversation
│   ├── auth.py          ← Coffre-fort clés API (chiffré)
│   └── permissions.py   ← Sécurité — filtre les actions
│
├── llm/
│   ├── registry.py      ← Catalogue des LLMs
│   ├── router.py        ← Sélecteur de LLM
│   └── providers/       ← Un fichier par LLM
│
├── prompts/             ← Prompts système (modifiables)
├── mcp/                 ← Client MCP officiel
├── connectors/          ← Telegram, Discord, WhatsApp
└── webui/               ← Interface web
```

---

## 🔒 Sécurité

- Les clés API sont **chiffrées** avec AES-128 (Fernet) et stockées localement
- Le LLM **ne peut jamais** exécuter d'action système directement
- Toutes les actions passent par une **PermissionGate** selon le mode actif
- Les fichiers sensibles sont dans `.gitignore` — ils ne seront **jamais** sur GitHub

---

## 🧩 Ajouter un nouveau LLM

Créer un fichier `llm/providers/mon_llm.py` :

```python
from llm.base import BaseLLM

class MonLLM(BaseLLM):
    name = "mon_llm"
    description = "Mon LLM custom"

    async def chat(self, system, messages, tools=None) -> str:
        # Ton appel API ici
        return "réponse"

    async def stream(self, system, messages, tools=None):
        yield await self.chat(system, messages, tools)
```

Puis l'enregistrer dans `llm/registry.py` :

```python
from llm.providers.mon_llm import MonLLM
LLMRegistry.register("mon_llm", MonLLM)
```

C'est tout. Il apparaît immédiatement dans l'UI et la CLI.

---

## 💻 Commandes CLI

```bash
python main.py                  # Lance avec interface web
python main.py --cli-only       # Mode terminal pur
python main.py --port 9000      # Change le port

# Dans le mode CLI :
/llm list                       # Liste les LLMs disponibles
/llm use groq                   # Change de LLM
/mode cyber                     # Change de mode
/key set openai sk-...          # Ajoute une clé API
/mcp connect http://...         # Connecte un serveur MCP
/status                         # Affiche l'état actuel
```

---

## 🗺️ Roadmap

- [x] Multi-LLM avec switching dynamique
- [x] Interface web style ChatGPT
- [x] MCP client officiel
- [x] Connecteurs Telegram / Discord / WhatsApp
- [x] Mode autonome avec planificateur
- [x] Chiffrement clés API
- [ ] Mémoire longue terme (embeddings)
- [ ] Plugin marketplace
- [ ] Version SaaS multi-tenant
- [ ] Interface mobile (PWA)
- [ ] Multi-agent (agents qui collaborent)

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

```bash
# Fork le repo, puis :
git clone https://github.com/darrylhdk/aurexis.git
git checkout -b feature/ma-fonctionnalite
# ... tes modifications ...
git commit -m "✨ Ajout de ma fonctionnalité"
git push origin feature/ma-fonctionnalite
# Ouvre une Pull Request
```

---

## 📄 Licence

MIT — Libre d'utilisation, modification et distribution.

---

<div align="center">

Fait avec ❤️ par **[Darryl](https://github.com/darrylhdk)**

⭐ Si ce projet t'est utile, laisse une étoile sur GitHub !

</div>
