"""
RLock — Reentrant Lock
======================
A regular Lock deadlocks if the same thread tries to acquire it twice.
RLock allows the *same* thread to acquire it multiple times — it must
release it the same number of times before another thread can acquire it.

Demo: BankAccount where transfer_to() acquires the RLock, then internally
calls withdraw() which acquires it again from the same thread.
"""

import threading
import time
import random


class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner   = owner
        self.balance = balance
        self._lock   = threading.RLock()   # ← RLock, not Lock

    def deposit(self, amount: float) -> None:
        with self._lock:                   # acquisition count → 1 (or 2 if called from transfer_to)
            print(f"  [{self.owner:6s}] Depositing  ${amount:7.2f}  "
                  f"| balance before: ${self.balance:8.2f}")
            self.balance += amount
            print(f"  [{self.owner:6s}] Deposit OK             "
                  f"| balance after:  ${self.balance:8.2f}")

    def withdraw(self, amount: float) -> bool:
        with self._lock:                   # acquisition count → 1 (or 2 if called from transfer_to)
            if amount > self.balance:
                print(f"  [{self.owner:6s}] ✗ Insufficient funds  "
                      f"| wanted ${amount:.2f}, have ${self.balance:.2f}")
                return False
            self.balance -= amount
            print(f"  [{self.owner:6s}] Withdrawing ${amount:7.2f}  "
                  f"| balance after:  ${self.balance:8.2f}")
            return True

    def transfer_to(self, recipient: "BankAccount", amount: float) -> None:
        with self._lock:                   # acquisition count → 1  (outer)
            print(f"\n  ── Transfer: {self.owner} ──▶ {recipient.owner}  "
                  f"${amount:.2f} ──")
            # withdraw() re-acquires the SAME RLock (count → 2).
            # With a plain Lock this line would deadlock forever.
            if self.withdraw(amount):      # count: 1 → 2 → back to 1
                recipient.deposit(amount)  # recipient has its own RLock
            # count drops back to 0 here; another thread may now acquire


def run_transfers(accounts: list[BankAccount]) -> None:
    """Randomly transfer money between accounts in parallel."""
    names = [a.owner for a in accounts]
    acct  = {a.owner: a for a in accounts}

    def worker(src_name: str, dst_name: str, amount: float) -> None:
        acct[src_name].transfer_to(acct[dst_name], amount)

    transfers = [
        ("Alice", "Bob",   200.00),
        ("Bob",   "Carol",  75.00),
        ("Carol", "Alice",  50.00),
        ("Alice", "Carol", 300.00),   # will fail — insufficient funds
        ("Bob",   "Alice",  30.00),
    ]

    threads = [
        threading.Thread(target=worker, args=(s, d, amt), name=f"{s}→{d}")
        for s, d, amt in transfers
    ]

    print("Starting transfers...\n")
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    print("=" * 58)
    print("  RLock — Reentrant Lock Demo")
    print("=" * 58)

    alice = BankAccount("Alice", 400.00)
    bob   = BankAccount("Bob",   250.00)
    carol = BankAccount("Carol", 180.00)

    print(f"\n  Initial balances:")
    for acct in (alice, bob, carol):
        print(f"    {acct.owner:6s}: ${acct.balance:.2f}")
    print()

    run_transfers([alice, bob, carol])

    print(f"\n  Final balances:")
    for acct in (alice, bob, carol):
        print(f"    {acct.owner:6s}: ${acct.balance:.2f}")

    total_before = 400 + 250 + 180
    total_after  = alice.balance + bob.balance + carol.balance
    print(f"\n  Total money (before): ${total_before:.2f}")
    print(f"  Total money (after):  ${total_after:.2f}")
    assert total_before == total_after, "Money was created or destroyed!"
    print("  ✓ Conservation of money verified — no race conditions")
    print()
    print("  Key point: transfer_to() calls withdraw() while already holding")
    print("  the RLock. A plain Lock would deadlock; RLock allows re-entry.")
