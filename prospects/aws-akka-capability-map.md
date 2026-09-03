# Where Akka leverages, overlaps, and enhances AWS

Relationship codes: **LEVERAGE** (Akka runs on it), **OVERLAP** (both do it, Akka replaces), **ENHANCE** (Akka adds on top of it), **NONE** (AWS only, Akka has no equivalent), **AKKA** (no AWS counterpart).


## Models, inference, and capacity

| AWS service | What AWS provides | Rel | Akka |
|---|---|---|---|
| Amazon Bedrock (inference) | Serverless token-metered access to Anthropic, Meta, Mistral, Amazon Nova, Cohere | LEVERAGE | Bedrock is a configured model provider. Akka provides semantic routing to these models. |
| Bedrock Provisioned Throughput | Reserved model units at a committed hourly rate | LEVERAGE | Akka routes to the provisioned endpoint. Commitment stays with AWS. |
| Bedrock Intelligent Prompt Routing | Routes between two models in one family on predicted quality | OVERLAP | Akka Optimize routes each request across vendors and families under customer policy, reserving frontier models for requests that need them. |
| Bedrock Marketplace / SageMaker JumpStart | Hosting for Hugging Face and third-party weights | LEVERAGE | Akka Optimize uses Bedrock's models and weights for training SLMs. |
| SageMaker Inference endpoints | Customer-managed model serving on EC2 or Inferentia | LEVERAGE | Akka calls the endpoint and reused SageMaker models. |
| EC2 Capacity Blocks for ML, UltraClusters, Trainium/Inferentia, SageMaker HyperPod | Reserved and on-demand GPU/accelerator capacity | LEVERAGE | Akka contracts the capacity with AWS and Akka provides an inference layer for self-hosting models, lowering the cost vs. token-metered Bedrock. |
| Bedrock Model Distillation | Distills a teacher model into a smaller student on customer prompts | OVERLAP | Akka Optimize grades live production traffic and trains smaller specialized models on the customer's proprietary data, owned by the customer and run in their environment. |
| SageMaker Training, Pipelines, Feature Store, Ground Truth, Clarify, Model Monitor | General ML lifecycle | NONE | Akka provides no general ML platform. |

## Agent frameworks and runtime

| AWS service | What AWS provides | Rel | Akka |
|---|---|---|---|
| AgentCore Runtime | Session-isolated agent hosting, per-vCPU-hour and per-GB-hour | OVERLAP | Agent, Workflow, Entity, View, Timer, and Endpoint components on one runtime with a 99.9999% platform SLA Akka owns. |
| AgentCore Memory | Short- and long-term agent memory, separately billed | OVERLAP | Durable in-memory state built into the runtime, 4ms reads and sub-10ms writes, replicated active-active. |
| AgentCore Gateway | Converts APIs and Lambdas into MCP tools | OVERLAP | HTTP, gRPC, and MCP endpoints are first-class components. |
| AgentCore Identity | Agent identity and OAuth token vending to tools | OVERLAP | Identity and authorization built into endpoints; customers federate AWS IAM into Akka. |
| AgentCore Observability | Agent traces into CloudWatch | OVERLAP + ENHANCE | Interaction logging, causal logging, and evaluations in the platform, exported over OTEL to CloudWatch or any collector. |
| AgentCore Policy | Tool-access rules at the agent-to-tool boundary, GA June 2026 | OVERLAP | Inline guardrails, policies, LLM-as-judge, sanitizers, HITL/HOTL, atomic PII scrub-with-explain. |
| AgentCore Evaluations | Agent trajectory and outcome scoring, GA March 2026 | OVERLAP | Continuous evaluation on production traffic, grading agents running in Akka or in third-party harnesses. We also provide red teaming. |
| AgentCore Code Interpreter | Sandboxed code execution for agents | NONE | Akka has no equivalent and calls it as a tool. |
| AgentCore Browser | Managed headless browser for agents | NONE | Akka has no equivalent and calls it as a tool. |
| Strands Agents SDK | Open-source Python agent SDK | OVERLAP | Akka SDK in Java, with durable execution, supervision, and clustering as SDK primitives. |
| Bedrock Flows | Visual prompt-and-Lambda chaining | OVERLAP | Workflows with durable execution, automatic retries, and step-level observability.  Akka Specify accepts any visual design as a specification. |
| Bedrock Prompt Management | Versioned prompt store | OVERLAP | Prompts versioned inside the agent component and covered by the build lifecycle in Akka Specify. |
| AWS Step Functions | Managed state-machine orchestration | OVERLAP | Akka Workflows hold state in the runtime. The agent calls out to no external state machine. |

