"""
Seed script: creates the Relationships & Modern Dating survey with 30 realistic fake participants.
Run from the project root: py -3.10 seed_relationships.py
"""
import json
import urllib.request

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
    "title": "Relationships & Modern Dating",
    "description": "30 statements about romantic relationships, friendship, dating culture, and modern connection.",
})
sid = survey["id"]
print(f"Created survey #{sid}: {survey['title']}")

# ── Statements ────────────────────────────────────────────────────────────────

statements_text = [
    # Romantic relationships
    "Most people settle in relationships rather than finding the \"right\" person.",
    "Long-term relationships require more effort than compatibility.",
    "Physical attraction is one of the most important factors in a relationship.",
    "Emotional compatibility matters more than shared interests.",
    "People often stay in relationships longer than they should.",
    "It's better to be single than in a mediocre relationship.",
    # Dating apps
    "Modern dating apps have made dating worse overall.",
    "Dating apps make it easier to find the right partner.",
    "People are more disposable in modern dating culture.",
    "Having too many options makes it harder to commit.",
    # Friendship & connection
    "It's harder to form deep connections as an adult.",
    "Most people don't have truly close friendships.",
    "Friendships require as much intentional effort as romantic relationships.",
    "People drift apart more because of neglect than conflict.",
    # Priorities
    "You should prioritize your partner over your friends.",
    "You should prioritize your personal growth over maintaining relationships.",
    "Relationships often require sacrificing individual desires.",
    # Dynamics
    "Jealousy is a natural and unavoidable part of relationships.",
    "Trust is more important than transparency in a relationship.",
    "Complete honesty is necessary for a healthy relationship.",
    # Self-knowledge & chemistry
    "People are generally bad at knowing what they want in a partner.",
    "Chemistry is more important than long-term compatibility.",
    "Love alone is not enough to sustain a relationship.",
    # Social media
    "Social media has negatively impacted relationships.",
    "Seeing others' relationships online creates unrealistic expectations.",
    "Most people present a version of themselves in relationships that isn't fully authentic.",
    # Vulnerability & loneliness
    "Vulnerability is necessary for strong relationships.",
    "It's better to have a few close friends than many casual ones.",
    "Loneliness is more common than people admit.",
    "Most people struggle to maintain meaningful relationships over time.",
]

stmt_ids = []
for text in statements_text:
    s = post(f"/surveys/{sid}/statements", {"text": text})
    stmt_ids.append(s["id"])
    print(f"  Added statement #{s['id']}: {text[:65]}...")

print(f"\nAdded {len(stmt_ids)} statements.")

# ── Participants & votes ──────────────────────────────────────────────────────
# Vote encoding: A=agree, D=disagree, P=pass
# 30 statements in the order above.

A, D, P = "agree", "disagree", "pass"

