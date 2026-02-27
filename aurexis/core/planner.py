"""
AUREXIS - Autonomous Planner
Used in 'autonomous' mode to decompose tasks into steps and execute them.
"""
import json, re
from typing import List, Dict, Optional


class Plan:
    def __init__(self, goal: str, steps: List[Dict]):
        self.goal = goal
        self.steps = steps
        self.current = 0
        self.results = []

    @property
    def is_complete(self):
        return self.current >= len(self.steps)

    def next_step(self) -> Optional[Dict]:
        if self.is_complete:
            return None
        return self.steps[self.current]

    def complete_step(self, result: str):
        step = self.steps[self.current]
        step["result"] = result
        self.results.append(result)
        self.current += 1


class Planner:
    """
    Calls the LLM to break a goal into structured steps,
    then executes each step via the orchestrator.
    """

    PLAN_PROMPT = """
You are a planning engine. Given a goal, return a JSON plan:
{{
  "goal": "<goal>",
  "steps": [
    {{"id": 1, "action": "<action>", "tool": "<tool_name_or_null>", "args": {{}}, "description": "..."}},
    ...
  ]
}}
Return ONLY valid JSON, no markdown.
Goal: {goal}
Available tools: {tools}
"""

    def __init__(self, llm, mcp_registry):
        self.llm = llm
        self.mcp_registry = mcp_registry

    async def create_plan(self, goal: str) -> Plan:
        tools = [t["name"] for t in self.mcp_registry.get_all_tools()]
        prompt = self.PLAN_PROMPT.format(goal=goal, tools=", ".join(tools) or "none")
        response = await self.llm.complete(prompt)
        
        # Extract JSON from response
        try:
            # Strip markdown fences if any
            clean = re.sub(r"```json?|```", "", response).strip()
            data = json.loads(clean)
            return Plan(data["goal"], data.get("steps", []))
        except Exception:
            # Fallback: single-step plan
            return Plan(goal, [{"id": 1, "action": "respond", "tool": None, "args": {}, "description": goal}])

    async def execute_plan(self, plan: Plan, executor) -> str:
        """Execute plan steps via tool executor"""
        while not plan.is_complete:
            step = plan.next_step()
            if step.get("tool"):
                try:
                    result = await executor(step["tool"], step.get("args", {}))
                except Exception as e:
                    result = f"Error: {e}"
            else:
                result = f"Step '{step['description']}' noted."
            plan.complete_step(result)

        return f"Plan completed. Steps: {len(plan.steps)}\nResults:\n" + "\n".join(
            f"  {i+1}. {r}" for i, r in enumerate(plan.results)
        )
