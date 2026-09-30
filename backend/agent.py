from typing import Dict, Optional

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import google_search, AgentTool, ToolContext
from .tools import get_top_funds, get_fund_analysis, get_partner_info, get_visualization_data

# =========================================================
# 0. MEMORY & STATE TOOLS (SHARED BETWEEN API & AGENT)
# =========================================================

#   USER_PROFILES[session_id] = {"risk_profile": "Konservatif", ...}
USER_PROFILES: Dict[str, Dict[str, str]] = {}


def _get_session_id(tool_context: Optional[ToolContext], explicit_session_id: Optional[str]) -> str:
    """
    Decide which session id to use:
    - If explicit_session_id is given (e.g. from HTTP /risk-profile), use that.
    - Else if ToolContext has a session_id, use that.
    - Else fall back to 'default'.
    """
    if explicit_session_id:
        return explicit_session_id
    if tool_context is not None and hasattr(tool_context, "session_id"):
        sid = getattr(tool_context, "session_id")
        if sid:
            return str(sid)
    return "default"


def manage_user_profile(
    action: str,
    key: str,
    value: str = None,
    tool_context: ToolContext = None,
    session_id: str = None,
) -> str:
    """
    Manages user memory/preferences.

    Args:
        action: 'save' to store info, 'read' to get info, 'delete' to remove.
        key: The category (e.g., 'risk_profile').
        value: The information to save (only for 'save').
        tool_context: Filled automatically when called as an ADK tool.
        session_id: Optional manual override (used from HTTP API).
    """
    sid = _get_session_id(tool_context, session_id)
    session_state = USER_PROFILES.setdefault(sid, {})

    if action == "save":
        if not value:
            return "Error: Value required."
        session_state[key] = value
        return f"Saved {key} for session '{sid}': {value}"

    elif action == "read":
        return f"User {key}: {session_state.get(key, 'Unknown')}"

    elif action == "delete":
        session_state.pop(key, None)
        return f"Deleted {key} for session '{sid}'."

    return "Invalid action."


def get_user_context(
    tool_context: ToolContext = None,
    session_id: str = None,
) -> str:
    """
    Returns comprehensive user context including risk profile, investment goals, and preferences.
    Use this at the start of conversations to understand the user's situation.
    
    Args:
        tool_context: Filled automatically when called as an ADK tool.
        session_id: Optional manual override.
    
    Returns:
        Formatted string with user's complete profile information.
    """
    sid = _get_session_id(tool_context, session_id)
    session_state = USER_PROFILES.get(sid, {})
    
    if not session_state:
        return f"No profile found for session '{sid}'. User has not filled out their risk profile yet."
    
    # Build context string
    context_parts = [f"User Profile for session '{sid}':"]
    
    if "name" in session_state and session_state["name"]:
        context_parts.append(f"- Name: {session_state['name']}")
    
    # Check both keys - 'risk_level' is from form, 'risk_profile' is from agent
    if "risk_level" in session_state:
        context_parts.append(f"- Risk Profile: {session_state['risk_level']}")
    elif "risk_profile" in session_state:
        context_parts.append(f"- Risk Profile: {session_state['risk_profile']}")
    
    if "horizon" in session_state:
        context_parts.append(f"- Investment Horizon: {session_state['horizon']}")
    
    if "goal" in session_state:
        context_parts.append(f"- Investment Goal: {session_state['goal']}")
    
    return "\n".join(context_parts)


