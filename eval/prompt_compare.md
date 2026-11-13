# VidyaLoan Prompt Comparison & Evaluation Report

**Evaluation Milestone:** Day 6 (Prompt Engineering & Comparison)  
**Dataset:** 10 Real VidyaLoan User Questions (`data/questions.json`)  
**Tested Provider / Model:** Google Gemini API (`gemini-3.5-flash`)  
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
| **Answer** | Yes, you can apply for an education loan for recognized technical and professional programs at Sanjivani University in India through the unified PM-Vidyalaxmi portal. Depending on your financial profile and institution eligibility, benefits include: 1) PM-USP CSIS: Offers a 100% interest subsidy during the moratorium period (course duration + 1 year) on loans up to Rs. 10 lakh for Economically Weaker Section (EWS) students with an annual family income up to Rs. 4.5 lakh. 2) PM-Vidyalaxmi Scheme: Provides collateral-free loans with a 75% credit guarantee for loans up to Rs. 7.5 lakh, and a 3% interest subvention during moratorium for loans up to Rs. 10 lakh (for annual family income up to Rs. 8 lakh), provided the institute/course is listed among eligible Quality Higher Education Institutions (QHEIs) based on NIRF rankings. | **Executive Summary:** Yes, you can apply for an education loan to pursue your studies at Sanjivani University (a recognized domestic institution in India). The exact benefits—such as interest subsidies or subventions—depend on your family's annual income, course approval, and the university's eligibility under government schemes.<br><br>**Structured Scheme Breakdown:**<br>1. *Eligibility Checklist:* Must be recognized domestic university; NIRF QHEI status for PM-Vidyalaxmi 3% subvention; Income ceilings (CSIS <= 4.5L, Vidyalaxmi <= 8.0L).<br>2. *Financial Benefits:* Collateral-free up to Rs. 7.5 lakh (75% credit guarantee via NCGTC/CGFSEL); moratorium period is course duration + 1 year; repayment tenure up to 15 years.<br>3. *Portal Steps:* Visit https://pmvidyalaxmi.co.in, fill Common Education Loan Application Form (CELAF), upload offer letter and income certificate. |
| **Confidence** | `0.95` | `0.95` |
| **Follow-Up** | Verify if your selected course at Sanjivani University is AICTE/UGC approved and check the institution's QHEI eligibility status on the PM-Vidyalaxmi portal (https://pmvidyalaxmi.co.in) before submitting your application. | Would you like help verifying whether your specific course at Sanjivani University qualifies for the 100% PM-USP CSIS interest subsidy or the 3% PM-Vidyalaxmi interest subvention based on your family's annual income? |
| **Verdict** | Good, concise summary. | **Winner (v2):** Provides structured guidance explaining how QHEI and NIRF criteria apply, plus step-by-step CELAF portal instructions. |

---

### Question 2: Eligibility for Diploma Programs
> **User Question:** *"Can I get loan for diploma?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | Yes, education loans are available for approved professional and technical diploma courses offered by recognized institutions in India under the IBA Model Education Loan Scheme. Additionally, under the PM-USP CSIS (Central Sector Interest Subsidy) scheme, eligible students with an annual family income up to Rs. 4.5 lakh pursuing recognized professional or technical diploma courses can receive a 100% interest subsidy during the moratorium period (course duration + 1 year) for loans up to Rs. 10 lakh. | Yes, you can get an education loan for a diploma course, provided it is a recognized professional or technical diploma offered by an approved institution in India.<br><br>### 1. Executive Summary<br>Education loans and Central Government interest subsidy schemes cover professional and technical diploma courses pursued in India after 10th or 12th standard, provided the institution and course are recognized by competent regulatory bodies (such as AICTE, State Boards of Technical Education, or UGC).<br><br>### 2. Eligibility & Scheme Breakdown<br>- **Approved Course Type:** Recognized professional/technical diplomas.<br>- **Income Ceilings:** PM-USP CSIS (<= Rs. 4.5 lakh) for 100% interest subsidy; PM-Vidyalaxmi (<= Rs. 8 lakh) for 3% subvention.<br>- **Financial Benefits:** 75% credit guarantee for loans up to Rs. 7.5 lakh; moratorium is course duration + 1 year.<br>- **Portal Steps:** Register on pmvidyalaxmi.co.in and complete CELAF. |
| **Confidence** | `1.0` | `1.0` |
| **Follow-Up** | Would you like to check if your specific diploma course and institute qualify for the PM-USP CSIS interest subsidy or apply through the central portal? | What specific diploma course are you planning to pursue, and is your institution AICTE or government-recognized? |
| **Verdict** | Clear and factual. | **Winner (v2):** Details AICTE / State Technical Board recognition criteria and clarifies subsidy rules. |

