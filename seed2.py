"""
Add 15 more realistic participants to survey #2.
Run: py -3.10 seed2.py
"""
import json
import urllib.request

BASE = "http://localhost:8000/api"
SURVEY_ID = 2

# Statement IDs for survey #2 (in order)
STMT_IDS = [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23,25,27,29,31,33,35,37,39,41,43,45]
# Positions:  0 1 2 3 4 5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29

# Statements for reference:
#  0  The federal government should play a larger role in regulating the economy.
#  1  Taxes on high-income individuals should be increased.
#  2  Reducing government spending should be a higher priority than expanding programs.
#  3  Universal basic income is a viable solution to economic inequality.
#  4  Large corporations have too much influence over public policy.
#  5  The U.S. should prioritize reducing the national debt over new spending.
#  6  Healthcare should be guaranteed by the government as a universal right.
#  7  Private healthcare markets produce better outcomes than government-run systems.
#  8  Prescription drug prices should be regulated by the federal government.
#  9  The U.S. should make it easier for immigrants to enter legally.
# 10  Border security should be significantly increased.
# 11  Undocumented immigrants should have a path to citizenship.
# 12  Immigration strengthens the U.S. economy overall.
# 13  Abortion should be legal in most or all cases.
# 14  Transgender individuals should have access to gender-affirming healthcare.
# 15  The government should not be involved in regulating personal social issues.
# 16  Public schools should include education on systemic racism.
# 17  Police departments should receive increased funding.
# 18  Criminal justice reform should prioritize reducing incarceration rates.
# 19  Non-violent drug offenses should not result in prison time.
# 20  Gun ownership should be more strictly regulated.
# 21  The Second Amendment should be interpreted broadly to protect gun rights.
# 22  Climate change should be a top priority for government action.
# 23  The U.S. should transition away from fossil fuels as quickly as possible.
# 24  Energy independence is more important than reducing emissions.
# 25  The U.S. should take a more active role in global conflicts.
# 26  Military spending should be reduced.
# 27  The U.S. should prioritize domestic issues over international involvement.
# 28  Social media companies should be more tightly regulated by the government.
# 29  Free speech should be protected even if it allows harmful or offensive content.

A, D, P = "agree", "disagree", "pass"

