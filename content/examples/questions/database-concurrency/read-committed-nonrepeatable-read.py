"""Demonstrate PostgreSQL Read Committed isolation mechanics and non-repeatable read hazards."""

class MVCCStore:
    def __init__(self):
        self.data = {1: {'price': 100, 'stock': 10}}

    def read_committed_query(self, row_id):
        # Under Read Committed, each statement acquires a fresh snapshot of the latest committed state
        return self.data[row_id]['price']

    def commit_update(self, row_id, new_price):
        self.data[row_id]['price'] = new_price

def test_read_committed_behavior():
    store = MVCCStore()

    # Session 1: Application checkout workflow opens transaction
    # Step 1: Session 1 reads product price = $100 to calculate invoice total
    price_step1 = store.read_committed_query(1)

    # Step 2: Meanwhile, admin pricing service in Session 2 updates price to $150 and commits
    store.commit_update(1, 150)

    # Step 3: Session 1 re-reads the product price in the SAME ongoing transaction:
    # Under Read Committed isolation, each statement acquires a NEW snapshot of the database!
    # Session 1 observes the newly committed price ($150) rather than the price read in Step 1.
    price_step3 = store.read_committed_query(1)

    non_repeatable_read = (price_step1 != price_step3)
    assert non_repeatable_read is True
    print(f"Read Committed non-repeatable read verified: step1_price={price_step1}, step3_price={price_step3}")

if __name__ == '__main__':
    test_read_committed_behavior()
