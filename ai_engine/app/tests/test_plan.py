"""
Verification test for the /plan endpoint.
"""
import asyncio
import json
from ai_engine.reasoning_generator import ReasoningGenerator

async def test_plan():
    generator = ReasoningGenerator()
    print("Testing /plan generator...")
    result = await generator.generate_plan(
        question="How does a battery work?",
        difficulty="beginner",
        generate_diagram=True,
        generate_image=True,
        generate_video=True
    )
    
    if result.get("status") == "success":
        print("Plan generated successfully!")
        print(json.dumps(result["plan"], indent=2))
    else:
        print(f"Plan generation failed: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(test_plan())
