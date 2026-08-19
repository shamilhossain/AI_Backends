import random
from fastapi import FastAPI
import inngest
import inngest.fast_api
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# 1 & 2. Initialize FastAPI application and Inngest client
app = FastAPI(title="AI Decision Flow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

inngest_client = inngest.Inngest(app_id="ai-decision-flow")

# 3. Create a dummy function mimicking an AI agent
def run_antigravity_agent(prompt: str) -> str:
    """Mimics an AI agent that prints the prompt and returns YES or NO."""
    print(f"🤖 Antigravity Agent received prompt: '{prompt}'")
    return random.choice(["YES", "NO"])

# 4. Create an Inngest function triggered by "workflow/run"
@inngest_client.create_function(
    fn_id="execute-ai-flow",
    trigger=inngest.TriggerEvent(event="workflow/run"),
)
async def execute_ai_flow(ctx: inngest.Context, step: inngest.StepSync):
    """
    Receives a graph of nodes and edges from the frontend, extracts the 
    prompt of the first node, and runs the AI agent using step.run.
    """
    event_data = ctx.event.data
    nodes = event_data.get("nodes", [])
    
    # Extract the prompt from the first node (if available)
    first_node_prompt = "No prompt provided"
    if nodes and len(nodes) > 0:
        first_node_prompt = nodes[0].get("prompt", first_node_prompt)
        
    # Run the dummy agent wrapped in an Inngest step
    result = await step.run(
        "run-antigravity-agent",
        lambda: run_antigravity_agent(first_node_prompt)
    )
    
    return {
        "status": "success",
        "agent_result": result
    }

# 5. Serve the Inngest function using inngest.fast_api.serve
inngest.fast_api.serve(
    app,
    inngest_client,
    [execute_ai_flow],
)

# 6. Simple GET route at "/"
@app.get("/")
async def root():
    return {"message": "AI Decision Flow Backend is running! 🚀"}

class RunFlowRequest(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

@app.post("/api/run-flow")
async def run_flow(request: RunFlowRequest):
    await inngest_client.send(
        inngest.Event(
            name="workflow/run",
            data={"nodes": request.nodes, "edges": request.edges}
        )
    )
    return {"status": "success", "message": "Workflow triggered"}
