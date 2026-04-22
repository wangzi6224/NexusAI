const healthStatusEl = document.getElementById("health-status");
const messageListEl = document.getElementById("message-list");
const chatFormEl = document.getElementById("chat-form");
const messageInputEl = document.getElementById("message-input");
const sendButtonEl = document.getElementById("send-button");

function appendMessage(role, content) {
  const itemEl = document.createElement("div");
  itemEl.className = `message-item ${role}`;

  const roleEl = document.createElement("div");
  roleEl.className = "message-role";
  roleEl.textContent = role === "user" ? "你" : "助手";

  const contentEl = document.createElement("div");
  contentEl.textContent = content;

  itemEl.appendChild(roleEl);
  itemEl.appendChild(contentEl);

  messageListEl.appendChild(itemEl);
  messageListEl.scrollTop = messageListEl.scrollHeight;
}

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

checkHealth();
