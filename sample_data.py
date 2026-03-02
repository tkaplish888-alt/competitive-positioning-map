# Pre-built sample data so demo mode runs without any API calls.
# SAMPLE_PAGES mirrors what the Project 2 scraper delivers — raw homepage text.
# SAMPLE_MESSAGING mirrors what extract_messaging returns — structured dicts.

SAMPLE_PAGES: dict[str, str] = {
    "valur": (
        "Valur helps families move wealth to the next generation with less going to taxes. "
        "Our platform gives you access to the same sophisticated estate-planning strategies that "
        "were once reserved for ultra-high-net-worth clients — GRATs, SLATs, ILITs, and more — "
        "at a fraction of the traditional cost. Work with our attorneys and advisors entirely online, "
        "on your schedule. Valur is built for the modern affluent family that wants proactive, "
        "tax-efficient wealth transfer without the friction of the old-guard law firm."
    ),
    "trust_and_will": (
        "Trust & Will makes it easy to create a legal will or living trust from home in minutes. "
        "We believe every family deserves an estate plan, not just wealthy ones. "
        "Answer a few simple questions and our guided experience walks you through the entire process — "
        "no lawyer appointments, no confusing paperwork, no high fees. "
        "Join over 500,000 members who have already protected their families with Trust & Will."
    ),
    "wealth_com": (
        "Wealth.com is the estate planning platform built for financial advisors and their clients. "
        "Give your clients a seamless, white-labeled estate-planning experience without adding headcount. "
        "Our platform integrates directly with your existing wealth-management stack, surfaces estate-plan "
        "gaps in client portfolios, and keeps documents updated automatically as laws change. "
        "Wealth.com turns estate planning from a referral risk into a retention advantage."
    ),
    "vanilla": (
        "Vanilla is the modern estate-planning platform for RIAs and family offices. "
        "Visualize your clients' full estate plans in a single dashboard, identify tax exposure, "
        "and collaborate with attorneys — all in one place. "
        "We translate complex trust structures into clear visuals so advisors can have deeper, "
        "more confident conversations about wealth transfer. "
        "Vanilla helps advisory firms differentiate on planning depth, not just portfolio performance."
    ),
    "holistiplan": (
        "Holistiplan is tax-planning software that gives financial advisors instant, client-ready "
        "tax analysis in seconds. Upload a tax return and Holistiplan generates a comprehensive "
        "planning summary with actionable opportunities — Roth conversions, loss harvesting, "
        "charitable strategies, and more. "
        "Built by CFPs for CFPs, Holistiplan helps advisors add measurable value beyond investment "
        "management and justify their fees with concrete, personalised planning insights."
    ),
    "gentreo": (
        "Gentreo makes creating a will, healthcare proxy, and power of attorney simple and affordable "
        "for everyone. For less than the cost of a single lawyer hour, you can protect your family "
        "and your pets in under 15 minutes. "
        "Update your documents any time as your life changes — marriage, new baby, new home. "
        "Gentreo is designed for everyday families who want peace of mind without the legal complexity."
    ),
}