def get_user_dashboard_funds(
    tool_context: ToolContext = None,
    session_id: str = None,
) -> str:
    """
    Returns the funds that appear on the user's dashboard based on their risk profile.
    This shows what funds have been recommended to them.
    
    Args:
        tool_context: Filled automatically when called as an ADK tool.
        session_id: Optional manual override.
    
    Returns:
        Information about recommended funds for the user's risk profile.
    """
    sid = _get_session_id(tool_context, session_id)
    session_state = USER_PROFILES.get(sid, {})
    
    # Check both keys - 'risk_level' is from form, 'risk_profile' is from agent
    risk_level = session_state.get("risk_level", "").strip()
    if not risk_level:
        risk_level = session_state.get("risk_profile", "").strip()
    
    if not risk_level:
        return "User has not set a risk profile yet. Cannot determine recommended funds."
    
    # Normalize risk level - support both English and Indonesian
    risk_upper = risk_level.upper()
    normalized_risk = risk_level
    
    if risk_upper.startswith("CONS") or risk_upper.startswith("KON"):
        normalized_risk = "Konservatif"
    elif risk_upper.startswith("MOD"):
        normalized_risk = "Moderat"
    elif risk_upper.startswith("BAL") or risk_upper.startswith("BER"):
        normalized_risk = "Berimbang"
    elif risk_upper.startswith("AGG") or risk_upper.startswith("AGR"):
        normalized_risk = "Agresif"
    
    # Map risk levels to allowed fund types
    risk_to_funds = {
        "Konservatif": ["PU"],  # Pasar Uang only
        "Moderat": ["PU", "PT"],  # Pasar Uang + Pendapatan Tetap
        "Berimbang": ["PU", "PT", "CP"],  # + Campuran
        "Agresif": ["PU", "PT", "CP", "SH"],  # All types including Saham
    }
    
    allowed_types = risk_to_funds.get(normalized_risk, [])
    
    if not allowed_types:
        return f"Unknown risk level: {risk_level}"
    
    # Get top funds for each allowed type
    result_parts = [
        f"Dashboard funds for {normalized_risk} profile:",
        f"Allowed fund types: {', '.join(allowed_types)}",
        ""
    ]
    
    for fund_type in allowed_types:
        try:
            funds_data = get_top_funds(fund_type)
            # FIX: Change "funds" to "data" to match actual API response
            if "data" in funds_data and funds_data["data"]:
                result_parts.append(f"{fund_type} funds:")
                for fund in funds_data["data"][:3]:  # Top 3 per type
                    result_parts.append(f"  - {fund.get('mfName', 'Unknown')}")
                result_parts.append("")
        except Exception as e:
            result_parts.append(f"{fund_type}: Error loading - {str(e)}")
            continue
    
    return "\n".join(result_parts)


# =========================================================
# --- SPECIALIST AGENTS ---
# =========================================================

# Vertex AI open models via LiteLLM
kimi_llm = LiteLlm(
    model="vertex_ai/moonshotai/kimi-k2-thinking-maas"
)

gpt_oss_llm = LiteLlm(
    model="vertex_ai/openai/gpt-oss-120b-maas"
)

llama_4_maverick = LiteLlm(
    model="vertex_ai/meta/llama-4-maverick-17b-128e-instruct-maas"
)


# 1. DATABASE AGENT (Logic for Risk Profile Enforcement)
db_agent = Agent(
    name="db_agent",
    model="gemini-2.0-flash",
    description="Useful for finding top funds and rankings.",
    instruction="""
    You are the Database Specialist.
    - Your ONLY job is to fetch fund data using 'get_top_funds'.
    - CRITICAL: Extract the specific category (e.g., 'Saham', 'Pasar Uang'). 
      Do NOT pass "Reksadana" to the tool.
    """,
    tools=[get_top_funds],
)

# 2. SEARCH AGENT
search_agent = Agent(
    name="search_agent",
    model="gemini-2.0-flash",
    description="Useful for finding real-time market news, definitions, or facts not in the database.",
    instruction="You are the Market Researcher. Use google_search for external info.",
    tools=[google_search],
)

# 3. ANALYST AGENT
analyst_agent = Agent(
    name="analyst_agent",
    model="gemini-2.5-pro",
    description="Useful for deep analysis, explaining 'Why', or crowding/nuance analysis.",
    instruction="""
    You are a Senior Quantitative Analyst.
    - Use 'get_fund_analysis' to get the raw weights and scores.
    - If you see a term you don't know, consult 'search_agent'.
    - Explain the data by connecting 'Feature Weight' to 'Fund Value'.
    - In addition to the key features most related to the fund performance, you must explain the crowding score to a nuance of the fund's underlying.
    - For the crowding score analysis, you may back it up with information on the fund's current top holding by consulting to 'search_agent'
    - You may also analyse and assume the user risk profile based on the context input by the user, but if you need more information, you may ask further info to the user
    
    IMPORTANT: 'historical_alpha_top_vs_rest' is NOT a confidence score.
    It represents the **Historical Excess Return (Alpha)** of our top recommendations vs the market.
    You do not have to tell this to the user, just keep in your mind when trying to explain.
    """,
    tools=[get_fund_analysis, AgentTool(agent=search_agent)],
)

# 4. CHANNEL AGENT (your version, kept as-is)
channel_agent = Agent(
    name="channel_agent",
    model="gemini-2.0-flash",
    description="Useful for purchasing guides, partner promotions (Bibit/Bareksa), and benefits.",
    instruction="""
    You are the Channel Partner Guide.
    - Use 'get_partner_info' to find promos, sales, and benefits for Bibit, Bareksa, or Banks.
    - Guide the user on how to buy via these partners.
    - If user asks about "ongoing sales", check the partner info tools first, then 'google_search' if needed.
    """,
    tools=[get_partner_info, AgentTool(agent=search_agent)],
)