# Columns: s1–s30 (same order as statements_text)
participants = [
    # 1. Bitter Cynic — been through painful breakups, pessimistic about love
    [A, A, A, A, A, A,  A, D, A, A,  A, A, P, A,  D, A, A,  D, A, P,  A, D, A,  A, A, A,  D, A, A, A],

    # 2. Hopeless Romantic — believes in soulmates, chemistry over everything
    [D, P, A, A, D, D,  A, D, D, P,  D, D, A, A,  P, D, A,  A, A, A,  D, A, D,  A, A, P,  A, A, D, P],

    # 3. Pragmatist — logical about love, knows it takes sustained work
    [A, A, P, A, A, P,  P, P, A, A,  A, P, A, A,  D, P, A,  D, A, A,  A, D, A,  A, A, A,  A, A, A, A],

    # 4. Independent Woman — career-focused, skeptical of sacrificing self for relationships
    [A, D, P, P, A, A,  A, D, A, A,  D, P, A, D,  D, A, A,  D, A, P,  A, D, P,  A, A, A,  P, A, A, A],

    # 5. App Optimist — met great partners on apps, modern dating has upsides
    [A, A, A, A, A, D,  D, A, D, D,  D, P, P, A,  P, P, A,  P, A, A,  P, A, P,  D, D, P,  A, A, D, P],

    # 6. Social Butterfly — deep friendships are as vital as romance
    [P, A, A, A, A, P,  P, P, P, P,  D, A, A, A,  D, P, A,  P, A, A,  P, P, A,  A, A, A,  A, A, A, A],

    # 7. Traditional Romantic — long marriage, old-school values, commitment above all
    [D, A, A, A, A, D,  A, D, A, P,  A, D, A, A,  A, D, A,  A, D, A,  D, A, A,  A, A, D,  A, A, A, A],

    # 8. Jaded Dater — exhausted by apps, many bad experiences, craves authenticity
    [A, A, A, A, A, A,  A, D, A, A,  A, A, A, A,  D, P, A,  A, P, P,  A, A, A,  A, A, A,  D, A, A, A],

    # 9. Attachment Theorist — studied attachment science, values vulnerability and secure bonds
    [D, A, P, A, A, P,  P, P, A, A,  A, D, A, A,  P, P, A,  A, A, A,  A, P, A,  A, A, A,  A, A, A, A],

    # 10. Serial Monogamist — always in relationships, uncomfortable being single
    [A, A, A, A, D, D,  A, P, A, A,  D, P, A, A,  A, D, A,  A, A, A,  D, A, D,  A, A, P,  A, P, A, A],

    # 11. Growth-Focused — relationships should serve personal development
    [A, A, D, P, A, A,  P, P, A, A,  A, A, A, A,  D, A, A,  D, A, P,  A, D, A,  A, P, A,  A, A, A, A],

    # 12. Anxious Attacher — fears abandonment, needs reassurance, highly relational
    [D, A, A, A, A, D,  A, D, A, A,  A, A, A, A,  A, D, A,  A, D, A,  A, A, D,  A, A, A,  A, D, A, A],

    # 13. Avoidant — values independence, struggles with intimacy, keeps distance
    [A, D, A, D, A, A,  A, D, A, A,  A, A, D, P,  D, A, D,  D, A, D,  A, D, A,  A, P, A,  D, A, A, A],

    # 14. Social Media Critic — technology is destroying authentic human connection
    [A, A, P, A, A, A,  A, D, A, A,  A, A, A, A,  D, P, A,  P, A, A,  A, P, A,  A, A, A,  P, A, A, A],

    # 15. Optimistic Realist — realistic but hopeful, relationships take work and are worth it
    [D, A, A, A, A, D,  P, P, P, P,  A, P, A, A,  P, P, A,  P, A, A,  P, P, A,  P, P, P,  A, A, A, P],

    # 16. Dating Coach — professional perspective, sees patterns across many clients
    [A, A, A, A, A, A,  A, D, A, A,  D, A, A, A,  D, P, A,  P, A, A,  A, D, A,  A, A, A,  A, A, A, A],

    # 17. Philosopher — questions assumptions about love, drawn to nuance
    [A, A, D, A, A, A,  P, P, A, P,  D, D, A, A,  D, A, A,  D, A, A,  A, A, D,  A, A, A,  A, A, A, A],

    # 18. Young Optimist (21) — hasn't been hurt yet, genuine faith in love
    [D, D, A, A, D, D,  D, A, D, D,  D, D, A, A,  P, D, D,  A, A, A,  D, A, D,  D, D, D,  A, A, D, D],

    # 19. Burnout — emotionally depleted from repeated relationship failures
    [A, A, A, A, A, A,  A, D, A, A,  A, A, P, A,  D, A, A,  D, A, P,  A, D, A,  A, A, A,  D, A, A, A],

    # 20. Securely Attached — stable relationship history, balanced and grounded
    [D, A, A, A, A, D,  P, P, D, P,  D, D, A, A,  P, P, A,  D, A, A,  D, P, A,  A, A, P,  A, A, A, P],

    # 21. Non-monogamous — open relationship model, challenges traditional assumptions
    [A, A, A, D, A, A,  P, P, D, D,  D, D, A, A,  D, A, D,  D, A, A,  A, A, D,  A, P, A,  A, A, A, A],

    # 22. Religious Traditional — faith shapes relationship values, commitment is sacred
    [D, A, A, A, A, D,  A, D, P, A,  A, P, A, A,  A, D, A,  A, D, A,  D, D, D,  A, A, D,  A, A, A, P],

    # 23. Independent Feminist — equality in relationships, resists traditional gender roles
    [A, A, D, A, A, A,  A, D, A, A,  A, A, A, A,  D, A, A,  D, A, A,  A, D, A,  A, A, A,  A, A, A, A],

    # 24. Introvert — values depth, few close connections, wary of surface-level relating
    [A, A, D, A, A, A,  D, D, A, A,  A, A, A, A,  D, A, A,  D, A, A,  A, D, A,  D, P, A,  A, A, A, A],

    # 25. Gen-Z Doomer — grew up on social media, deeply cynical about modern connection
    [A, A, A, A, A, A,  A, D, A, A,  A, A, A, A,  D, A, A,  P, A, A,  A, A, A,  A, A, A,  D, A, A, A],

    # 26. Married 20 Years — long-term experience, values commitment and earned trust
    [D, A, A, A, P, D,  A, D, P, A,  A, D, A, A,  A, D, A,  P, D, A,  D, D, A,  P, P, D,  A, A, A, P],

    # 27. App Entrepreneur — works in tech, bullish on data-driven matching
    [A, A, A, A, A, D,  D, A, D, D,  D, P, P, A,  P, P, A,  P, A, A,  P, A, P,  D, D, P,  A, P, D, D],

    # 28. Therapist — professional counselor, nuanced clinical perspective
    [A, A, P, A, A, P,  P, P, A, A,  D, P, A, A,  D, P, A,  D, A, A,  A, D, A,  A, A, A,  A, A, A, A],

    # 29. Chronic Single — long stretch of solitude, craves but struggles to find connection
    [A, A, A, D, A, A,  A, D, A, A,  A, A, A, D,  D, A, A,  D, A, A,  A, A, A,  A, A, A,  D, A, A, A],

    # 30. Newly Divorced — reassessing everything after a long marriage ended
    [A, A, A, A, A, A,  A, D, A, A,  A, A, A, A,  D, A, A,  D, A, A,  A, D, A,  A, A, A,  D, A, A, A],
]

labels = [
    "Bitter Cynic",
    "Hopeless Romantic",
    "Pragmatist",
    "Independent Woman",
    "App Optimist",
    "Social Butterfly",
    "Traditional Romantic",
    "Jaded Dater",
    "Attachment Theorist",
    "Serial Monogamist",
    "Growth-Focused",
    "Anxious Attacher",
    "Avoidant",
    "Social Media Critic",
    "Optimistic Realist",
    "Dating Coach",
    "Philosopher",
    "Young Optimist",
    "Burnout",
    "Securely Attached",
    "Non-monogamous",
    "Religious Traditional",
    "Independent Feminist",
    "Introvert",
    "Gen-Z Doomer",
    "Married 20 Years",
    "App Entrepreneur",
    "Therapist",
    "Chronic Single",
    "Newly Divorced",
]

assert len(participants) == 30, f"Expected 30 participants, got {len(participants)}"
for i, votes in enumerate(participants):
    assert len(votes) == 30, f"Participant {i+1} has {len(votes)} votes, expected 30"

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
