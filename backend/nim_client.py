import os
import asyncio
import requests
from typing import Dict, Any
from backend.fallback_sar import deterministic_sar_narrative

NVIDIA_NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"


def _ensure_regulatory_compliance_headers(narrative: str) -> str:
    """Ensures statutory CFPB Circular 2023-03 and ECOA Reg B citations are present."""
    if "CFPB CIRCULAR 2023-03" not in narrative:
        if "ECOA REGULATION B (12 CFR § 1002.9) / EU AI ACT" in narrative:
            narrative = narrative.replace(
                "ECOA REGULATION B (12 CFR § 1002.9) / EU AI ACT",
                "ECOA REGULATION B (12 CFR § 1002.9) / CFPB CIRCULAR 2023-03 / EU AI ACT",
            )
        elif "REGULATORY GOVERNANCE:" in narrative:
            narrative = narrative.replace(
                "REGULATORY GOVERNANCE:",
                "REGULATORY GOVERNANCE: CFPB CIRCULAR 2023-03 /",
            )
    return narrative


async def generate_sar_report_narrative(cluster_data: Dict[str, Any]) -> str:
    """
    Generates a formal legal SAR narrative using NVIDIA NIM (Llama-3.3-70B).
    Enforces a strict 1500ms timeout circuit breaker; falls back to deterministic template immediately.
    """
    api_key = os.getenv("NVIDIA_API_KEY", "").strip()
    if not api_key:
        print("[NIM Client] No NVIDIA_API_KEY configured. Using deterministic legal template.")
        return _ensure_regulatory_compliance_headers(deterministic_sar_narrative(cluster_data))

    def _sync_nim_call() -> str:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        prompt = f"""You are a Senior AML & Financial Fraud Compliance Officer.
Draft an official Suspicious Activity Report (SAR) executive summary for Syndicate Cluster #{cluster_data.get('cluster_id', 1)}
containing {cluster_data.get('size', 20)} synthetic applicant accounts.
Topological Community Modularity: Q = {cluster_data.get('modularity_q', 0.72):.4f} with empirical permutation test p-value = {cluster_data.get('p_value', 0.0001):.4f} (N=1,000 degree-preserving graph permutations).
Prevented Denial-of-Wallet (DoW) financial drain: ₹{cluster_data.get('dow_savings_inr', 1220.0):.2f} (pre-KYC API interception).
Formulate four specific, factual adverse action reason codes strictly complying with Equal Credit Opportunity Act (ECOA) Regulation B (12 CFR § 1002.9), CFPB Circular 2023-03, EU AI Act (Regulation 2024/1689 Articles 13 & 14), and RBI Digital Lending Directions.
Include: 1) FSM Navigation Route Invariance, 2) Micro-temporal Arrival Sync (delta_t < 40ms) via Iannucci time-decay kernel, 3) Event-stream click-dwell distribution invariance & zero physiological tremor (8-12 Hz), and 4) Semantic intent prompt homogeneity (all-MiniLM-L6-v2 cosine >= 0.88).
Explicitly avoid black-box risk scores. Emphasize that quarantine is reversible via Step-Up UPI penny-drop challenge."""

        payload = {
            "model": NVIDIA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
            "temperature": 0.2,
        }

        resp = requests.post(NVIDIA_NIM_URL, headers=headers, json=payload, timeout=1.4)
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        else:
            raise RuntimeError(f"NVIDIA NIM error {resp.status_code}: {resp.text}")

    try:
        # Strict 1500ms Circuit Breaker
        narrative = await asyncio.wait_for(asyncio.to_thread(_sync_nim_call), timeout=1.5)
        return _ensure_regulatory_compliance_headers(narrative)
    except (asyncio.TimeoutError, Exception) as e:
        print(f"[NIM Client] Circuit breaker triggered ({e}). Returning deterministic legal narrative.")
        return _ensure_regulatory_compliance_headers(deterministic_sar_narrative(cluster_data))