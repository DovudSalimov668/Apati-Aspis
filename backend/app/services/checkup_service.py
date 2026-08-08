from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class OptionSchema(BaseModel):
    id: str
    text: str
    points: int

class QuestionSchema(BaseModel):
    id: str
    category: str
    category_title: str
    question: str
    options: List[OptionSchema]

class CheckupSubmissionRequest(BaseModel):
    answers: Dict[str, str]  # question_id -> option_id

QUESTIONS: List[QuestionSchema] = [
    QuestionSchema(
        id="q1",
        category="phishing",
        category_title="Phishing & Email Safety",
        question="What do you do if you receive an email from your bank asking you to click a link to verify your account immediately?",
        options=[
            OptionSchema(id="a", text="Click the link and log in immediately", points=0),
            OptionSchema(id="b", text="Reply to the email asking if it is authentic", points=0),
            OptionSchema(id="c", text="Open a new browser tab, go directly to official bank website or call official support", points=10)
        ]
    ),
    QuestionSchema(
        id="q2",
        category="phishing",
        category_title="Phishing & Email Safety",
        question="How do you check if a website domain is authentic before entering login credentials?",
        options=[
            OptionSchema(id="a", text="Check if the webpage design looks professional", points=0),
            OptionSchema(id="b", text="Inspect the domain name in the address bar for exact spelling", points=10),
            OptionSchema(id="c", text="Assume it is safe if a lock icon is displayed", points=2)
        ]
    ),
    QuestionSchema(
        id="q3",
        category="passwords",
        category_title="Password Hygiene",
        question="How do you manage passwords across your online accounts?",
        options=[
            OptionSchema(id="a", text="Use the same password for most accounts", points=0),
            OptionSchema(id="b", text="Use 2 or 3 variation passwords", points=3),
            OptionSchema(id="c", text="Use unique, complex passwords stored in a secure password manager", points=10)
        ]
    ),
    QuestionSchema(
        id="q4",
        category="passwords",
        category_title="Password Hygiene",
        question="Do you reuse passwords across financial and primary email accounts?",
        options=[
            OptionSchema(id="a", text="Never — every critical account has a completely unique password", points=10),
            OptionSchema(id="b", text="Sometimes for non-important sites", points=4),
            OptionSchema(id="c", text="Always reuse main password", points=0)
        ]
    ),
    QuestionSchema(
        id="q5",
        category="mfa",
        category_title="Multi-Factor Authentication",
        question="Which of your primary online accounts have Multi-Factor Authentication (MFA/2FA) enabled?",
        options=[
            OptionSchema(id="a", text="None", points=0),
            OptionSchema(id="b", text="Only 1 or 2 financial accounts", points=5),
            OptionSchema(id="c", text="All primary email, banking, and social accounts", points=10)
        ]
    ),
    QuestionSchema(
        id="q6",
        category="mfa",
        category_title="Multi-Factor Authentication",
        question="What type of Multi-Factor Authentication (MFA) method do you primarily use?",
        options=[
            OptionSchema(id="a", text="SMS / Text Message verification codes", points=6),
            OptionSchema(id="b", text="Authenticator App (e.g. Google/Microsoft Authenticator or hardware key)", points=10),
            OptionSchema(id="c", text="No MFA used", points=0)
        ]
    ),
    QuestionSchema(
        id="q7",
        category="social_engineering",
        category_title="Social Engineering Defense",
        question="A caller claiming to be IT support asks for your SMS verification code or password to fix an urgent issue. What do you do?",
        options=[
            OptionSchema(id="a", text="Give them the code to fix the issue quickly", points=0),
            OptionSchema(id="b", text="Refuse to share codes/passwords and verify through official directory", points=10),
            OptionSchema(id="c", text="Ask them to call back later", points=2)
        ]
    ),
    QuestionSchema(
        id="q8",
        category="social_engineering",
        category_title="Social Engineering Defense",
        question="An urgent social media message from a friend asks you to send gift cards or money due to an emergency. What is your first step?",
        options=[
            OptionSchema(id="a", text="Send money immediately to help them", points=0),
            OptionSchema(id="b", text="Contact the friend directly via phone or in person to verify", points=10),
            OptionSchema(id="c", text="Reply on social media asking for proof", points=2)
        ]
    ),
    QuestionSchema(
        id="q9",
        category="payment_safety",
        category_title="Payment & Checkout Safety",
        question="When shopping on an unfamiliar online store, which payment method provides the safest protection?",
        options=[
            OptionSchema(id="a", text="Direct wire transfer or debit card", points=0),
            OptionSchema(id="b", text="Credit card with buyer fraud protection or trusted payment service", points=10),
            OptionSchema(id="c", text="Gift card or cryptocurrency", points=0)
        ]
    ),
    QuestionSchema(
        id="q10",
        category="payment_safety",
        category_title="Payment & Checkout Safety",
        question="How do you verify online checkout pages before entering payment card details?",
        options=[
            OptionSchema(id="a", text="Verify HTTPS encryption and domain match before typing details", points=10),
            OptionSchema(id="b", text="Pay regardless if the deal price is low", points=0),
            OptionSchema(id="c", text="Check third-party seller reviews", points=5)
        ]
    ),
    QuestionSchema(
        id="q11",
        category="device_security",
        category_title="Device & Software Security",
        question="How quickly do you install security updates for your OS and web browser?",
        options=[
            OptionSchema(id="a", text="Immediately / Automatic updates enabled", points=10),
            OptionSchema(id="b", text="Delay updates for several months", points=2),
            OptionSchema(id="c", text="Never install updates", points=0)
        ]
    ),
    QuestionSchema(
        id="q12",
        category="device_security",
        category_title="Device & Software Security",
        question="What security lock features are active on your personal phone and computer?",
        options=[
            OptionSchema(id="a", text="Screen lock passcode/biometrics and full disk encryption", points=10),
            OptionSchema(id="b", text="Simple screen lock passcode only", points=5),
            OptionSchema(id="c", text="No passcode or security lock", points=0)
        ]
    )
]

