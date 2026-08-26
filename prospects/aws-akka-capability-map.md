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