## Knowledge, retrieval, and data

| AWS service | What AWS provides | Rel | Akka |
|---|---|---|---|
| Bedrock Knowledge Bases | Managed RAG: ingestion, chunking, embedding, retrieval | LEVERAGE | Akka has no equivalent and integrates with it.  |
| Neptune Analytics GraphRAG | Graph-backed retrieval under Knowledge Bases | LEVERAGE | Akka has no equivalent and integrates with it. |
| OpenSearch Serverless vector engine, Aurora pgvector, MemoryDB vector | Vector indexes | LEVERAGE | Akka has no equivalent and integrates with it. |
| Amazon Kendra | Enterprise search with connectors | LEVERAGE | Akka has no equivalent and integrates with it. |
| Bedrock Data Automation, Textract, Comprehend | Document extraction and NLP over unstructured input | LEVERAGE | Akka has no equivalent and integrates with it. |
| Glue, Lake Formation, Athena, Redshift | ETL, catalog, query, warehouse | LEVERAGE | Akka publishes events and evidence downstream. |
| Amazon S3 | Object storage | LEVERAGE | Akka uses Amazon S3 as our backing store for AI tracing, audit records, evidence, and policy artifacts. |

## Safety and applied AI

| AWS service | What AWS provides | Rel | Akka |
|---|---|---|---|
| Bedrock Guardrails | Content filters, denied topics, PII redaction, contextual grounding at the inference boundary | OVERLAP + ENHANCE | Akka supplies the guardrail framework — inline guardrails, sanitizers, judges, and halts at every step of the agent lifecycle. Most customers run third-party specialty safety models inside that framework; Bedrock Guardrails is one of them. |
| Transcribe, Polly, Rekognition, Translate, Lex, Connect | Speech, vision, translation, contact centre | LEVERAGE | Called as tools. Akka carries the streaming and session state around them. |

## State, eventing, and streaming

| AWS service | What AWS provides | Rel | Akka |
|---|---|---|---|
| Aurora, RDS, DynamoDB | Managed databases the customer wires into the agent framework | OVERLAP | Event-sourced entities, key-value entities, durable workflow state, and AI memory inside the platform, with no integration to build. |
| ElastiCache, MemoryDB | Managed cache | OVERLAP | Durable in-memory state is the primary store. |
| Kinesis, MSK, SQS, SNS, EventBridge | Managed streaming and messaging | OVERLAP + LEVERAGE | Streaming built into the runtime, backpressured, petabyte-scale, no external broker (Tubi: 5B tokens/sec). Akka consumes and publishes to these where they carry enterprise traffic. |
| Kinesis Data Analytics, Managed Flink | Stream processing | OVERLAP | CQRS Views project entity events into queryable read models. |
| EventBridge Scheduler | Cron and one-off scheduling | OVERLAP | Timers bound to components, durable across restart. |

## Compute, network, and security

| AWS service | What AWS provides | Rel | Akka |
|---|---|---|---|
| EKS, EC2 | Kubernetes and instances | LEVERAGE | EKS is the runtime backbone for the platform in the customer VPC. |
| Lambda, Fargate | Serverless compute | OVERLAP | Akka components are long-lived and stateful. Lambdas remain reachable as tools. |
| API Gateway, ALB | Managed API front door | LEVERAGE | Akka HTTP and gRPC endpoints are components that can be managed by AWS API Gateway. Customers front them with API Gateway where an existing gateway policy requires it. |
| IAM, KMS, Secrets Manager | Identity, keys, secrets | LEVERAGE | Customers federate IAM into Akka; KMS holds the keys. |
| PrivateLink, VPC, Route 53 | Private connectivity | LEVERAGE | Customer VPC is the default deployment. PrivateLink reaches enterprise data when the platform runs in Akka's account. |
| CloudWatch, X-Ray, Managed Prometheus | Metrics, traces, logs | LEVERAGE | Akka exports OTEL to CloudWatch or any collector the customer chooses. |
| CloudTrail, Config, Audit Manager, Security Hub | Control-plane audit and posture | LEVERAGE | These record AWS API calls. Akka records agent decisions in a hash-chained evidence ledger. The customer keeps both records. |
| AWS Marketplace | Procurement and committed-spend drawdown | LEVERAGE | Akka transacts through Marketplace against the customer's AWS commit. |

