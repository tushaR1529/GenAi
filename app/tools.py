# app/tools.py
"""
VidyaLoan Agent Tools:
1. education_loan_cost_calculator: Computes moratorium interest, government subsidy/subvention,
   and post-moratorium monthly EMI under PM-Vidyalaxmi and PM-USP CSIS guidelines.
2. vidyaloan_rag_search: Grounded semantic search over VidyaLoan scheme documents.
"""
from typing import Any, Dict, List, Optional
from app.rag import answer_vidyaloan_question
from app.vectorstore import get_vectorstore


def education_loan_cost_calculator(
    loan_amount: float,
    interest_rate: float,
    course_years: float,
    family_income: float,
    is_qhei: bool = False,
    repayment_years: float = 15.0,
) -> Dict[str, Any]:
    """
    Calculate education loan cost under Indian Government Schemes (PM-Vidyalaxmi & PM-USP CSIS).

    Parameters:
    - loan_amount (float): Principal loan amount in INR (e.g. 750000 for Rs. 7.5 lakh).
    - interest_rate (float): Annual interest rate (e.g. 9.5 for 9.5%).
    - course_years (float): Duration of course in years (e.g. 4 for B.Tech, 2 for MBA/Diploma).
    - family_income (float): Gross annual family income in INR (e.g. 400000 for Rs. 4 lakh).
    - is_qhei (bool): Whether the institute is an approved Quality Higher Education Institution.
    - repayment_years (float): Repayment tenure in years after moratorium (standard up to 15 years).

    Returns:
    - Dict with detailed breakdown of moratorium interest, government subsidy share,
      student interest share, and post-moratorium monthly EMI.
    """
    loan_amount = float(loan_amount)
    # Normalize interest rate (if passed as 0.095, convert to 9.5 for consistency)
    if interest_rate < 1.0:
        rate_percent = interest_rate * 100.0
    else:
        rate_percent = float(interest_rate)
    rate_decimal = rate_percent / 100.0

    course_years = float(course_years)
    family_income = float(family_income)
    is_qhei = bool(is_qhei)
    repayment_years = float(repayment_years) if repayment_years and repayment_years > 0 else 15.0

    # 1. Moratorium Period: Course Duration + 1 Year (IBA Model Loan)
    moratorium_years = course_years + 1.0

    # 2. Total Moratorium Interest (Simple interest charged during moratorium)
    total_moratorium_interest = loan_amount * rate_decimal * moratorium_years

    # 3. Government Subsidy / Subvention Share Determination
    applied_scheme = "Standard IBA Model Education Loan"
    subsidy_type = "None"
    subsidy_rate = 0.0
    govt_moratorium_share = 0.0

    # Subvention applies up to Rs. 10 lakh loan principal ceiling
    subvention_eligible_loan = min(loan_amount, 1000000.0)

    if family_income <= 450000.0:
        # Case A: PM-USP CSIS (Full 100% Interest Subsidy for income <= 4.5 Lakh)
        applied_scheme = "PM-USP CSIS (Central Sector Interest Subsidy)"
        subsidy_type = "100% Full Interest Subsidy"
        subsidy_rate = rate_decimal
        govt_moratorium_share = subvention_eligible_loan * subsidy_rate * moratorium_years
        # If loan exceeds 10 lakh, student pays interest on excess portion
        if loan_amount > 1000000.0:
            excess_loan = loan_amount - 1000000.0
            excess_interest = excess_loan * rate_decimal * moratorium_years
        else:
            excess_interest = 0.0

    elif family_income <= 800000.0 and is_qhei:
        # Case B: PM-Vidyalaxmi (3% Interest Subvention for income <= 8 Lakh at QHEI)
        applied_scheme = "PM-Vidyalaxmi Scheme (3% Interest Subvention)"
        subsidy_type = "3% Interest Subvention"
        subvention_rate = min(0.03, rate_decimal)
        subsidy_rate = subvention_rate
        govt_moratorium_share = subvention_eligible_loan * subvention_rate * moratorium_years

    elif family_income <= 800000.0 and not is_qhei:
        applied_scheme = "PM-Vidyalaxmi Ineligible (Non-QHEI Institution)"
        subsidy_type = "Ineligible for 3% Subvention (Requires NIRF QHEI)"
        govt_moratorium_share = 0.0

    else:
        applied_scheme = "Standard Education Loan (Income > Rs. 8 Lakh)"
        subsidy_type = "None (Above Government Subvention Ceiling)"
        govt_moratorium_share = 0.0

    # 4. Student Share of Moratorium Interest
    student_moratorium_share = max(0.0, total_moratorium_interest - govt_moratorium_share)

    # 5. Principal at Repayment Start (Any unpaid student moratorium interest is capitalized)
    repayment_principal = loan_amount + student_moratorium_share

    # 6. Monthly EMI Calculation post-moratorium
    # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    monthly_rate = rate_decimal / 12.0
    total_months = int(repayment_years * 12)

    if monthly_rate > 0 and total_months > 0:
        compound_factor = (1.0 + monthly_rate) ** total_months
        monthly_emi = (repayment_principal * monthly_rate * compound_factor) / (compound_factor - 1.0)
    else:
        monthly_emi = repayment_principal / max(1, total_months)

    total_repayment_amount = monthly_emi * total_months
    total_repayment_interest = max(0.0, total_repayment_amount - repayment_principal)

    # 7. Credit Guarantee Facility (CGFSEL / PM-Vidyalaxmi)
    has_credit_guarantee = (loan_amount <= 750000.0)
    credit_guarantee_text = (
        "75% Credit Guarantee via NCGTC (Collateral-Free & Guarantor-Free)"
        if has_credit_guarantee
        else "Bank Discretionary (Collateral or third-party guarantee may be requested above Rs. 7.5 lakh)"
    )

    summary_text = (
        f"Loan Amount: Rs. {loan_amount:,.2f} at {rate_percent:.2f}% p.a. for {course_years:.0f}-year course.\n"
        f"Scheme: {applied_scheme}\n"
        f"Moratorium Period: {moratorium_years:.1f} years (Course + 1 year)\n"
        f"Total Moratorium Interest: Rs. {total_moratorium_interest:,.2f}\n"
        f"Government Share: Rs. {govt_moratorium_share:,.2f} ({subsidy_type})\n"
        f"Student Share: Rs. {student_moratorium_share:,.2f}\n"
        f"Post-Moratorium Monthly EMI: Rs. {monthly_emi:,.2f} for {repayment_years:.0f} years ({total_months} months)\n"
        f"Credit Guarantee: {credit_guarantee_text}"
    )

    return {
        "loan_amount": round(loan_amount, 2),
        "interest_rate_percent": round(rate_percent, 2),
        "course_years": round(course_years, 1),
        "moratorium_years": round(moratorium_years, 1),
        "family_income": round(family_income, 2),
        "is_qhei": is_qhei,
        "scheme_applied": applied_scheme,
        "subsidy_type": subsidy_type,
        "total_moratorium_interest": round(total_moratorium_interest, 2),
        "government_share": round(govt_moratorium_share, 2),
        "student_moratorium_share": round(student_moratorium_share, 2),
        "repayment_principal": round(repayment_principal, 2),
        "repayment_years": round(repayment_years, 1),
        "repayment_months": total_months,
        "monthly_emi": round(monthly_emi, 2),
        "total_repayment_amount": round(total_repayment_amount, 2),
        "total_repayment_interest": round(total_repayment_interest, 2),
        "credit_guarantee": credit_guarantee_text,
        "is_collateral_free": has_credit_guarantee,
        "summary": summary_text,
    }