SAMPLE_MESSAGING: dict[str, dict] = {
    "valur": {
        "value_propositions": [
            "Tax-efficient wealth transfer for modern families",
            "Institutional-grade estate strategies made accessible",
            "Attorney-guided planning entirely online",
            "Significant tax savings vs. doing nothing",
        ],
        "target_audience": (
            "Affluent families with $1M–$20M in assets who want proactive wealth transfer "
            "planning but find traditional law firms slow, expensive, and opaque"
        ),
        "key_claims": [
            "Access GRATs, SLATs, and ILITs previously reserved for ultra-high-net-worth clients",
            "Complete the process online on your schedule",
            "Fraction of the cost of a traditional law firm",
            "Built for the modern affluent family",
            "Proactive, tax-efficient wealth transfer without friction",
        ],
        "differentiators": (
            "Combines sophisticated irrevocable trust strategies previously inaccessible to most "
            "with a fully digital, attorney-backed workflow at a democratised price point"
        ),
        "tone": "sophisticated, empowering",
        "positioning_summary": (
            "Valur positions itself as the democratiser of elite estate planning, bringing "
            "tax-minimisation strategies once exclusive to the ultra-wealthy to affluent families "
            "through a modern, digital-first platform. "
            "The brand emphasises financial sophistication and tangible tax savings over simplicity, "
            "targeting clients who want to be proactive stewards of generational wealth."
        ),
    },
    "trust_and_will": {
        "value_propositions": [
            "Affordable estate planning for every family",
            "Create a legal will or trust in minutes from home",
            "Simple guided experience with no lawyer required",
            "Peace of mind at a fraction of traditional costs",
        ],
        "target_audience": (
            "Broad consumer market — middle-class families who have been putting off estate "
            "planning because it feels expensive, complicated, or inaccessible"
        ),
        "key_claims": [
            "Over 500,000 members have already protected their families",
            "Legal documents completed entirely online",
            "No lawyer appointments or confusing paperwork",
            "Estate planning made easy and affordable",
            "Every family deserves an estate plan",
        ],
        "differentiators": (
            "Mass-market accessibility and price point; positions estate planning as a "
            "universal right rather than a luxury, with a consumer-brand voice and guided UX"
        ),
        "tone": "approachable, reassuring",
        "positioning_summary": (
            "Trust & Will occupies the accessible end of the estate-planning market, "
            "using democratic language to appeal to the large segment who have never created "
            "any estate documents. "
            "The brand competes on simplicity and price rather than planning depth, targeting "
            "families motivated by basic protection rather than tax optimisation."
        ),
    },
    "wealth_com": {
        "value_propositions": [
            "Estate planning as an advisor retention tool",
            "White-labeled platform for financial advisors",
            "Automated document maintenance as laws change",
            "Surfaces estate-plan gaps in client portfolios",
        ],
        "target_audience": (
            "Financial advisors and RIAs who want to offer estate-planning services to clients "
            "without building in-house expertise or risking referral relationships"
        ),
        "key_claims": [
            "Integrates directly with existing wealth-management stacks",
            "Turns estate planning from a referral risk into a retention advantage",
            "White-labeled client experience with no added headcount",
            "Automatically updates documents as laws change",
            "Surfaces estate-plan gaps at the portfolio level",
        ],
        "differentiators": (
            "B2B focus on financial advisors rather than end consumers; "
            "frames estate planning as an AUM retention and differentiation strategy"
        ),
        "tone": "professional, strategic",
        "positioning_summary": (
            "Wealth.com targets financial advisors as its primary customer, framing estate "
            "planning as a client-retention and competitive-differentiation tool rather than "
            "a consumer product. "
            "Its positioning centres on seamless integration with existing advisory workflows "
            "and the business case for advisors to own estate planning rather than outsourcing it."
        ),
    },
    "vanilla": {
        "value_propositions": [
            "Visual estate-plan dashboards for advisors",
            "Identify tax exposure across client portfolios",
            "Advisor-attorney collaboration in one platform",
            "Planning depth as a competitive differentiator",
        ],
        "target_audience": (
            "RIAs and family offices whose advisors need to discuss complex trust structures "
            "with confidence and differentiate beyond investment returns"
        ),
        "key_claims": [
            "Visualise full estate plans in a single dashboard",
            "Translates complex trust structures into clear visuals",
            "Enables deeper, more confident wealth-transfer conversations",
            "Helps advisory firms differentiate on planning depth",
            "Built for RIAs and family offices",
        ],
        "differentiators": (
            "Emphasis on visual clarity and advisor confidence rather than document generation; "
            "positions complex estate structures as a communication and differentiation asset"
        ),
        "tone": "polished, expert",
        "positioning_summary": (
            "Vanilla positions itself as the visualisation and collaboration layer for sophisticated "
            "estate planning, helping RIAs and family offices translate complex structures into "
            "client-facing conversations. "
            "Unlike document-generation tools, Vanilla's differentiation is advisor empowerment "
            "and planning depth, appealing to firms that compete on comprehensive wealth management."
        ),
    },
    "holistiplan": {
        "value_propositions": [
            "Instant tax analysis from an uploaded tax return",
            "Client-ready planning summaries in seconds",
            "Concrete ROI justification for advisory fees",
            "Actionable tax opportunities surfaced automatically",
        ],
        "target_audience": (
            "CFP-credentialed financial advisors who want to add measurable value beyond "
            "portfolio management and demonstrate fee justification through tax planning"
        ),
        "key_claims": [
            "Built by CFPs for CFPs",
            "Upload a tax return and get a comprehensive planning summary instantly",
            "Surfaces Roth conversions, loss harvesting, charitable strategies automatically",
            "Helps advisors justify their fees with personalised insights",
            "Adds measurable value beyond investment management",
        ],
        "differentiators": (
            "Laser focus on tax planning rather than estate planning; "
            "peer-built credibility and speed-to-insight as core value drivers"
        ),
        "tone": "analytical, peer-to-peer",
        "positioning_summary": (
            "Holistiplan occupies the tax-planning niche within the broader financial-planning "
            "software market, positioning itself as the fastest path from a client tax return "
            "to a concrete, advisor-led planning conversation. "
            "The brand speaks directly to CFPs as professional peers, emphasising fee justification "
            "and measurable client value over comprehensive estate or wealth-transfer capabilities."
        ),
    },
    "gentreo": {
        "value_propositions": [
            "Wills, healthcare proxies, and POAs for everyday families",
            "Under 15 minutes and less than the cost of one lawyer hour",
            "Update documents any time as life changes",
            "Peace of mind without legal complexity",
        ],
        "target_audience": (
            "Everyday middle-income families who want basic legal protection documents "
            "without the cost or intimidation of hiring a lawyer"
        ),
        "key_claims": [
            "Complete essential documents in under 15 minutes",
            "Costs less than a single lawyer hour",
            "Covers wills, healthcare proxies, and powers of attorney",
            "Update any time as life circumstances change",
            "Designed for everyday families",
        ],
        "differentiators": (
            "Extreme simplicity and price accessibility targeting first-time consumers of legal "
            "services; speed and affordability anchor the brand rather than planning sophistication"
        ),
        "tone": "friendly, accessible",
        "positioning_summary": (
            "Gentreo competes at the most accessible tier of estate planning, targeting families "
            "who have no existing legal documents and are primarily motivated by price and simplicity. "
            "The brand avoids any financial or tax-planning language, instead anchoring on speed, "
            "affordability, and life-event flexibility to lower the barrier to a first estate plan."
        ),
    },
}
