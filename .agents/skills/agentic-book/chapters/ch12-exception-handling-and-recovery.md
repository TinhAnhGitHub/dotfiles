# Chapter 12: Exception Handling and Recovery

## Core Idea
Agents operating in real-world environments inevitably meet failures: bad tool inputs, unavailable services, malformed outputs, and unpredictable inputs. The Exception Handling and Recovery pattern turns fragile agents into resilient ones by giving them a standardized capability to **anticipate, detect, handle, and recover** from operational failures. The goal is not zero failures but maintained operational integrity — minimize downtime, preserve state so work can be retried or rolled back, and fail gracefully rather than collapse. It pairs proactive preparation (validation, timeouts, monitoring) with reactive strategies (logging, retries, fallbacks, degradation, escalation), and often works together with reflection: a failed attempt can trigger a reflective re-analysis and a reattempt with a refined approach.

## Frameworks Introduced
- **Detect → Handle → Recover lifecycle**: Identify the error, respond with a planned strategy, then restore stable operation.
  - *Detect*: validate tool outputs, check API error codes (e.g., 404 Not Found, 500 Internal Server Error), watch for unusually slow responses, and flag incoherent responses that deviate from expected formats. Other agents or dedicated monitoring systems can add proactive anomaly detection.
  - *Handle*: log for diagnostics, retry transient failures (sometimes with adjusted parameters), use fallbacks to preserve functionality, degrade gracefully when full recovery isn't possible, and notify human operators or other agents when intervention is needed.
  - *Recover*: roll back recent changes/transactions, diagnose the root cause, self-correct or replan by adjusting plan, logic, or parameters, and escalate to a human or higher-level system for severe cases.
- **Checkpoint and rollback**: snapshot state before risky multi-step changes so you can undo effects after a failure.

## Key Concepts
- **Transient failure**: Likely to succeed after a delay or tweak — rate limits, temporary service outages, network blips.
- **Permanent failure**: Retry will not help without changed input or authority — e.g., "insufficient funds," "market closed," malformed arguments.
- **Retry with backoff**: Re-attempt transient failures using bounded attempts and increasing delays, avoiding retry storms.
- **Fallback**: Swap in an alternative tool, method, or data source to keep delivering value.
- **Graceful degradation**: Maintain partial functionality when complete recovery is impossible.
- **Idempotency**: Design actions so retries do not duplicate side effects (charges, messages, state changes).
- **State rollback / undo**: Reverse recent changes to return to a stable state.
- **Self-correction / replanning**: Adjust the plan, prompt, or parameters to avoid repeating the error.
- **Escalation**: Delegate to a human operator or higher-level system when automation cannot safely recover.
- **Notification / alerting**: Inform operators or peer agents when help is required.
- **Timeouts**: Bound how long an operation may run so hung services surface as detectable errors instead of infinite hangs.

## Mental Models
- **Recovery policy lives in orchestration, not in the optimistic model instructions.** The main plan assumes success; a separate layer decides what to do when it fails.
- **Every retry has a classification and a budget.** Classify the cause (transient vs. permanent) before acting; permanent failures should not consume retry budget.
- **Narrowest safe recovery first.** Prefer the least destructive action that restores safety: degrade before rollback, rollback before escalation.
- **Never confuse silence with success.** A swallowed error that hides partial work produces false success and is worse than a surfaced failure.

## Anti-patterns / Failure Modes
- **Retry everything**: applies retries to permanent failures, creating storms and repeating harmful actions.
- **Retry side effects without idempotency**: duplicates charges, messages, database writes, or state changes.
- **Hide failure**: catches and suppresses errors, turning partial work into reported success and losing auditability.
- **Unbounded retries / no backoff**: hammering a degraded service and amplifying outages.
- **Crash on first error**: no fallback or degradation, so a single hiccup halts the whole task.
- **Rollback without diagnosis**: undoes the symptom but not the cause, guaranteeing recurrence.

## Implementation Sketch
A generic recovery loop, expressed as illustrative pseudocode (not source):

```
try:
    result = await tool.call(input)
    validate(result)              # format, schema, error codes, sanity
except TransientError as e:
    if retries_used < budget:
        sleep(backoff(retries_used))
        return retry(input)       # adjust parameters if needed
    return fallback(input)        # alternative tool / degraded path
except PermanentError as e:
    log(e)                        # do not retry; input is the problem
    notify(operator, e)
    return degrade() or escalate()

# After side-effecting work:
checkpoint(state)                 # snapshot before irreversible change
try:
    commit(work)
except Failure:
    rollback(state)               # undo to last checkpoint
    diagnose()                    # find root cause
    replan() or escalate()
```

The ADK example in the chapter demonstrates a *structural* version of this: a `SequentialAgent` chains a `primary_handler` (tries `get_precise_location_info`), a `fallback_handler` (inspects `state["primary_location_failed"]`; if true, extracts the city from the query and uses `get_general_area_info`), and a `response_agent` (presents `state["location_result"]` or apologizes if absent). The ordered sub-agents provide layered retrieval with a built-in fallback, and state carries the failure signal between stages.

## Worked Example
A location agent is given a user's address. The `primary_handler` calls a precise-geocoding tool, which fails (service error). It records `state["primary_location_failed"] = true`. The `fallback_handler` sees the flag, extracts the city from the user's original query, and calls a coarser `get_general_area_info` tool to return the city and region. The `response_agent` then presents the approximate location. If even the fallback fails, `location_result` stays empty and the agent apologizes rather than crashing. A second scenario: a calendar write times out but the request may have already succeeded. Rather than blindly retrying, the agent checks an idempotency key or reads the calendar first, then reports the uncertainty instead of creating a duplicate event.

## Key Takeaways
1. **Failures are expected, not exceptional.** Design for them proactively; reliability is a core requirement in dynamic environments.
2. **Classify before recovering.** Distinguish transient from permanent errors — this decides whether to retry, fall back, roll back, or escalate.
3. **Bound your recovery.** Use timeouts, exponential backoff, retry budgets, and idempotency keys to avoid storms and duplicate effects.
4. **Checkpoint before irreversible work** so you can roll back and diagnose instead of leaving the system in a corrupted state.
5. **Preserve value through fallbacks and graceful degradation** — deliver a safe partial result rather than nothing.
6. **Make failures visible.** Log for diagnostics, surface partial completion and uncertainty, and notify operators or peers when needed.
7. **Close the loop with recovery:** roll back, self-correct/replan, and escalate only when automation cannot safely proceed.

## Connects To
- **Reflection**: A failed attempt with a raised exception can trigger reflective analysis and a refined reattempt (e.g., an improved prompt).
- **Tool design (Ch 5)**: Tools should expose structured, classifiable errors (typed exceptions, status codes) so detection and classification work.
- **Monitoring and observability**: Detection leans on logging, timeouts, and anomaly monitoring; recovery outcomes should themselves be logged for later diagnosis.
- **Escalation**: When safe automated recovery is impossible, defer to a human operator or higher-level system.
