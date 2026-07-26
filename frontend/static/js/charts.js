export function createRiskChart() {
  const chartTarget = document.getElementById("riskChart");
  if (!chartTarget || !window.Chart) {
    return null;
  }

  const colors = getThemeColors();
  return new Chart(chartTarget, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "Model probability",
        data: [],
        borderColor: colors.primary,
        backgroundColor: colors.primaryFill,
        tension: 0.32,
        fill: true,
        pointRadius: 4
      }]
    },
    options: getChartOptions(100)
  });
}

export function createModelChart() {
  const chartTarget = document.getElementById("modelChart");
  if (!chartTarget || !window.Chart) {
    return null;
  }

  const colors = getThemeColors();
  return new Chart(chartTarget, {
    type: "bar",
    data: {
      labels: ["Precision", "Recall", "F1-score"],
      datasets: [{
        label: "Fraud class performance",
        data: [0.81, 0.91, 0.86],
        backgroundColor: [colors.accent, colors.warning, colors.primary],
        borderRadius: 6
      }]
    },
    options: getChartOptions(1)
  });
}

export function updateRiskChart(chart, transactions) {
  if (!chart) {
    return;
  }

  const recent = [...transactions].slice(0, 8).reverse();
  const colors = getThemeColors();
  chart.data.labels = recent.map((_, index) => `T${index + 1}`);
  chart.data.datasets[0].data = recent.map((transaction) => transaction.risk || 0);
  chart.data.datasets[0].borderColor = colors.primary;
  chart.data.datasets[0].backgroundColor = colors.primaryFill;
  chart.options = getChartOptions(100);
  chart.update();
}

function getChartOptions(maxValue) {
  const colors = getThemeColors();
  return {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      y: {
        beginAtZero: true,
        max: maxValue,
        ticks: { color: colors.muted },
        grid: { color: colors.grid }
      },
      x: {
        ticks: { color: colors.muted },
        grid: { display: false }
      }
    },
    plugins: {
      legend: {
        labels: { color: colors.text }
      }
    }
  };
}

function getThemeColors() {
  const styles = getComputedStyle(document.body);
  const primary = styles.getPropertyValue("--primary").trim() || "#5eb1ff";
  return {
    primary,
    accent: styles.getPropertyValue("--accent").trim() || "#42d392",
    warning: styles.getPropertyValue("--warning").trim() || "#f5a623",
    text: styles.getPropertyValue("--text").trim() || "#eef4f8",
    muted: styles.getPropertyValue("--muted").trim() || "#9cacbc",
    grid: styles.getPropertyValue("--line").trim() || "rgba(255,255,255,0.08)",
    primaryFill: colorToRgba(primary, 0.16),
  };
}

function colorToRgba(color, alpha) {
  if (!color.startsWith("#") || color.length !== 7) {
    return color;
  }
  const red = parseInt(color.slice(1, 3), 16);
  const green = parseInt(color.slice(3, 5), 16);
  const blue = parseInt(color.slice(5, 7), 16);
  return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
}

