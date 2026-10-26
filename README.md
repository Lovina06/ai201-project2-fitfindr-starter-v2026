# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr helps users discover thrifted clothing items and style them with their existing wardrobe. A user types a natural language query describing what they're looking for (e.g., "vintage graphic tee under $30 size M"), and the system searches through secondhand listings, suggests 1-2 outfit combinations using items they already own, and generates a social media-ready caption about the find. If no items match the search, the system provides helpful suggestions for broadening the query instead of proceeding with empty results.



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listings database for clothing items matching a text description, optionally filtered by size and maximum price.
- **Inputs:** `description` (str), `size` (str | None), `max_price` (float | None)
- **Returns:** A list of listing dicts (each with id, title, description, category, style_tags, size, condition, price, colors, brand, platform), sorted best match first, limited to config.SEARCH_RESULT_LIMIT.
- **When it has nothing:** Returns an empty list `[]` (not None, not an exception).

### `suggest_outfit`

- **What it does:** Calls the model to suggest one or two outfit combinations using the thrifted item and the user's existing wardrobe.
- **Inputs:** `new_item` (dict - a listing dict), `wardrobe` (dict with 'items' key holding a list of wardrobe item dicts)
- **Returns:** A non-empty string with outfit suggestions (specific combinations if wardrobe has items, general styling advice if wardrobe is empty).
- **When it has nothing:** Never returns empty - if wardrobe is empty, returns general styling advice for the item instead of specific combinations.

### `create_fit_card`

- **What it does:** Calls the model to generate a social media caption (2-4 sentences) about the thrifted find, incorporating the outfit suggestion and item details.
- **Inputs:** `outfit` (str - the outfit suggestion from suggest_outfit), `new_item` (dict - the listing dict)
- **Returns:** A 2-4 sentence caption string that reads like a real social post, mentions the item, price, and platform, and captures the vibe.
- **When it has nothing:** If outfit is empty or whitespace, returns a descriptive error message rather than crashing (e.g., "Cannot create fit card: no outfit suggestion provided").

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If search_listings returns an empty list, put a message in the session explaining what to try (broader description, higher max_price, different size) and stop before calling suggest_outfit. Otherwise, take the first result from the list, pass it to suggest_outfit with the user's wardrobe, then pass the outfit suggestion and item to create_fit_card, storing all results in the session.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Asking the model to extract description, size, and max_price from the user's natural language query.

**What moves through the session:** query → parsed (description/size/max_price) → search_results → selected_item (first result) → wardrobe → outfit_suggestion → fit_card. If search_results is empty, error is set and flow stops before selected_item.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are 2 outfit combinations using your new Y2K butterfly baby tee...
  
### Outfit 1: Classic Y2K Streetwear
* Top: Y2K Butterfly Print Baby Tee
* Bottoms: Baggy straight-leg jeans (dark wash)
* Outerwear: Black cropped zip hoodie
* Shoes: Chunky white sneakers
* Accessories: Black crossbody bag

### Outfit 2: Casual Vintage Contrast
* Top: Y2K Butterfly Print Baby Tee
* Bottoms: Wide-leg khaki trousers
* Accessories: Brown leather belt, Vintage black denim jacket
* Shoes: Black combat boots

  Fit card: Found the ultimate Y2K baby tee on Depop for just $18 and I am literally 
  obsessed with this butterfly print. 🦋 It's giving major early 2000s energy, especially 
  styled with some baggy denim or chunky combat boots. Snagged a medium that fits more 
  like a small, so it's the exact right kind of cropped. ✨
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; import json; results = search_listings('graphic tee', max_price=30); print(f'Found {len(results)} results'); print(json.dumps(results[0] if results else {}, indent=2))"

Found 7 results
{
  "id": "lst_002",
  "title": "Y2K Baby Tee — Butterfly Print",
  "description": "Super cute early 2000s baby tee with butterfly graphic...",
  "category": "tops",
  "style_tags": ["y2k", "vintage", "graphic tee", "cottagecore"],
  "size": "S/M",
  "condition": "excellent",
  "price": 18.0,
  "colors": ["white", "pink", "purple"],
  "brand": null,
  "platform": "depop"
}
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Here are two outfit combinations using your new vintage Levi's 501s and pieces from your existing wardrobe:

### Look 1: Casual Streetwear & Monochrome Contrast
* Top: White ribbed tank top
* Outerwear: Vintage black denim jacket (worn open)
* Shoes: Chunky white sneakers
* Accessories: Black crossbody bag

