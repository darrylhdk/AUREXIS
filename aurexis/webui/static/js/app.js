/* AUREXIS - Frontend App */

const API = "";
let currentSessionId = generateUID();
let isStreaming = false;

// ── State ──────────────────────────────────────────────────

const state = {
  activeLLM: "phi2_local",
  activeMode: "assistant",
  messages: [],
};

// ── Init ───────────────────────────────────────────────────

window.addEventListener("load", async () => {
  await loadStatus();
  await loadAPIKeys();
  await loadMCPServers();
  loadOfficialMCPCatalog();
});

async function loadStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    
    state.activeLLM = data.active_llm;
    state.activeMode = data.active_mode;
    
    document.getElementById("llmSelect").value = data.active_llm;
    document.getElementById("statusText").textContent = `AUREXIS v1.0 — ${data.active_llm}`;
    updateBadges();
    setModeActive(data.active_mode);
    
  } catch (e) {
    document.getElementById("statusText").textContent = "Déconnecté";
    document.querySelector(".status-dot").style.background = "var(--error)";
  }
}

// ── Sending Messages ───────────────────────────────────────

async function sendMessage() {
  const input = document.getElementById("messageInput");
  const text = input.value.trim();
  if (!text || isStreaming) return;
  
  input.value = "";
  input.style.height = "auto";
  hideWelcome();
  
  appendMessage("user", text);
  const typingEl = appendTyping();
  
  isStreaming = true;
  document.getElementById("sendBtn").disabled = true;
  
  try {
    if (state.activeMode === "autonomous") {
      await runAutonomous(text, typingEl);
    } else {
      await streamChat(text, typingEl);
    }
  } catch (e) {
    typingEl.remove();
    appendMessage("assistant", `❌ Erreur: ${e.message}`);
  } finally {
    isStreaming = false;
    document.getElementById("sendBtn").disabled = false;
  }
}

async function streamChat(text, typingEl) {
  const res = await fetch("/api/chat/stream", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ message: text, session_id: currentSessionId }),
  });
  
  if (!res.ok) throw new Error(await res.text());
  
  typingEl.remove();
  const msgEl = appendMessage("assistant", "");
  const bubble = msgEl.querySelector(".message-bubble");
  
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let fullText = "";
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split("\n");
    
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const token = line.slice(6);
        if (token === "[DONE]") break;
        fullText += token;
        bubble.innerHTML = renderMarkdown(fullText);
        scrollToBottom();
      }
    }
  }
}

async function runAutonomous(goal, typingEl) {
  typingEl.remove();
  const msgEl = appendMessage("assistant", "");
  const bubble = msgEl.querySelector(".message-bubble");
  bubble.innerHTML = `<div class="plan-container"><p>🧠 Planification de l'objectif...</p></div>`;
  
  const res = await fetch("/api/autonomous", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ goal, session_id: currentSessionId }),
  });
  
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split("\n").filter(l => l.startsWith("data: "));
    
    for (const line of lines) {
      try {
        const event = JSON.parse(line.slice(6));
        updateAutonomousDisplay(bubble, event);
        scrollToBottom();
      } catch (e) {}
    }
  }
}

function updateAutonomousDisplay(bubble, event) {
  const container = bubble.querySelector(".plan-container") || bubble;
  
  if (event.type === "plan") {
    let html = `<strong>📋 Plan d'exécution:</strong><div class="plan-steps">`;
    for (const step of event.data.steps) {
      html += `<div class="plan-step" id="step-${step.id}">
        <span>${step.id}. ${step.action}</span>
        ${step.tool ? `<small> [${step.tool}]</small>` : ""}
      </div>`;
    }
    html += `</div>`;
    container.innerHTML = html;
    
  } else if (event.type === "step_done") {
    const el = document.getElementById(`step-${event.step_id}`);
    if (el) {
      el.classList.add("done");
      el.innerHTML += ` ✅`;
    }
    
  } else if (event.type === "step_failed") {
    const el = document.getElementById(`step-${event.step_id}`);
    if (el) {
      el.classList.add("failed");
      el.innerHTML += ` ❌`;
    }
    
  } else if (event.type === "complete") {
    container.innerHTML += `<hr style="margin:12px 0;border-color:var(--border)">
      <strong>✅ Résultat final:</strong><br>${renderMarkdown(event.summary)}`;
  }
}

