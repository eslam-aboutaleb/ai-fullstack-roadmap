/**
 * Simulate React Fiber concurrent work loop and lane-based priority scheduling.
 */

class FiberScheduler {
  constructor() {
    this.urgentQueue = [];
    this.transitionQueue = [];
    this.completed = [];
  }

  schedule(taskName, priority) {
    if (priority === "urgent") {
      this.urgentQueue.push({ taskName, priority });
    } else {
      this.transitionQueue.push({ taskName, priority });
    }
  }

  workLoop() {
    // Process high-priority lanes (discrete user interactions) before background transitions
    while (this.urgentQueue.length > 0) {
      const fiber = this.urgentQueue.shift();
      this.completed.push(fiber);
    }

    while (this.transitionQueue.length > 0) {
      const fiber = this.transitionQueue.shift();
      this.completed.push(fiber);
    }
  }
}

const scheduler = new FiberScheduler();
// Queue background transition first, then urgent user click
scheduler.schedule("transition-data-table", "transition");
scheduler.schedule("urgent-button-click", "urgent");
scheduler.schedule("transition-chart-render", "transition");

scheduler.workLoop();

const urgentFirst = scheduler.completed[0].taskName === "urgent-button-click";
console.log(
  `React Fiber workloop verified: urgent_completed_first=${urgentFirst}, total_fibers_reconciled=${scheduler.completed.length}`
);
