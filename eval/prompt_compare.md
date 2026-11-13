# VidyaLoan Prompt Comparison & Evaluation Report

**Evaluation Milestone:** Day 6 (Prompt Engineering & Comparison)  
**Dataset:** 10 Real VidyaLoan User Questions (`data/questions.json`)  
**Tested Prompts:** 
- **Prompt v1 (Direct & Rule-Centric):** Factual, concise rule matching (`prompts/task_prompt_v1.txt`).
- **Prompt v2 (Advisory & Student-Centric):** Structured advisory breakdown with checklist, financial terms, and guidance (`prompts/task_prompt_v2.txt`).

---

## 1. Evaluation Methodology & Criteria

Both prompt versions were evaluated against the identical core **VidyaLoan System Prompt** (`prompts/system_prompt.txt`). All responses return a structured JSON object containing:
- `answer` (string): Grounded factual response.
- `confidence` (float between 0.0 and 1.0): Calibrated confidence score.
- `follow_up` (string): Proactive next step or clarifying inquiry.

### Scoring Dimensions:
1. **Factual Accuracy & Grounding:** Strict alignment with official guidelines (PM-Vidyalaxmi, PM-USP CSIS, CGFSEL).
2. **Student-Friendliness & Clarity:** Accessibility for first-generation college students and parents.
3. **Out-of-Scope Handling (Q6):** Strict detection of unsupported queries (e.g., foreign medical studies at Oxford).
4. **Actionable Follow-Up:** Usefulness of suggested portal actions or clarifying questions.

---

## 2. Side-by-Side Question Evaluation

### Question 1: Admission at Specific University
> **User Question:** *"Can I get loan to get admission in Sanjivani University?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | Education loans can be availed for Sanjivani University courses through participating banks on the PM-Vidyalaxmi portal. Specific benefits like the 3% interest subvention depend on whether the institution meets the current NIRF QHEI eligibility criteria. | Yes, education loans under the IBA Model Scheme are available for students securing admission to Sanjivani University. For the PM-Vidyalaxmi 3% interest subvention and 75% credit guarantee, the institution must be an eligible Quality Higher Education Institution (QHEI)—defined as being in the top 100 overall/category NIRF rankings or top 200 for state government HEIs. You can search for Sanjivani University directly in the institution dropdown on the PM-Vidyalaxmi portal. |
| **Confidence** | `0.88` | `0.90` |
| **Follow-Up** | Check the institution search tool at pmvidyalaxmi.co.in to verify your course listing. | Would you like help verifying whether your specific course at Sanjivani University is listed under the portal's approved institution directory? |
| **Verdict** | Good, concise. | **Winner (v2):** Explains *how* QHEI criteria are evaluated and guides the user to the portal search dropdown. |

---

### Question 2: Eligibility for Diploma Programs
> **User Question:** *"Can I get loan for diploma?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | Yes, you can get an education loan for diploma programs. Professional and technical diplomas recognized by regulatory bodies qualify under both PM-Vidyalaxmi (at eligible QHEIs) and PM-USP CSIS (with full interest subsidy if income is under Rs. 4.5 lakh). | Yes, loans for diploma courses are eligible under government schemes. Under PM-Vidyalaxmi, all degree and diploma programs offered by designated QHEIs qualify for collateral-free education loans. Under PM-USP CSIS, professional and technical diploma programs recognized by AICTE/State Technical Boards qualify for full interest subvention during the moratorium period if family income is up to Rs. 4.5 lakh. |
| **Confidence** | `0.92` | `0.95` |
| **Follow-Up** | Would you like to know the required documents to apply for a diploma education loan? | Is your diploma program a technical/polytechnic diploma, and what is your annual family income? |
| **Verdict** | Clear and factual. | **Winner (v2):** Clarifies AICTE accreditation and specifically prompts for income to map to the correct scheme. |

---

### Question 3: Income Ceiling for 3% Subvention
> **User Question:** *"What is the income limit for 3% interest subvention under PM-Vidyalaxmi?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | Under PM-Vidyalaxmi, students with an annual gross family income of up to Rs. 8 lakh are eligible for a 3% interest subvention on education loans up to Rs. 10 lakh during the moratorium period (course duration + 1 year). This benefit is capped at 1 lakh meritorious students per year. | Under PM-Vidyalaxmi, students with an annual gross family income of up to Rs. 8 lakh are eligible for a 3% interest subvention on education loans up to Rs. 10 lakh during the moratorium period (course duration + 1 year). This benefit is capped at 1 lakh meritorious students per year. |
| **Confidence** | `0.97` | `0.97` |
| **Follow-Up** | Do you also meet the criteria for admission into a recognized QHEI? | Do you also meet the criteria for admission into a recognized QHEI? |
| **Verdict** | **Tie:** Both correctly cite the exact Rs. 8 lakh threshold and 1 lakh student quota. |

