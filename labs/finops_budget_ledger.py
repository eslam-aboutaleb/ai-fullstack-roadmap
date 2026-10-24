"""Local provider-cost accounting with atomic user budgets and retries.

All amounts are integer millionths of USD (microUSD); rate in USD/million
tokens multiplied by tokens produces microUSD. This is a bounded reference
implementation, not an actual provider invoice or usage-meter integration.
"""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
import sqlite3
import tempfile


def charge_micro_usd(*, input_tokens, cached_input_tokens, output_tokens,
                     input_usd_per_m, cache_usd_per_m, output_usd_per_m):
    if any(type(x) is not int or x < 0 for x in
           (input_tokens,cached_input_tokens,output_tokens)):
        raise ValueError("token counts must be nonnegative integers")
    if cached_input_tokens > input_tokens:
        raise ValueError("cached tokens exceed total input tokens")
    rates=[Decimal(str(x)) for x in
           (input_usd_per_m,cache_usd_per_m,output_usd_per_m)]
    if any(not rate.is_finite() or rate<0 for rate in rates):
        raise ValueError("rates must be finite and nonnegative")
    amount=((input_tokens-cached_input_tokens)*rates[0]
            +cached_input_tokens*rates[1]+output_tokens*rates[2])
    return int(amount.to_integral_value(rounding=ROUND_CEILING))


class Ledger:
    def __init__(self, path):
        self.db=sqlite3.connect(str(path),timeout=10,isolation_level=None,
                                check_same_thread=False)
        self.db.execute("PRAGMA busy_timeout=10000")
        self.db.execute("""CREATE TABLE IF NOT EXISTS holds (
            id TEXT PRIMARY KEY, owner TEXT NOT NULL, task TEXT NOT NULL,
            cap INTEGER NOT NULL, budget INTEGER NOT NULL,
            status TEXT NOT NULL, actual INTEGER,
            price_revision TEXT NOT NULL
        )""")

    def close(self):
        self.db.close()

    def _begin(self):
        self.db.execute("BEGIN IMMEDIATE")

    def reserve(self, owner, attempt_id, task_id, max_micro_usd,
                budget_micro_usd, price_revision):
        if not all(isinstance(x,str) and x.strip() for x in
                   (owner,attempt_id,task_id,price_revision)):
            raise ValueError("trusted scope and stable attempt IDs required")
        if any(type(x) is not int or x<0 for x in (max_micro_usd,budget_micro_usd)):
            raise ValueError("nonnegative integer microUSD amounts required")
        self._begin()
        try:
            existing=self.db.execute(
                "SELECT owner, task, cap, budget, price_revision FROM holds WHERE id=?",
                (attempt_id,)).fetchone()
            if existing:
                if existing!=(owner,task_id,max_micro_usd,budget_micro_usd,price_revision):
                    raise ValueError("attempt replay conflicts with original reservation")
                self.db.execute("COMMIT")
                return False
            used=self.db.execute("""SELECT COALESCE(SUM(CASE WHEN status='settled'
                THEN actual ELSE cap END),0) FROM holds WHERE owner=?""",(owner,)).fetchone()[0]
            if used+max_micro_usd>budget_micro_usd:
                raise PermissionError("owner cost budget exhausted")
            self.db.execute("INSERT INTO holds VALUES (?,?,?,?,?,?,?,?)",
                            (attempt_id,owner,task_id,max_micro_usd,budget_micro_usd,
                             "reserved",None,price_revision))
            self.db.execute("COMMIT")
            return True
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    def settle(self, owner, attempt_id, actual_micro_usd):
        # Unknown provider usage is NOT treated as free; retain the reservation.
        if actual_micro_usd is None:
            return False
        if type(actual_micro_usd) is not int or actual_micro_usd<0:
            raise ValueError("actual charge must be a nonnegative integer")
        self._begin()
        try:
            row=self.db.execute("SELECT owner,cap,status,actual FROM holds WHERE id=?",
                                (attempt_id,)).fetchone()
            if row is None or row[0]!=owner:
                raise PermissionError("attempt is not owned by principal")
            if row[2]=="settled":
                if row[3]!=actual_micro_usd:
                    raise ValueError("conflicting settlement")
                self.db.execute("COMMIT")
                return False
            if actual_micro_usd>row[1]:
                raise ValueError("charge exceeds authorized reservation; reconcile externally")
            self.db.execute("UPDATE holds SET status='settled',actual=? WHERE id=?",
                            (actual_micro_usd,attempt_id))
            self.db.execute("COMMIT")
            return True
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    def usage(self, owner):
        rows=self.db.execute("SELECT status,cap,actual FROM holds WHERE owner=?",
                             (owner,)).fetchall()
        return {'settled':sum(row[2] for row in rows if row[0]=='settled'),
                'reserved':sum(row[1] for row in rows if row[0]=='reserved'),
                'attempts':len(rows)}


def check():
    # 200 prompt tokens, of which 50 were cache reads. Rates are illustrative
    # USD per million tokens; not a live vendor price claim.
    cost=charge_micro_usd(input_tokens=200,cached_input_tokens=50,output_tokens=80,
                          input_usd_per_m="2",cache_usd_per_m="0.5",output_usd_per_m="8")
    assert cost==965
    try:charge_micro_usd(input_tokens=4,cached_input_tokens=5,output_tokens=0,
                         input_usd_per_m=1,cache_usd_per_m=0,output_usd_per_m=1)
    except ValueError:pass
    else:raise AssertionError("cache count beyond input not rejected")
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/"ledger.sqlite3"
        led=Ledger(path)
        assert led.reserve("A","attempt-1","task-1",1000,2000,"price-r1")
        assert not led.reserve("A","attempt-1","task-1",1000,2000,"price-r1")
        assert led.settle("A","attempt-1",None) is False
        assert led.usage("A")['reserved']==1000
        try:led.settle("B","attempt-1",5)
        except PermissionError:pass
        else:raise AssertionError("tenant B settled A's attempt")
        assert led.settle("A","attempt-1",cost)
        assert led.usage("A")=={'settled':965,'reserved':0,'attempts':1}
        assert not led.settle("A","attempt-1",cost)
        assert led.reserve("A","retry-2","task-1",1000,2000,"price-r1")
        try:led.reserve("A","retry-3","task-1",100,2000,"price-r1")
        except PermissionError:pass
        else:raise AssertionError("attempt budget overspent")
        assert led.settle("A","retry-2",200)
        assert led.usage("A")=={'settled':1165,'reserved':0,'attempts':2}
        led.close()
        # Real SQLite write transactions coordinate separate connections.
        def competitor(i):
            other=Ledger(path)
            try:
                try:return other.reserve("B",f"b-{i}","task-B",500,1000,"r1")
                except PermissionError:return False
            finally:other.close()
        with ThreadPoolExecutor(max_workers=6) as pool:
            accepted=list(pool.map(competitor,range(8)))
        assert sum(accepted)==2,accepted
        verify=Ledger(path)
        assert verify.usage("B")['reserved']==1000
        assert verify.usage("A")['settled']==1165
        verify.close()
    print("FinOps cost and atomic budget ledger: priced cache, retry, scope, quota, concurrency PASS")


if __name__=="__main__":
    check()
