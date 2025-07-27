console.log("✅ Chat JS loaded");
function toggleChat() {
  const box = document.getElementById("chat-box");
  box.style.display = box.style.display === "none" ? "block" : "none";
}

function appendMessage(content, sender = 'bot') {
  const msg = document.createElement('div');
  msg.classList.add('chat-msg', sender === 'user' ? 'user-msg' : 'bot-msg');
  msg.innerText = content;
  document.getElementById('chat-body').appendChild(msg);
  document.getElementById('chat-body').scrollTop = 9999;
}

function sendMessage() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;

  appendMessage(text, 'user');
  input.value = '';

  fetch('/chatbot/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ message: text })
  })
  .then(res => res.json())
  .then(data => {
    if (data.response) {
      appendMessage(data.response);  // ✅ updated to match Django's key
    } else if (data.reply) {
      appendMessage(data.reply);     // fallback if "reply" is used
    } else if (data.error) {
      appendMessage("⚠️ Error: " + data.error);
    } else {
      appendMessage("⚠️ Unexpected server response.");
    }
  })
  .catch(err => {
    console.error(err);
    appendMessage("❌ Error: Couldn't reach server.");
  });
}

function sendFAQ(question) {
  appendMessage(question, 'user');

  fetch('/chatbot/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ message: question })
  })
  .then(res => res.json())
  .then(data => {
    if (data.response) {
      appendMessage(data.response);
    } else if (data.reply) {
      appendMessage(data.reply);
    } else if (data.error) {
      appendMessage("⚠️ Error: " + data.error);
    } else {
      appendMessage("⚠️ Unexpected server response.");
    }
  })
  .catch(err => {
    console.error(err);
    appendMessage("❌ Error: Couldn't reach server.");
  });
}

// Hide chat box initially
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("chat-box").style.display = "none";
});
