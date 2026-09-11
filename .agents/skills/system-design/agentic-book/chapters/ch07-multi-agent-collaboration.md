# Chapter 7: Multi-Agent Collaboration

## Core Idea
A single monolithic agent is efficient for well-defined problems but bottlenecks on complex, multi-domain tasks. The Multi-Agent Collaboration pattern structures a system as a cooperative ensemble of specialized agents: a high-level objective is decomposed into sub-problems, each assigned to an agent with the tools, data access, and reasoning best suited to it. The collective output then exceeds what any single agent could achieve. This synergy is not automatic—it depends on explicit role boundaries, standardized communication protocols, and a shared ontology that lets agents exchange data, delegate sub-tasks, and coordinate toward a coherent result.

## Frameworks Introduced
The pattern is operationalized through orchestration frameworks that model agents, tasks, and their interaction procedures:
- **Crew AI**: defines Agents (roles/goals/backstory), Tasks (description/expected_output), and a Crew run with a chosen Process (e.g., sequential).
- **Google ADK**: builds hierarchies via parent/child `sub_agents`, plus purpose-built orchestrators—`SequentialAgent`, `ParallelAgent`, `LoopAgent`, and `AgentTool` (agent-as-tool).
- Communication topologies themselves act as a "framework": single agent, network, supervisor, supervisor-as-tool, hierarchical, and custom.

## Key Concepts
- **Task decomposition**: splitting a high-level objective into discrete, assignable sub-problems.
- **Specialized role**: an agent with a defined goal and tailored tools/knowledge (e.g., researcher, analyst, writer, critic).
- **Communication protocol & shared ontology**: standardized messages and a common vocabulary enabling data exchange and coordination.
- **Sequential handoff**: one agent's output becomes the next agent's input (a pipeline).
- **Parallel processing**: independent agents run concurrently; results are combined.
- **Debate and consensus**: agents with varied perspectives discuss options to reach an informed decision.
- **Supervisor / coordinator**: a central hub for task allocation, communication, and conflict resolution.
- **Critic-reviewer loop**: creators produce drafts; a reviewer group assesses for correctness, policy, security, quality, and alignment; the creator revises.
- **Delegation contract**: typed input/output plus evidence requirements passed between agents.
- **Topology**: the overall communication structure (see below).
- **Synergy**: collective performance exceeding any single member's potential.

## Mental Models
- **Compose an organization, not a persona**: divide work by genuine capability and context boundaries, not by decorative role labels.
- **Coordination is a tax**: every added agent and handoff adds overhead; specialization must pay for it.
- **Topology matches complexity**: simplest structure that solves the task wins—escalate only when decomposition, parallelism, or robustness demands it.
- **Ownership resolves ambiguity**: someone must own the final output and resolve conflicts.

## Collaboration Topologies
A spectrum of interrelationship models exists, each with trade-offs:
1. **Single Agent**: autonomous, no inter-agent communication. Simple to run, but bounded by one agent's scope and resources.
2. **Network**: decentralized, peer-to-peer agents sharing information and tasks. Resilient (no single point of failure) but hard to keep coherent and expensive to coordinate at scale.
3. **Supervisor**: one coordinator allocates tasks, routes communication, and resolves conflicts. Clear authority, but the supervisor is a single point of failure and a potential bottleneck.
4. **Supervisor-as-Tool**: the supervisor does not command but supplies resources, tools, data, or analytical support to other agents, preserving their autonomy.
5. **Hierarchical**: multiple layers of supervisors overseeing lower ones down to operational agents. Scales to large decompositions with distributed decision-making within boundaries.
6. **Custom**: bespoke structures—often hybrids—tuned to specific metrics, dynamic environments, or domain knowledge. Maximum flexibility, maximum design effort.

## Use Cases
- **Complex research & analysis**: searcher, summarizer, trend-identifier, and synthesizer agents mirroring a human research team.
- **Software development**: requirements analyst, code generator, tester, and documentation writer passing outputs along.
- **Creative content**: market research, copywriter, image-generation designer, and scheduling agents.
- **Financial analysis**: stock-data fetcher, news-sentiment analyzer, technical analyst, and recommendation agent.
- **Support escalation**: front-line agent hands complex issues to specialists (sequential handoff by complexity).
- **Supply chain optimization**: agents as nodes (suppliers, manufacturers, distributors) balancing inventory and logistics.
- **Network ops & remediation**: agents triage and pinpoint failures, integrating with existing ML tooling.

