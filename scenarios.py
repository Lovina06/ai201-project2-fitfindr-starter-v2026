"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # State preservation: check item ID flows through session. Criterion 3.
        "name": "state: item ID preservation",
        "query": "vintage Levi's jeans",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Fit card quality: should mention price and platform. Criterion 4.
        "name": "fit card: has price and platform",
        "query": "flannel shirt under $25",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Same query multiple times to check fit card variation. Criterion 4.
        "name": "fit card: variation check",
        "query": "track jacket size M",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Price ceiling: all results should be under max_price. Criterion 5.
        "name": "price ceiling: under $20",
        "query": "graphic tee under $20",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Another price ceiling test with different limit. Criterion 5.
        "name": "price ceiling: under $40",
        "query": "vintage pants under $40",
        "wardrobe": "example",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