## No AWS counterpart

| Capability | What it is |
|---|---|
| Akka Specify | Two independently versioned and tested lifecycles — a functional contract and a safeguard contract — generating, testing, and running one certified service. AWS offers no path for a product manager, domain expert, or risk officer to contribute. |
| 99.9999% platform SLA | Entire platform, backed by contractual indemnities, sub-1-minute RTO, zero-byte RPO, active-active across regions. Bedrock publishes 99.9% on API errors with service credits as the only remedy. |
| Regulation and control repository | Pre-deployment classification against 190 regulations and 1,040 controls, 671 carrying a financial penalty. |
| Hash-chained evidence ledger and sealed Governance Posture Package | Immutable record of agent decisions and a sealed audit artifact. |
| Akka Verify | Proves conformance from the running system against both contracts. |
| Evalkit and redkit | Evaluation and red-team corpora run against the deployed system. |
| Portability | The same platform runs on Azure, GCP, customer Kubernetes, on-prem, and sovereign cloud. AgentCore runs on AWS. |

## What you pay for

A production agent on AgentCore meters every service it touches. The Akka platform fee covers
those meters. The customer keeps paying AWS for the infrastructure the platform runs on.

| AWS chargeable item | Without Akka | With Akka |
|---|---|---|
| AgentCore Runtime | Per vCPU-hour, per GB-hour | Included |
| AgentCore Memory | Per record stored, per retrieval | Included |
| AgentCore Gateway | Per tool call, per tool search | Included |
| AgentCore Observability | Per GB ingested into CloudWatch | Included |
| AgentCore Policy | Per policy decision | Included |
| AgentCore Evaluations | Per evaluation | Included |
| Bedrock model inference | Per token | Included |
| Bedrock Guardrails | Per text unit | Included |
| Bedrock Model Distillation | Per training run | Included |
| AWS Step Functions | Per state transition | Included |
| DynamoDB, Aurora | Per request, per GB | Included |
| ElastiCache, MemoryDB | Per node-hour | Included |
| Kinesis, MSK, SQS, SNS | Per shard-hour, per message | Included |
| Managed Flink | Per KPU-hour | Included |
| EventBridge, EventBridge Scheduler | Per event, per invocation | Included |
| EKS | N/A | Per cluster-hour |
| EC2 | N/A | Per instance-hour |
| EC2 GPU capacity | N/A | Per accelerator-hour |
| RDS | N/A | Per instance-hour plus storage |
| S3 | N/A | Per GB stored and per request |

Akka provides spec-driven delivery, guardrails, red teaming, evaluations, AI policies, AI
orchestration, AI memory, AI routing, inference, and SLM training within a single integrated stack
that depends upon commodity infrastructure provided by the hyperscaler. Akka charges a fixed,
annual fee without metering. With the hyperscaler, you integrate various high margin services
together to create an AI solution. Each of those metered services include the relevant compute,
storage, and I/O infrastructure within their fees.

## AgentCore and the Akka SDK in detail

A production agent on AgentCore is assembled from separately provisioned services: Runtime, Memory, Gateway, Identity, Observability, Policy, Evaluations, and the managed harness that wires them together. Akka provides the same capabilities as components inside one deployable service on one runtime. AgentCore hosts an agent written in any framework and any language; the Akka SDK is Java.

Every AgentCore figure below is an AWS-published default taken from the AgentCore quota documentation on 28 August 2026. AWS marks some quotas adjustable through Service Quotas and the rest fixed.

### Execution and session lifetime

AgentCore Runtime places each user session in a dedicated microVM with isolated CPU, memory and filesystem, then terminates the microVM and sanitizes its memory when the session ends. A session is capped at 2 vCPU and 8 GB. The Instances compute type runs agents on EC2 in the customer's own account and raises the session ceiling to 14 days.