participants = [
    # 11. Green / Climate-First Progressive
    # Climate is the #1 issue; anti-corporate; strong social programs; pro-immigration
    # Slightly less culture-war focused than the SJ Progressive
    (
        "Green / Climate-First Progressive",
        [A, A, D, A, A, D,   A, D, A,   A, D, A, A,   A, A, D, A,   D, A, A,   A, D,   A, A, D,   D, A, D,   A, D]
    ),

    # 12. Religious Social Conservative
    # Strongly anti-abortion, anti-trans; opposes federal overreach but supports some spending;
    # pro-police; skeptical of immigration; traditional values on every social issue
    (
        "Religious Social Conservative",
        [D, D, A, D, P, A,   D, A, P,   D, A, D, P,   D, D, D, D,   A, D, D,   D, A,   D, D, A,   P, D, D,   D, A]
    ),

    # 13. Blue-Collar / Union Democrat
    # Pro-labor economics; skeptical of UBI and elite-driven immigration; pro-gun;
    # socially moderate; not culture-war focused; wants trade protection
    (
        "Blue-Collar Union Democrat",
        [A, A, D, D, A, D,   A, D, A,   D, A, D, A,   A, P, P, D,   P, A, A,   D, A,   D, D, P,   D, P, A,   A, A]
    ),

    # 14. Neoconservative
    # Pro-military intervention; free market; hawkish on foreign policy;
    # socially moderate-conservative; anti-regulation domestically; pro-immigration
    (
        "Neoconservative",
        [D, D, A, D, A, A,   D, A, A,   D, A, D, A,   D, P, P, D,   A, D, D,   D, A,   P, D, A,   A, D, D,   D, A]
    ),

    # 15. Anti-War Progressive (Chomsky / Hedges style)
    # Anti-imperialist; anti-military spending; strong social programs;
    # pro-civil liberties; skeptical of both parties; anti-corporate
    (
        "Anti-War Progressive",
        [A, A, D, A, A, D,   A, D, A,   A, D, A, A,   A, A, A, A,   D, A, A,   A, D,   A, A, D,   D, A, A,   D, A]
    ),

    # 16. Pro-Business / Third Way Democrat (Bloomberg style)
    # Socially liberal; fiscally moderate; pro-market but pro-regulation on healthcare/drugs;
    # pro-immigration; lukewarm on climate action pace; anti-populist
    (
        "Pro-Business Third Way Democrat",
        [D, A, P, D, A, P,   D, A, A,   A, P, A, A,   A, A, P, P,   P, A, A,   P, D,   A, P, D,   P, D, D,   A, A]
    ),

    # 17. Rural Conservative
    # Pro-gun as a core identity; anti-immigration; skeptical of federal government;
    # socially conservative; self-reliant ethos; suspicious of urban liberal agenda
    (
        "Rural Conservative",
        [D, D, A, D, A, A,   D, A, P,   D, A, D, D,   D, D, A, D,   A, D, D,   D, A,   D, D, A,   D, D, A,   D, A]
    ),

    # 18. Young Disengaged / Vibe Voter
    # Mixed; leans socially liberal but skeptical of institutions; anti-establishment;
    # passes on hard policy questions; somewhat libertarian on personal freedom
    (
        "Young Disengaged Swing Voter",
        [P, A, P, P, A, P,   A, D, A,   A, P, A, A,   A, A, A, P,   P, A, A,   A, P,   A, P, D,   D, D, P,   D, A]
    ),

    # 19. Tech Libertarian (Silicon Valley)
    # Anti-regulation on business and tech; strongly pro-immigration (especially skilled);
    # socially liberal; anti-speech regulation; UBI skeptic; pro-free market
    (
        "Tech Libertarian",
        [D, D, D, D, A, D,   D, A, D,   A, D, A, A,   A, A, A, P,   D, A, A,   D, A,   P, D, D,   D, P, D,   D, A]
    ),

    # 20. Evangelical Conservative
    # Very socially conservative; pro-life as primary issue; pro-gun; anti-drug;
    # somewhat skeptical of big business but anti-government; moral traditionalist
    (
        "Evangelical Conservative",
        [D, D, A, D, P, A,   D, A, P,   D, A, D, P,   D, D, D, D,   A, D, D,   D, A,   D, D, A,   P, D, D,   D, A]
    ),

    # 21. Criminal Justice Reform Advocate
    # Laser-focused on policing and incarceration; pro-social programs;
    # progressive but not across the board; skeptical of military and police budgets
    (
        "Criminal Justice Reform Advocate",
        [A, A, D, A, A, D,   A, D, A,   A, D, A, A,   A, A, D, A,   D, A, A,   A, D,   A, A, D,   D, A, D,   A, D]
    ),

    # 22. Hispanic Conservative
    # Socially conservative; pro-family; pragmatic on immigration (wants order but path to citizenship);
    # pro-border security; skeptical of welfare; religious values
    (
        "Hispanic Conservative",
        [D, D, A, D, A, A,   D, A, A,   D, A, A, A,   D, D, A, D,   A, D, D,   D, A,   D, D, A,   P, D, D,   D, A]
    ),

    # 23. Working-Class Populist Left (Bernie-adjacent but culturally moderate)
    # Anti-corporate; pro-worker; skeptical of globalization and immigration's wage effects;
    # pro-gun; socially mixed; anti-war; anti-elite
    (
        "Working-Class Populist Left",
        [A, A, D, A, A, D,   A, D, A,   D, A, A, A,   A, P, P, D,   D, A, A,   D, A,   D, D, P,   D, A, A,   A, A]
    ),

    # 24. Constitutional / States-Rights Conservative
    # Strict constitutionalist; anti-federal overreach; pro-gun (2nd Amendment absolutist);
    # wants states to decide social issues; skeptical of military adventurism; anti-debt
    (
        "Constitutional / States-Rights Conservative",
        [D, D, A, D, A, A,   D, A, D,   A, A, D, A,   D, P, A, D,   A, D, A,   D, A,   D, D, A,   D, D, A,   D, A]
    ),

    # 25. Independent Pragmatist / True Centrist
    # Evaluates each issue individually; no party loyalty; accepts tradeoffs;
    # skeptical of both regulatory overreach and market failure; anti-war; pro-free speech
    (
        "Independent Pragmatist",
        [P, A, P, D, A, P,   A, P, A,   A, P, A, A,   A, P, A, P,   A, A, A,   P, P,   A, P, P,   P, P, P,   A, A]
    ),
]


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


print(f"Adding {len(participants)} participants to survey #{SURVEY_ID}...\n")

for label, votes in participants:
    assert len(votes) == len(STMT_IDS), f"{label}: got {len(votes)} votes, expected {len(STMT_IDS)}"
    session = post(f"/surveys/{SURVEY_ID}/sessions", {})
    pid = session["id"]
    payload = [{"statement_id": STMT_IDS[j], "vote": votes[j]} for j in range(len(STMT_IDS))]
    post(f"/sessions/{pid}/responses", payload)
    print(f"  #{pid:3d} {label}")

print(f"\nDone. Survey now has {10 + len(participants)} participants total.")
print(f"Results: http://localhost:5173/results/{SURVEY_ID}")
