# Evaluation

RepoBrain v1 evaluates two things:

- retrieval quality
- grounding quality

## Fixture Repos

- Python service fixture
- TypeScript application fixture

## Metrics

- Recall@k
- Mean Reciprocal Rank
- citation accuracy
- edit-target hit rate

## Acceptance Queries

- "Where is payment retry logic implemented?"
- "Trace login with Google from route to service"
- "What breaks if I change auth callback handling?"
- "Which files should I edit to add GitHub login?"

## Regression Thresholds

Suggested minimums for the built-in fixture pack:

- Recall@3 >= 0.66
- MRR >= 0.50
- citation accuracy >= 0.66
- edit-target hit rate >= 0.66

## Failure Modes To Track

- wrong route file outranks the actual callback handler
- background job is retrieved without the queue or handler
- provider-specific login requests miss config or service code
- confidence remains high even when evidence is thin
