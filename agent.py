"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.
    """
    session = new_session(query, wardrobe)
    trace.start_trace()

    try:
        # Parse query using the model to extract description, size, and max_price
        from generate import generate
        parse_prompt = f"""Extract search parameters from this query:
Query: "{query}"

Return ONLY a JSON object with these fields (use null if not mentioned):
- description: keywords describing the item
- size: size if mentioned (e.g., "M", "S/M", "W30 L30")
- max_price: maximum price as a number (no dollar sign)

Example: {{"description": "vintage graphic tee", "size": "M", "max_price": 30}}"""

        try:
            import json
            parsed_text = generate(parse_prompt)
            # Extract JSON from response (might have extra text)
            json_start = parsed_text.find('{')
            json_end = parsed_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                session["parsed"] = json.loads(parsed_text[json_start:json_end])
            else:
                # Fallback: basic parsing
                session["parsed"] = {
                    "description": query,
                    "size": None,
                    "max_price": None
                }
        except Exception:
            # Fallback to treating whole query as description
            session["parsed"] = {
                "description": query,
                "size": None,
                "max_price": None
            }

        trace.step("parse_query", inputs={"query": query}, returned=session["parsed"])

        # Call search_listings with parsed parameters (via MCP)
        from mcp_client import call_tool
        parsed = session["parsed"]
        search_inputs = {
            "description": parsed.get("description", query),
            "size": parsed.get("size"),
            "max_price": parsed.get("max_price"),
        }
        session["search_results"] = call_tool("search_listings", search_inputs)
        trace.step("search_listings (via MCP)", inputs=search_inputs, returned=session["search_results"])

        # BRANCH: Check if search returned results
        if not session["search_results"]:
            session["error"] = (
                "No items found matching your search. Try: broadening your description, "
                "increasing your price limit, or trying a different size."
            )
            trace.step("branch", note="empty search, stopping before suggest_outfit")
            return session

        # Select first item from results
        session["selected_item"] = session["search_results"][0]
        trace.step("select_item", returned=session["selected_item"])

        # Get outfit suggestion
        session["outfit_suggestion"] = suggest_outfit(
            new_item=session["selected_item"],
            wardrobe=session["wardrobe"]
        )
        wardrobe_size = len(session["wardrobe"].get("items", []))
        trace.step("suggest_outfit",
                  inputs={"item": session["selected_item"].get("title"), "wardrobe": f"{wardrobe_size} items"},
                  returned=session["outfit_suggestion"])

        # Create fit card
        session["fit_card"] = create_fit_card(
            outfit=session["outfit_suggestion"],
            new_item=session["selected_item"]
        )
        trace.step("create_fit_card", returned=session["fit_card"])

        return session

    except ModelUnavailable as e:
        session["error"] = (
            "Could not reach the model to process your request. "
            "Please check your API key in .env and try again."
        )
        trace.step("model_unavailable", note=f"API error: {str(e)}")
        return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