// ── Chat Management ────────────────────────────────────────

function appendMessage(role, content) {
  const container = document.getElementById("messages");
  
  const wrapper = document.createElement("div");
  wrapper.className = `message-wrapper ${role}`;
  
  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = role === "user" ? "U" : "⬡";
  
  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.innerHTML = content ? renderMarkdown(content) : "";
  
  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  container.appendChild(wrapper);
  
  scrollToBottom();
  return wrapper;
}

function appendTyping() {
  const container = document.getElementById("messages");
  const wrapper = document.createElement("div");
  wrapper.className = "message-wrapper assistant typing-indicator";
  wrapper.innerHTML = `
    <div class="message-avatar">⬡</div>
    <div class="message-bubble"><div class="dots">
      <div class="dot"></div><div class="dot"></div><div class="dot"></div>
    </div></div>`;
  container.appendChild(wrapper);
  scrollToBottom();
  return wrapper;
}

function hideWelcome() {
  const welcome = document.querySelector(".welcome-screen");
  if (welcome) welcome.remove();
}

function clearChat() {
  const container = document.getElementById("messages");
  container.innerHTML = "";
  newSession();
}

function newSession() {
  currentSessionId = generateUID();
  const container = document.getElementById("messages");
  container.innerHTML = `
    <div class="welcome-screen">
      <div class="welcome-logo">⬡</div>
      <h1 class="welcome-title">AUREXIS</h1>
      <p class="welcome-subtitle">Votre Agent IA universel, local et extensible</p>
      <div class="quick-actions">
        <button class="quick-action" onclick="sendQuick('Qu\\'est-ce que tu peux faire?')">Capacités</button>
        <button class="quick-action" onclick="sendQuick('Liste les MCP disponibles')">MCP disponibles</button>
        <button class="quick-action" onclick="sendQuick('Aide-moi à écrire un business plan')">Business plan</button>
        <button class="quick-action" onclick="sendQuick('Analyse une CVE récente')">Analyse CVE</button>
      </div>
    </div>`;
}

function sendQuick(text) {
  document.getElementById("messageInput").value = text;
  sendMessage();
}

// ── LLM & Mode ─────────────────────────────────────────────

async function changeLLM(llmId) {
  try {
    await fetch("/api/llm/set", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ llm_id: llmId }),
    });
    state.activeLLM = llmId;
    updateBadges();
  } catch (e) {
    console.error("Erreur changement LLM:", e);
  }
}

async function setMode(mode) {
  try {
    await fetch("/api/mode/set", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ mode }),
    });
    state.activeMode = mode;
    setModeActive(mode);
    updateBadges();
  } catch (e) {
    console.error("Erreur changement mode:", e);
  }
}

function setModeActive(mode) {
  document.querySelectorAll(".mode-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  });
}

function updateBadges() {
  const llmNames = {
    phi2_local: "Phi-2 Local", openai: "GPT-4o", anthropic: "Claude",
    mistral: "Mistral", groq: "Groq", kimi: "Kimi", custom: "Custom API"
  };
  const modeNames = {
    assistant: "Assistant", cyber: "Cyber", business: "Business", autonomous: "Autonome"
  };
  
  document.getElementById("activeLLMBadge").textContent = llmNames[state.activeLLM] || state.activeLLM;
  document.getElementById("activeModeBadge").textContent = modeNames[state.activeMode] || state.activeMode;
}

// ── API Keys ───────────────────────────────────────────────

async function loadAPIKeys() {
  try {
    const res = await fetch("/api/keys/list");
    const data = await res.json();
    
    const list = document.getElementById("apiKeysList");
    list.innerHTML = "";
    
    for (const provider of data.providers) {
      list.innerHTML += `<div class="api-key-item">
        <span class="provider-name">${provider}</span>
        <span class="key-status">✓ Configurée</span>
        <button onclick="deleteKey('${provider}')">✕</button>
      </div>`;
    }
  } catch (e) {}
}

async function saveAPIKey() {
  const provider = document.getElementById("keyProvider").value;
  const key = document.getElementById("keyValue").value.trim();
  
  if (!key) return alert("Veuillez entrer une clé API");
  
  try {
    await fetch("/api/keys/save", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ provider, key }),
    });
    document.getElementById("keyValue").value = "";
    await loadAPIKeys();
    
    // Réinitialiser le provider LLM
    if (["openai", "anthropic", "mistral", "groq", "kimi"].includes(provider)) {
      await fetch("/api/llm/invalidate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ provider }),
      });
    }
  } catch (e) {
    alert("Erreur: " + e.message);
  }
}

