/**
 * Demonstrate asynchronous flow coordination with Promise.allSettled and resilient UI rendering.
 */

async function fetchTelemetryMetrics() {
  return { latencyMs: 142, cacheHitRate: 0.94 };
}

async function fetchOptionalRecommendations() {
  // Simulate third-party service outage (503 Service Unavailable)
  throw new Error("Service Unavailable: recommendations engine offline");
}

async function loadDashboardData() {
  // Using Promise.all would fail the ENTIRE dashboard if the optional recommendations fail!
  // Promise.allSettled allows resilient partial rendering:
  const [metricsResult, recsResult] = await Promise.allSettled([
    fetchTelemetryMetrics(),
    fetchOptionalRecommendations()
  ]);

  const uiState = {
    metrics: metricsResult.status === "fulfilled" ? metricsResult.value : null,
    metricsError: metricsResult.status === "rejected" ? metricsResult.reason.message : null,
    recommendations: recsResult.status === "fulfilled" ? recsResult.value : [],
    recommendationsNotice: recsResult.status === "rejected" ? "Recommendations currently unavailable" : null
  };

  return uiState;
}

loadDashboardData().then(state => {
  if (state.metrics === null) throw new Error("Core metrics should have loaded");
  if (state.recommendationsNotice === null) throw new Error("Optional failure notice expected");
  console.log(`Resilient dashboard loaded: metrics_ok=${state.metrics !== null}, degraded_optional=${state.recommendationsNotice !== null}`);
});