Akka addresses an agent instance by identity. The runtime routes each request to whichever cluster node currently owns that instance's state, and relocates the state as nodes join and leave. A run that waits on a human for three days holds no compute while it waits and resumes on whichever node is available when the human answers.

| Mechanism | AWS AgentCore | Akka |
|---|---|---|
| Unit of isolation | One microVM per user session, terminated at session end | One actor per agent or entity instance, single-owner sharded across the cluster and relocated while the system serves traffic |
| Hardware per unit | 2 vCPU and 8 GB per session, fixed | Instances share node capacity, and a single core holds 200 million actors |
| Session duration | 8 hours on microVMs, adjustable through `maxLifetime`; 14 days on Instances | No ceiling. A workflow suspends across crashes, deployments and days, then resumes at the step it stopped on |
| Synchronous request | 15 minutes, fixed | Long work runs as workflow steps, each with a timeout the developer sets and a default of 5 seconds |
| Idle behaviour | 15 minutes of inactivity terminates the execution environment, and a new one is created for the session | Idle state leaves memory and is rebuilt from its snapshot and journal on the next request |
| Streaming | 60-minute maximum connection, 64 KB WebSocket frames, 250 frames per second per connection, all fixed | Token-by-token model output over SSE and gRPC, backpressured end to end, with no external broker |
| Payload | 100 MB per request or response, fixed, with 10 MB streaming chunks | Set in service configuration |
| Concurrency ceiling | 5,000 active session workloads per account in N. Virginia and Oregon, 2,500 in other Regions, adjustable | Set by cluster size. Akka adds nodes as demand rises and scales to zero when a service goes idle |
| Admission rate | 25 new sessions per second and 1,000 data-plane requests per second per account, both adjustable | Akka applies no account-level admission quota, and backpressure propagates to the producer |

### Agent state and memory

AgentCore Memory is a regional service the agent calls across the network. `CreateEvent` writes conversation turns and `RetrieveMemoryRecords` reads them back. Long-term records are produced asynchronously by extraction strategies running against a token budget. Each memory resource holds at most six strategies, and events expire between 7 and 365 days.

Akka session memory is an event-sourced entity in the same runtime as the agent, identified by a session id and shared by every agent that uses that id. Reads complete in 4ms and writes in under 10ms because the state is already in memory on the node handling the request. The journal behind it is the same journal that restores the agent after a node failure.

A View projects entity events, workflow state changes, topic messages, or another Akka service's event stream into a read model that answers the queries an entity id cannot. Queries are declared on the view with `@Query` and reached over HTTP or gRPC. One view holds several tables and joins across them. A view is eventually consistent with the component that feeds it, and its queries run on compute that scales independently of the write side.

| Mechanism | AWS AgentCore | Akka |
|---|---|---|
| Where memory lives | A separate managed service, reached over the network | An event-sourced entity on the same runtime, held in memory on the node that owns it |
| Write path | `CreateEvent`, capped at 100 messages and 10 MB per event, 100 KB per message, and 5 calls per second per actor per session | The agent writes the user message and the model response automatically as events on the session entity |
| Read shaping | Retrieval of extracted records by namespace | `MemoryProvider.limitedWindow().readLast(n)`, read-only and write-only modes, and `MemoryFilter` to include or exclude messages by agent component id or agent role |
| Long-term knowledge | Built-in extraction strategies, 6 per memory resource, capped at 150,000 tokens per minute per account and 50,000 per session for episodic extraction | Durable memory in entities and views, with compaction that summarizes older context while the detail stays in the journal |
| Context window control | Extraction and summarization strategies | A 156 KiB history window by default, compaction, and a per-call limit on how many messages reach the model |
| Retention | Event expiration between 7 and 365 days | The journal is retained for the life of the service, and the interaction log is retained on the schedule the regulation sets |
| External store | AgentCore Memory, or a database the customer wires in | `MemoryProvider.custom()` implements the `SessionMemory` interface against any store |
| Query across instances | Retrieval from Memory by namespace, or a database the customer wires in and keeps updated | A View built from entity events, workflow state, topics or another service's stream, queried with `@Query` |
| Live query results | Polling the Memory or database API | `@Query(streamUpdates = true)` holds the result open and pushes matching updates as server-sent events, resuming from the last seen event id after a reconnect |
| Read-side scaling | `RetrieveMemoryRecords` at 30 requests per second per account, adjustable | Read-side queries run on compute that scales separately from the write side |
| Multi-region | A regional resource | Entities and workflows replicate across regions, with writes routed to a primary region and reads served locally |

