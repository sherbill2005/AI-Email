# Feature: AI-Powered Email Filtering and Categorization

This document outlines the workflow, algorithms, and project structure for implementing a new feature that allows users to define rules to filter and find specific emails. The core of this feature is an AI model that can understand the user's intent behind a rule (e.g., "find job-related emails") and apply it to the content of the emails.

## 1. Workflow

The overall workflow for this feature can be broken down into two main parts: Rule Management and AI-Powered Email Filtering.

### 1.1. Rule Management

1.  **User Defines Rules:** The user creates one or more rules through a new set of API endpoints. Each rule will consist of a natural language description of the emails to be found (e.g., "Emails related to job applications and recruitment", "Invoices and receipts", "Newsletters from tech companies").
2.  **Rules are Stored:** The rules are saved in a dedicated MongoDB collection. Each rule will have a unique ID, a name, and a natural language description.

### 1.2. AI-Powered Email Filtering

1.  **User Initiates Filtering:** The user triggers the filtering process via a new API endpoint, selecting one or more rules to apply.
2.  **Fetch Emails:** The system fetches the user's emails from their Gmail account. The scope of fetching can be defined (e.g., last 100 emails, unread emails, emails from the last 7 days).
3.  **AI-Powered Rule Application:** The filtering service retrieves the user-defined rules from the database. For each email, the AI model analyzes its content (subject and body) against the natural language description of each rule.
4.  **Categorize and Return:** If the AI model determines that an email's content matches a rule's description with a high confidence score, the email is categorized with that rule's name. The system then returns a list of the filtered and categorized emails to the user.

## 2. Algorithms and Filtering Logic

The primary approach for this feature is AI-based classification. A simpler, keyword-based matching system can be maintained as a secondary option for more explicit filtering needs.

### 2.1. Primary Approach: AI-Powered Rule Engine

This approach leverages a Natural Language Processing (NLP) model to classify emails based on their content. This is more flexible and powerful than simple keyword matching as it can understand the semantics and context of the email content.

*   **Zero-Shot Classification:** We will use a pre-trained model from the Hugging Face Hub capable of zero-shot text classification. The user's natural language rule description (e.g., "job listing," "receipt," "social media update") will be used as the candidate labels for the classification model. This allows the user to define rules in a very intuitive and flexible way.

**Algorithm:**

1.  For each email, extract the text content (subject and body).
2.  For each user-defined rule to be applied, use the rule's natural language `description` as a classification label.
3.  Pass the email content and the set of rule descriptions (labels) to the zero-shot classification model.
4.  The model will return a probability score for each label. If the score for a label exceeds a certain threshold (e.g., 0.8), the email is classified as belonging to that category.

**Recommended Model:** A model like `facebook/bart-large-mnli` or other models fine-tuned on NLI (Natural Language Inference) are good candidates for zero-shot classification.

### 2.2. Secondary Approach: Simple Matching

This approach uses straightforward matching on the email's metadata and content and can be used for rules that require very specific and literal matching.

*   **Sender Matching:** Matches the `From` field against a list of senders.
*   **Subject/Body Keyword Matching:** Matches keywords in the email's subject or body.

## 3. Proposed Project Structure Changes

To implement this feature, the following additions and modifications to the project structure are proposed:

```
app/
├── apis/
│   └── v1/
│       ├── routes.py
│       └── rules_routes.py  # New: Routes for rule management
├── core/
│   └── config.py
├── db_utils/
│   ├── mongo.py
│   └── redis.py
├── models/
│   ├── email_model.py
│   ├── user_model.py
│   └── rule_model.py      # New: Pydantic model for rules
├── schemas/
│   ├── email_schema.py
│   ├── user_schema.py
│   └── rule_schema.py       # New: Schema for rule creation and response
├── services/
│   ├── ai_model_services.py
│   ├── orchestration_service.py
│   ├── service_handler.py
│   ├── filtering_service.py # New: Service for filtering emails
│   └── rule_service.py      # New: Service for CRUD operations on rules
│   └── google_services/
│   └── user_services/
└── utils/
    └── helpers.py
```

## 4. API Endpoint Definitions

### 4.1. Rule Management (`/apis/v1/rules`)

*   **`POST /`**: Create a new rule.
    *   **Request Body:** `RuleCreationSchema` (name, description)
    *   **Response:** `RuleResponseSchema` (the created rule)
*   **`GET /`**: Get all rules.
    *   **Response:** `List[RuleResponseSchema]`
*   **`GET /{rule_id}`**: Get a single rule by its ID.
    *   **Response:** `RuleResponseSchema`
*   **`PUT /{rule_id}`**: Update an existing rule.
    *   **Request Body:** `RuleUpdateSchema`
    *   **Response:** `RuleResponseSchema`
*   **`DELETE /{rule_id}`**: Delete a rule.
    *   **Response:** `{"message": "Rule deleted successfully"}`

### 4.2. Email Filtering (`/apis/v1/filter`)

*   **`POST /`**: Filter emails based on a set of rules.
    *   **Request Body:** `{"rule_ids": ["id1", "id2"]}`
    *   **Response:** A list of categorized emails.

## 5. Database Schema for Rules

A new collection named `rules` will be created in MongoDB. Each document in this collection will represent a filtering rule.

**Pydantic Model (`rule_model.py`):**

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Rule(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    description: str # Natural language description of the rule for the AI model
```