## Anti-Patterns / Failure Modes
- **Single point of failure**: the supervisor crashes and takes the system down; mitigate with fallbacks or redundancy.
- **Bottleneck**: an overwhelmed supervisor serializes everything, killing the benefit of parallelism.
- **Agent sprawl**: coordination and communication costs exceed the value of specialization.
- **Unowned output**: no agent resolves conflicts or verifies coherence, producing fragmented results.
- **Broken handoff contract**: agents pass incompatible data due to a missing shared ontology or vague expected outputs.
- **Critic-blind loops**: reviewer feedback is ignored or never traced back to a concrete revision.

## Implementation Sketch
Illustrative pseudocode (not framework source):

```
# Crew-style sequential crew
researcher = Agent(role="analyst",   goal="summarize AI trends")
writer     = Agent(role="writer",    goal="draft blog post")
crew = Crew(
    agents=[researcher, writer],
    tasks=[
        Task(desc="top 3 AI trends",  output="summary + sources"),
        Task(desc="500-word post",    output="final article",
             context=[research_task]),   # handoff dependency
    ],
    process=sequential,
)
print(crew.kickoff())

# ADK-style hierarchical delegation
coordinator = LlmAgent(instruction="delegate greetings->Greeter, tasks->TaskExecutor")
coordinator.sub_agents = [greeter, task_doer]   # parent-child

# ADK-style agent-as-tool (invoke an agent like a function)
image_tool = AgentTool(agent=image_generator_agent,
                       description="generate an image from a prompt")
artist.tools = [image_tool]
```

## Worked Example
**Generate a blog post about AI trends.** Define a researcher agent (find and summarize top trends with sources) and a writer agent (produce an engaging 500-word post). Wire both into a Crew with `Process.sequential` so the writing task's `context` depends on the research task's output. Kick off the crew; the researcher's summary flows into the writer as a handoff contract, yielding a coherent article. For a hierarchical variant, a Coordinator agent delegates greeting sub-tasks to a Greeter and execution sub-tasks to a custom `TaskExecutor(BaseAgent)` via `sub_agents`, demonstrating parent-child delegation. Iterative workflows use `LoopAgent` (run sub-agents up to `max_iterations`, stopping on a condition), linear flows use `SequentialAgent` (save step1 output to `session.state["data"]`, feed to step2), concurrent work uses `ParallelAgent` (weather + news fetchers), and reuse is achieved by wrapping an agent in `AgentTool` so a parent "artist" agent calls an "image generator" agent as a tool.

## Key Takeaways
1. Decompose complex tasks into sub-problems assigned to agents with the right tools and expertise.
2. Make roles, boundaries, and handoff contracts explicit; share a common ontology so outputs are compatible.
3. Choose topology intentionally—single, network, supervisor, supervisor-as-tool, hierarchical, or custom—matching task complexity, autonomy, robustness, and coordination cost.
4. Use critic-reviewer loops to cut hallucinations and improve correctness for code, research, and compliance-sensitive output.
5. Frameworks (Crew AI, Google ADK) provide primitives—Crew/Task, Sequential/Parallel/Loop agents, AgentTool—to express these patterns without building orchestration from scratch.
6. Design for failure: guard against single points of failure, supervisor bottlenecks, and agent sprawl.
7. Measure coordination overhead; remove agents whose cost exceeds their specialization value.

## Connects To
- **Planning pattern**: sequential handoffs resemble planning but explicitly route through distinct agents.
- **Hierarchical / delegation**: the supervisor and hierarchical topologies generalize single-agent delegation into multi-agent form.
- **Critic-reviewer**: pairs naturally with any generation pattern needing quality, security, or compliance assurance.
- **External environment**: understanding collaboration flows naturally into how agents act on and observe the outside world.
- **Multi-Agent Collaboration Mechanisms: A Survey** (arXiv 2501.06322) and surveys of multi-agent frameworks for deeper theory.