async function deleteKey(provider) {
  if (!confirm(`Supprimer la clé ${provider}?`)) return;
  await fetch("/api/keys/delete", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ provider }),
  });
  await loadAPIKeys();
}

// ── MCP Servers ────────────────────────────────────────────

async function loadMCPServers() {
  try {
    const res = await fetch("/api/mcp/servers");
    const data = await res.json();
    
    const list = document.getElementById("mcpList");
    
    if (data.servers.length === 0) {
      list.innerHTML = '<span class="empty-state">Aucun serveur MCP</span>';
      return;
    }
    
    list.innerHTML = data.servers.map(s => `
      <div class="mcp-item">
        <span class="dot-connected">●</span>
        <span>${s.name} (${s.tools_count} tools)</span>
        <button class="icon-btn" onclick="removeMCP('${s.name}')">✕</button>
      </div>`).join("");
  } catch (e) {}
}

async function addMCPServer() {
  const name = document.getElementById("mcpName").value.trim();
  const url = document.getElementById("mcpUrl").value.trim();
  
  if (!name || !url) return alert("Nom et URL requis");
  
  try {
    const res = await fetch("/api/mcp/add", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ name, url }),
    });
    const data = await res.json();
    
    if (data.success) {
      closeModal("mcpModal");
      await loadMCPServers();
    } else {
      alert("Connexion échouée. Vérifiez que le serveur MCP est en cours d'exécution.");
    }
  } catch (e) {
    alert("Erreur: " + e.message);
  }
}

async function removeMCP(name) {
  await fetch("/api/mcp/remove", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ name }),
  });
  await loadMCPServers();
}

async function loadOfficialMCPCatalog() {
  try {
    const res = await fetch("/api/mcp/catalog");
    const data = await res.json();
    
    const container = document.getElementById("catalogItems");
    if (container) {
      container.innerHTML = data.servers.map(s => `
        <div class="catalog-item">
          <div>
            <strong>${s.name}</strong>
            <small style="color:var(--text-muted);display:block">${s.description}</small>
          </div>
          <button class="small-btn" onclick="prefillMCP('${s.name}','${s.url}')" style="width:auto;padding:4px 10px">Ajouter</button>
        </div>`).join("");
    }
  } catch (e) {}
}

function prefillMCP(name, url) {
  document.getElementById("mcpName").value = name;
  document.getElementById("mcpUrl").value = url;
}

// ── Settings ───────────────────────────────────────────────

async function saveSettings() {
  const customUrl = document.getElementById("customApiUrl").value;
  const customModel = document.getElementById("customModel").value;
  const webhookToken = document.getElementById("webhookToken").value;
  
  await fetch("/api/settings/save", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ custom_api_url: customUrl, custom_model: customModel, webhook_verify_token: webhookToken }),
  });
  
  closeModal("settingsModal");
}

// ── Modals ─────────────────────────────────────────────────

function showAPIKeysModal() {
  loadAPIKeys();
  document.getElementById("apiKeysModal").style.display = "flex";
}

function showMCPModal() {
  document.getElementById("mcpModal").style.display = "flex";
}

function showSettings() {
  document.getElementById("settingsModal").style.display = "flex";
}

function closeModal(id) {
  document.getElementById(id).style.display = "none";
}

// Close on outside click
document.querySelectorAll(".modal-overlay").forEach(el => {
  el.addEventListener("click", (e) => {
    if (e.target === el) el.style.display = "none";
  });
});

// ── Utilities ──────────────────────────────────────────────

function handleKeydown(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 200) + "px";
}

function scrollToBottom() {
  const container = document.getElementById("messages");
  container.scrollTop = container.scrollHeight;
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
}

function generateUID() {
  return Math.random().toString(36).slice(2, 10);
}

function renderMarkdown(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\n/g, '<br>');
}
