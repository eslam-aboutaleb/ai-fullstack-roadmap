let generation = 7;
let view = null;
function publish(owner, value) {
  if (owner !== generation) return false;
  view = value;
  return true;
}
const oldOwner = generation;
generation = 8;
if (publish(oldOwner, "old account")) throw new Error("stale result accepted");
if (!publish(8, "current account") || view !== "current account") throw new Error("current result rejected");
console.log("stale rejected; current accepted");
