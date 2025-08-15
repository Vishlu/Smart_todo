# API/utils_ai.py
import os
import json
import re
from datetime import datetime, timedelta


def _most_recent_text(ctx_entries):
    """
    Return the text of the most recent context entry.
    ctx_entries should be ordered newest first.
    """
    if not ctx_entries:
        return ""
    try:
        first = ctx_entries[0]
    except Exception:
        first = None
        for item in ctx_entries:
            first = item
            break
    return (getattr(first, "content", str(first)) or "").strip()


def _generate_short_title(text):
    """Generate a short title from the first sentence/words of text."""
    if not text:
        return ""
    t = " ".join(text.split())
    sentences = re.split(r'[.!?]\s+', t)
    base = sentences[0] if sentences and sentences[0] else t
    words = base.split()
    title = " ".join(words[:8])
    return title.capitalize() if title else base[:40].strip()


def _heuristic_ai(title, desc, ctx_entries):
    """Fallback local AI heuristic for suggestions."""
    recent_text = _most_recent_text(ctx_entries)
    combined = f"{(title or '')} {(desc or '')} {recent_text}".strip().lower()

    # Priority score
    score = 3.0
    if any(k in combined for k in ["urgent", "asap", "tomorrow", "deadline", "due"]):
        score += 4
    if len(desc or "") > 200:
        score += 1.5
    score = min(score, 10.0)

    # Deadline heuristic
    days = max(1, int(7 - int(score // 1)))
    suggested_deadline = (datetime.now() + timedelta(days=days)).date().isoformat()

    # Category
    category = "General"
    if any(w in combined for w in ["meeting", "slides", "client"]):
        category = "Work / Meetings"
    elif any(w in combined for w in ["bug", "deploy", "api", "fix", "issue"]):
        category = "Work / Dev"
    elif any(w in combined for w in ["email", "reply", "inbox", "compose"]):
        category = "Email"
    elif any(w in combined for w in ["buy", "grocer", "shopping", "purchase"]):
        category = "Personal / Shopping"

    # Suggested title
    suggested_title = (title or "").strip() or _generate_short_title(recent_text) or _generate_short_title(desc or "")

    # Enhanced description
    enhanced_description = (desc or "").strip()
    if not enhanced_description:
        if recent_text:
            first_sentence = re.split(r'[.!?]\s+', recent_text)[0]
            enhanced_description = first_sentence[:200].strip()
        else:
            enhanced_description = suggested_title or "No description provided."
    if len(enhanced_description) > 500:
        enhanced_description = enhanced_description[:500].rsplit(" ", 1)[0] + "..."

    return {
        "suggested_title": suggested_title,
        "priority_score": round(score, 2),
        "suggested_deadline": suggested_deadline,
        "category": category,
        "enhanced_description": enhanced_description
    }


def get_ai_suggestions_with_gemini(title, desc, ctx_entries):
    """
    Use Gemini AI to generate smart task suggestions.
    Falls back to heuristic if Gemini fails.
    """
    try:
        import google.generativeai as genai

        # Load API key
        api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyDWyYmlvq0xZImhrL43JAIkqKeiwOpv30Y"
        if not api_key:
            raise RuntimeError("No GEMINI_API_KEY found in environment.")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        recent_text = _most_recent_text(ctx_entries)

        prompt = f"""
You are a concise task assistant. Use ONLY the most recent context below.

Return ONLY a valid JSON object with:
- suggested_title (short, <= 8 words)
- priority_score (0-10, number)
- suggested_deadline (YYYY-MM-DD)
- category (short label)
- enhanced_description (<= 200 chars)

TASK_TITLE: {title}
TASK_DESCRIPTION: {desc}
MOST_RECENT_CONTEXT: {recent_text}
"""

        resp = model.generate_content(prompt)
        text = resp.text.strip()
        data = json.loads(text)

        return {
            "suggested_title": data.get("suggested_title") or title or _generate_short_title(recent_text),
            "priority_score": float(data.get("priority_score", 5)),
            "suggested_deadline": data.get("suggested_deadline") or datetime.now().date().isoformat(),
            "category": data.get("category", "General"),
            "enhanced_description": data.get("enhanced_description", desc or "") or ""
        }

    except Exception as e:
        print("[Gemini fallback] error:", e)
        return _heuristic_ai(title, desc, ctx_entries)












# # API/utils_ai.py
# import os
# import json
# import re
# from datetime import datetime, timedelta

# def _most_recent_text(ctx_entries):
#     """
#     Return the content text of the most recent context entry (or "" if none).
#     ctx_entries may be a list or queryset already ordered with newest first.
#     """
#     if not ctx_entries:
#         return ""
#     try:
#         first = ctx_entries[0]
#     except Exception:
#         # fallback if not indexable
#         first = None
#         for item in ctx_entries:
#             first = item
#             break
#     return (first.content if first else "").strip()


# def _generate_short_title(text):
#     """
#     Heuristic to create a short task title from a sentence or first few words.
#     """
#     if not text:
#         return ""
#     # remove newlines and extra spaces
#     t = " ".join(text.split())
#     # take first sentence if present
#     sentences = re.split(r'[.!?]\s+', t)
#     base = sentences[0] if sentences and sentences[0] else t
#     words = base.split()
#     title = " ".join(words[:8])  # up to 8 words
#     # Capitalize first char
#     if title:
#         return title[0].upper() + title[1:]
#     return base[:40].strip()


# def get_ai_suggestions(title, desc, ctx_entries):
#     """
#     Simple local heuristic that:
#       - Uses ONLY the most recent context (not top 3)
#       - Produces suggested_title, enhanced_description, category, suggested_deadline, priority_score
#     """
#     recent_text = _most_recent_text(ctx_entries)
#     combined = f"{(title or '')} {(desc or '')} {recent_text}".strip().lower()

#     # Priority scoring heuristic
#     score = 3.0
#     if any(k in combined for k in ["urgent","asap","tomorrow","deadline","due"]):
#         score += 4
#     if len(desc or "") > 200:
#         score += 1.5
#     score = min(score, 10.0)

#     # deadline: closer for higher score
#     days = max(1, int(7 - int(score // 1)))
#     suggested_deadline = (datetime.now() + timedelta(days=days)).date().isoformat()

#     # category heuristics (use recent_text + title/desc)
#     category = "General"
#     if any(w in combined for w in ["meeting","slides","client"]):
#         category = "Work / Meetings"
#     elif any(w in combined for w in ["bug","deploy","api","fix","issue"]):
#         category = "Work / Dev"
#     elif any(w in combined for w in ["email","reply","inbox","compose"]):
#         category = "Email"
#     elif any(w in combined for w in ["buy","grocer","shopping","purchase"]):
#         category = "Personal / Shopping"

#     # suggested title: prefer given title, else generate from most recent context, else from desc
#     suggested_title = (title or "").strip()
#     if not suggested_title:
#         suggested_title = _generate_short_title(recent_text) or _generate_short_title(desc or "")

#     # enhanced description: prefer given desc, else short summary from the most recent context
#     enhanced_description = (desc or "").strip()
#     if not enhanced_description:
#         if recent_text:
#             # take first sentence or up to 160 chars
#             first_sentence = re.split(r'[.!?]\s+', recent_text)[0]
#             enhanced_description = first_sentence[:200].strip()
#         else:
#             enhanced_description = suggested_title or "No description provided."

#     # Keep enhanced_description short — do NOT dump the whole context
#     if len(enhanced_description) > 500:
#         enhanced_description = enhanced_description[:500].rsplit(" ", 1)[0] + "..."

#     return {
#         "suggested_title": suggested_title,
#         "priority_score": round(score, 2),
#         "suggested_deadline": suggested_deadline,
#         "category": category,
#         "enhanced_description": enhanced_description
#     }


# def get_ai_suggestions_with_gemini(title, desc, ctx_entries):
#     """
#     Gemini path: pass ONLY the most recent context to the model and request a JSON
#     with suggested_title, priority_score, suggested_deadline, category, enhanced_description.

#     Falls back to local heuristic on any error.
#     """
#     try:
#         import google.generativeai as genai
#         api_key = os.getenv("AIzaSyDWyYmlvq0xZImhrL43JAIkqKeiwOpv30Y")
#         if not api_key:
#             raise RuntimeError("No GEMINI_API_KEY in environment")

#         genai.configure(api_key=api_key)
#         model = genai.GenerativeModel("gemini-1.5-flash")

#         recent_text = _most_recent_text(ctx_entries)

#         prompt = f"""
# You are a concise task assistant. Use ONLY the MOST RECENT context (below) to suggest a single task.
# Return ONLY a valid JSON object (no commentary) with these keys:
# - suggested_title (short, <= 8 words)
# - priority_score (0-10, number)
# - suggested_deadline (YYYY-MM-DD)
# - category (one short label)
# - enhanced_description (short summary, <= 200 chars)

# TASK_TITLE: {title}
# TASK_DESCRIPTION: {desc}
# MOST_RECENT_CONTEXT: {recent_text}
# """

#         resp = model.generate_content(prompt)
#         text = resp.text.strip()

#         # Parse model JSON output safely
#         data = json.loads(text)
#         return {
#             "suggested_title": data.get("suggested_title") or title or _generate_short_title(recent_text),
#             "priority_score": float(data.get("priority_score", 5)),
#             "suggested_deadline": data.get("suggested_deadline") or datetime.now().date().isoformat(),
#             "category": data.get("category", "General"),
#             "enhanced_description": data.get("enhanced_description", desc or "") or (data.get("enhanced_description") or "")
#         }
#     except Exception as e:
#         # If anything fails, fallback to heuristic
#         # (print for debug in dev)
#         print("[Gemini fallback] error:", e)
#         return get_ai_suggestions(title, desc, ctx_entries)

