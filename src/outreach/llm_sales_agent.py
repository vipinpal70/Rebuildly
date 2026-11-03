import json
import logging
import httpx
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

SALES_AGENT_SYSTEM_PROMPT = """You are an elite B2B Sales Director & High-Converting Copywriter specializing in web design & digital modernization outreach to local business owners (e.g. Dentists, Lawyers, Clinics, Service Providers).

Your goal: Generate highly personalized, human-sounding, zero-spam outreach copy across 4 channels based on technical audit data and modern site previews.

Rules for copy generation:
1. LinkedIn Connection Note: MUST be under 300 characters. Conversational, complimentary, referencing their business name and a specific technical/mobile improvement opportunity. No hard sales pitch.
2. Cold Email: Plain-text format ONLY. Subject line must be short, curiosity-driven (3-5 words). Body must be concise (120-180 words), highlighting 2 specific technical audit gaps (e.g., page speed, mobile UX, missing online booking) and introducing their bespoke live preview website. No spam trigger words (avoid "guaranteed", "free offer", "act fast").
3. WhatsApp / SMS Draft: 2-3 short conversational sentences asking if they had a moment to review the modern preview site created for them.
4. Call Script Notes: Structured bullet points for a 60-second phone call: Opener/Hook, Technical audit findings, Preview site callout, Closing question.

Return ONLY a valid JSON object matching this exact schema:
{
  "linkedin_draft": "string",
  "email_subject_draft": "string",
  "email_body_draft": "string",
  "whatsapp_draft": "string",
  "call_script_notes": "string"
}
"""


async def generate_sales_copy_with_llm(
    business_name: str,
    category: str,
    city: str,
    website: Optional[str],
    google_rating: Optional[float],
    review_count: Optional[int],
    findings: list,
    preview_url: str,
    fallback_drafts: Dict[str, str]
) -> Dict[str, str]:
    """Generates hyper-personalized 4-channel sales copy using Claude API / Anthropic LLM.
    If API key is unavailable or request fails, falls back gracefully to template engine.
    """
    from src.llm.config import load_llm_config
    cfg = await load_llm_config()
    api_key = cfg.api_key
    provider = cfg.provider
    if not api_key:
        logger.info("No Anthropic/Claude API key found in config. Using template engine fallback.")
        return fallback_drafts

    user_prompt = f"""Generate sales copy for the following local business:
- Business Name: {business_name}
- Niche/Category: {category}
- City: {city}
- Current Website: {website or 'None / Outdated'}
- Google Rating: {google_rating or 'N/A'} ({review_count or 0} reviews)
- Technical Audit Findings: {json.dumps(findings)}
- Bespoke Modern Preview Site URL: {preview_url}

Generate the JSON output now."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Check provider or default to Anthropic
            if provider == "anthropic" or (cfg.source == "env" and api_key.startswith("sk-ant")):
                # Call Anthropic Claude API Messages endpoint
                # Try models in order: claude-3-5-haiku-20241022, claude-3-haiku-20240307, claude-3-5-sonnet-20241022
                target_models = [cfg.model, "claude-3-5-haiku-20241022", "claude-3-haiku-20240307", "claude-3-5-sonnet-20241022"]
                # Deduplicate list preserving order
                models_to_try = []
                for m in target_models:
                    if m and m not in models_to_try:
                        models_to_try.append(m)

                response = None
                for model in models_to_try:
                    logger.info(f"Calling Claude API with model {model}...")
                    headers = {
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    }
                    payload = {
                        "model": model,
                        "max_tokens": 1000,
                        "system": SALES_AGENT_SYSTEM_PROMPT,
                        "messages": [
                            {"role": "user", "content": user_prompt}
                        ]
                    }
                    res = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
                    if res.status_code == 200:
                        response = res
                        break
                    else:
                        logger.warning(f"Claude API model {model} returned {res.status_code}: {res.text}")

                if not response or response.status_code != 200:
                    logger.warning("Claude API calls failed. Falling back to template engine.")
                    return fallback_drafts

                data = response.json()
                content_text = data["content"][0]["text"]

            elif provider == "openai" or (cfg.source == "env" and api_key.startswith("sk-")):
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": (cfg.model if cfg.source == "admin" else settings.LLM_MODEL) or "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": SALES_AGENT_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "response_format": {"type": "json_object"}
                }
                res = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                if res.status_code != 200:
                    logger.warning(f"OpenAI API returned {res.status_code}: {res.text}")
                    return fallback_drafts
                data = res.json()
                content_text = data["choices"][0]["message"]["content"]

            else:
                logger.warning(f"Unsupported LLM provider {provider}. Using fallback.")
                return fallback_drafts

            # Extract JSON from LLM response text
            cleaned_text = content_text.strip()
            if "```json" in cleaned_text:
                cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_text:
                cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()

            parsed = json.loads(cleaned_text)
            logger.info("Successfully generated sales copy with LLM Sales Skill!")

            return {
                "linkedin_draft": parsed.get("linkedin_draft", fallback_drafts["linkedin_draft"]),
                "email_subject_draft": parsed.get("email_subject_draft", fallback_drafts["email_subject_draft"]),
                "email_body_draft": parsed.get("email_body_draft", fallback_drafts["email_body_draft"]),
                "whatsapp_draft": parsed.get("whatsapp_draft", fallback_drafts["whatsapp_draft"]),
                "call_script_notes": parsed.get("call_script_notes", fallback_drafts["call_script_notes"]),
            }

    except Exception as e:
        logger.error(f"Error executing LLM Sales Copy Generation: {e}", exc_info=True)
        return fallback_drafts