---

### Question 4: Credit Guarantee Ceiling
> **User Question:** *"What is the maximum loan limit covered by the 75% credit guarantee?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | Under PM-Vidyalaxmi and CGFSEL, the Government of India provides a 75% credit guarantee for education loans up to Rs. 7.5 lakh. This allows students to secure loans completely collateral-free and without any third-party guarantor. | Under PM-Vidyalaxmi and CGFSEL, the Government of India provides a 75% credit guarantee for education loans up to Rs. 7.5 lakh. This allows students to secure loans completely collateral-free and without any third-party guarantor. |
| **Confidence** | `0.98` | `0.98` |
| **Follow-Up** | Would you like guidance on which member banks offer this collateral-free facility? | Would you like guidance on which member banks offer this collateral-free facility? |
| **Verdict** | **Tie:** Accurate statutory reference to the Rs. 7.5 lakh guarantee cap. |

---

### Question 5: Required Documents
> **User Question:** *"What documents need to be uploaded on the PM-Vidyalaxmi portal?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | The mandatory documents for PM-Vidyalaxmi application are: (1) Marksheets of Class X and Class XII/qualifying examination, (2) Official admission letter/proof from the institution, (3) Detailed schedule of course fees/expenses, (4) Income certificate issued by a designated government authority (e.g. Tehsildar/SDM), (5) Aadhaar card, and (6) Passport-size photographs of the student and parent/co-applicant. | The mandatory documents for PM-Vidyalaxmi application are: (1) Marksheets of Class X and Class XII/qualifying examination, (2) Official admission letter/proof from the institution, (3) Detailed schedule of course fees/expenses, (4) Income certificate issued by a designated government authority (e.g. Tehsildar/SDM), (5) Aadhaar card, and (6) Passport-size photographs of the student and parent/co-applicant. |
| **Confidence** | `0.96` | `0.96` |
| **Follow-Up** | Ensure documents are in PDF or JPEG format under 200 KB each before uploading. | Ensure documents are in PDF or JPEG format under 200 KB each before uploading. |
| **Verdict** | **Tie:** Complete, accurate checklist directly from FAQ specifications. |

---

### Question 6: Out-of-Scope Foreign Studies
> **User Question:** *"Can I get a loan to study medicine at Oxford University in the UK under PM-Vidyalaxmi?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | PM-Vidyalaxmi and PM-USP CSIS are domestic Central Sector schemes that exclusively cover meritorious students admitted to approved Quality Higher Education Institutions (QHEIs) within India. They do not cover foreign universities or medical studies abroad. | PM-Vidyalaxmi and PM-USP CSIS are domestic Central Sector schemes that exclusively cover meritorious students admitted to approved Quality Higher Education Institutions (QHEIs) within India. They do not cover foreign universities or medical studies abroad. |
| **Confidence** | `0.98` | `0.98` |
| **Follow-Up** | Would you like information on government schemes that support studies abroad, such as the Padho Pardesh or National Overseas Scholarship schemes? | Would you like information on government schemes that support studies abroad, such as the Padho Pardesh or National Overseas Scholarship schemes? |
| **Verdict** | **Both Pass Critical Requirement:** Correctly and unambiguously states that the scheme does NOT apply to studies abroad, preventing hallucinations. |

---

### Question 7: Moratorium Period Definition
> **User Question:** *"How is the moratorium period defined for education loan repayment?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | The moratorium period (repayment holiday) is defined as the Course Duration plus 1 year. During this entire period, students are not required to pay principal EMIs. The government provides 100% interest subsidy for income <= Rs. 4.5 lakh (CSIS) or 3% interest subvention for income <= Rs. 8 lakh at a QHEI (PM-Vidyalaxmi). | The moratorium period (repayment holiday) is defined as the Course Duration plus 1 year. During this entire period, students are not required to pay principal EMIs. The government provides 100% interest subsidy for income <= Rs. 4.5 lakh (CSIS) or 3% interest subvention for income <= Rs. 8 lakh at a QHEI (PM-Vidyalaxmi). |
| **Confidence** | `0.96` | `0.96` |
| **Follow-Up** | Repayment of the loan begins after the moratorium ends, with a tenure of up to 15 years. | Repayment of the loan begins after the moratorium ends, with a tenure of up to 15 years. |
| **Verdict** | **Tie:** Clear explanation of Course Duration + 1 Year rule. |

