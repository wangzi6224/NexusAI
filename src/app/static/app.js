const healthStatusEl = document.getElementById("health-status");
const messageListEl = document.getElementById("message-list");
const chatFormEl = document.getElementById("chat-form");
const messageInputEl = document.getElementById("message-input");
const sendButtonEl = document.getElementById("send-button");
const clearHistoryButtonEl = document.getElementById("clear-history-button");
const modelSelectEl = document.getElementById("model-select");

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderBasicMarkdown(text) {
  let html = escapeHtml(text);

  html = html.replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>");
  html = html.replace(/`([^`\n]+)`/g, "<code>$1</code>");
  html = html.replace(/\n/g, "<br>");

  return html;
}

function appendMessage(role, content) {
  const itemEl = document.createElement("div");
  itemEl.className = `message-item ${role}`;

  const roleEl = document.createElement("div");
  roleEl.className = "message-role";
  roleEl.textContent = role === "user" ? "你" : "助手";

  const contentEl = document.createElement("div");

  if (role === "assistant") {
    contentEl.innerHTML = renderBasicMarkdown(content);
  } else {
    contentEl.textContent = content;
  }

  itemEl.appendChild(roleEl);
  itemEl.appendChild(contentEl);

  messageListEl.appendChild(itemEl);
  messageListEl.scrollTop = messageListEl.scrollHeight;
}

async function loadModels() {
  const response = await fetch("/models");
  const data = await response.json();

  modelSelectEl.innerHTML = "";

  data.available_models.forEach((model) => {
    const optionEl = document.createElement("option");
    optionEl.value = model;
    optionEl.textContent = model;
    optionEl.selected = model === data.current_model;
    modelSelectEl.appendChild(optionEl);
  });
}

async function selectModel(model) {
  const response = await fetch("/model/select", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "模型切换失败");
  }

  return response.json();
}

function clearMessageList() {
  messageListEl.innerHTML = "";
}

async function loadHistory() {
  try {
    const response = await fetch("/history");
    const data = await response.json();

    clearMessageList();

    data.forEach((item) => {
      appendMessage("user", item.user_input);
      appendMessage("assistant", item.answer);
    });
  } catch (error) {
    appendMessage("assistant", "历史记录加载失败");
  }
}

async function clearHistory() {
  const response = await fetch("/history/clear", {
    method: "POST",
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "清空历史失败");
  }

  return response.json();
}

clearHistoryButtonEl.addEventListener("click", async () => {
  try {
    await clearHistory();
    clearMessageList();
    appendMessage("assistant", "会话已清空");
  } catch (error) {
    appendMessage("assistant", `清空失败：${error.message}`);
  }
});

async function checkHealth() {
  try {
    const response = await fetch("/health");
    const data = await response.json();

    if (data.ok) {
      healthStatusEl.textContent = `服务状态：正常`;
    } else {
      healthStatusEl.textContent = `服务状态：异常 - ${data.message}`;
    }
  } catch (error) {
    healthStatusEl.textContent = `服务状态：检查失败`;
  }
}

async function sendMessage(message) {
  const response = await fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "请求失败");
  }

  return response.json();
}

chatFormEl.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInputEl.value.trim();
  if (!message) {
    return;
  }

  appendMessage("user", message);

  messageInputEl.value = "";
  sendButtonEl.disabled = true;
  sendButtonEl.textContent = "发送中...";

  try {
    const data = await sendMessage(message);
    appendMessage("assistant", data.answer);
  } catch (error) {
    appendMessage("assistant", `请求失败：${error.message}`);
  } finally {
    sendButtonEl.disabled = false;
    sendButtonEl.textContent = "发送";
    messageInputEl.focus();
  }
});

modelSelectEl.addEventListener("change", async (event) => {
  const selectedModel = event.target.value;

  try {
    await selectModel(selectedModel);
    appendMessage("assistant", `当前模型已切换为：${selectedModel}`);
  } catch (error) {
    appendMessage("assistant", `模型切换失败：${error.message}`);
  }
});

checkHealth();
loadHistory();
loadModels();
