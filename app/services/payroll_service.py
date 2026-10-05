"""
DEMO ESTIMATOR ONLY — not verified against current Thai tax law or SSF
rules. SSF_RATE and SSF_MAX_BASE are placeholders that need confirming
against the current official rate/wage ceiling before any real use.

Withholding tax (PND.1) is intentionally left at 0, not faked at a flat
rate — real Thai personal income tax withholding is progressive brackets
with allowances, and a wrong flat-rate guess here is worse than an honest
"not implemented." Do not run real payroll against this without a
qualified accountant reviewing both the SSF numbers and adding real WHT
bracket logic first.
"""

SSF_RATE = 0.05        # PLACEHOLDER — verify current employee SSF rate
SSF_MAX_BASE = 15000    # PLACEHOLDER — verify current SSF wage ceiling (บาท/เดือน)


def estimate_payslip(monthly_salary: float) -> dict:
    ssf_base = min(monthly_salary, SSF_MAX_BASE)
    ssf = round(ssf_base * SSF_RATE, 2)
    withholding_tax = 0.0  # deliberately not implemented — see module docstring
    net = round(monthly_salary - ssf - withholding_tax, 2)
    return {"gross_pay": monthly_salary, "ssf_deduction": ssf, "withholding_tax": withholding_tax, "net_pay": net}
