# ⚡ ProcessPulse AI
### Where Your AI Should Actually Go

> *"Only 11% of companies are seeing measurable benefits from AI projects today.
> That's not an adoption problem. That's a context problem."*
> — **Alex Rinke, Co-CEO, Celonis** · Celosphere 2025

---

## What This Project Does

ProcessPulse AI is a Process Intelligence dashboard that demonstrates **why AI fails without business context** — and shows exactly where AI interventions will deliver measurable ROI.

It analyses enterprise process event logs (Order-to-Cash and Procure-to-Pay), identifies value-leaking bottlenecks, scores AI readiness per activity, and generates a phased implementation roadmap with a full ROI business case.

---

## Features

| Tab | What It Shows |
|-----|--------------|
| 📊 Process Overview | Actual vs intended process flow, variant distribution, cycle time analysis |
| 🔍 Bottleneck Analysis | Top 5 value-leaking activities with cost quantification |
| 🤖 AI Opportunity Map | 4-dimension AI readiness scoring, scatter plot, technology matching |
| 💰 ROI Calculator | Waterfall chart, adjustable assumptions, payback period |
| 🗺️ Implementation Roadmap | 3-phase plan + BA deliverables checklist |

---

## Run Locally

```bash
# 1. Clone / download the project
cd processpulse

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
streamlit run app.py
```

---

## Deploy to Streamlit Cloud (Free)

1. Push this folder to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → select `app.py`
4. Deploy → share the URL on LinkedIn

---

## Tech Stack

- **Python** · Pandas · NumPy
- **Streamlit** · Plotly
- **Process Mining** concepts (PM4Py-compatible event log format)
- **SAP S/4HANA** domain knowledge (O2C, P2P processes)
- **Celonis** Process Intelligence methodology

---

## About

Built by **Rutwik Satish**
MS Engineering Management · Northeastern University (May 2026)
Celonis Process Mining Certified · SAP S/4HANA · McKinsey Forward

**Target roles:** AI Business Analyst · Process Intelligence Consultant · AI Operations Consultant

**Companies to tag:** @Celonis, @SAP, @Deloitte, @Accenture, @IBM, @Capgemini

---

## LinkedIn Post Template

```
I read that only 11% of companies see measurable AI benefits.
Alex Rinke (Celonis Co-CEO) called it a "context problem" at Celosphere 2025.

So I built ProcessPulse AI to show what that actually means.

The app analyses an Order-to-Cash process and finds:
→ Only X% of cases follow the intended path
→ Top 5 bottlenecks wasting [N],000+ hours
→ $[X]M in AI-recoverable value hiding in plain sight

The insight: AI deployed without process intelligence optimises the WRONG steps.

Built with: Celonis methodology · SAP S/4HANA domain knowledge ·
Python/Streamlit · Process Mining

🔗 [your streamlit link]
GitHub: [your repo]

@Celonis @SAP
#ProcessMining #AIStrategy #BusinessAnalyst #ProcessIntelligence #DigitalTransformation
```
