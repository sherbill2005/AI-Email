# Advanced Rule Prioritization and Sub-Rules

## Feature Goal
To enhance the email filtering system by allowing users to define nested rules with priority tags, enabling more granular control over email processing, scoring, and storage decisions.

## Key Concepts & Requirements

### 1. Priority Tags
*   Each rule (and sub-rule) can be assigned a priority: `High`, `Medium`, `Low`.
*   These priorities will influence the overall match percentage and processing flow.

### 2. Sub-Rules (Nested Rules)
*   A main rule can contain a list of sub-rules.
*   Example: A "Job Related Emails" rule can have sub-rules like "Data Entry Jobs", "Location: USA", "Location: UK".
*   The system should process the main rule first, and if it matches, then proceed to evaluate its sub-rules.

### 3. Weighted Scoring
*   The match percentage for an email will be an aggregation of its sub-rule matches, weighted by priority.
*   **Proposed Weights:**
    *   `High` Priority Match: 50% weight
    *   `Low` Priority Match: 25% weight
    *   (Consider `Medium` Priority: e.g., 35-40% weight, or decide if it's needed)

### 4. Conditional Processing & Storage Rules

*   **Storage Threshold:** Emails are only stored in MongoDB if match score ≥ 50%.

*   **High-Priority Rules:**
    *   If defined and **not matched** → Reject immediately (score capped below 50%).
    *   If matched → Automatically store (50% threshold satisfied).

*   **Low-Priority Rules:**
    *   Each low-priority match = 25%.
    *   Need at least 2 matches (25% + 25% = 50%) to store.

*   **Case Scenarios:**

| Case | High Priority Rule | Low Priority Matches | Total Score | Result |
|---|---|---|---|---|
| 1 | ✅ Match | 0 | 50% | ✅ Store |
| 2 | ✅ Match | 1 | 75% | ✅ Store |
| 3 | ✅ Match | 2+ | ≥100% | ✅ Store |
| 4 | ❌ No Match (but high-priority exists) | Any | Capped < 50% | ❌ Reject |
| 5 | 🚫 No High Priority Defined | 2 | 50% | ✅ Store |
| 6 | 🚫 No High Priority Defined | 3 | 75% | ✅ Store |
| 7 | 🚫 No High Priority Defined | 1 | 25% | ❌ Reject |
| 8 | 🚫 No High Priority Defined | 0 | 0% | ❌ Reject |

## Impact on Existing System

### 1. Data Models (`app/models/rules_model.py`, `app/schemas/rules_schema.py`)
*   **`RuleModel`:**
    *   Add a `priority` field (e.g., `Enum` type: `High`, `Medium`, `Low`).
    *   Modify `RuleModel` to allow for a list of nested `RuleModel` instances (e.g., `sub_rules: List[RuleModel] = []`). This will require careful consideration of recursion in Pydantic.
*   **`RuleCreate`, `RuleUpdate` Schemas:** Update to include `priority` and `sub_rules`.

### 2. Filtering Logic (`app/services/filtering_service.py`)
*   **`EmailFilteringService.filter_emails_by_rules`:**
    *   Needs to be updated to handle the recursive evaluation of sub-rules.
    *   Implement the weighted score aggregation based on priority.
    *   Implement the conditional processing logic (e.g., if high-priority sub-rule doesn't match).
    *   The final return should be the aggregated percentage score.

### 3. Orchestration (`app/services/orchestration_service.py`)
*   The `process_incoming_email_notification` will need to use the new aggregated score from `EmailFilteringService` to decide whether to save the email to MongoDB (based on the 50% threshold).

### 4. API Endpoints (`app/apis/v1/rules_routes.py`, `app/apis/v1/filtering_routes.py`)
*   **Rule Management API:** The `rules_routes.py` will need to be updated to support creating and updating rules with nested structures and priority tags.
*   **Filtering API:** The `filtering_routes.py` might need minor adjustments if the input/output formats change due to the new scoring.
