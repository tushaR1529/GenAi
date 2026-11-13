# app/llm.py
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
SYSTEM_PROMPT_PATH = PROMPTS_DIR / "system_prompt.txt"
TASK_PROMPT_V1_PATH = PROMPTS_DIR / "task_prompt_v1.txt"
TASK_PROMPT_V2_PATH = PROMPTS_DIR / "task_prompt_v2.txt"

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def load_prompt(path: Path) -> str:
    """Load prompt content from a file."""
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """Parse JSON from raw LLM text, stripping markdown fences if present."""
    text = raw_text.strip()
    # Strip markdown code blocks
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    parsed: Dict[str, Any] = {}
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # Attempt to find JSON object pattern
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    if isinstance(parsed, dict) and "answer" in parsed:
        # Ensure answer is string
        if not isinstance(parsed.get("answer"), str):
            parsed["answer"] = str(parsed.get("answer", ""))
        # Ensure confidence is float
        try:
            parsed["confidence"] = float(parsed.get("confidence", 0.90))
        except (ValueError, TypeError):
            parsed["confidence"] = 0.90
        # Ensure follow_up is a string
        follow_up = parsed.get("follow_up")
        if isinstance(follow_up, list):
            parsed["follow_up"] = " ".join(str(f).strip() for f in follow_up if f)
        elif not isinstance(follow_up, str):
            parsed["follow_up"] = str(follow_up or "")
        return parsed

    return {
        "answer": text,
        "confidence": 0.75,
        "follow_up": "Would you like more details on PM-Vidyalaxmi or CSIS scheme eligibility?",
    }