### Look 2: Cozy Retro Layers
* Top: Oversized grey crewneck sweatshirt
* Shoes: Black combat boots
* Accessories: Brown leather belt, black crossbody bag
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('Pair with baggy straight-leg jeans and chunky white sneakers for effortless streetwear vibes', load_listings()[0]))"

Still can't believe I scored these vintage Levi's 501s on Depop for just $38! The medium wash and natural knee fading are literally the definition of the perfect broken-in denim. Can't wait to style them with a chunky white sneaker and a baggy tee for the ultimate effortless streetwear fit.
```

```
$ python -c "from tools import create_fit_card; ..."

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1: Size matching in search_listings**

- *What I asked for:* Implement size filtering in search_listings to match user's size query against listing sizes.
- *What came back:* Claude Code suggested simple substring matching (`if size_lower in lst_size_lower`), but warned that this would incorrectly match "s" in "us 9" or "l" in "xl", causing shoes to appear when someone asks for a small top.
- *What I changed:* Added word-boundary aware matching using `.split()` to check if the size appears as a standalone token, plus special handling for compound sizes like "S/M" by splitting on "/". This prevents false matches while still catching valid compound sizes.

**Moment 2: Empty wardrobe path in suggest_outfit**

- *What I asked for:* Implement suggest_outfit to generate outfit suggestions using the item and wardrobe.
- *What came back:* Claude Code implemented the function but initially focused only on the non-empty wardrobe case. The TODO comment explicitly said "It may be empty. Handle that" and warned that "Unit 4 has you trigger the empty wardrobe on purpose."
- *What I changed:* Added a check for `wardrobe.get("items", [])` and branched on whether it's empty. Empty wardrobe gets a different prompt asking for general styling advice rather than specific combinations, ensuring the function never returns empty string and handles both paths gracefully.

**Moment 3 (Unit 4): MCP trace integration in agent.py**

- *What I asked for:* Add trace.step() calls throughout run_agent() to make the MCP call visible in the trace output.
- *What came back:* Claude Code suggested adding trace.step() after each major operation, including a specific step for "search_listings (via MCP)" to distinguish the MCP call from direct tool calls. It also suggested adding a branch trace step to show when the loop stops early.
- *What I changed:* Implemented all trace.step() calls exactly as suggested, with descriptive labels like "search_listings (via MCP)" that clearly identify the integration point. The trace now shows the exact 5-step happy path and 3-step empty-search path, making the branch logic immediately visible in output.

**Moment 4 (Unit 4): ModelUnavailable exception handling**

