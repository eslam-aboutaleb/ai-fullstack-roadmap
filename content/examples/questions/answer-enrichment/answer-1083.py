class Cart:
    def __init__(self):
        self.items = []
    def add(self, item):
        self.items.append(item)
a, b = Cart(), Cart()
a.add("book")
assert a.items == ["book"] and b.items == []
assert a.items is not b.items
print("cart A=['book']; cart B=[]")
