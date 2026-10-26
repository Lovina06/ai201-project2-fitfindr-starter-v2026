# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** 4 of 5 because my search uses keyword overlap scoring, which is sensitive to phrasing. A query like "tee with graphic" might score differently than "graphic tee" even though they mean the same thing. The model-based query parsing helps, but it can't perfectly normalize every way someone might describe an item. 5 of 5 would require semantic search or embedding-based matching.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** 5 of 5 is reasonable because this is pure control flow — if search_listings returns an empty list, the branch condition is deterministic. Unlike criterion 1 (which depends on search quality and phrasing), this just checks `if not results:` and stops. There's no variability: either the list is empty or it isn't. A miss here means the branch logic is broken.

---

## 3. State preservation through the pipeline

For 5 different queries that return results, the listing ID stored in session["selected_item"]["id"] matches the ID of the item that suggest_outfit and create_fit_card actually used — in all 5 of 5 tries.

**Why this target:** 5 of 5 because state passing through the session dictionary is deterministic — if the session stores the right item once, it should always store it. A miss here means the loop is passing data incorrectly, not that there's acceptable variation. This catches bugs like passing load_listings()[0] directly to suggest_outfit instead of session["selected_item"].



---

## 4. Fit card contains required elements

For 5 different items, each generated fit card mentions the price, the platform, and is between 2-6 sentences long — in at least 4 of 5 tries.

**Why this target:** 4 of 5 because the model generates variable text and might occasionally phrase things differently (e.g., "found on Depop for $30" vs stating them separately). The length bound (2-6 sentences) allows variation while preventing captions that are too short (just the item name) or too long (a paragraph that no one would post). Price and platform are essential info that should almost always appear.



---

## 5. Search respects price ceiling

For 5 different queries with a max_price specified, every listing in the search results has price ≤ max_price — 5 of 5 tries.

**Why this target:** 5 of 5 because price filtering is a simple numeric comparison with no ambiguity — an item either costs more than the ceiling or it doesn't. A failure here means the filter is broken, not that there's acceptable variation. This is critical because returning a $60 jacket when someone set max_price=50 breaks user trust immediately.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
