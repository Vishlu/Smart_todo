"""
Install dependencies:
    pip install google-generativeai textblob
    python -m textblob.download_corpora
"""

import json
import re
from string import Template
from datetime import datetime, timedelta, timezone
from textblob import TextBlob  # For sentiment analysis

import google.generativeai as genai

# ----------------------------
# CONFIGURE GEMINI
# ----------------------------
genai.configure(api_key="AIzaSyDWyYmlvq0xZImhrL43JAIkqKeiwOpv30Y")

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# ----------------------------
# ENHANCED PROMPT TEMPLATE
# ----------------------------
PROMPT_TMPL = Template(r"""
You are an advanced task management assistant with context analysis capabilities.
Analyze the given context and source, then return a STRICT JSON object with:

1) title (short, clear)
2) description (detailed with key requirements)
3) category (Work, Academic, Personal, etc.)
4) deadline (structured as:
   - date: "YYYY-MM-DD HH:MM" 
   - text: natural language description)
5) status (Pending/On-Progress/Done)
6) priority_score (1-10)
7) sentiment_analysis (positive/neutral/negative)
8) keywords (list of important terms)
9) time_required (estimated hours needed)
10) best_time (suggested time window for execution)
11) dependencies (list of prerequisite tasks if any)

Current datetime (IST): ${now_ist}
Assume timezone: Asia/Kolkata (UTC+05:30).

Example Output:
{
  "title": "Complete Project Report",
  "description": "Finalize the quarterly project report including all metrics and submit to manager",
  "category": "Work",
  "deadline": {
    "date": "2025-08-16 14:00",
    "text": "tomorrow by 2 PM"
  },
  "status": "Pending",
  "priority_score": 8,
  "sentiment_analysis": "neutral",
  "keywords": ["report", "metrics", "submission"],
  "time_required": 4,
  "best_time": "morning (9 AM - 12 PM)",
  "dependencies": ["gather metrics", "review draft"]
}

Now process this task:

Context: ${context}
Source: ${source}

Rules:
- RETURN VALID JSON ONLY (no markdown, no extra text)
- Use double quotes for all strings
- Include ALL fields (set to empty/nulls if unknown)
- For deadlines with no time, use "00:00"
- Estimate time_required realistically
- Suggest best_time based on task type and urgency
""")


# ----------------------------
# ENHANCED HELPER FUNCTIONS
# ----------------------------
def now_ist_str():
    """Return current IST time formatted as 'YYYY-MM-DD HH:MM'."""
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M")

def analyze_sentiment(text: str) -> str:
    """Perform basic sentiment analysis using TextBlob"""
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return "positive"
    elif analysis.sentiment.polarity < -0.1:
        return "negative"
    return "neutral"

def extract_keywords(text: str) -> list:
    """Extract important keywords using simple NLP"""
    blob = TextBlob(text)
    nouns = [word.lower() for word, tag in blob.tags if tag.startswith('NN')]
    verbs = [word.lower() for word, tag in blob.tags if tag.startswith('VB')]
    return list(set(nouns + verbs))[:5]  # Return top 5 unique keywords

def build_prompt(context: str, source: str) -> str:
    return PROMPT_TMPL.substitute(
        context=context.strip(),
        source=source.strip(),
        now_ist=now_ist_str(),
    )

def extract_json(text: str):
    """Robust JSON extraction with improved error handling"""
    try:
        # First try direct parse
        text = text.strip()
        if text.startswith('{') and text.endswith('}'):
            return json.loads(text)
        
        # Handle code fences if present
        fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
        if fenced:
            return json.loads(fenced.group(1))
        
        # Fallback: find first complete JSON object
        first = text.find('{')
        last = text.rfind('}')
        if first != -1 and last != -1:
            return json.loads(text[first:last+1])
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
    return None

