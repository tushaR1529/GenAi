"""
Unit tests for the education_loan_cost_calculator agent tool.
"""
from app.tools import education_loan_cost_calculator


def test_csis_full_subsidy_under_4_point_5_lakh():
    # 8 Lakh loan, 9.5% interest, 4 years course, 4 Lakh family income (CSIS eligible)
    res = education_loan_cost_calculator(
        loan_amount=800000.0,
        interest_rate=9.5,
        course_years=4.0,
        family_income=400000.0,
        is_qhei=True,
        repayment_years=10.0,
    )
    # Moratorium = 4 + 1 = 5 years
    assert res["moratorium_years"] == 5.0
    expected_total_moratorium = 800000.0 * 0.095 * 5.0  # 380,000
    assert res["total_moratorium_interest"] == expected_total_moratorium

    # CSIS provides 100% full interest subsidy
    assert res["scheme_applied"].startswith("PM-USP CSIS")
    assert res["government_share"] == expected_total_moratorium
    assert res["student_moratorium_share"] == 0.0
    # Principal at repayment remains base loan amount
    assert res["repayment_principal"] == 800000.0


def test_pm_vidyalaxmi_3_percent_subvention():
    # 7.5 Lakh loan, 9.0% interest, 4 years course, 6 Lakh family income, QHEI = True
    res = education_loan_cost_calculator(
        loan_amount=750000.0,
        interest_rate=9.0,
        course_years=4.0,
        family_income=600000.0,
        is_qhei=True,
        repayment_years=10.0,
    )
    assert res["moratorium_years"] == 5.0
    # Govt pays 3% points subvention
    expected_govt_share = 750000.0 * 0.03 * 5.0  # 112,500
    expected_total_moratorium = 750000.0 * 0.09 * 5.0  # 337,500
    assert res["scheme_applied"].startswith("PM-Vidyalaxmi Scheme")
    assert res["government_share"] == expected_govt_share
    assert res["student_moratorium_share"] == expected_total_moratorium - expected_govt_share


def test_pm_vidyalaxmi_non_qhei_ineligible():
    # 7.5 Lakh loan, income 6 Lakh, but NOT a QHEI
    res = education_loan_cost_calculator(
        loan_amount=750000.0,
        interest_rate=9.0,
        course_years=4.0,
        family_income=600000.0,
        is_qhei=False,
    )
    assert "Ineligible" in res["scheme_applied"]
    assert res["government_share"] == 0.0
    assert res["student_moratorium_share"] == res["total_moratorium_interest"]


def test_standard_loan_income_above_8_lakh():
    # Family income 12 Lakh (> 8 Lakh ceiling)
    res = education_loan_cost_calculator(
        loan_amount=1000000.0,
        interest_rate=10.0,
        course_years=3.0,
        family_income=1200000.0,
        is_qhei=True,
    )
    assert "Standard Education Loan" in res["scheme_applied"]
    assert res["government_share"] == 0.0
    assert res["student_moratorium_share"] == res["total_moratorium_interest"]


def test_credit_guarantee_thresholds():
    # Under or equal to 7.5 Lakh: 75% credit guarantee, no collateral required
    res_under = education_loan_cost_calculator(
        loan_amount=750000.0,
        interest_rate=9.0,
        course_years=4.0,
        family_income=500000.0,
    )
    assert res_under["is_collateral_free"] is True
    assert "75%" in res_under["credit_guarantee"]

    # Above 7.5 Lakh: credit guarantee not applicable, collateral/third-party guarantor required
    res_above = education_loan_cost_calculator(
        loan_amount=1000000.0,
        interest_rate=9.0,
        course_years=4.0,
        family_income=500000.0,
    )
    assert res_above["is_collateral_free"] is False


def test_monthly_emi_and_repayment_math():
    res = education_loan_cost_calculator(
        loan_amount=500000.0,
        interest_rate=8.5,
        course_years=4.0,
        family_income=300000.0,
        repayment_years=10.0,
    )
    assert res["monthly_emi"] > 0
    assert res["total_repayment_amount"] > res["repayment_principal"]