- *What I asked for:* Handle the ModelUnavailable exception that can occur when the Gemini API is overloaded or unreachable.
- *What came back:* Claude Code wrapped the entire run_agent() flow in a try-except block catching ModelUnavailable, setting session["error"] with a helpful message about checking the API key, and adding a trace.step() call to record the failure. This caught the real 503 error that occurred during evaluation Try 3.
- *What I changed:* Kept the implementation as-is. The error message is user-friendly (mentions .env and "try again"), the session state stays consistent (error set, later fields remain None), and the trace clearly shows "model_unavailable" in the step log. This is exactly the defensive programming Unit 4 asked for.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all tools | 4 of 5 | PASS | PASS | FAIL* | PASS | PASS | MET (4/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item ID preserved through session | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card has price & platform | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search respects price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

*Try 3 failed due to 503 ModelUnavailable error (API overloaded), error handler worked correctly.

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
# From run_eval.py → run_agent() → results/run_2026-10-26_1844_before.md
# Criterion 4, Try 1: "flannel shirt under $25"

Selected item: Flannel Shirt — Red Plaid ($22.0, thredUp)
Search returned 5 results

Outfit suggestion:
Here are two outfit combinations using your new red plaid flannel shirt...

### Outfit 1: Casual Weekend Layers
* Top: Red Plaid Flannel (worn open over white ribbed tank)
* Bottoms: Baggy straight-leg jeans (dark wash)
* Shoes: Chunky white sneakers
* Accessories: Black crossbody bag

### Outfit 2: Moody Grunge Vibes
* Top: Red Plaid Flannel (buttoned up)
* Bottoms: Wide-leg khaki trousers
* Outerwear: Vintage black denim jacket
* Shoes: Black combat boots

Fit card:
Scored this perfect red plaid flannel on thredUp for just $22 and it's giving major 90s grunge energy. Already planning to layer it over a white tank with my baggiest jeans and chunky sneakers for the ultimate casual weekend vibe. If you sleep on this one, that's on you! 🍂✨
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all 3 tools | 4/5 | **MET** (4/5) | Counted tries where session had fit_card filled (not None). Try 3 hit ModelUnavailable 503 error, other 4 completed all tools. |
| 2 | Impossible query stops before suggest_outfit | 5/5 | **MET** (5/5) | Checked that session["error"] was set and session["fit_card"] was None in all 5 tries. All stopped at the branch with helpful message. |
| 3 | Item ID preserved through session state | 5/5 | **MET** (5/5) | Verified selected_item ID matches the item shown in fit card. All 5 tries selected "Vintage Levi's 501" with consistent ID lst_001. |
| 4 | Fit card mentions price & platform | 4/5 | **MET** (5/5) | Searched fit card text for "$" and platform name. All 5 tries mentioned "$22" and "thredUp" explicitly. Exceeded target. |
| 5 | Search respects price ceiling | 5/5 | **MET** (5/5) | Checked max_price in parsed query against all returned item prices. "under $20" returned items at $18, $16, $15. "under $40" returned items at $38, $35, $28. All within limits. |

**Diagnoses**

No criteria were missed. All five met or exceeded their targets.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  dict with keys: item, wardrobe
      out: Here are 2 outfit combinations using your new Y2K butterfly baby tee and pieces from your wardrobe...
[5] create_fit_card
      out: Found the ultimate Y2K baby tee on Depop for just $18 and I am literally obsessed...
```

**Empty search**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch
      →    empty search, stopping before suggest_outfit
```

**On the MCP move:** Changed agent.py to call `mcp_client.call_tool("search_listings", {...})` instead of the direct `search_listings(...)` function call. Registered the tool in mcp_server.py with @mcp.tool() decorator, full description, and typed inputs. Behavior is identical - agent produces the same results through MCP as it did with direct calls. The MCP call is clearly visible in the trace as step [2] "search_listings (via MCP)".



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

Added sentence-count validation to `create_fit_card()` in tools.py. The function now counts sentence-ending punctuation (. ! ?) and if the result is outside the 2-4 sentence spec, it makes a second generate() call with an explicit constraint reminder. This tightens Criterion 4 from just checking that price/platform are mentioned to also validating the format meets the documented spec.

**Which failure it was meant to fix:**

This wasn't fixing a failure (all criteria passed), but rather preventing future regression. The "before" run had fit cards that technically met Criterion 4 (mentioned price and platform) but some were verbose or rambling. The spec says "2-4 sentences" and the prompt asks for that, but without validation the model sometimes ignores it. This change enforces the constraint programmatically.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item ID preserved through session | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card has price & platform | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search respects price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->

The sentence-count validation had a mixed impact:

**What improved:** Criterion 1 went from 4/5 to 5/5. The "before" run hit a ModelUnavailable 503 error on Try 3, but the "after" run had no API failures. This is unrelated to my code change — it's just API availability variance between the two runs.

**What stayed the same:** Criteria 2-5 remained at 5/5 PASS. The validation didn't break anything, which is good.

**What the validation actually did:** Looking at fit card character counts in the output (237-366 chars in "after" vs similar range in "before"), the sentence validator didn't noticeably tighten length. The model already respects the 2-4 sentence constraint most of the time. The validation is defensive programming that would catch outliers, but this dataset didn't trigger any retries.

**Verdict:** The improvement was "defensive" rather than "corrective" — it prevents future regression on a spec the model already follows, rather than fixing an observed failure. In a real system this is valuable (catches edge cases before they reach users), but in this evaluation it didn't change measurable outcomes.



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

**No criteria missed**, but areas for future improvement:

1. **Query parsing brittleness**: Currently uses a model call to extract description/size/max_price, with a brittle JSON extraction that falls back to treating the whole query as description. A regex-based parser would be faster, cheaper, and more reliable. Stopped here because the model-based approach passes all tests and handling malformed JSON properly would require more error cases than the assignment scope covers.

2. **Size matching edge cases**: The word-boundary approach handles "S/M" and avoids "s" in "us 9", but doesn't handle compound sizes like "W30 L32" or size ranges like "6-8". Would need a size normalization layer to catch these. Stopped because the test data doesn't include these formats and building a comprehensive size parser is its own project.

3. **Fit card variation**: Even with temperature > 0 and cache disabled, fit cards for the same item across multiple tries can be similar in structure (opening enthusiasm + specific detail + call to action). The sentence-count validator I added in the improvement helps with format, but doesn't enforce variety. Would need to track previously generated cards in session state and explicitly prompt for differentiation. Stopped because Criterion 4 targets 4/5, not 5/5, accepting that some similarity is expected when describing the same item.



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
