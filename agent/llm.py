def build_prompt(agent_name, task, context):
    return f"""
NUNVIZHI - MULTI-AGENT AI SYSTEM

AGENT NAME:
{agent_name}

TASK:
{task}

AVAILABLE DATA:
{context}

INSTRUCTIONS:

1. Analyze only the provided data.
2. Identify important patterns.
3. Explain limitations.
4. Provide practical recommendations.
5. Do not invent measurements.
6. Do not claim real-time monitoring.
7. Do not assume external traffic is campus traffic.
8. Do not invent energy measurement units.

OUTPUT FORMAT:

- Findings
- Analysis
- Recommendations
- Limitations
"""
