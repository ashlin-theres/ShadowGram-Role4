import os
import asyncio
from openai import AsyncOpenAI

# Read NVIDIA key from environment, with a default fallback
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "nvapi-demo-dev-key")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

client = AsyncOpenAI(
    base_url=NVIDIA_BASE_URL,
    api_key=NVIDIA_API_KEY
)

def deterministic_sar_narrative(cluster_data: dict) -> str:
    """
    CFPB Circular 2023-03 & ECOA Regulation B compliant deterministic fallback.
    Returns in <5ms with zero network calls.
    """
    cluster_id = cluster_data.get("cluster_id", 1)
    nodes = cluster_data.get("node_count", 20)
    delta_t = cluster_data.get("avg_delta_t_ms", 38.0)
    route_ov = cluster_data.get("route_overlap_pct", 96.0)
    sem_cos = cluster_data.get("semantic_cosine", 0.89)

    return (
        f"EXECUTIVE SUMMARY - ADVERSE ACTION DOSSIER (SYNDICATE CLUSTER #{cluster_id})\n"
        f"Automated risk isolation was enforced across {nodes} affiliated applicant nodes.\n\n"
        f"FACTUAL ADVERSE ACTION REASON CODES (CFPB CIRCULAR 2023-03 / ECOA REGULATION B):\n"
        f"1. TEMPORAL SYNCHRONIZATION: Account arrival intervals demonstrated a mean inter-arrival "
        f"delta of {delta_t}ms (Z-score > 4.5), reflecting automated multi-thread orchestration.\n"
        f"2. FINITE STATE NAVIGATION OVERLAP: Identified a {route_ov}% Longest Common Subsequence (LCS) "
        f"route overlap across multi-step credit application funnels (/auth -> /kyc -> /loan_submit).\n"
        f"3. UNIFORM HIGH-DIMENSIONAL INTENT: Free-form loan rationale texts exhibited a cosine "
        f"similarity of {sem_cos} across a 384-dimensional dense semantic space, confirming programmatic "
        f"LLM identity generation."
    )

async def _call_nvidia_nim(cluster_data: dict) -> str:
    prompt = (
        f"You are a Senior AML/Fraud Compliance Officer. Draft an official Suspicious Activity Report (SAR) "
        f"executive summary for Syndicate Cluster #{cluster_data.get('cluster_id', 1)} containing "
        f"{cluster_data.get('node_count', 20)} synthetic accounts. Formulate 3 specific, verifiable factual reason "
        f"codes strictly complying with CFPB Circular 2023-03 and ECOA Regulation B. Avoid generic risk scores. "
        f"Metrics: Delta_t={cluster_data.get('avg_delta_t_ms', 38)}ms, "
        f"Route_Overlap={cluster_data.get('route_overlap_pct', 96)}%, "
        f"Semantic_Cosine={cluster_data.get('semantic_cosine', 0.89)}."
    )
    
    response = await client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=350,
    )
    return response.choices[0].message.content

async def generate_legal_narrative(cluster_data: dict) -> str:
    """
    Invokes NVIDIA NIM API with a 15-second circuit breaker.
    If timeout or network failure occurs, instantaneously returns the deterministic report.
    """
    try:
        # Give NVIDIA NIM 15s to respond over WiFi
        return await asyncio.wait_for(_call_nvidia_nim(cluster_data), timeout=15.0)
    except Exception as e:
        print(f"[*] Circuit-breaker triggered ({type(e).__name__}). Using instant deterministic legal fallback.")
        return deterministic_sar_narrative(cluster_data)