---

### Question 3: Income Ceiling for 3% Subvention
> **User Question:** *"What is the income limit for 3% interest subvention under PM-Vidyalaxmi?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | Under the PM-Vidyalaxmi scheme, the annual family income limit to qualify for the 3% interest subvention is up to Rs. 8 lakh. This subvention applies during the moratorium period for education loans up to Rs. 10 lakh, targeted at meritorious students pursuing domestic higher education in eligible Quality Higher Education Institutions (QHEIs), capped at 1 lakh students per year. | Executive Summary: Under the PM-Vidyalaxmi scheme, the maximum annual family income limit to qualify for the 3% interest subvention is Rs. 8 lakh per annum.<br><br>Structured Breakdown:<br>1. Eligibility Checklist: Gross family income up to Rs. 8 lakh per year; admissions in NIRF QHEIs in India.<br>2. Financial Benefits: 3% interest subvention during moratorium on loans up to Rs. 10 lakh (capped at 1 lakh students/year); 75% credit guarantee for loans up to Rs. 7.5 lakh.<br>3. Portal Steps: Complete CELAF at https://pmvidyalaxmi.co.in with income certificate and QHEI admission confirmation. |
| **Confidence** | `1.0` | `1.0` |
| **Follow-Up** | Would you like guidance on how to check eligible QHEI institutions or apply on the PM-Vidyalaxmi portal (pmvidyalaxmi.co.in)? | Would you like help verifying whether your target college/university falls under the official Quality Higher Education Institutions (QHEI) list for PM-Vidyalaxmi? |
| **Verdict** | **Tie:** Both correctly cite the exact Rs. 8 lakh income threshold, Rs. 10 lakh loan ceiling, and 1 lakh student quota. |

---

### Question 4: Credit Guarantee Ceiling
> **User Question:** *"What is the maximum loan limit covered by the 75% credit guarantee?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | Under the PM-Vidyalaxmi scheme, the maximum loan limit covered by the 75% credit guarantee (provided by the Government of India through NCGTC) is Rs. 7.5 lakh. Loans up to this amount are completely collateral-free and guarantor-free for eligible students admitted to Quality Higher Education Institutions (QHEIs) in India. | Executive Summary: Under the PM-Vidyalaxmi scheme and Credit Guarantee Fund Scheme for Education Loans (CGFSEL), the maximum loan limit covered by the 75% credit guarantee is Rs. 7.5 lakh. This guarantee is provided by the Government of India through NCGTC to ensure collateral-free and guarantor-free access to education loans.<br><br>Structured Breakdown:<br>1. Eligibility: Top QHEIs in India recognized under NIRF.<br>2. Financial Benefits: 75% guarantee coverage by NCGTC up to Rs. 7.5 lakh without third-party guarantors or collateral.<br>3. Portal Steps: Apply via CELAF on pmvidyalaxmi.co.in. |
| **Confidence** | `1.0` | `1.0` |
| **Follow-Up** | Would you like guidance on how to apply for this collateral-free loan using the Common Education Loan Application Form (CELAF) on pmvidyalaxmi.co.in? | Would you like help checking if your prospective college is listed as an eligible Quality Higher Education Institution (QHEI) under the PM-Vidyalaxmi portal? |
| **Verdict** | **Tie:** Both accurately state the Rs. 7.5 lakh ceiling backed by NCGTC/CGFSEL. |

---

### Question 5: Required Documents
> **User Question:** *"What documents need to be uploaded on the PM-Vidyalaxmi portal?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | To apply for an education loan under the PM-Vidyalaxmi scheme on the portal (https://pmvidyalaxmi.co.in), you need to complete the Common Education Loan Application Form (CELAF) and upload the following standard documents: 1. Proof of Identity and Address (Aadhaar Card, PAN Card, Passport, etc.). 2. Academic Records (10th, 12th, degree marksheets). 3. Proof of Admission (Offer letter from QHEI). 4. Course Fee Structure schedule. 5. Income Certificate (for 3% subvention up to Rs. 8L). 6. Bank Account Statements (last 6 months). 7. Passport-size Photographs. | Executive Summary: To apply for a collateral-free education loan on the unified PM-Vidyalaxmi portal (https://pmvidyalaxmi.co.in), students must upload standard identity, academic, financial, and admission documents via the Common Education Loan Application Form (CELAF).<br><br>Document Checklist for PM-Vidyalaxmi Portal:<br>1. Identity & Address Proof: Aadhaar Card, PAN Card, Passport.<br>2. Academic Records: Mark sheets/certificates of Class 10th, 12th, graduation, rank cards.<br>3. Admission & Fees Proof: Official admission letter from QHEI + fee schedule.<br>4. Income Proof: Authorized state government Income Certificate.<br>5. Financial Statements: 6 months bank statements.<br>6. Photographs of student and co-applicant. |
| **Confidence** | `0.95` | `0.95` |
| **Follow-Up** | Would you like guidance on how to check if your institution is listed among the eligible Quality Higher Education Institutions (QHEIs) under PM-Vidyalaxmi? | Would you like assistance in checking if your institute is included in the list of eligible QHEIs under PM-Vidyalaxmi? |
| **Verdict** | **Tie:** Both provide complete, highly accurate document checklists. |

