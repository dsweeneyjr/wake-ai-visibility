# Wake Tech AI Visibility Observatory

## Vision

As AI-powered search becomes a primary way people discover colleges, Wake Tech needs a way to measure how AI platforms represent the college, identify opportunities to improve visibility, and monitor changes over time.

This project will create a dashboard that tracks Wake Tech's presence across AI platforms including ChatGPT, Gemini, Perplexity, and others.

---

# Goals

Build a system that can answer questions like:

- How often is Wake Tech recommended?
- Which programs are recommended most often?
- Which competitors are recommended instead?
- What Wake Tech pages are cited?
- Which competitor pages are cited?
- What topics are we missing?
- How is our visibility changing over time?

---

# MVP (Demo for Kelley)

The first version only needs to:

- Read a list of prompts
- Submit prompts to ChatGPT
- Save every response
- Score Wake Tech visibility
- Display the results in a dashboard

No automation.

No fancy charts.

Just prove the concept.

---

# Future Versions

## Version 0.2

- Gemini integration
- Perplexity integration

---

## Version 0.3

Automatically detect:

- Wake Tech mentioned
- Position in answer
- Competitors
- Citations

---

## Version 0.4

Weekly scheduled runs.

Historical trends.

---

## Version 1.0

Executive dashboard.

Department dashboards.

Email summaries.

Alerts.

---

# Data Model

Every prompt should create one record.

Fields:

Run Date

Prompt

Category

AI Platform

Response

Wake Tech Mentioned

Position

Competitors Mentioned

Wake Tech URLs Cited

Competitor URLs Cited

Sentiment

Hallucination

Visibility Score

Notes

---

# Success

A successful MVP lets us answer:

"How visible is Wake Tech across AI search?"

with actual data instead of guesses.

---

# Long-Term Vision

Become the primary platform Wake Tech uses to monitor AI search visibility and provide actionable recommendations for improving discoverability across generative search platforms.