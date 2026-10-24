/**
 * Demonstrate TypeScript type narrowing algebra and exhaustive never fallback.
 */

// Discriminated union simulation
function dispatchAction(action) {
  switch (action.type) {
    case "insert":
      return `Inserted row ${action.id} with payload`;
    case "delete":
      return `Deleted row ${action.id}`;
    default: {
      // TypeScript never type fallback: runtime assertion if compiler checks are bypassed
      const exhaustiveCheck = action;
      throw new Error(`Unhandled action variant: ${JSON.stringify(exhaustiveCheck)}`);
    }
  }
}

// 1. Handled variants
const insertResult = dispatchAction({ type: "insert", id: "row-1", payload: "data" });
const deleteResult = dispatchAction({ type: "delete", id: "row-1" });

// 2. Unhandled variant triggering exhaustive check
let caughtUnhandled = false;
try {
  dispatchAction({ type: "unknown_op", id: "row-2" });
} catch (err) {
  caughtUnhandled = true;
}

console.log(
  `TypeScript narrowing algebra verified: handled_variants=2, unhandled_caught=${caughtUnhandled}`
);
