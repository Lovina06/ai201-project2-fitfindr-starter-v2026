"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    # Load all listings
    listings = load_listings()

    # Filter by max_price if provided
    if max_price is not None:
        listings = [lst for lst in listings if lst["price"] <= max_price]

    # Filter by size if provided
    if size is not None:
        size_lower = size.lower()
        filtered = []
        for lst in listings:
            lst_size_lower = lst["size"].lower()
            # Match if size appears as a word boundary to avoid "s" matching "us 9"
            # or "l" matching "xl". Check for exact match or as part of compound sizes.
            if size_lower in lst_size_lower.split() or size_lower == lst_size_lower:
                filtered.append(lst)
            elif "/" in lst_size_lower and size_lower in lst_size_lower.split("/"):
                # Handle sizes like "S/M" where we want "S" or "M" to match
                filtered.append(lst)
        listings = filtered

    # Score by keyword overlap with description
    desc_keywords = description.lower().split()
    scored = []
    for lst in listings:
        # Combine searchable text fields
        searchable = (
            lst["title"].lower() + " " +
            lst["description"].lower() + " " +
            " ".join(lst["style_tags"]) + " " +
            lst["category"].lower()
        )
        # Count keyword matches
        score = sum(1 for keyword in desc_keywords if keyword in searchable)
        if score > 0:
            scored.append((score, lst))

    # Sort by score descending
    scored.sort(reverse=True, key=lambda x: x[0])

    # Return top results, up to SEARCH_RESULT_LIMIT
    return [lst for score, lst in scored[:config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    # Check if wardrobe is empty
    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:
        # Empty wardrobe: ask for general styling advice
        prompt = f"""Suggest how to style this thrifted item in 1-2 outfit ideas.

Item: {new_item['title']}
Description: {new_item['description']}
Category: {new_item['category']}
Style tags: {', '.join(new_item['style_tags'])}
Colors: {', '.join(new_item['colors'])}

Give general styling advice since the user doesn't have a wardrobe profile yet."""
    else:
        # Non-empty wardrobe: suggest specific combinations
        wardrobe_list = "\n".join([
            f"- {item['name']} ({item['category']}): {', '.join(item['colors'])}"
            for item in wardrobe_items
        ])

        prompt = f"""Suggest 1-2 outfit combinations using this new thrifted item with pieces from the user's wardrobe.

New item: {new_item['title']}
Description: {new_item['description']}
Category: {new_item['category']}
Style tags: {', '.join(new_item['style_tags'])}
Colors: {', '.join(new_item['colors'])}

User's wardrobe:
{wardrobe_list}

Suggest specific combinations naming items from their wardrobe."""

    return generate(prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    # Guard against empty outfit
    if not outfit or not outfit.strip():
        return "Cannot create fit card: no outfit suggestion provided."

    # Build prompt for caption generation
    prompt = f"""Write a short, authentic social media caption (2-4 sentences) about this thrifted find.

Item: {new_item['title']}
Price: ${new_item['price']}
Platform: {new_item['platform']}
Description: {new_item['description']}
Outfit suggestion: {outfit}

Make it sound like a real person posting about their find, not a product description. Mention the price, platform, and capture the vibe. Be specific and enthusiastic."""

    return generate(prompt)
