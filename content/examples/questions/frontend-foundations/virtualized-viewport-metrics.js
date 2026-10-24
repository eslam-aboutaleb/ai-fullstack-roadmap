/**
 * Simulate virtualized list windowing and Cumulative Layout Shift (CLS) prevention.
 */

function calculateVirtualWindow(scrollTop, viewportHeight, rowHeight, totalItems, overscan = 1) {
  const totalHeight = totalItems * rowHeight;
  const rawStart = Math.floor(scrollTop / rowHeight);
  const rawEnd = Math.ceil((scrollTop + viewportHeight) / rowHeight);

  const startIndex = Math.max(0, rawStart - overscan);
  const endIndex = Math.min(totalItems - 1, rawEnd + overscan);

  const visibleCount = endIndex - startIndex + 1;
  const topPadding = startIndex * rowHeight;
  const bottomPadding = (totalItems - 1 - endIndex) * rowHeight;

  return {
    startIndex,
    endIndex,
    visibleCount,
    topPadding,
    bottomPadding,
    totalHeight
  };
}

// 10,000 items, rowHeight = 40px, viewportHeight = 120px (3 items visible), scrollTop = 400px (item index 10)
const win = calculateVirtualWindow(400, 120, 40, 10000, 1);
// rawStart = 10, rawEnd = 13. With overscan 1: startIndex = 9, endIndex = 14 => 6 items (or if total is 5 active nodes)
// Let's test with overscan 0 for exact viewport test:
const winExact = calculateVirtualWindow(400, 120, 40, 10000, 0); // startIndex 10, endIndex 13 -> 4 items

// Pre-allocated height prevents layout shift during scrolling
const layoutShiftScore = win.topPadding + win.visibleCount * 40 + win.bottomPadding === win.totalHeight ? 0 : 1;

console.log(
  `Virtualized viewport verified: active_dom_nodes=${win.visibleCount}, total_dataset_items=10000, cls_score=${layoutShiftScore}`
);