---

### Question 6: Out-of-Scope Foreign Studies
> **User Question:** *"Can I get a loan to study medicine at Oxford University in the UK under PM-Vidyalaxmi?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | No, you cannot get an education loan under PM-Vidyalaxmi to study at Oxford University in the UK. The PM-Vidyalaxmi scheme exclusively covers domestic higher education programs at eligible Quality Higher Education Institutions (QHEIs) in India based on NIRF and central institution rankings. Studies abroad are not covered under PM-Vidyalaxmi or PM-USP CSIS. | Executive Summary: No, you cannot get an education loan under the PM-Vidyalaxmi scheme to study medicine at Oxford University or any other foreign university. The PM-Vidyalaxmi scheme is strictly designed for domestic higher education within India.<br><br>Scheme Scope & Breakdown:<br>1. Eligibility Criteria (Domestic Only): Limited to top QHEIs in India based on NIRF rankings. Foreign studies strictly out of scope.<br>2. Financial Benefits: Applicable only to domestic courses.<br>3. Alternative Advice: General bank commercial education loan schemes for foreign studies are required. |
| **Confidence** | `1.0` | `1.0` |
| **Follow-Up** | Would you like information on eligible domestic medical institutions under PM-Vidyalaxmi or standard education loan options available for foreign studies? | Would you like information on top domestic Indian medical institutions (QHEIs) covered under PM-Vidyalaxmi, or guidance on general commercial loan requirements for studying abroad? |
| **Verdict** | **Both Pass Critical Requirement:** Strictly rejects foreign university studies under PM-Vidyalaxmi, preventing hallucination. |

---

### Question 7: Moratorium Period Definition
> **User Question:** *"How is the moratorium period defined for education loan repayment?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | Under Indian government education loan guidelines (including IBA Model Loan standards, PM-Vidyalaxmi, and PM-USP CSIS), the moratorium period is defined as the total course duration plus 1 year, or 6 months after securing employment, whichever occurs earlier. Repayment of the loan principal begins after this moratorium period ends. | Executive Summary: Under Indian government education loan frameworks (including PM-Vidyalaxmi and PM-USP CSIS), the moratorium period is defined as the total duration of the enrolled course plus 1 year, or 6 months after securing employment, whichever occurs earlier. During this holiday period, students are not required to pay back the principal loan amount.<br><br>Structured Breakdown:<br>1. Definition & Duration: Course Duration + 1 Year (or 6 months post-employment, whichever earlier); Repayment up to 15 years after.<br>2. Financial Benefits During Moratorium: 100% interest subsidy for income <= 4.5L (CSIS) or 3% subvention for income <= 8L (Vidyalaxmi).<br>3. Application Workflow: Unified portal via CELAF. |
| **Confidence** | `1.0` | `1.0` |
| **Follow-Up** | Would you like to know how interest subvention or subsidy works during the moratorium period under PM-Vidyalaxmi or PM-USP CSIS? | Would you like help checking whether your institute is listed as an eligible QHEI under PM-Vidyalaxmi or calculating your scheme eligibility based on your annual family income? |
| **Verdict** | Concise & accurate. | **Winner (v2):** Clearly explains what happens during the moratorium regarding interest subventions. |

---