def vidyaloan_rag_search(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Search VidyaLoan guidelines and FAQs to retrieve grounded scheme rules and citations.
    """
    return answer_vidyaloan_question(query, top_k=top_k)


AVAILABLE_TOOLS = {
    "education_loan_cost_calculator": {
        "func": education_loan_cost_calculator,
        "description": (
            "Calculates education loan costs under Indian Government Schemes (PM-Vidyalaxmi & CSIS). "
            "Given loan_amount, interest_rate, course_years, family_income, is_qhei, and repayment_years: "
            "computes moratorium interest (course + 1 year), government's share (100% if income <= 4.5 lakh via CSIS, "
            "3% points if <= 8 lakh at a QHEI), and monthly EMI."
        ),
        "parameters": {
            "loan_amount": "Principal loan amount in INR (float, e.g. 750000)",
            "interest_rate": "Annual interest rate as percentage (float, e.g. 9.5)",
            "course_years": "Duration of the course in years (float, e.g. 4)",
            "family_income": "Gross annual family income in INR (float, e.g. 400000)",
            "is_qhei": "Whether institute is a recognized Quality Higher Education Institution (bool)",
            "repayment_years": "Repayment tenure in years after moratorium (float, default 15)",
        },
    },
    "vidyaloan_rag_search": {
        "func": vidyaloan_rag_search,
        "description": (
            "Performs semantic search over official PM-Vidyalaxmi, PM-USP CSIS, and CGFSEL documents "
            "to answer policy, eligibility, and procedural queries with source citations."
        ),
        "parameters": {
            "query": "The question or topic to search (string)",
            "top_k": "Number of document chunks to retrieve (int, default 3)",
        },
    },
}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a registered tool with provided arguments."""
    if tool_name not in AVAILABLE_TOOLS:
        raise ValueError(f"Unknown tool '{tool_name}'. Available: {list(AVAILABLE_TOOLS.keys())}")

    func = AVAILABLE_TOOLS[tool_name]["func"]
    return func(**arguments)


if __name__ == "__main__":
    print("Testing education_loan_cost_calculator...")
    # Case 1: CSIS eligible (income <= 4.5L)
    res_csis = education_loan_cost_calculator(
        loan_amount=750000,
        interest_rate=9.5,
        course_years=4,
        family_income=350000,
        is_qhei=True,
    )
    print("\n[Case 1 - CSIS <= 4.5L]:")
    print(res_csis["summary"])

    # Case 2: PM-Vidyalaxmi eligible (income <= 8L at QHEI)
    res_vidya = education_loan_cost_calculator(
        loan_amount=800000,
        interest_rate=9.5,
        course_years=4,
        family_income=650000,
        is_qhei=True,
    )
    print("\n[Case 2 - PM-Vidyalaxmi <= 8L @ QHEI]:")
    print(res_vidya["summary"])
