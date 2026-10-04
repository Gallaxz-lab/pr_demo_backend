"""
Double-entry general ledger. Every money-moving action elsewhere in the app
(order payment verified, marketplace settlement imported, supplier invoice
posted, goods received) calls post_journal_entry() here instead of just
updating a status field — so the system can produce a real trial balance,
not just dashboard numbers that look about right.

Accounting note on channel treatment: a LINE/manual order is treated as
cash received immediately on verification (Debit Cash) since an admin just
confirmed a payment slip. A marketplace order (Shopee/Lazada) is treated as
Accounts Receivable at verification instead — the platform owes you, not
the customer — and only becomes Cash when the matching settlement import
clears that receivable. This is a deliberate simplification of real
accrual accounting, not a bug; a production system would also handle
partial settlements, refunds, and multi-currency, none of which are here.
"""
from sqlalchemy.orm import Session
from app import models

CHART_OF_ACCOUNTS = [
    ("1000", "Cash", models.AccountType.asset),
    ("1100", "Accounts Receivable", models.AccountType.asset),
    ("1200", "Inventory", models.AccountType.asset),
    ("2000", "Accounts Payable", models.AccountType.liability),
    ("2100", "VAT Payable", models.AccountType.liability),
    ("3000", "Owner's Equity", models.AccountType.equity),
    ("4000", "Sales Revenue", models.AccountType.revenue),
    ("5000", "Cost of Goods Sold", models.AccountType.expense),
    ("5100", "Marketplace Fees Expense", models.AccountType.expense),
    ("5200", "General Operating Expense", models.AccountType.expense),
]


def seed_chart_of_accounts(db: Session):
    for code, name, type_ in CHART_OF_ACCOUNTS:
        if not db.query(models.Account).filter_by(code=code).first():
            db.add(models.Account(code=code, name=name, type=type_))
    db.commit()


def get_account(db: Session, code: str) -> models.Account:
    account = db.query(models.Account).filter_by(code=code).first()
    if not account:
        raise ValueError(f"Unknown account code {code} — check CHART_OF_ACCOUNTS")
    return account


def post_journal_entry(db: Session, memo: str, reference: str, lines: list[tuple[str, float, float]]) -> models.JournalEntry:
    """lines: list of (account_code, debit, credit). Must balance — an
    unbalanced entry is refused rather than silently posted, since a ledger
    that can drift out of balance isn't one."""
    total_debit = round(sum(d for _, d, _ in lines), 2)
    total_credit = round(sum(c for _, _, c in lines), 2)
    if total_debit != total_credit:
        raise ValueError(f"Unbalanced journal entry: debits {total_debit} != credits {total_credit}")

    entry = models.JournalEntry(memo=memo, reference=reference)
    db.add(entry)
    db.flush()
    for code, debit, credit in lines:
        account = get_account(db, code)
        db.add(models.JournalLine(entry_id=entry.id, account_id=account.id, debit=debit, credit=credit))
    db.commit()
    db.refresh(entry)
    return entry


def trial_balance(db: Session) -> list[dict]:
    rows = []
    for a in db.query(models.Account).all():
        lines = db.query(models.JournalLine).filter_by(account_id=a.id).all()
        debit = sum(l.debit for l in lines)
        credit = sum(l.credit for l in lines)
        rows.append({"code": a.code, "name": a.name, "type": a.type.value, "debit": debit, "credit": credit, "balance": debit - credit})
    return rows