### Question 8: Collateral & Third-Party Guarantee
> **User Question:** *"Is collateral or third-party guarantee required for loans up to Rs. 7.5 lakh?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | No, collateral or a third-party guarantee is not required for education loans up to Rs. 7.5 lakh under the PM-Vidyalaxmi scheme and Credit Guarantee Fund Scheme for Education Loans (CGFSEL). The Government of India provides 75% credit guarantee coverage through NCGTC to lending banks for loans up to Rs. 7.5 lakh, ensuring fully collateral-free and guarantor-free access for eligible students. | Executive Summary: No, collateral or third-party guarantee is NOT required for education loans up to Rs. 7.5 lakh under government education loan guidelines and schemes like PM-Vidyalaxmi. These loans are completely collateral-free and guarantor-free, backed by a 75% credit guarantee coverage provided by the Government of India through NCGTC.<br><br>Structured Breakdown:<br>1. Eligibility: Income <= 8L for 3% subvention, <= 4.5L for CSIS.<br>2. Financial Benefits: Zero collateral or guarantor up to Rs. 7.5 lakh.<br>3. Application Steps: Digital submission on pmvidyalaxmi.co.in. |
| **Confidence** | `1.0` | `1.0` |
| **Follow-Up** | Would you like guidance on applying through the unified portal at https://pmvidyalaxmi.co.in using the Common Education Loan Application Form (CELAF)? | Would you like help checking if your institute is listed under the QHEI eligible list for PM-Vidyalaxmi, or would you like details on the document checklist needed for your CELAF application? |
| **Verdict** | **Tie:** Clear, definitive negative answer backed by CGFSEL rules. |

---

### Question 9: Mandatory Bank Account
> **User Question:** *"Is it mandatory to have an existing bank account to apply on the portal?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | No, it is not mandatory to have an existing bank account with the lending bank to apply for an education loan on the portal. Students can submit their application without a prior relationship with the bank. However, once the loan is approved/sanctioned, a bank account will be opened in the student's name for loan disbursement. | Executive Summary: No, it is not mandatory to have an existing bank account with the selected lending bank to apply for an education loan on the official portal. You can register and submit your application using the Common Education Loan Application Form (CELAF). A savings bank account will be opened with the lending bank upon loan sanction for disbursement purposes.<br><br>Structured Breakdown:<br>1. Portal Registration: Basic details (Mobile & Email).<br>2. CELAF Submission: Academic, personal, and income info.<br>3. Post-Sanction: Bank facilitates account opening upon approval. |
| **Confidence** | `1.0` | `1.0` |
| **Follow-Up** | Would you like to know the steps to apply using the Common Education Loan Application Form (CELAF) on the PM-Vidyalaxmi portal (https://pmvidyalaxmi.co.in)? | Would you like assistance in checking whether your chosen institution is on the eligible QHEI list or determining your exact interest subsidy eligibility? |
| **Verdict** | **Tie:** Both alleviate user concern and clarify the post-sanction account opening procedure. |

---

### Question 10: Scheme Selection for Sub-5 Lakh Income
> **User Question:** *"Which loan I should apply for less than 5 lakh income?"*

| Dimension | Prompt v1 (Direct) | Prompt v2 (Advisory) |
| :--- | :--- | :--- |
| **Answer** | For an annual family income of less than Rs. 5 lakh (specifically up to Rs. 4.5 lakh), you are eligible for the PM-USP CSIS (Central Sector Interest Subsidy) scheme, which provides a full (100%) interest subsidy during the moratorium period (course duration + 1 year) on loans up to Rs. 10 lakh for approved professional/technical courses in India. Additionally, if your income is up to Rs. 8 lakh, you can apply under the PM-Vidyalaxmi scheme for collateral-free, guarantor-free education loans at eligible Quality Higher Education Institutions (QHEIs), featuring a 75% credit guarantee for loans up to Rs. 7.5 lakh and a 3% interest subvention on loans up to Rs. 10 lakh during the moratorium period. | For a family income under Rs. 5 lakh, here is the best scheme pathway:<br>1. If income is <= Rs. 4.5 lakh: Apply for PM-USP CSIS to get 100% full interest subsidy on loans up to Rs. 10 lakh during the moratorium.<br>2. If income is between Rs. 4.5 lakh and Rs. 5 lakh: Apply for PM-Vidyalaxmi (income ceiling up to Rs. 8 lakh) to get a 3% interest subvention during the moratorium at eligible QHEIs.<br>Both schemes provide collateral-free loans backed by government credit guarantees. |
| **Confidence** | `0.95` | `0.95` |
| **Follow-Up** | Check if your prospective institution is an eligible QHEI and apply online via the unified PM-Vidyalaxmi portal at https://pmvidyalaxmi.co.in using the Common Education Loan Application Form (CELAF). | What is your exact certified annual income, and is your course technical or professional? |
| **Verdict** | Accurate scheme boundaries. | **Winner (v2):** Structured decision tree format makes the distinction between <= 4.5L (CSIS) vs 4.5L-5.0L (PM-Vidyalaxmi) immediately obvious to families. |

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