def normalize_result(d: dict) -> dict:
    """Enhanced normalization with new fields"""
    if not isinstance(d, dict):
        return {}
    
    # Handle priority_score correctly
    try:
        priority_score = int(d.get("priority_score", 5))
        priority_score = max(1, min(10, priority_score))
    except (ValueError, TypeError):
        priority_score = 5
    
    # Handle time_required correctly
    try:
        time_required = float(d.get("time_required", 1))
        time_required = max(0, time_required)
    except (ValueError, TypeError):
        time_required = 1
    
    # Ensure all fields exist with defaults
    out = {
        "title": d.get("title", "").strip(),
        "description": d.get("description", "").strip(),
        "category": d.get("category", "Uncategorized").strip(),
        "deadline": {
            "date": d.get("deadline", {}).get("date", ""),
            "text": d.get("deadline", {}).get("text", "")
        },
        "status": d.get("status", "Pending").strip(),
        "priority_score": priority_score,
        "sentiment_analysis": d.get("sentiment_analysis", "neutral").lower(),
        "keywords": list(set(d.get("keywords", [])))[:5],  # Ensure unique, max 5
        "time_required": time_required,
        "best_time": d.get("best_time", "Anytime").strip(),
        "dependencies": list(set(d.get("dependencies", [])))  # Unique dependencies
    }
    
    # Validate status
    valid_status = {"pending", "on-progress", "done"}
    out["status"] = out["status"].lower().replace(" ", "-")
    if out["status"] not in valid_status:
        out["status"] = "pending"
    
    # Add sentiment analysis if missing
    if not out["sentiment_analysis"] or out["sentiment_analysis"] == "neutral":
        out["sentiment_analysis"] = analyze_sentiment(out["description"])
    
    # Add keywords if missing
    if not out["keywords"]:
        out["keywords"] = extract_keywords(out["title"] + " " + out["description"])
    
    return out

def analyze_task(context: str, source: str) -> dict | None:
    """Enhanced task analysis with fallback logic"""
    prompt = build_prompt(context, source)
    try:
        convo = model.start_chat(history=[])
        convo.send_message(prompt)
        raw = convo.last.text
        data = extract_json(raw)
        
        if not data:
            print("\n[WARN] Model returned invalid JSON. Attempting repair...")
            # Fallback to simpler analysis if JSON parsing fails
            return {
                "title": context[:50] + ("..." if len(context) > 50 else ""),
                "description": f"Task received via {source}: {context}",
                "category": "Uncategorized",
                "deadline": {"date": "", "text": "unspecified"},
                "status": "Pending",
                "priority_score": 5,
                "sentiment_analysis": analyze_sentiment(context),
                "keywords": extract_keywords(context),
                "time_required": 1,
                "best_time": "Anytime",
                "dependencies": []
            }
            
        return normalize_result(data)
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {str(e)}")
        return None

def print_form(result: dict):
    """Enhanced output formatting with new fields"""
    print("\n===== ENHANCED TASK ANALYSIS =====")
    print(f"Title:         {result.get('title')}")
    print(f"Description:   {result.get('description')}")
    print(f"Category:      {result.get('category')}")
    print(f"Status:        {result.get('status').capitalize()}")
    print(f"Priority:      {result.get('priority_score')}/10")
    print(f"Sentiment:     {result.get('sentiment_analysis').capitalize()}")
    
    deadline = result.get('deadline', {})
    print(f"\nDeadline:      {deadline.get('text', 'Not specified')}")
    if deadline.get('date'):
        print(f"               ({deadline.get('date')})")
    
    print(f"\nTime Required: ~{result.get('time_required', 0)} hours")
    print(f"Best Time:     {result.get('best_time')}")
    
    if result.get('keywords'):
        print(f"\nKeywords:      {', '.join(result.get('keywords', []))}")
    
    if result.get('dependencies'):
        print(f"\nDependencies:  {', '.join(result.get('dependencies', []))}")

# ----------------------------
# MAIN EXECUTION
# ----------------------------
if __name__ == "__main__":
    print("==== AI TASK ANALYZER PRO ====")
    print("Now with sentiment analysis, scheduling suggestions, and enhanced deadline tracking!\n")
    
    context = input("Enter your task/context: ").strip()
    while not context:
        print("Please enter a valid task description")
        context = input("Enter your task/context: ").strip()

    sources = ["Note", "WhatsApp", "E-mail", "Calendar", "Other"]
    print("\nSelect Source:")
    for i, s in enumerate(sources, 1):
        print(f"{i}. {s}")
    
    while True:
        try:
            choice = int(input("Enter choice (1-5): ").strip())
            if 1 <= choice <= 5:
                source = sources[choice - 1]
                break
        except ValueError:
            pass
        print("Invalid choice. Please enter a number between 1-5.")

    print("\nAnalyzing your task...")
    result = analyze_task(context, source)

    if result:
        print_form(result)
    else:
        print("\n[ERROR] Could not analyze the task. Please try again.")