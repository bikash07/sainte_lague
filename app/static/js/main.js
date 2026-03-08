const TAB_ACTIVE_CLASS = "is-active";
const charts = {};
let dashboardData = null;

function activateTab(targetId) {
  const tabs = Array.from(document.querySelectorAll(".tab"));
  const panels = Array.from(document.querySelectorAll(".panel"));
  tabs.forEach((tab) =>
    tab.classList.toggle(TAB_ACTIVE_CLASS, tab.dataset.tabTarget === targetId),
  );
  panels.forEach((panel) =>
    panel.classList.toggle(TAB_ACTIVE_CLASS, panel.id === targetId),
  );
}

function resizeCharts() {
  Object.values(charts).forEach((chart) => {
    if (chart && typeof chart.resize === "function") {
      chart.resize();
    }
  });
}

function initTabs() {
  const tabs = Array.from(document.querySelectorAll(".tab"));
  if (!tabs.length) return;

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetId = tab.dataset.tabTarget;
      activateTab(targetId);
      if (targetId === "fptp-panel" && !charts.fptp) {
        renderFptpChart();
      }
      requestAnimationFrame(resizeCharts);
    });
  });
}

function buildPieChart(key, canvasId, labels, values, palette) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !labels.length || !values.length || typeof Chart === "undefined") {
    return;
  }
  if (charts[key]) {
    charts[key].destroy();
  }

  const backgroundColor = labels.map((_, idx) => palette[idx % palette.length]);
  charts[key] = new Chart(canvas, {
    type: "pie",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor,
          borderColor: "#ffffff",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 1,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            usePointStyle: true,
            boxWidth: 10,
            font: {
              family: "Instrument Sans",
              size: 12,
            },
          },
        },
        tooltip: {
          callbacks: {
            label(context) {
              return `${context.label}: ${context.parsed}`;
            },
          },
        },
      },
    },
  });
}

function palette() {
  return [
    "#1f4e79",
    "#2d6ca2",
    "#3b7bb5",
    "#4e93cf",
    "#6daedf",
    "#8cc2ea",
    "#f38d68",
    "#de6f4d",
    "#c7523f",
  ];
}

function renderPrChart() {
  if (!dashboardData) return;
  buildPieChart("pr", "prPieChart", dashboardData.pr.labels, dashboardData.pr.values, palette());
}

function renderFptpChart() {
  if (!dashboardData) return;
  buildPieChart(
    "fptp",
    "fptpPieChart",
    dashboardData.fptp.labels,
    dashboardData.fptp.values,
    palette(),
  );
}

function initCharts() {
  dashboardData = window.dashboardData;
  if (!dashboardData) return;

  renderPrChart();
  const isFptpActive = document.getElementById("fptp-panel")?.classList.contains(TAB_ACTIVE_CLASS);
  if (isFptpActive) {
    renderFptpChart();
  }
}

function initResizeHandler() {
  let resizeTimer = null;
  window.addEventListener("resize", () => {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(resizeCharts, 120);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initCharts();
  initResizeHandler();
});
