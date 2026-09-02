# Chapter 2: Introduction to Machine Learning Systems Design

**Source**: Designing Machine Learning Systems — Chip Huyen, Chapter 2

## Core Idea

ML systems design starts with why, not with an algorithm. A business objective must be translated into measurable ML objectives, bounded by system requirements, and revisited through an iterative lifecycle. Only then should the team frame the request as a task with inputs, outputs, and an objective function. Data quality and quantity remain foundational: sophisticated algorithms cannot rescue data that is irrelevant, stale, biased, or mislabeled.

## Frameworks Introduced

The four broad system requirements are reliability, scalability, maintainability, and adaptability. The six-step loop is project scoping; data engineering and training-data creation; model development; deployment; monitoring and continual learning; and business analysis feeding the next scope. Problem framing distinguishes classification, regression, binary, multiclass, high-cardinality, and multilabel tasks. Multiple objectives can be decoupled into separate models whose outputs are combined at serving time.

## Key Concepts

Business metrics may be revenue, conversion, retention, cost, or customer satisfaction; accuracy and F1 matter only insofar as they influence them. A/B tests can connect model behavior to business outcomes, but complex pipelines may make attribution difficult. Reliability means correct behavior despite faults, including silent prediction errors. Scalability includes model complexity, request volume, and model count, plus automated monitoring, retraining, and reproducible artifact management. Maintainability requires documented code, versioned code/data/artifacts, reproducibility, and collaboration across engineers and subject-matter experts. Adaptability means detecting improvement opportunities and updating for shifting data and requirements without service interruption.

Framing changes difficulty. Classification predicts a category; regression predicts a continuous value, and either can sometimes be reframed as the other. Multiclass assigns one class, whereas multilabel permits several and complicates annotation and thresholding. High-cardinality classification makes rare classes and data collection difficult; hierarchical classification can split a large taxonomy into stages. For next-app prediction, classifying over every app makes adding an app expensive. A regression-style score over user, context, and app features produces one score per candidate and accommodates new apps more easily.

An objective or loss function guides learning and is distinct from a business objective. When ranking a feed, quality and engagement can be combined into one weighted loss, but changing the weights requires retraining. Separate quality and engagement models allow the serving layer to adjust their score weights without retraining and allow different maintenance schedules.

## Mental Models

Treat requirements as a contract among stakeholders, with must-haves distinguished from preferences. Treat the lifecycle as a cycle, not “collect, train, deploy, done.” Treat problem framing as an architectural decision: it determines label shape, candidate growth, retraining burden, and evaluation. Treat data as an essential resource rather than a final polish; more low-quality data can hurt.

## Anti-patterns

- Celebrating an ML metric without a business hypothesis.
- Beginning with a complex model before a baseline and working pipeline.
- Packing conflicting goals into one inseparable model by default.
- Randomly choosing a task framing that makes new classes or candidates expensive.
- Assuming data quantity automatically compensates for poor quality.
- Ignoring reliability, tail latency, maintainability, or adaptation until launch.

## Worked Example

A bank receives slow customer-service responses. Investigation finds that routing each request to one of four departments is the bottleneck. The request becomes a classification problem: the customer request is input, the department is output, and the training objective compares predicted with actual routing. The same design can later be measured against response time and customer outcomes, not only classification scores.

## Key Takeaways

Start with business impact and stakeholder requirements. Select a task framing that supports the operational future. Prefer decoupled objectives when trade-offs and update cadences differ. Build a loop that can collect data, evaluate outcomes, and change scope. Intelligent algorithms and data both matter, but usable data is non-negotiable.

## Connects To

Chapter 3 supplies the data systems needed by the loop. Chapter 4 curates samples and labels; Chapter 5 turns them into features; Chapter 6 trains and evaluates models. Deployment and post-deployment chapters complete the iterative cycle.