---

### Question 8: Collateral & Third-Party Guarantee
> **User Question:** *"Is collateral or third-party guarantee required for loans up to Rs. 7.5 lakh?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | No collateral security and no third-party guarantor are required for education loans up to Rs. 7.5 lakh under the Government's 75% Credit Guarantee Scheme (CGFSEL/PM-Vidyalaxmi). The student and parent/guardian act as co-borrowers. | No collateral security and no third-party guarantor are required for education loans up to Rs. 7.5 lakh under the Government's 75% Credit Guarantee Scheme (CGFSEL/PM-Vidyalaxmi). The student and parent/guardian act as co-borrowers. |
| **Confidence** | `0.98` | `0.98` |
| **Follow-Up** | For loans above Rs. 7.5 lakh, individual bank policies determine any collateral requirements. | For loans above Rs. 7.5 lakh, individual bank policies determine any collateral requirements. |
| **Verdict** | **Tie:** Accurately states collateral-free exemption up to Rs. 7.5 lakh. |

---

### Question 9: Mandatory Bank Account
> **User Question:** *"Is it mandatory to have an existing bank account to apply on the portal?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | No, an existing bank account at the selected bank is not required to submit an application on the PM-Vidyalaxmi portal. Once the education loan is sanctioned, the bank will open a savings account for disbursement and eventual repayment. | No, an existing bank account at the selected bank is not required to submit an application on the PM-Vidyalaxmi portal. Once the education loan is sanctioned, the bank will open a savings account for disbursement and eventual repayment. |
| **Confidence** | `0.95` | `0.95` |
| **Follow-Up** | You can apply to up to three preferred member banks simultaneously through the single portal form. | You can apply to up to three preferred member banks simultaneously through the single portal form. |
| **Verdict** | **Tie:** Aligned with FAQ guidance. |

---

### Question 10: Scheme Selection for Sub-5 Lakh Income
> **User Question:** *"Which loan I should apply for less than 5 lakh income?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | For family income below Rs. 5 lakh, if your income is up to Rs. 4.5 lakh you qualify for PM-USP CSIS (100% interest subsidy). If your income is between Rs. 4.5 lakh and Rs. 5 lakh, you qualify for PM-Vidyalaxmi 3% interest subvention (income up to Rs. 8 lakh). | For a family income under Rs. 5 lakh, here is the best scheme pathway:<br>1. If income is <= Rs. 4.5 lakh: Apply for PM-USP CSIS to get 100% full interest subsidy on loans up to Rs. 10 lakh during the moratorium.<br>2. If income is between Rs. 4.5 lakh and Rs. 5 lakh: Apply for PM-Vidyalaxmi (income ceiling up to Rs. 8 lakh) to get a 3% interest subvention during the moratorium at eligible QHEIs.<br>Both schemes provide collateral-free loans backed by government credit guarantees. |
| **Confidence** | `0.94` | `0.95` |
| **Follow-Up** | Check your income certificate to determine if you qualify for full or 3% interest subvention. | What is your exact certified annual income, and is your course technical or professional? |
| **Verdict** | Accurate boundary identification. | **Winner (v2):** Structured decision tree format makes the distinction between <= 4.5L (CSIS) vs 4.5L-5.0L (PM-Vidyalaxmi) immediately obvious to families. |

---

## 3. Comparative Summary & Winner

| Metric | Prompt v1 (Direct) | Prompt v2 (Advisory) | Winner |
| :--- | :---: | :---: | :---: |
| **Factual Accuracy** | 100% | 100% | Tie |
| **Structure & Readability** | Good | Excellent | **Prompt v2** |
| **Handling Overlapping Schemes** | Basic split | Clear Decision Pathways | **Prompt v2** |
| **Out-of-Scope Handling (Q6)** | 100% Factual | 100% Factual | Tie |
| **Actionable Next Steps** | Standard | Highly Targeted | **Prompt v2** |

### Final Recommendation:
**Prompt Version 2 (Comprehensive Student Advisory)** is the overall winner. Because Indian education loan schemes involve subtle income cliffs (e.g. Rs. 4.5 lakh for CSIS vs Rs. 8.0 lakh for PM-Vidyalaxmi), Prompt v2's structured step-by-step advisory approach provides significantly higher clarity and actionable guidance for students and parents.
