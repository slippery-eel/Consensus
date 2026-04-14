"""
Seed script: creates the political opinions survey with 10 realistic fake participants.
Run from the project root: py -3.10 seed.py
"""
import json
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api"


def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


# ── Survey ────────────────────────────────────────────────────────────────────

survey = post("/surveys", {
    "title": "American Political Opinions",
    "description": "30 statements spanning government, healthcare, immigration, social issues, crime, guns, climate, foreign policy, and technology.",
})
sid = survey["id"]
print(f"Created survey #{sid}: {survey['title']}")

# ── Statements ────────────────────────────────────────────────────────────────

statements_text = [
    # Government & Economy
    "The federal government should play a larger role in regulating the economy.",
    "Taxes on high-income individuals should be increased.",
    "Reducing government spending should be a higher priority than expanding programs.",
    "Universal basic income is a viable solution to economic inequality.",
    "Large corporations have too much influence over public policy.",
    "The U.S. should prioritize reducing the national debt over new spending.",
    # Healthcare
    "Healthcare should be guaranteed by the government as a universal right.",
    "Private healthcare markets produce better outcomes than government-run systems.",
    "Prescription drug prices should be regulated by the federal government.",
    # Immigration
    "The U.S. should make it easier for immigrants to enter legally.",
    "Border security should be significantly increased.",
    "Undocumented immigrants should have a path to citizenship.",
    "Immigration strengthens the U.S. economy overall.",
    # Social Issues
    "Abortion should be legal in most or all cases.",
    "Transgender individuals should have access to gender-affirming healthcare.",
    "The government should not be involved in regulating personal social issues.",
    "Public schools should include education on systemic racism.",
    # Crime & Policing
    "Police departments should receive increased funding.",
    "Criminal justice reform should prioritize reducing incarceration rates.",
    "Non-violent drug offenses should not result in prison time.",
    # Guns
    "Gun ownership should be more strictly regulated.",
    "The Second Amendment should be interpreted broadly to protect gun rights.",
    # Climate & Energy
    "Climate change should be a top priority for government action.",
    "The U.S. should transition away from fossil fuels as quickly as possible.",
    "Energy independence is more important than reducing emissions.",
    # Foreign Policy
    "The U.S. should take a more active role in global conflicts.",
    "Military spending should be reduced.",
    "The U.S. should prioritize domestic issues over international involvement.",
    # Technology & Society
    "Social media companies should be more tightly regulated by the government.",
    "Free speech should be protected even if it allows harmful or offensive content.",
]

stmt_ids = []
for text in statements_text:
    s = post(f"/surveys/{sid}/statements", {"text": text})
    stmt_ids.append(s["id"])
    print(f"  Added statement #{s['id']}: {text[:60]}...")

print(f"\nAdded {len(stmt_ids)} statements.")

# ── Participants & votes ──────────────────────────────────────────────────────
# Vote encoding: A=agree, D=disagree, P=pass
# Order matches statements_text above (30 statements)
#
# Profiles:
#  1. Progressive Liberal        6. Democratic Socialist
#  2. Traditional Conservative   7. National Populist
#  3. Libertarian                8. Social Justice Progressive
#  4. Moderate Democrat          9. Fiscal Conservative / Social Moderate
#  5. Moderate Republican       10. Classical Liberal / Centrist

A, D, P = "agree", "disagree", "pass"

participants = [
    # 1. Progressive Liberal
    # strongly pro-government, pro-social programs, anti-gun, climate hawk
    [A, A, D, A, A, D,   A, D, A,   A, D, A, A,   A, A, D, A,   D, A, A,   A, D,   A, A, D,   D, A, D,   A, D],

    # 2. Traditional Conservative
    # anti-regulation, pro-market, pro-border, anti-abortion, pro-gun, climate skeptic
    [D, D, A, D, A, A,   D, A, P,   D, A, D, P,   D, D, A, D,   A, D, D,   D, A,   D, D, A,   A, D, D,   D, A],

    # 3. Libertarian
    # small government, anti-regulation, pro-immigration, pro-civil liberties, anti-military
    [D, D, A, P, A, A,   D, A, D,   A, D, A, A,   A, A, A, P,   D, A, A,   D, A,   P, D, D,   D, A, A,   D, A],

    # 4. Moderate Democrat
    # center-left, pragmatic, pro-healthcare, pro-immigration, cautious on radical changes
    [A, A, P, D, A, P,   A, D, A,   A, P, A, A,   A, A, P, A,   P, A, A,   A, D,   A, A, D,   P, P, P,   A, A],

    # 5. Moderate Republican
    # fiscally conservative, socially mixed, pro-business, pragmatic on immigration
    [D, P, A, D, A, A,   D, A, A,   P, A, P, A,   D, P, A, D,   A, P, P,   P, A,   A, D, A,   A, D, D,   P, A],

    # 6. Democratic Socialist
    # very left on economics, pro-worker, anti-corporate, strong social programs
    [A, A, D, A, A, D,   A, D, A,   A, D, A, A,   A, A, D, A,   D, A, A,   A, D,   A, A, D,   D, A, A,   A, P],

    # 7. National Populist (MAGA-style)
    # anti-immigration, anti-establishment, economic nationalist, socially conservative
    [A, D, A, D, A, A,   D, D, A,   D, A, D, D,   D, D, P, D,   A, D, D,   D, A,   D, D, A,   D, D, A,   D, A],

    # 8. Social Justice Progressive
    # strong on racial equity, anti-police, pro-trans, climate activist, anti-free speech harms
    [A, A, D, A, A, D,   A, D, A,   A, D, A, A,   A, A, D, A,   D, A, A,   A, D,   A, A, D,   D, A, D,   A, D],

    # 9. Fiscal Conservative / Social Moderate
    # low taxes, balanced budget, socially tolerant, pro-business, pragmatic
    [D, D, A, D, A, A,   D, A, A,   A, A, P, A,   A, A, A, P,   A, P, A,   P, A,   A, D, A,   P, P, P,   P, A],

    # 10. Classical Liberal / Anti-Establishment Centrist
    # pro-civil liberties, skeptical of both parties, pro-free speech, anti-war
    [P, A, P, D, A, P,   A, D, A,   A, P, A, A,   A, A, A, P,   P, A, A,   P, P,   A, P, D,   D, D, D,   D, A],
]

labels = [
    "Progressive Liberal",
    "Traditional Conservative",
    "Libertarian",
    "Moderate Democrat",
    "Moderate Republican",
    "Democratic Socialist",
    "National Populist",
    "Social Justice Progressive",
    "Fiscal Conservative / Social Moderate",
    "Classical Liberal / Centrist",
]

print()
for i, (votes, label) in enumerate(zip(participants, labels)):
    session = post(f"/surveys/{sid}/sessions", {})
    participant_id = session["id"]

    payload = [
        {"statement_id": stmt_ids[j], "vote": votes[j]}
        for j in range(len(stmt_ids))
    ]
    post(f"/sessions/{participant_id}/responses", payload)
    print(f"  Participant #{participant_id} ({label}): {len(payload)} votes submitted")

print(f"\nDone. Survey ID = {sid}")
print(f"Take the survey: http://localhost:5173/survey/{sid}")
print(f"View results:    http://localhost:5173/results/{sid}")