### Multi-step orchestration

The managed agent harness in AgentCore runs the model-and-tool loop and takes per-invocation caps on iterations, timeout and tokens. Durable multi-step execution comes from AWS Step Functions, which calls the agent harness through an `InvokeHarness` state and holds the position of the run outside the agent. Session storage persists the files an agent wrote across a stop and resume, and where the reasoning had reached is reconstructed from Memory events or from the state machine.

The Akka Workflow component is the durable execution engine, and it runs on the same runtime as the agent. A step returns a `StepEffect` that updates state and transitions to the next step, and each transition is persisted before the next step begins, so a restart resumes at the last completed step boundary.

| Mechanism | AWS AgentCore | Akka |
|---|---|---|
| Durable execution | Step Functions runs the state machine outside the agent | The Workflow component stores its state in the runtime and persists every step transition as an event |
| Retries | Configured on the Step Functions state and on the agent harness invocation | `RecoverStrategy.maxRetries(n).failoverTo(step)`, set per workflow and overridden per step |
| Timeouts | 15 minutes for a synchronous invocation and 8 hours for an asynchronous job | `WorkflowSettings` carries a workflow timeout, a default step timeout, and per-step overrides |
| Undoing partial work | Written by the customer in the state machine | Compensation handlers reverse completed steps when a later step fails, which is the saga pattern inside the component |
| Human in the loop | An external queue and a state machine wait state | The workflow durably suspends and resumes, holds no compute while it waits, and emits `HumanDecisionRecorded` |
| Regional failover | Regional resources, replicated by the customer | Workflows run active-active across regions, and failover preserves progress and prevents duplicate side effects |

### Tools and the protocol surface

AgentCore Gateway converts OpenAPI, Smithy and Lambda targets into MCP tools, fronts other agents over A2A, routes inference across model providers, and searches a large tool catalogue semantically so the prompt carries fewer tool definitions.

In Akka a tool is a Java method annotated with `@FunctionTool`, defined on the agent itself, on an interface implemented elsewhere in the service, or on the command handler of an entity, workflow or view. Remote MCP servers are registered by URL with header and tool filters. The runtime executes the tool-call loop and stops it at `akka.javasdk.agent.max-tool-call-steps`, which defaults to 100 steps per request.

| Mechanism | AWS AgentCore | Akka |
|---|---|---|
| Tool definition | An OpenAPI, Smithy or Lambda target registered on a gateway | A method annotated `@FunctionTool`, including a command handler on a stateful component |
| Catalogue size | 100 targets per gateway and 1,000 tools per target, both adjustable | Set by the service. Tool schemas are held in memory alongside the agent |
| Tool discovery | Semantic tool search, capped at 25 searches per minute | Tools are registered on the agent, and MCP servers are filtered by tool name at registration |
| Invocation limits | 200 tool calls per second per gateway and per account, 6 MB payload, 15-minute timeout, all adjustable | 100 tool-call steps per request and response cycle by default, set in configuration |
| Publishing tools | Gateway exposes registered targets as MCP tools | `@McpEndpoint` publishes the service's own tools, and `@HttpEndpoint` and `@GrpcEndpoint` expose the same agent to other clients |
| Execution locality | The gateway invokes the target, and the agent reads the result over the network | The tool runs inside the runtime that owns the agent's state, so a guardrail decides before the call executes and the log records whether it executed |

### Endpoints and the API surface

An agent on AgentCore implements the Runtime service contract, which fixes a port and a mount path for each protocol: HTTP on port 8080 at `/invocations` with `/ws` for WebSocket, MCP on port 8000 at `/mcp`, A2A on port 9000 at the root, and AG-UI on port 8080. Callers reach the agent through `InvokeAgentRuntime` with SigV4 or OAuth 2.0. Each agent carries up to 10 endpoints, and an endpoint points at an immutable version, so a rollback repoints the endpoint at the version that worked.

