# HISN AI — Hackathon MVP

**Your AI-Powered Cyber Shield**  
An early-stage, explainable cyber-safety prototype that screens suspicious messages and URLs, explains risk indicators, and links similar reports into possible campaigns.

## Problem
People often recognize phishing and impersonation attempts only after they have clicked a link or shared sensitive information. Single-message warnings also miss the fact that several messages may be part of one coordinated campaign.

## Solution
This MVP demonstrates three workflows:
1. **Message and URL screening:** transparent heuristic checks for urgency, credential requests, impersonation, threats, reward lures, and selected URL warning signs.
2. **Campaign similarity:** compares submitted cases using word overlap and matching hostnames to surface possible relationships.
3. **Awareness dashboard:** summarizes the cases entered in the current session and gives safe next-step advice.

## Important scope statement
This is a hackathon prototype, not a production cybersecurity product and not a validated AI classifier. The current baseline is a transparent rules-based model so judges can inspect why a warning was raised. Similarity is an investigative lead only, not proof of maliciousness or identity. It does not contact websites, banks, telecom providers, police, or government systems; it does not block links, freeze accounts, or monitor devices.

## Technical choices
- **Python + Streamlit:** fastest route to a working interactive web demo with minimal setup.
- **Regex and URL parsing:** lightweight, explainable baseline; avoids sending user content to external services.
- **Token Jaccard similarity + hostname match:** simple demonstration of campaign linking.
- **Session-only storage:** cases remain in the current app session; no external database is used.

### Trade-offs and limitations
- Rules may miss novel scams and may flag legitimate messages.
- Arabic dialects, obfuscation, image OCR, voice/deepfake analysis, and real threat-intelligence feeds are not implemented.
- Similarity is intentionally simple and should be validated on a labeled dataset before operational use.
- No external API is called; this improves privacy and reliability for the demo but limits detection coverage.

### What we would do with more time
- Build a properly evaluated Arabic/English classifier using a curated, permissioned dataset.
- Add calibrated confidence scores, explainability, adversarial testing, and independent security review.
- Add safe reputation lookups through approved threat-intelligence sources.
- Add encrypted persistence with retention controls and consent.
- Conduct usability tests and measure precision, recall, false-positive rate, and latency.
- Explore authorized integrations with relevant UAE stakeholders only after legal, privacy, and security review.

## Privacy and safety design
- Use synthetic sample messages during the hackathon.
- Do not paste real passwords, OTPs, card numbers, Emirates ID numbers, or private personal data.
- The app does not upload content to a third-party AI service.
- Data is held in Streamlit session state for the current session only.
- The prototype does not make accusations or automated enforcement decisions.

## Build and run
Requires Python 3.10+.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL printed by Streamlit (usually http://localhost:8501).

## Repository structure
```text
HISN_AI_MVP/
├── app.py
├── requirements.txt
├── README.md
└── docs/
    ├── architecture.md
    ├── privacy.md
    └── demo_script.md
```

## Demo checklist
- [ ] Run `streamlit run app.py`
- [ ] Paste a synthetic phishing example
- [ ] Show the risk indicators and advice
- [ ] Submit a second similar message
- [ ] Open campaign linking and explain similarity
- [ ] Open dashboard and explain that counts are demo-session data
- [ ] Explain limitations honestly
