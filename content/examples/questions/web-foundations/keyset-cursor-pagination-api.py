"""Demonstrate Keyset cursor pagination in REST APIs vs shifting OFFSET pagination under concurrent writes."""
import base64
import json

class ItemRepository:
    def __init__(self):
        # 20 items chronologically ordered descending (newest first)
        self.items = [
            {"id": i, "created_at": 1700000000 + i, "title": f"Document {i}"}
            for i in range(20, 0, -1)
        ]

    def encode_cursor(self, created_at, item_id):
        raw = json.dumps({"created_at": created_at, "id": item_id})
        return base64.urlsafe_b64encode(raw.encode()).decode()

    def decode_cursor(self, cursor_str):
        if not cursor_str:
            return None
        raw = base64.urlsafe_b64decode(cursor_str.encode()).decode()
        return json.loads(raw)

    def paginate_keyset(self, cursor_str=None, limit=5):
        cursor = self.decode_cursor(cursor_str)
        results = []
        for item in self.items:
            if cursor:
                # Keyset predicate: (created_at < cursor_time) OR (created_at == cursor_time AND id < cursor_id)
                if item["created_at"] > cursor["created_at"]:
                    continue
                if item["created_at"] == cursor["created_at"] and item["id"] >= cursor["id"]:
                    continue
            results.append(item)
            if len(results) == limit:
                break
                
        next_cursor = None
        if len(results) == limit:
            last = results[-1]
            next_cursor = self.encode_cursor(last["created_at"], last["id"])
            
        return results, next_cursor

repo = ItemRepository()

# Client fetches Page 1 (items 20 down to 16):
page_1, next_cursor_1 = repo.paginate_keyset(limit=5)
assert [i["id"] for i in page_1] == [20, 19, 18, 17, 16]

# CONCURRENT WRITE: A new item 21 is inserted at the top of the feed before Page 2 is requested!
repo.items.insert(0, {"id": 21, "created_at": 1700000021, "title": "Document 21"})

# Client fetches Page 2 using cursor:
# In OFFSET pagination (limit=5, offset=5), inserting item 21 causes item 16 to be returned AGAIN (duplicate item)!
# With Keyset cursor pagination, the cursor precisely anchors position, returning items 15 down to 11 without duplicates:
page_2, next_cursor_2 = repo.paginate_keyset(cursor_str=next_cursor_1, limit=5)
assert [i["id"] for i in page_2] == [15, 14, 13, 12, 11]

# Zero duplicate items across page 1 and page 2:
page1_ids = set(i["id"] for i in page_1)
page2_ids = set(i["id"] for i in page_2)
assert len(page1_ids.intersection(page2_ids)) == 0

print(f"Keyset pagination verified: page_1={list(page1_ids)}, page_2={list(page2_ids)}, zero_overlap=True")