In Akka an endpoint is a component in the same service as the agent. `@HttpEndpoint("/prefix")` classes expose typed HTTP methods, `@GrpcEndpoint` classes serve a protobuf service definition, and `@McpEndpoint` publishes tools, resources and prompt templates over the MCP Streamable HTTP transport. `@Acl` sits on the class or the method and names the principals allowed through. The same agent is reachable over HTTP, gRPC and MCP from one deployment.

| Mechanism | AWS AgentCore | Akka |
|---|---|---|
| Protocol surface | HTTP, MCP, A2A and AG-UI, each on the port and mount path the service contract fixes | `@HttpEndpoint`, `@GrpcEndpoint` and `@McpEndpoint` classes in the service, with A2A for agent-to-agent traffic |
| Inbound authentication | SigV4 or OAuth 2.0 at the runtime endpoint | `@Acl` principals at class and method level: the internet, any Akka service, or a named service |
| Versioned entry points | 10 endpoints per agent, adjustable, each pointing at an immutable version | Routes map hostnames and path prefixes to services, and rolling updates move traffic to the new version in waves |
| Public front door | API Gateway or an ALB in front of the runtime endpoint | Endpoints serve traffic directly, and customers front them with API Gateway where a gateway policy requires it |
| Calls between components | The agent calls another agent over A2A or through the gateway | The ComponentClient calls another component in the same service, and service-to-service calls carry the caller's identity |

### Streaming and event flow

AgentCore streams a model response to the caller over server-sent events and holds a bidirectional WebSocket for interactive sessions, capped at 60 minutes with 64 KB frames and 250 frames per second. Kinesis, MSK, EventBridge and Managed Flink provide event ingestion and stream processing, and the customer connects them to the agent.

Akka Streaming runs in the same runtime as the agent. A Consumer subscribes with `@Consume.FromEventSourcedEntity`, `@Consume.FromKeyValueEntity`, `@Consume.FromWorkflow`, `@Consume.FromTopic` or `@Consume.FromServiceStream`, and publishes with `@Produce.ToTopic` or `@Produce.ServiceStream`. Delivery is at least once, so a consumer is written to tolerate a duplicate. Event streams between Akka services need no broker and are backpressured from consumer to producer, and Tubi runs 5 billion tokens per second through that path.

| Mechanism | AWS AgentCore | Akka |
|---|---|---|
| Response streaming | Server-sent events from `/invocations`, and WebSocket for bidirectional sessions | Token-by-token model output to an HTTP endpoint as server-sent events, or over a gRPC stream |
| Event ingestion | Kinesis, MSK or EventBridge, wired to the agent by the customer | Consumers subscribe to entity journals, workflow state changes, broker topics, and event streams published by other Akka services |
| Stream processing | Managed Flink or Kinesis Data Analytics | Consumers and views process the stream inside the runtime that owns the state |
| Flow control | Frame size and frame rate caps per connection | Backpressure reaches the producer, so a slow consumer slows the source and no work is dropped |
| Delivery guarantee | Set by the service the customer wires in | At least once, with duplicate handling in the consumer |
| External brokers | Kinesis, MSK, SQS, SNS and EventBridge | Kafka on Confluent Cloud, AWS MSK, Aiven or a self-hosted cluster, and Google Cloud Pub/Sub |

### Identity and authorization

AgentCore Identity issues a workload identity to each agent, federates Okta, Microsoft Entra ID and Amazon Cognito for inbound authentication, and vends OAuth tokens and API keys to tools from a credential vault. An account holds 11,000 workload identities and 50 credential providers of each type.

Akka authorizes at the component boundary with `@Acl`, which names the principals allowed to reach an endpoint or a method: the internet, any Akka service, or a named service. The platform operates zero-trust with workload attestation. Every interaction-log event embeds the SPIFFE workload identity, the delegation chain from human to agent to sub-agent to tool, the effective permissions, the policy bindings and the governance version, all resolved at the moment of execution.

### Guardrails and policy enforcement

AgentCore Policy evaluates Cedar policies at the agent-to-tool boundary. A policy engine holds 1,000 policies of up to 10 KB each, 200 KB of policy per resource, and a Cedar schema of up to 400 KB generated from the tools across its gateways. AWS marks every one of those Policy limits fixed.