# 5. VISUALIZATION AGENT
viz_agent = Agent(
    name="viz_agent",
    model="gemini-2.0-flash",
    description="Useful for generating charts, graphs, or performance comparisons.",
    instruction="""
    You are the Data Visualization Expert.
    - If user wants to see "Performance stats" or "Top 10% vs Rest", call 'get_visualization_data(viz_type='performance_comparison')'.
    - If user wants "Head to Head" of specific funds, call 'get_visualization_data(viz_type='head_to_head', fund_names='...')'.
    - Output the data clearly and describe the chart to the user.
    """,
    tools=[get_visualization_data],
)

# --- ROOT AGENT ---
root_agent = Agent(
    name="GetU_Advisor",
    model="gemini-2.5-pro",
    description="Main interface.",
    instruction="""
    You are GetU Advisor, an AI-powered Indonesian mutual fund (Reksadana) advisor 
    created by PT. GET Kemajuan Bangsa. 
    
    CRITICAL IDENTITY RULES:
    - You ARE GetU Advisor. NEVER say you are Gemini, ChatGPT, Claude, or any other AI.
    - If asked "who are you?" or "siapa kamu?", respond: "Saya adalah GetU Advisor, 
      asisten investasi Reksadana yang dibuat oleh PT. GET Kemajuan Bangsa untuk 
      membantu investor Indonesia menemukan Reksadana yang sesuai."
    - Always introduce yourself as GetU Advisor when greeting users.
    
    RESPONSE FORMAT:
    - Use **bold** for fund names and important terms
    - Use bullet points (•) for lists
    - Use proper markdown formatting
    - Keep responses clear, structured, and professional
    - Add line breaks between sections for readability
    
    STEP 0: UNDERSTAND USER CONTEXT (ALWAYS DO THIS FIRST)
    - At the start of EVERY conversation, call 'get_user_context' to understand:
      * User's name and preferences
      * Their risk profile and investment goals  
      * Their investment horizon
    - Use this context to personalize ALL responses
    - If user has a name, greet them by name
    - Reference their specific situation when giving advice
    - If no profile exists, politely suggest they fill out the risk profile form
    
    STEP 1: HANDLE PROFILE & LANGUAGE
    - Always answer in the same language as the user.
    - When you refer to fund, please use either of these terms: Reksadana (Bahasa Indonesia), Fund or Mutual Fund (English)
    - If user says "I am Conservative/Aggressive", SAVE it using 'manage_user_profile(action="save", key="risk_profile", value=...)' immediately.
    - The user may express some of their behavior or preference like risk appetite, and target return (but you should educate if it does not makes sense),
      you consult with "analyst_agent" to analyse and assume what could be the risk profile and recommend the funds accordingly.
    - Everytime you give or list mutual fund recommendation, please also consult with "viz_agent" to show 'performance_comparison', Returns the Alpha (OOS Reliability) stats. This shows how much better the Top 10% mutual funds are compared to the Rest 90%.
      In addition to alpha, also show the recommended funds stats againts the average of the rest 90% 

    STEP 2: GATEKEEPING (RISK CHECK) & DASHBOARD AWARENESS
    - If user asks for a recommendation ("Best Fund", "Top Saham"):
      1. First call 'get_user_context' to check their risk profile.
      2. If no profile -> ASK user to fill out risk profile form. STOP.
      3. If profile exists -> CHECK if the request matches:
         - Konservatif: Only 'Pasar Uang' (PU) allowed.
         - Moderat: Only 'PU' & 'Pendapatan Tetap' (PT) allowed.
         - Berimbang: 'PU', 'PT', 'Campuran' (CP) allowed.
         - Agresif: All allowed.
      4. If BLOCKED -> Refuse politely ("Based on your [profile], I cannot recommend [type].").
      5. If ALLOWED -> Call 'get_user_dashboard_funds' to see what's already recommended, then call `db_agent` if needed.
    
    - When discussing funds, reference their dashboard:
      * "I see you have [Fund X] in your dashboard..."
      * "Based on your [profile] profile, your dashboard shows..."
      * "Let me explain why [Fund Y] was recommended to you..."

    STEP 3: ROUTING (Non-Recommendation Requests)
    - 'search_agent': Market News.
    - 'analyst_agent': Deep Analysis ("Why is X good?").
    - 'channel_agent': Buying info, Promos.
    - 'viz_agent': Charts, Stats.
    """,
    tools=[
        get_user_context,  # NEW: Get comprehensive user profile
        get_user_dashboard_funds,  # NEW: Get user's recommended funds
        AgentTool(agent=db_agent),
        AgentTool(agent=search_agent),
        AgentTool(agent=analyst_agent),
        AgentTool(agent=channel_agent),
        AgentTool(agent=viz_agent),
        manage_user_profile,  # Legacy tool for backwards compatibility
    ],
)
