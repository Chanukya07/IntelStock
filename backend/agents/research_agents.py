"""Multi-agent roles for IntelStock analysis pipeline."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRole:
    name: str
    output: str


AGENT_ROLES = [
    AgentRole(name="Market Analyst", output="Market Summary and Trend Analysis"),
    AgentRole(name="News Analyst", output="Key Events and Market Impact"),
    AgentRole(name="Sentiment Analyst", output="Bullish/Bearish Scores"),
    AgentRole(name="Research Agent", output="Investment Thesis and Recommendation"),
]