An Akka guardrail implements the `TextGuardrail` interface and is named in `application.conf`. The runtime applies it on every interaction, and no application code invokes it. Each entry binds to agents by component id or by agent role, declares a category, and lists the boundaries it applies to: `model-request`, `model-response`, `mcp-tool-request` and `mcp-tool-response`. A guardrail returns PASS, BLOCK or ERROR while the runtime holds the call, required guardrails fail closed, and `report-only` runs a new guardrail in observation before it starts blocking.

| Mechanism | AWS AgentCore | Akka |
|---|---|---|
| Enforcement point | The agent-to-tool boundary at the gateway | The model request, the model response, the tool request and the tool response |
| Policy language | Cedar, with policies generated from observed traffic | Java implementations of `TextGuardrail`, bound by configuration and owned by the compliance policy matrix |
| Failure mode | Set by the policy engine | Required guardrails fail closed, so a timeout or an error stops the action |
| Sensitive data | Bedrock Guardrails redacts PII at the inference boundary | Sanitizers redact, mask or reshape content at any step, and PII scrub-with-explain keeps the decision explainable after the attribute is removed |
| Human control | Built by the customer | HITL boundaries, durable workflow pause and resume, and a kill switch that halts in-flight and future tool and model calls and moves the system to a defined safe state |

### Evaluation

AgentCore Evaluations scores spans after a run completes. Online evaluation samples sessions and reads up to 1,000 spans from each sampled session. Built-in evaluators are capped at 100 evaluations and 200,000 input tokens per minute. An on-demand evaluation runs one evaluator and an online configuration runs ten. A batch job covers 500 sessions, with five running at once. A/B testing allows one test per gateway with two treatments.

An Akka evaluator is an Agent whose result implements `EvaluationResult`, which carries a pass or fail and the explanation behind it, and both land in metrics and traces. Observing mode reads runs after they complete. Inline mode runs in the transactional path as a guardrail. Inline mode stops, re-prompts or escalates before a response is emitted, and records the action, the verdict and the audit entry in one transaction. Akka Optimize grades production traffic continuously on the same records, including traffic from agents running in third-party harnesses.

### Interaction records and observability

AgentCore emits agent traces over OpenTelemetry into CloudWatch GenAI Observability, and its online evaluation reads a sample of sessions. Sampling is the cost control for a telemetry pipeline. A sampled record set contains the runs the sampler kept and omits the rest.

The Akka interaction log is non-sampled by contract and cryptographically hash-chained, in petabyte-scale storage that is indexed and queryable. The record the auditor receives is the record the runtime emitted. The same record feeds replay testing, conformance reconstruction, drift detection, test-dataset generation, incident investigation, and the training loop in Akka Optimize. Akka exports telemetry over OpenTelemetry, Prometheus remote write and Splunk HEC, so CloudWatch continues to receive it.

### Cluster behaviour under failure

Akka nodes form a self-organizing cluster with no primary node and no central coordinator. Nodes communicate over brokerless encrypted gRPC, and built-in split-brain resolution keeps the cluster consistent through a network partition. Shards rebalance as nodes join and leave, and requests follow the state. Calls to external systems are guarded with circuit breakers, retries with backoff and supervision, so a failing downstream stays isolated instead of cascading. The state on a lost node is rebuilt by replaying its latest snapshot and the events after it.

Rolling updates proceed in waves across regions while the system serves traffic, and they carry data-model changes without a maintenance window. Multi-region deployment is active-active, and each instance has a primary region that takes its writes. Routing is region-aware. Replication filters keep named records inside a geography for residency. Recovery targets are sub-1-minute RTO and zero-byte RPO, under a 99.9999% availability SLA that Akka owns and backs with contractual indemnities. AgentCore Runtime terminates the microVM at session end and sanitizes its memory, and Bedrock publishes 99.9% on API errors with service credits as the remedy.

### What the customer provisions

A production agent on AgentCore is provisioned as a Runtime agent, a Memory resource with its strategies, a Gateway with its targets, workload identities and credential providers in Identity, a policy engine in Policy, evaluation configurations, a Step Functions state machine, and a database. Each is a separate resource with its own quota and its own IAM role, and each account-level quota is a ceiling the whole estate shares.

An Akka service is one deployable unit. Agents, workflows, entities, views, timers, consumers and endpoints are classes in the same codebase. The components in that codebase share the runtime, the deployment, the identity model and the interaction log. The service runs on EKS in the customer's own VPC.
