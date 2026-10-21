visible = {"D": {"revision": 4, "deleted": True}}
def apply(key, revision, deleted):
    current = visible.get(key)
    if current is None or revision > current["revision"]:
        visible[key] = {"revision": revision, "deleted": deleted}
        return True
    return False
assert not apply("D", 2, False)
assert visible["D"] == {"revision": 4, "deleted": True}
print("revision-2 backfill rejected; revision-4 deletion retained")