RECOMMENDATIONS_MAP: Dict[str, str] = {
    "phishing": "Always inspect browser address bar domain spelling. Never click link prompts in unsolicited emails.",
    "passwords": "Adopt a secure password manager to generate and store unique passwords for every online account.",
    "mfa": "Enable Multi-Factor Authentication (MFA) using an Authenticator App across all email and financial accounts.",
    "social_engineering": "Never share MFA codes, passcodes, or passwords over phone or messaging apps under any pressure.",
    "payment_safety": "Use credit cards with buyer protection or virtual cards instead of debit cards or wire transfers online.",
    "device_security": "Enable automatic OS/browser security updates and enforce strong passcode screen locks."
}

def evaluate_checkup_submission(answers: Dict[str, str]) -> Dict[str, Any]:
    """
    Evaluates checkup submission deterministically.
    Returns total score (0-100), security level, category scores, weakest category, and recommendations.
    """
    category_totals: Dict[str, int] = {}
    category_maxes: Dict[str, int] = {}
    category_titles: Dict[str, str] = {}

    question_map = {q.id: q for q in QUESTIONS}

    for q in QUESTIONS:
        cat = q.category
        if cat not in category_totals:
            category_totals[cat] = 0
            category_maxes[cat] = 0
            category_titles[cat] = q.category_title
        category_maxes[cat] += 10  # Max 10 pts per question

        selected_opt_id = answers.get(q.id)
        if selected_opt_id:
            opt = next((o for o in q.options if o.id == selected_opt_id), None)
            if opt:
                category_totals[cat] += opt.points

    # Calculate overall total score (scale 0-100)
    total_earned = sum(category_totals.values())
    total_max = sum(category_maxes.values())
    overall_score = round((total_earned / total_max) * 100) if total_max > 0 else 0

    # Calculate individual category scores (0-100)
    category_scores: Dict[str, Dict[str, Any]] = {}
    weakest_cat_key = None
    lowest_cat_score = 101

    for cat_key, earned in category_totals.items():
        cat_max = category_maxes[cat_key]
        score_pct = round((earned / cat_max) * 100) if cat_max > 0 else 0
        category_scores[cat_key] = {
            "title": category_titles[cat_key],
            "score": score_pct,
            "earned": earned,
            "max": cat_max
        }
        if score_pct < lowest_cat_score:
            lowest_cat_score = score_pct
            weakest_cat_key = cat_key

    # Overall Security Level
    if overall_score >= 85:
        security_level = "EXCELLENT"
    elif overall_score >= 70:
        security_level = "HIGH"
    elif overall_score >= 50:
        security_level = "MODERATE"
    else:
        security_level = "LOW"

    # Compile tailored recommendations
    recommendations: List[str] = []
    if weakest_cat_key and weakest_cat_key in RECOMMENDATIONS_MAP:
        recommendations.append(f"Priority Focus ({category_titles[weakest_cat_key]}): {RECOMMENDATIONS_MAP[weakest_cat_key]}")

    for cat_key, info in category_scores.items():
        if info["score"] < 70 and cat_key != weakest_cat_key:
            recommendations.append(f"{info['title']}: {RECOMMENDATIONS_MAP[cat_key]}")

    if not recommendations:
        recommendations.append("Outstanding digital security hygiene! Maintain your current practices and stay vigilant.")

    return {
        "overall_score": overall_score,
        "security_level": security_level,
        "category_scores": category_scores,
        "weakest_category": category_titles.get(weakest_cat_key, "None"),
        "recommendations": recommendations
    }
