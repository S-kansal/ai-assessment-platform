# MVP Product Specification — AI Engineering Assessment Platform

> **Version:** 1.1 · **Status:** Draft · **Date:** March 2026

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Design Principles](#2-design-principles)
3. [Target Users](#3-target-users)
4. [Role Being Assessed](#4-role-being-assessed)
5. [Capability Matrix](#5-capability-matrix)
6. [Task Types](#6-task-types)
7. [Structure of an Assessment Task](#7-structure-of-an-assessment-task)
8. [Evaluation Philosophy](#8-evaluation-philosophy)
9. [Telemetry Signals Captured During Assessment](#9-telemetry-signals-captured-during-assessment)
10. [MVP Features](#10-mvp-features)
11. [MVP Constraints](#11-mvp-constraints)
12. [Non Goals](#12-non-goals)
13. [MVP Success Criteria](#13-mvp-success-criteria)
14. [System Boundaries](#14-system-boundaries)

---

## 1. Product Overview

### The Problem

Technical hiring is broken — and nowhere more visibly than in AI engineering.

The standard interview playbook still leans on algorithm puzzles, whiteboard coding challenges, and theoretical knowledge checks borrowed from an era when "software engineering" meant building CRUD applications and optimising data structures. These methods were designed to test computer science fundamentals, not the day-to-day reality of modern AI engineers who spend their time wiring together retrieval pipelines, tuning prompts, debugging hallucinating agents, and shipping evaluation frameworks.

The result is a persistent mismatch: companies filter for candidates who can invert binary trees but have no reliable signal on whether those same candidates can diagnose why a RAG system is returning irrelevant documents or why an LLM agent is calling the wrong tools.

### The Shift Toward AI System Engineering

The industry has moved decisively toward **applied AI engineering**. The fastest-growing engineering roles today involve:

- Designing and maintaining **Retrieval-Augmented Generation (RAG)** systems
- Crafting and iterating on **prompts and prompt chains**
- Building and debugging **autonomous agents**
- Implementing **evaluation pipelines** to monitor model quality at scale
- Integrating **model APIs** (OpenAI, Anthropic, open-source models) into production applications

These are not theoretical skills. They require hands-on debugging intuition, systems thinking, and iterative problem-solving — none of which are captured by a timed algorithm quiz.

### Our Approach: Simulation-Based Assessment

The **AI Engineering Assessment Platform** replaces abstract coding puzzles with **realistic, simulation-based assessments** that mirror the actual work of an AI engineer. Candidates interact with simulated AI systems — broken RAG pipelines, unstable prompts, misbehaving agents — and are evaluated on how they diagnose, debug, and fix real-world problems.

This approach is grounded in a simple principle: **the best predictor of job performance is a structured sample of the job itself.**

### How We Differ

| Dimension | Traditional Platforms (HackerRank, LeetCode) | AI Assessment Platform |
|---|---|---|
| **Task Focus** | Algorithmic puzzles and data structure problems | AI system debugging and iterative problem-solving |
| **Knowledge Type** | Theoretical computer science | Applied AI engineering |
| **Problem Format** | Isolated coding challenges with fixed inputs/outputs | Realistic system scenarios with simulated AI components |
| **Evaluation Method** | Binary pass/fail on test cases | Multidimensional scoring including reasoning and process |
| **Candidate Experience** | Competitive puzzle-solving under time pressure | Realistic engineering work with debugging and iteration |
| **Signal Quality** | Measures algorithmic ability | Measures ability to build and debug AI systems |
| **Relevance to Role** | Low correlation with day-to-day AI engineering work | Direct simulation of on-the-job tasks |

---

## 2. Design Principles

Core principles guiding the platform design.

### Work-Sample Testing

Candidates must perform tasks similar to real AI engineering work. The platform prioritizes realistic problem solving over theoretical questions. Every assessment scenario is modelled on actual engineering challenges encountered in production AI systems.

### Process-Aware Evaluation

The platform evaluates *how* candidates solve problems, not just their final answers. Debugging strategy, hypothesis formation, and iteration quality are all first-class evaluation signals alongside task completion.

### Deterministic Testing Environment

AI simulations must produce consistent, repeatable outputs so that candidates are evaluated fairly. Given the same inputs and actions, the simulation environment returns the same results — eliminating variance caused by non-deterministic model behaviour.

### Behavioral Signal Capture

Telemetry data such as iteration count, debugging path, and reasoning actions must be captured throughout the assessment. These behavioural signals provide the raw data for scoring dimensions beyond simple task success.

### Task Isolation

Each assessment task must test a single capability to maintain measurement clarity. A RAG debugging task measures RAG debugging ability; a prompt engineering task measures prompt engineering ability. Cross-capability contamination is avoided by design.

### Extensible Architecture

The system must allow new task types and AI capabilities to be added over time without requiring fundamental changes to the platform's core infrastructure. Task definitions, simulation configurations, and scoring rubrics are designed as pluggable components.

---

## 3. Target Users

### Primary Users — Hiring Teams

The platform is built for **engineering hiring teams** who are responsible for evaluating AI engineering talent:

- **Engineering Managers** who need to assess whether candidates can operate autonomously on AI system problems from day one.
- **AI/ML Team Leads** who need to validate practical competence with RAG systems, prompt engineering, and agent architectures before extending offers.
- **ML Platform Teams** building internal AI infrastructure and seeking engineers who can debug and extend complex pipelines.
- **Technical Recruiters** and recruiting teams hiring for AI engineering roles who need a structured, standardised evaluation tool that goes beyond resume screening.

**Their core question is singular:**

> *"Can this candidate actually build and debug AI systems — or do they just know the theory?"*

The platform provides a definitive, evidence-backed answer through simulated task performance, behavioural telemetry, and structured scoring.

### Secondary Users — Candidates

AI engineer candidates are the people who **take the assessments**. The candidate experience is designed around the following principles:

- **Realistic engineering tasks** — Candidates work on problems that feel like genuine engineering work, not contrived puzzles. This respects their time and gives them a fair opportunity to demonstrate real ability.
- **Reasoning and iteration are valued** — The platform captures *how* candidates approach problems, not just whether they get the right answer. Iterative debugging, hypothesis testing, and systematic reasoning are all positively scored.
- **Not a puzzle contest** — There are no trick questions, obscure edge cases designed to trip candidates up, or artificial time constraints that reward memorisation over thinking. The assessment rewards the skills that matter on the job.

---

## 4. Role Being Assessed

### MVP Focus: AI Application Engineer / Applied AI Engineer

For the MVP, the platform targets a **single role**: the **AI Application Engineer** (also referred to as Applied AI Engineer, LLM Engineer, or AI Systems Engineer depending on the organisation).

This role sits at the **application layer** of the AI stack. These engineers do not train foundation models or conduct ML research. Instead, they build, integrate, and operate the systems that turn model capabilities into working products.

### Typical Responsibilities

An AI Application Engineer is expected to:

- **Build RAG systems** — Design and implement retrieval-augmented generation pipelines including document ingestion, chunking strategies, embedding generation, vector storage, retrieval logic, and response synthesis.
- **Design prompts** — Author, test, and iterate on system prompts, user-facing prompts, and prompt chains that drive model behaviour in production applications.
- **Debug AI outputs** — Investigate and resolve issues such as hallucinations, off-topic responses, inconsistent outputs, and quality regressions across model versions.
- **Integrate model APIs** — Connect applications to LLM providers (OpenAI, Anthropic, Google, open-source models), manage API configurations, handle rate limiting, implement fallback strategies, and optimise cost.
- **Orchestrate AI workflows** — Build multi-step pipelines and agentic workflows where models, tools, retrievers, and business logic interact in sequence.
- **Implement evaluation pipelines** — Design and deploy automated evaluation frameworks that monitor output quality, detect regressions, and measure system performance over time.

### Why This Role First

This role was selected for the MVP because:

1. **Highest industry demand** — AI Application Engineer is one of the fastest-growing technical roles. Nearly every technology company is investing in LLM-powered products, creating massive demand for engineers who can build and operate these systems.
2. **Broadest applicability** — Most companies hiring AI talent are hiring at the application layer. They need engineers who can ship AI features, not researchers who can write papers.
3. **Clear skill boundaries** — The role has well-defined, testable competencies (prompt engineering, RAG debugging, agent orchestration) that translate naturally into simulation-based assessment tasks.

---

## 5. Capability Matrix

| Capability | Description | Example Behavior |
|---|---|---|
| Prompt Engineering | Designing and iterating prompts to achieve reliable outputs | Improve prompt to eliminate hallucination |
| RAG Debugging | Diagnosing failures in retrieval-augmented systems | Identify bad chunking causing wrong answers |
| Workflow Reasoning | Understanding multi-step AI system pipelines | Detect failure in retrieval stage |
| Output Evaluation | Assessing correctness of AI outputs | Identify hallucinated facts |
| Failure Diagnosis | Root-cause analysis of system issues | Identify prompt formatting bug |

This matrix forms the foundation for the platform's scoring model, capability taxonomy, and candidate skill measurement system. Each capability maps to one or more task types, and candidate scores are broken down along these dimensions to give hiring teams a granular view of strengths and gaps.

---

## 6. Task Types

The MVP includes four simulation-based task types. Each task places the candidate inside a realistic scenario with a broken or underperforming AI system and evaluates their ability to diagnose and fix the problem.

### Task Type 1: RAG Debugging

**Scenario:** A user asks a question and the system returns an incorrect or irrelevant answer, despite the correct source documents being present in the knowledge base.

**What the candidate sees:**
- The user query and the system's incorrect response
- Access to the document store and retrieval logs
- The prompt template used for response generation
- Retrieval results showing which chunks were pulled

**The candidate must identify and fix issues such as:**
- **Retrieval failure** — the retriever is pulling wrong documents due to poor query-embedding alignment
- **Chunking problems** — source documents are split in ways that break critical context across chunk boundaries
- **Prompt formatting issues** — retrieved context is injected into the prompt incorrectly, causing the model to ignore or misinterpret the evidence

---

### Task Type 2: Prompt Stability Fix

**Scenario:** A candidate receives a production prompt that produces **inconsistent and unreliable outputs** — sometimes correct, sometimes off-topic, sometimes hallucinated — even when given identical or similar inputs.

**Goal:** Improve the prompt's robustness and output consistency without changing the underlying model.

**Evaluation focuses on:**
- **Instruction clarity** — rewriting vague or ambiguous instructions into precise, unambiguous directives
- **Prompt structure** — reorganising prompt sections (system instruction, context, constraints, output format) to reduce model confusion
- **Few-shot examples** — adding or improving examples that anchor the model's behaviour and reduce output variance

---

### Task Type 3: Agent Failure Diagnosis

**Scenario:** An AI agent designed to complete multi-step tasks is **repeatedly calling incorrect tools** or executing tool calls in the wrong order, causing task failures.

**The candidate must:**
- **Analyse tool schemas** — review the available tools, their descriptions, parameter definitions, and expected behaviours to identify ambiguity or misalignment
- **Inspect reasoning traces** — examine the agent's step-by-step reasoning logs to understand why it selected the wrong tools
- **Fix orchestration logic** — correct the agent's system prompt, tool descriptions, or workflow configuration to resolve the misbehaviour

---

### Task Type 4: AI Output Evaluation

**Scenario:** The candidate receives a set of model-generated outputs for a given query and context, and must evaluate their quality.

**The candidate must identify:**
- **Correct outputs** — responses that accurately and completely answer the query based on available context
- **Hallucinated outputs** — responses that contain fabricated information not supported by the provided context
- **Reasoning behind evaluation** — a clear explanation of why each output is classified as correct, partially correct, or hallucinated, citing specific evidence

---

## 7. Structure of an Assessment Task

Every assessment task follows a consistent structure so the platform can evaluate candidates reliably across different task types and scenarios.

### Context

A high-level description of the system being tested. This orients the candidate by explaining the business purpose, the users of the system, and the general technology involved.

### System Description

A detailed explanation of the simulated AI system the candidate will interact with — whether it is a RAG pipeline, a prompt workflow, an agent system, or another AI component. This includes the key components, data flow, and how the system is expected to behave when operating correctly.

### Tools Available

Tools candidates can use during debugging:

- **Prompt editor** — modify system prompts, user prompts, and prompt templates
- **System logs** — inspect execution logs, error messages, and trace outputs
- **Retrieval viewer** — examine retrieved documents, chunk contents, and similarity scores
- **Test query runner** — execute queries against the simulated system and observe outputs

### Problem Statement

A clear description of the failure or unexpected behaviour the candidate must diagnose. This explains what is going wrong without revealing the root cause.

### Interactive Environment

Candidates interact with the simulated system through:

- Prompt editing and submission
- Running test queries and observing model outputs
- Inspecting logs and retrieval results
- Analysing system traces and debugging information

### Candidate Actions

Possible actions candidates can perform during the assessment:

- Modify prompt templates or instructions
- Inspect system logs and error traces
- Inspect retrieved documents and chunk boundaries
- Run test queries against the simulated system
- Submit a written explanation of the root cause and fix

### Success Criteria

Each task defines explicit success criteria that determine whether the candidate has solved the problem. Example success criteria include:

- The system produces the correct output for the test query
- The hallucination is eliminated from the response
- The root cause is correctly identified in the candidate's explanation

### Example Task: RAG Debugging

**Context:** A customer support chatbot uses a document retrieval pipeline to answer product questions from a knowledge base.

**Problem:** The model is answering incorrectly even though the correct document exists in the knowledge base. Users are receiving confident but wrong answers.

**The candidate must:**
1. Inspect retrieved chunks to determine if the correct document is being retrieved
2. Inspect the prompt template to check how retrieved context is injected
3. Adjust the prompt or retrieval settings to resolve the incorrect answers

---

## 8. Evaluation Philosophy

### Beyond Right or Wrong

Traditional coding assessments operate on a binary model: the code passes the test cases, or it doesn't. AI engineering work is fundamentally different. Two engineers might solve the same prompt engineering problem with very different approaches, both valid. One engineer might reach a solution quickly through experience; another might reach a better solution through systematic experimentation.

**The platform evaluates the full arc of problem-solving, not just the endpoint.**

### Evaluation Dimensions

Candidate performance is measured across five dimensions, combining **objective task success** with **behavioural telemetry** and **efficiency signals**:

#### Task Success
> Did the candidate solve the problem?

The most straightforward dimension. Measures whether the candidate's final submission resolves the issue — the RAG system returns correct answers, the prompt produces stable outputs, the agent calls the right tools.

#### Diagnostic Reasoning
> Did they correctly identify the root cause?

Measures whether the candidate diagnosed the actual underlying issue, not just applied a superficial fix. A candidate who identifies that retrieval failures stem from a chunking strategy problem scores higher than one who brute-forces a prompt workaround.

#### Iteration Strategy
> Did they improve the system through structured, iterative changes?

Measures the quality of the candidate's debugging process. Effective AI engineers form hypotheses, test them, observe results, and refine their approach. The platform captures this iteration loop through telemetry.

#### Tool Usage
> Did they effectively use the available debugging tools and information?

Measures whether the candidate leveraged available resources — logs, retrieval results, trace outputs, documentation — to inform their debugging. Strong candidates use evidence; weak candidates guess.

#### Time Efficiency
> How quickly did they reach a working solution?

A secondary signal that, combined with the other dimensions, distinguishes between experienced engineers who recognise patterns quickly and those who are still developing their intuition.

### Why Process Matters

AI engineering problems rarely have a single correct answer. A prompt can be improved in dozens of valid ways. A RAG retrieval issue can be addressed at the chunking layer, the embedding layer, or the prompt layer. By capturing the candidate's full reasoning and iteration process, the platform provides hiring teams with **far richer signal** than a binary pass/fail metric — enabling confident, defensible hiring decisions.

---

## 9. Telemetry Signals Captured During Assessment

The platform records behavioural telemetry throughout each assessment session to measure candidate problem-solving processes. These signals go beyond task outcomes to capture the full arc of how a candidate approaches, investigates, and resolves AI system problems.

| Signal | Description |
|---|---|
| `prompt_edit` | Candidate modifies a prompt template or instruction |
| `test_run` | Candidate runs a model query against the simulated system |
| `retrieval_inspection` | Candidate inspects retrieved chunks or retrieval results |
| `tool_usage` | Candidate invokes an available debugging tool |
| `reasoning_note` | Candidate writes an explanation or reasoning annotation |
| `solution_submit` | Candidate submits their final answer or fix |

These signals power the platform's behavioural evaluation system. By analysing the sequence, frequency, and timing of these events, the Scoring Engine measures iteration patterns (how many prompt edits before a test run), debugging strategies (whether the candidate inspects logs before making changes), and reasoning behaviour (whether the candidate documents their thinking). This telemetry data also enables the session replay feature in the Hiring Manager Dashboard.

---

## 10. MVP Features

The MVP consists of six core components that together deliver the end-to-end assessment experience.

### Candidate Interface

A **web-based interface** where candidates complete their assessments. The interface provides:

- **Task briefing panel** — reads the scenario description, objectives, and available resources
- **Interactive workspace** — a working area where candidates interact with the simulated AI system (edit prompts, inspect retrieval results, view agent traces)
- **Submission mechanism** — allows candidates to submit their fixes and solutions when ready
- **Clean, focused design** — minimal distractions, professional appearance, with clear navigation between task sections

### Task Engine

The **orchestration layer** responsible for delivering assessment tasks to candidates:

- Loads task definitions (scenario, initial system state, evaluation criteria)
- Manages task lifecycle (assignment, timing, submission)
- Serves task content to the candidate interface
- Validates submissions against task requirements

### Simulation Environment

The core differentiator — a **simulated AI system** that candidates interact with as if they were debugging a real production system:

- **Prompt engine** — simulates an LLM that responds to prompt changes, allowing candidates to iterate on prompts and observe output differences
- **RAG pipeline** — simulates document retrieval, chunking, embedding, and context injection with configurable failure modes
- **Agent workflow** — simulates a tool-using agent with reasoning traces, tool call logs, and configurable misbehaviours

The simulation environment produces **deterministic, repeatable behaviour** so that candidate performance is comparable across sessions.

### Telemetry System

A **behavioural logging system** that captures candidate actions throughout the assessment:

- Records every meaningful action: prompt edits, parameter changes, log inspections, tool interactions
- Timestamps all events for session reconstruction
- Captures debugging steps and reasoning attempts
- Provides the raw data that powers the Scoring Engine and session replay

### Scoring Engine

The **evaluation computation layer** that transforms raw telemetry and task outcomes into structured scores:

- **Task success scoring** — automated evaluation of whether the candidate's final submission resolves the issue
- **Behavioural analysis** — processes telemetry to assess diagnostic reasoning, iteration strategy, and tool usage
- **Time-based signals** — factors time efficiency into overall scoring
- **Composite scoring** — produces a weighted overall score and per-dimension breakdown

### Hiring Manager Dashboard

A **web-based dashboard** for hiring teams to review candidate results:

- **Candidate scorecard** — overall score with capability breakdown across all evaluation dimensions
- **Dimension analysis** — detailed view of performance in each scored dimension (task success, diagnostic reasoning, iteration strategy, tool usage, time efficiency)
- **Session replay** — step-by-step replay of the candidate's assessment session, showing their actions, edits, and debugging process in chronological order
- **Comparison view** — ability to compare candidates side-by-side on key metrics

---

## 11. MVP Constraints

The MVP intentionally limits scope to ensure rapid validation and manageable engineering complexity. These constraints define the boundaries within which the first version operates.

- **One role supported:** AI Application Engineer only
- **Four task types implemented:** RAG Debugging, Prompt Stability Fix, Agent Failure Diagnosis, and AI Output Evaluation
- **Deterministic simulation environments:** All simulations produce consistent, repeatable outputs
- **No real LLM API calls:** The simulation environment uses pre-configured responses, not live model inference
- **Maximum test duration:** 60 minutes per assessment session
- **Maximum tasks per assessment:** 4 tasks per candidate session

These constraints ensure **fairness** (every candidate encounters the same deterministic environment), **reproducibility** (results are consistent and comparable across sessions), and **development focus** (the engineering team can validate the core assessment model before expanding scope).

---

## 12. Non Goals

The following items are **explicitly excluded from the MVP**. These represent valid product directions that may appear on the future roadmap, but are intentionally out of scope for the first version to maintain focus and shipping velocity.

### Certification Programs
The platform will **not** offer certifications, badges, or credential programs for candidates. The MVP is an assessment tool for hiring teams, not a credentialing system.

### Public Preparation Tests
There will be **no public-facing practice tests or preparation materials**. The integrity of the assessment depends on task scenarios not being publicly available. Preparation resources may be considered in the future with appropriate test rotation.

### Multiple Role Assessments
The MVP assesses **one role only**: AI Application Engineer. Assessment modules for other roles (ML Engineer, Data Engineer, AI Research Engineer, MLOps Engineer) are future extensions.

### Large Question Libraries
The MVP launches with a **small, curated set of assessment tasks** (one per task type). Building a large, rotating question bank is a future investment that depends on validating the core assessment model first.

### Adaptive Testing
The assessment is **fixed-format** in the MVP. Adaptive testing that adjusts difficulty based on candidate performance is a future enhancement requiring significant additional complexity in the Task Engine and Scoring Engine.

### Enterprise Integrations
The MVP operates as a **standalone platform**. Integrations with ATS platforms (Greenhouse, Lever, Ashby), SSO providers, HRIS systems, and other enterprise tools are not included. These will be prioritised based on customer demand post-launch.

---

## 13. MVP Success Criteria

The MVP will be considered successful if the following conditions are met:

1. **Candidates can complete tasks without technical issues.** The Candidate Interface, Task Engine, and Simulation Environment function reliably end-to-end, allowing candidates to read tasks, interact with simulated systems, and submit solutions without errors or interruptions.

2. **Telemetry logs capture full candidate behaviour.** The Telemetry System records all meaningful candidate actions — prompt edits, test runs, log inspections, reasoning notes, and submissions — with accurate timestamps and complete session coverage.

3. **Tasks produce meaningful score variation across candidates.** Assessment tasks differentiate between candidates of varying skill levels, producing a distribution of scores rather than clustering all candidates at the same level.

4. **Hiring managers can review candidate results through the dashboard.** The Hiring Manager Dashboard displays candidate scorecards, capability breakdowns, and session replays in a clear, actionable format.

5. **Platform operates reliably with at least 10 concurrent assessment sessions.** The system handles multiple simultaneous candidates without degradation in performance, simulation accuracy, or telemetry capture.

These criteria ensure the platform produces **measurable hiring signal** — validated through real candidate assessments and hiring team feedback — before expanding feature scope, adding new roles, or investing in enterprise integrations.

---

## 14. System Boundaries

The following clarifies what the platform is responsible for versus what falls outside its scope.

**The AI Assessment Platform is responsible for:**

- Delivering assessment tasks to candidates
- Simulating AI system behaviour (RAG pipelines, prompt engines, agent workflows)
- Capturing candidate telemetry throughout assessment sessions
- Evaluating task outcomes against defined success criteria
- Computing candidate capability scores across all evaluation dimensions
- Presenting results and session replays to hiring managers

**The platform is NOT responsible for:**

- Resume screening or candidate sourcing
- Scheduling interviews or managing calendars
- Applicant tracking or hiring pipeline management
- HR workflow management (offer letters, onboarding, compliance)
- Training, fine-tuning, or hosting AI models

These boundaries ensure the platform remains focused on its core value proposition — measuring applied AI engineering ability — without duplicating functionality provided by existing ATS, HRIS, or scheduling tools.

---

*This document defines the scope, philosophy, and feature set for the MVP of the AI Engineering Assessment Platform. All implementation planning, technical architecture, and sprint planning should reference this specification as the source of truth for what is — and what is not — in scope.*
