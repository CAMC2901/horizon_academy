// DOM Elements
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');

// Landing Page Elements
const landingPage = document.getElementById('landing-page');
const appContainer = document.getElementById('app-container');
const startBtn = document.getElementById('start-btn');
const backBtn = document.getElementById('back-btn');
const escalationBtn = document.getElementById('escalation-btn');

// Inscription Modal Elements
const inscriptionModal = document.getElementById('inscription-modal');
const openInscriptionBtn = document.getElementById('open-inscription-btn');
const navInscriptionLink = document.getElementById('nav-inscription-link');
const heroInscriptionBtn = document.getElementById('hero-inscription-btn');
const closeModalBtn = document.getElementById('close-modal-btn');
const inscriptionForm = document.getElementById('inscription-form');
const inscriptionAlert = document.getElementById('inscription-alert');

// Metrics DOM elements
const metricQueries = document.getElementById('metric-queries');
const metricCache = document.getElementById('metric-cache');
const metricEscalations = document.getElementById('metric-escalations');
const metricCost = document.getElementById('metric-cost');

// Polling interval for metrics
let metricsInterval;

function createMessageElement(text, sender) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}`;
  
  const bubbleDiv = document.createElement('div');
  bubbleDiv.className = 'bubble';
  
  // Basic markdown rendering for bold text and links
  let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Linkify URLs (specifically for the Google forms link)
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  formattedText = formattedText.replace(urlRegex, '<a href="$1" target="_blank" style="color: inherit; text-decoration: underline;">$1</a>');
  
  bubbleDiv.innerHTML = formattedText;
  msgDiv.appendChild(bubbleDiv);
  
  return msgDiv;
}

function showTypingIndicator() {
  const div = document.createElement('div');
  div.className = 'typing-indicator';
  div.id = 'typing-indicator';
  div.innerHTML = '<span></span><span></span><span></span>';
  chatMessages.appendChild(div);
  scrollToBottom();
}

function removeTypingIndicator() {
  const indicator = document.getElementById('typing-indicator');
  if (indicator) {
    indicator.remove();
  }
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function updateMetrics() {
  try {
    const res = await fetch('/api/metrics');
    if (res.ok) {
      const data = await res.json();
      metricQueries.textContent = data.processedQueries;
      metricCache.textContent = data.cacheHits;
      metricEscalations.textContent = `${(data.escalationRate * 100).toFixed(0)}%`;
      metricCost.textContent = `$${data.totalCostUSD}`;
    }
  } catch (error) {
    console.error('Failed to fetch metrics:', error);
  }
}

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const message = chatInput.value.trim();
  if (!message) return;
  
  // Clear input
  chatInput.value = '';
  
  // Add user message to UI
  chatMessages.appendChild(createMessageElement(message, 'user'));
  scrollToBottom();
  
  showTypingIndicator();
  
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    
    removeTypingIndicator();
    
    if (res.ok) {
      const data = await res.json();
      chatMessages.appendChild(createMessageElement(data.reply, 'assistant'));
    } else {
      chatMessages.appendChild(createMessageElement("Lo siento, ocurrió un error en el servidor. Intenta de nuevo más tarde.", 'assistant'));
    }
  } catch (error) {
    removeTypingIndicator();
    chatMessages.appendChild(createMessageElement("Error de conexión. Revisa tu internet.", 'assistant'));
  }
  
  scrollToBottom();
  updateMetrics();
});

// Modal controls
function openModal() {
  if (inscriptionModal) {
    inscriptionModal.classList.remove('hidden');
    if (inscriptionAlert) {
      inscriptionAlert.className = 'inscription-alert hidden';
      inscriptionAlert.textContent = '';
    }
  }
}

function closeModal() {
  if (inscriptionModal) {
    inscriptionModal.classList.add('hidden');
  }
}

if (openInscriptionBtn) openInscriptionBtn.addEventListener('click', openModal);
if (navInscriptionLink) navInscriptionLink.addEventListener('click', (e) => { e.preventDefault(); openModal(); });
if (heroInscriptionBtn) heroInscriptionBtn.addEventListener('click', openModal);
if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);

if (inscriptionModal) {
  inscriptionModal.addEventListener('click', (e) => {
    if (e.target === inscriptionModal) closeModal();
  });
}

// Inscription Form Submission
if (inscriptionForm) {
  inscriptionForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const nombre = document.getElementById('ins-nombre').value.trim();
    const correo = document.getElementById('ins-correo').value.trim();
    const telefono = document.getElementById('ins-telefono').value.trim();
    const curso = document.getElementById('ins-curso').value;
    const nivel = document.getElementById('ins-nivel').value;
    const modalidad = document.getElementById('ins-modalidad').value;
    const franja_horaria = document.getElementById('ins-franja').value;

    try {
      const res = await fetch('/api/inscriptions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre,
          correo,
          telefono,
          curso,
          nivel,
          modalidad,
          franja_horaria
        })
      });

      if (res.ok) {
        inscriptionAlert.className = 'inscription-alert success';
        inscriptionAlert.textContent = '🎉 ¡Inscripción registrada con éxito! Te contactaremos pronto.';
        inscriptionForm.reset();
        setTimeout(closeModal, 2500);
      } else {
        const errData = await res.json();
        inscriptionAlert.className = 'inscription-alert error';
        inscriptionAlert.textContent = `❌ Error: ${errData.detail || 'No se pudo guardar la inscripción.'}`;
      }
    } catch (error) {
      console.error('Error submitting inscription:', error);
      inscriptionAlert.className = 'inscription-alert error';
      inscriptionAlert.textContent = '❌ Error de conexión al registrar la inscripción.';
    }
  });
}

// Initial setup
async function initializeApp() {
  // Reset metrics on page reload so each session starts fresh
  try {
    await fetch('/api/metrics/reset', { method: 'POST' });
  } catch (err) {
    console.error('Failed to reset metrics:', err);
  }

  updateMetrics();
  metricsInterval = setInterval(updateMetrics, 10000); // Update every 10 seconds

  // Fetch config for the escalation button
  try {
    const res = await fetch('/api/config');
    if (res.ok) {
      const data = await res.json();
      if (data.escalation_form_url && escalationBtn) {
        escalationBtn.href = data.escalation_form_url;
        escalationBtn.classList.remove('hidden');
      }
    }
  } catch (error) {
    console.error('Failed to fetch config:', error);
  }
}

// Handle transition from landing page to chat
if (startBtn) {
  startBtn.addEventListener('click', () => {
    landingPage.classList.add('fade-out');
    
    setTimeout(() => {
      landingPage.classList.add('hidden');
      appContainer.classList.remove('hidden');
      appContainer.classList.add('fade-in');
      appContainer.classList.remove('fade-out');
      chatInput.focus();
    }, 400);
  });
}

// Handle transition back to landing page
if (backBtn) {
  backBtn.addEventListener('click', () => {
    appContainer.classList.add('fade-out');
    appContainer.classList.remove('fade-in');

    setTimeout(() => {
      appContainer.classList.add('hidden');
      landingPage.classList.remove('hidden');
      landingPage.classList.remove('fade-out');
    }, 400);
  });
}

initializeApp();
