import { shortId } from "../utils.js";
import { buildGraph } from "./model.js";

export function drawNetwork(transactions) {
  const canvas = document.getElementById("networkCanvas");
  if (!canvas) {
    return;
  }

  const ctx = canvas.getContext("2d");
  const graph = buildGraph(transactions);
  const nodes = [...graph.nodes.keys()];
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const cssWidth = Math.max(320, rect.width || canvas.clientWidth || 720);
  const cssHeight = Number(canvas.getAttribute("height") || 420);
  canvas.width = Math.floor(cssWidth * dpr);
  canvas.height = Math.floor(cssHeight * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const width = cssWidth;
  const height = cssHeight;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) * 0.36;
  const styles = getComputedStyle(document.body);
  const bg = styles.getPropertyValue("--bg-soft").trim() || "#0e141a";
  const text = styles.getPropertyValue("--text").trim() || "#dbe5ed";
  const primary = styles.getPropertyValue("--primary").trim() || "#5eb1ff";
  const accent = styles.getPropertyValue("--accent").trim() || "#44d19d";
  const warning = styles.getPropertyValue("--warning").trim() || "#f5c451";
  const danger = styles.getPropertyValue("--danger").trim() || "#ff6b6b";

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, width, height);

  const positions = new Map();
  nodes.forEach((id, index) => {
    const angle = (Math.PI * 2 * index) / nodes.length - Math.PI / 2;
    positions.set(id, {
      x: centerX + Math.cos(angle) * radius,
      y: centerY + Math.sin(angle) * radius
    });
  });

  graph.edges.slice(-24).forEach((edge) => {
    const source = positions.get(edge.source);
    const target = positions.get(edge.target);
    if (!source || !target) {
      return;
    }

    ctx.strokeStyle = edge.risk >= 70 ? danger : primary;
    ctx.globalAlpha = edge.risk >= 70 ? 0.78 : 0.42;
    ctx.lineWidth = Math.max(1, Math.min(5, Math.log10(edge.amount + 1)));
    ctx.beginPath();
    ctx.moveTo(source.x, source.y);
    ctx.lineTo(target.x, target.y);
    ctx.stroke();
    ctx.globalAlpha = 1;
  });

  nodes.forEach((id) => {
    const node = graph.nodes.get(id);
    const position = positions.get(id);
    const nodeRadius = 7 + Math.min(10, node.degree * 1.4);

    ctx.beginPath();
    ctx.fillStyle = node.pageRank > 0.16 ? warning : accent;
    ctx.arc(position.x, position.y, nodeRadius, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = text;
    ctx.font = "12px Inter, Segoe UI, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(shortId(id), position.x, position.y + nodeRadius + 16);
  });
}