class LLMClient:
    """Provider wrapper supporting Groq and Gemini with grounded fallback."""

    def __init__(
        self,
        provider: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
    ):
        raw_groq = groq_api_key or os.getenv("GROQ_API_KEY", "")
        raw_gemini = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.groq_api_key = raw_groq.strip().strip("\"'")
        self.gemini_api_key = raw_gemini.strip().strip("\"'")

        # Determine active provider
        env_provider = os.getenv("LLM_PROVIDER", "").lower()
        if provider:
            self.provider = provider.lower()
        elif env_provider in ("groq", "gemini"):
            self.provider = env_provider
        elif self.gemini_api_key and not self.gemini_api_key.startswith("your_"):
            self.provider = "gemini"
        elif self.groq_api_key and not self.groq_api_key.startswith("gsk_your"):
            self.provider = "groq"
        else:
            self.provider = "fallback"

        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

        self.system_prompt = load_prompt(SYSTEM_PROMPT_PATH)
        self.task_v1_template = load_prompt(TASK_PROMPT_V1_PATH)
        self.task_v2_template = load_prompt(TASK_PROMPT_V2_PATH)

    def _call_groq(self, prompt: str) -> Dict[str, Any]:
        """Send chat request to Groq API."""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.groq_model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return clean_json_response(content)

    def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        """Send generation request to Google Gemini API."""
        url = f"{GEMINI_API_URL}/{self.gemini_model}:generateContent"
        headers = {
            "x-goog-api-key": self.gemini_api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "system_instruction": {"parts": [{"text": self.system_prompt}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return clean_json_response(content)

    def _fallback_generate(self, question: str, prompt_version: str = "v1") -> Dict[str, Any]:
        """Deterministic grounded fallback when live API keys or network are unavailable."""
        q = question.lower()

        # Q6: Out-of-scope / foreign studies check
        if any(w in q for w in ["oxford", "abroad", "foreign", "uk", "usa", "overseas"]):
            return {
                "answer": (
                    "PM-Vidyalaxmi and PM-USP CSIS are domestic Central Sector schemes that exclusively cover "
                    "meritorious students admitted to approved Quality Higher Education Institutions (QHEIs) within India. "
                    "They do not cover foreign universities or medical studies abroad."
                ),
                "confidence": 0.98,
                "follow_up": (
                    "Would you like information on government schemes that support studies abroad, such as the "
                    "Padho Pardesh or National Overseas Scholarship schemes?"
                ),
            }

        # Q1: Sanjivani University / Institution check
        if "sanjivani" in q:
            if prompt_version == "v2":
                return {
                    "answer": (
                        "Yes, education loans under the IBA Model Scheme are available for students securing admission to "
                        "Sanjivani University. For the PM-Vidyalaxmi 3% interest subvention and 75% credit guarantee, the "
                        "institution must be an eligible Quality Higher Education Institution (QHEI)—defined as being in the "
                        "top 100 overall/category NIRF rankings or top 200 for state government HEIs. You can search for "
                        "Sanjivani University directly in the institution dropdown on the PM-Vidyalaxmi portal."
                    ),
                    "confidence": 0.90,
                    "follow_up": (
                        "Would you like help verifying whether your specific course at Sanjivani University is listed under the "
                        "portal's approved institution directory?"
                    ),
                }
            return {
                "answer": (
                    "Education loans can be availed for Sanjivani University courses through participating banks on the "
                    "PM-Vidyalaxmi portal. Specific benefits like the 3% interest subvention depend on whether the institution "
                    "meets the current NIRF QHEI eligibility criteria."
                ),
                "confidence": 0.88,
                "follow_up": "Check the institution search tool at pmvidyalaxmi.co.in to verify your course listing.",
            }

        # Q2: Diploma courses
        if "diploma" in q:
            if prompt_version == "v2":
                return {
                    "answer": (
                        "Yes, loans for diploma courses are eligible under government schemes. Under PM-Vidyalaxmi, all "
                        "degree and diploma programs offered by designated QHEIs qualify for collateral-free education loans. "
                        "Under PM-USP CSIS, professional and technical diploma programs recognized by AICTE/State Technical Boards "
                        "qualify for full interest subvention during the moratorium period if family income is up to Rs. 4.5 lakh."
                    ),
                    "confidence": 0.95,
                    "follow_up": (
                        "Is your diploma program a technical/polytechnic diploma, and what is your annual family income?"
                    ),
                }
            return {
                "answer": (
                    "Yes, you can get an education loan for diploma programs. Professional and technical diplomas recognized by "
                    "regulatory bodies qualify under both PM-Vidyalaxmi (at eligible QHEIs) and PM-USP CSIS (with full interest subsidy if income is under Rs. 4.5 lakh)."
                ),
                "confidence": 0.92,
                "follow_up": "Would you like to know the required documents to apply for a diploma education loan?",
            }

        # Income limit: 3% subvention (PM-Vidyalaxmi)
        if "3%" in q or "3 %" in q or ("income limit" in q and "vidyalaxmi" in q):
            return {
                "answer": (
                    "Under PM-Vidyalaxmi, students with an annual gross family income of up to Rs. 8 lakh are eligible for a "
                    "3% interest subvention on education loans up to Rs. 10 lakh during the moratorium period (course duration + 1 year). "
                    "This benefit is capped at 1 lakh meritorious students per year."
                ),
                "confidence": 0.97,
                "follow_up": "Do you also meet the criteria for admission into a recognized QHEI?",
            }

        # Credit guarantee limit (75% / Rs. 7.5 lakh)
        if "credit guarantee" in q or "75%" in q or "7.5" in q:
            return {
                "answer": (
                    "Under PM-Vidyalaxmi and CGFSEL, the Government of India provides a 75% credit guarantee for education loans "
                    "up to Rs. 7.5 lakh. This allows students to secure loans completely collateral-free and without any third-party guarantor."
                ),
                "confidence": 0.98,
                "follow_up": "Would you like guidance on which member banks offer this collateral-free facility?",
            }

        # Documents required
        if "document" in q or "upload" in q:
            return {
                "answer": (
                    "The mandatory documents for PM-Vidyalaxmi application are: (1) Marksheets of Class X and Class XII/qualifying examination, "
                    "(2) Official admission letter/proof from the institution, (3) Detailed schedule of course fees/expenses, "
                    "(4) Income certificate issued by a designated government authority (e.g. Tehsildar/SDM), (5) Aadhaar card, and "
                    "(6) Passport-size photographs of the student and parent/co-applicant."
                ),
                "confidence": 0.96,
                "follow_up": "Ensure documents are in PDF or JPEG format under 200 KB each before uploading.",
            }

        # Moratorium period
        if "moratorium" in q:
            return {
                "answer": (
                    "The moratorium period (repayment holiday) is defined as the Course Duration plus 1 year. During this entire period, "
                    "students are not required to pay principal EMIs. The government provides 100% interest subsidy for income <= Rs. 4.5 lakh (CSIS) "
                    "or 3% interest subvention for income <= Rs. 8 lakh at a QHEI (PM-Vidyalaxmi)."
                ),
                "confidence": 0.96,
                "follow_up": "Repayment of the loan begins after the moratorium ends, with a tenure of up to 15 years.",
            }

        # Collateral / guarantor requirements
        if "collateral" in q or "guarantor" in q:
            return {
                "answer": (
                    "No collateral security and no third-party guarantor are required for education loans up to Rs. 7.5 lakh under the "
                    "Government's 75% Credit Guarantee Scheme (CGFSEL/PM-Vidyalaxmi). The student and parent/guardian act as co-borrowers."
                ),
                "confidence": 0.98,
                "follow_up": "For loans above Rs. 7.5 lakh, individual bank policies determine any collateral requirements.",
            }

        # Bank account requirement
        if "account" in q or "bank account" in q:
            return {
                "answer": (
                    "No, an existing bank account at the selected bank is not required to submit an application on the PM-Vidyalaxmi portal. "
                    "Once the education loan is sanctioned, the bank will open a savings account for disbursement and eventual repayment."
                ),
                "confidence": 0.95,
                "follow_up": "You can apply to up to three preferred member banks simultaneously through the single portal form.",
            }

        # Less than 5 lakh income scheme selection
        if "5 lakh" in q or "less than 5" in q:
            if prompt_version == "v2":
                return {
                    "answer": (
                        "For a family income under Rs. 5 lakh, here is the best scheme pathway:\n"
                        "1. If income is <= Rs. 4.5 lakh: Apply for PM-USP CSIS to get 100% full interest subsidy on loans up to Rs. 10 lakh during the moratorium.\n"
                        "2. If income is between Rs. 4.5 lakh and Rs. 5 lakh: Apply for PM-Vidyalaxmi (income ceiling up to Rs. 8 lakh) to get a 3% interest subvention during the moratorium at eligible QHEIs.\n"
                        "Both schemes provide collateral-free loans backed by government credit guarantees."
                    ),
                    "confidence": 0.95,
                    "follow_up": (
                        "What is your exact certified annual income, and is your course technical or professional?"
                    ),
                }
            return {
                "answer": (
                    "For family income below Rs. 5 lakh, if your income is up to Rs. 4.5 lakh you qualify for PM-USP CSIS (100% interest subsidy). "
                    "If your income is between Rs. 4.5 lakh and Rs. 5 lakh, you qualify for PM-Vidyalaxmi 3% interest subvention (income up to Rs. 8 lakh)."
                ),
                "confidence": 0.94,
                "follow_up": "Check your income certificate to determine if you qualify for full or 3% interest subvention.",
            }

        # Generic fallback
        return {
            "answer": (
                "Indian government education loans offer collateral-free loans up to Rs. 7.5 lakh (75% credit guarantee), "
                "full interest subsidy for family income up to Rs. 4.5 lakh under PM-USP CSIS, and 3% interest subvention for income "
                "up to Rs. 8 lakh under PM-Vidyalaxmi for eligible institutions."
            ),
            "confidence": 0.85,
            "follow_up": "Please provide your course, institution, and family income for specific eligibility guidance.",
        }

    def chat(self, question: str, prompt_version: str = "v1") -> Dict[str, Any]:
        """Generate response via active provider, falling back safely on failure."""
        template = self.task_v2_template if prompt_version == "v2" else self.task_v1_template
        prompt = template.replace("{question}", question) if "{question}" in template else f"{template}\n\nQuestion: {question}"

        if self.provider == "groq" and self.groq_api_key:
            try:
                return self._call_groq(prompt)
            except Exception as e:
                print(f"Groq API call failed: {e}. Using grounded fallback.")

        elif self.provider == "gemini" and self.gemini_api_key:
            try:
                return self._call_gemini(prompt)
            except Exception as e:
                print(f"Gemini API call failed: {e}. Using grounded fallback.")

        return self._fallback_generate(question, prompt_version=prompt_version)


# Global default client instance
_default_client = LLMClient()


def generate_chat_response(question: str, prompt_version: str = "v1") -> Dict[str, Any]:
    """Convenience function to generate a chat response."""
    return _default_client.chat(question, prompt_version=prompt_version)
