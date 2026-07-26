import { postJson } from "../api.js";
import { createRiskChart, updateRiskChart } from "../charts.js";
import { seedTransactions, samples } from "../data/samples.js";
import { drawNetwork } from "../graph/canvas.js";
import { buildGraph } from "../graph/model.js";
import { escapeHtml, formatCurrency, formatPercent, setText } from "../utils.js";

const state = {
  transactions: [...seedTransactions],
  riskChart: null
};

export function initMonitorPage() {
  document.getElementById("transactionForm").addEventListener("submit", handleTransactionSubmit);
  document.querySelectorAll("[data-sample]").forEach((button) => {
    button.addEventListener("click", () => loadSample(button.dataset.sample));
  });

  state.riskChart = createRiskChart();
  renderMonitor();
  drawNetwork(state.transactions);
  window.addEventListener("resize", () => drawNetwork(state.transactions));
  window.addEventListener("themechange", () => {
    drawNetwork(state.transactions);
    updateRiskChart(state.riskChart, state.transactions);
  });
}

function loadSample(sampleName) {
  const sample = samples[sampleName];
  if (!sample) {
    return;
  }

  document.getElementById("sender").value = sample.sender;
  document.getElementById("receiver").value = sample.receiver;
  document.getElementById("amount").value = sample.amount;
  document.getElementById("type").value = sample.type;
}

async function handleTransactionSubmit(event) {
  event.preventDefault();

  const transaction = {
    sender: document.getElementById("sender").value.trim(),
    receiver: document.getElementById("receiver").value.trim(),
    amount: Number(document.getElementById("amount").value),
    type: document.getElementById("type").value
  };

  if (!transaction.sender || !transaction.receiver || !Number.isFinite(transaction.amount) || transaction.amount <= 0) {
    updateResult({
      risk: 0,
      label: "Invalid transaction",
      message: "Sender, receiver, and a positive amount are required.",
      level: "danger"
    });
    return;
  }

  setScanLoading(true);

  try {
    const prediction = await postJson("/api/predict", transaction);

    if (prediction.error) {
      throw new Error(prediction.error);
    }

    const risk = Math.round(prediction.risk_score);
    const result = {
      risk,
      label: prediction.fraud_prediction === 1 ? "Fraud predicted" : "Likely legitimate",
      message: `Model probability: ${formatPercent(prediction.fraud_probability)} using threshold ${formatPercent(prediction.threshold)}. Alerts: ${prediction.alerts?.length || 0}.`,
      level: prediction.fraud_prediction === 1 ? "danger" : risk >= 40 ? "warn" : "safe"
    };

    state.transactions.unshift({
      ...transaction,
      risk,
      prediction: prediction.fraud_prediction,
      probability: prediction.fraud_probability
    });

    updateResult(result);
    renderMonitor();
    drawNetwork(state.transactions);
  } catch (error) {
    updateResult({
      risk: 0,
      label: "Backend unavailable",
      message: `${error.message}. Start the backend with python app.py and open http://127.0.0.1:5000.`,
      level: "danger"
    });
  } finally {
    setScanLoading(false);
  }
}

function setScanLoading(isLoading) {
  const button = document.querySelector("#transactionForm .primary-action");
  if (!button) {
    return;
  }

  button.disabled = isLoading;
  button.textContent = isLoading ? "Running model..." : "Assess risk";
}

function renderMonitor() {
  const graph = buildGraph(state.transactions);
  const risks = state.transactions.map((transaction) => transaction.risk || 0);
  const flagged = state.transactions.filter((transaction) => transaction.prediction === 1).length;
  const averageRisk = risks.length
    ? Math.round(risks.reduce((total, risk) => total + risk, 0) / risks.length)
    : 0;

  setText("totalTransactions", state.transactions.length);
  setText("flaggedTransactions", flagged);
  setText("averageRisk", `${averageRisk}%`);
  setText("knownAccounts", graph.nodes.size);
  setText("graphSummary", `${graph.nodes.size} nodes, ${graph.edges.length} edges`);

  renderTransactionTable();
  updateRiskChart(state.riskChart, state.transactions);
}

function renderTransactionTable() {
  const table = document.getElementById("transactionTable");
  if (!table) {
    return;
  }

  table.innerHTML = state.transactions.slice(0, 8).map((transaction) => {
    const riskClass = transaction.prediction === 1 ? "risk-high" : transaction.risk >= 40 ? "risk-mid" : "risk-low";
    return `
      <tr>
        <td>${escapeHtml(transaction.sender)}</td>
        <td>${escapeHtml(transaction.receiver)}</td>
        <td>${escapeHtml(transaction.type)}</td>
        <td>${formatCurrency(transaction.amount)}</td>
        <td class="${riskClass}">${transaction.risk}%</td>
      </tr>
    `;
  }).join("");
}

function updateResult(result) {
  const card = document.getElementById("resultCard");
  if (!card) {
    return;
  }

  card.className = `result-card ${result.level}`;
  card.classList.remove("is-hidden");
  setText("resultTitle", `${result.label}: ${result.risk}%`);
  setText("resultText", result.message);
  document.getElementById("riskFill").style.width = `${result.risk}%`;
}

