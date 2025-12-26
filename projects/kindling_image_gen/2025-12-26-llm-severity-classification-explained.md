# LLM Severity Classification - Learning Deep Dive

**Date:** December 26, 2025
**Context:** Gemini Tier 1 Review - Low Priority Issue
**Brent Learning Mode:** Why keyword filtering is brittle and how LLM classification is better

---

## The Problem: Keyword Filtering

**Before:**
```python
# Collect all issues from vision analysis
all_issues = []
for criterion in analysis.values():
    if isinstance(criterion, dict) and 'issues' in criterion and criterion['issues']:
        all_issues.extend(criterion['issues'])

# Filter out "minor" issues using keyword matching
critical_issues = [
    issue for issue in all_issues
    if not any(minor in issue.lower() for minor in ['minor', 'slight', 'small', 'slightly'])
]

# Fail image if ANY critical issues found
passes_threshold = (
    overall_score >= 7.0
    and checklist_completion >= 0.85
    and len(critical_issues) == 0  # No critical issues allowed
)
```

**What this does:**
- LLM describes issues as plain strings: `"Slightly elongated fingers on left hand"`
- Python scans each issue string for keywords: `['minor', 'slight', 'small', 'slightly']`
- If keyword found → classify as "minor" (acceptable)
- If keyword NOT found → classify as "critical" (reject image)

---

## Why Keyword Filtering is Brittle

### Problem 1: False Negatives (Missing Critical Issues)

**Example:**
```json
{
  "issues": ["Hand has 7 fingers, slightly visible in shadow"]
}
```

**What happens:**
- Keyword match: `"slightly"` found → classified as **Minor**
- Reality: 7 fingers is a **Critical** anatomical error!
- Result: **Image passes when it shouldn't**

The keyword `"slightly"` referred to visibility, NOT severity. Keyword filtering can't understand context.

---

### Problem 2: False Positives (Rejecting Good Images)

**Example:**
```json
{
  "issues": ["Small compression artifact in top-right corner"]
}
```

**What happens:**
- Keyword match: `"small"` found → classified as **Minor** ✅
- But what if LLM wrote it differently:

```json
{
  "issues": ["Compression artifact visible in top-right corner"]
}
```

- Keyword match: NO keywords → classified as **Critical** ❌
- Reality: Compression artifacts are usually minor!
- Result: **Image rejected for a trivial issue**

The same issue described differently gets classified incorrectly.

---

### Problem 3: Language Variability

LLMs can describe the same severity using different words:

**All mean "minor" but use different words:**
- "Tiny noise in shadows"
- "Barely noticeable artifacts"
- "Insignificant blur"
- "Trivial imperfection"
- "Negligible distortion"

Keyword filtering would miss most of these and classify them as critical.

---

### Problem 4: Compound Issues

**Example:**
```json
{
  "issues": ["Minor noise in background BUT severe anatomical deformity in hands"]
}
```

**What happens:**
- Keyword match: `"minor"` found → classified as **Minor**
- Reality: Contains a **severe anatomical deformity**!
- Result: **Critical issue missed because "minor" appeared somewhere in the text**

Keyword matching can't parse complex sentences.

---

## The Solution: LLM Classification

**After:**
```python
# Updated prompt asks LLM to classify each issue
Return JSON format with SEVERITY CLASSIFICATION for each issue:
{
    "anatomical_correctness": {
        "score": 7,
        "feedback": "Generally correct with one issue",
        "issues": [
            {
                "description": "Extra finger on left hand",
                "severity": "Critical"
            }
        ]
    }
}

SEVERITY CLASSIFICATION:
- "Critical" = Issues that make the image UNACCEPTABLE
- "Minor" = Issues that are noticeable but ACCEPTABLE
```

**Now the LLM decides:**
```python
for issue in criterion['issues']:
    if isinstance(issue, dict):
        all_issues.append(issue['description'])
        if issue.get('severity') == 'Critical':
            critical_issues.append(issue['description'])
```

---

## Why LLM Classification is Better

### Advantage 1: Context Awareness

**LLM can understand nuance:**

```json
{
  "description": "Hand has 7 fingers, slightly visible in shadow",
  "severity": "Critical"
}
```

LLM knows:
- "7 fingers" is a critical anatomical error
- "slightly visible" just describes visibility
- Severity is determined by the DEFECT, not the visibility

**Keyword filtering would classify this as "Minor" due to "slightly".**

---

### Advantage 2: Consistent Classification

**Same severity, different wording, same result:**

```json
[
  {"description": "Tiny noise in background", "severity": "Minor"},
  {"description": "Barely noticeable artifacts", "severity": "Minor"},
  {"description": "Insignificant blur", "severity": "Minor"}
]
```

LLM understands they're all minor issues, regardless of exact wording.

---

### Advantage 3: Handles Complex Descriptions

**Multi-part issue:**
```json
{
  "description": "Background has minor compression artifacts, but main subject has severe anatomical deformity with 6 fingers",
  "severity": "Critical"
}
```

LLM reads the whole sentence, identifies the severe deformity as the dominant issue, and classifies it correctly.

---

### Advantage 4: Structured, Type-Safe Data

**Before (strings):**
```python
issues = ["Extra finger", "Small noise"]
# Have to parse strings to determine severity
```

**After (structured):**
```python
issues = [
    {"description": "Extra finger", "severity": "Critical"},
    {"description": "Small noise", "severity": "Minor"}
]
# Severity is explicit, queryable, type-safe
```

Benefits:
- Can filter by severity in queries
- Can count critical vs minor issues
- Can display different icons/colors by severity
- Easy to extend (add "Warning" severity later)

---

## How It Works: Behind the Scenes

### Step 1: Prompt Update

```
SEVERITY CLASSIFICATION:
- "Critical" = Issues that make the image UNACCEPTABLE (missing major checklist items, severe deformities, broken composition)
- "Minor" = Issues that are noticeable but ACCEPTABLE (small artifacts, slight imperfections, minor quirks)
```

This gives the LLM clear criteria for classification.

---

### Step 2: LLM Generates Structured JSON

```json
{
  "anatomical_correctness": {
    "score": 7,
    "feedback": "Anatomy mostly correct with one issue",
    "issues": [
      {
        "description": "Left hand has 6 fingers instead of 5",
        "severity": "Critical"
      },
      {
        "description": "Slightly longer thumb on right hand",
        "severity": "Minor"
      }
    ]
  }
}
```

LLM evaluates each issue against the criteria and assigns severity.

---

### Step 3: Python Parses Structured Data

```python
for issue in criterion['issues']:
    if isinstance(issue, dict):
        all_issues.append(issue['description'])
        if issue.get('severity') == 'Critical':
            critical_issues.append(issue['description'])
```

No string parsing, no keyword matching, just direct field access.

---

### Step 4: Decision Logic

```python
passes_threshold = (
    overall_score >= 7.0
    and checklist_completion >= 0.85
    and len(critical_issues) == 0  # No LLM-classified critical issues
)
```

Image passes only if:
- Score >= 7/10
- 85%+ checklist complete
- Zero issues classified as "Critical" by LLM

---

## Example Comparison

### Scenario: Hand with 6 Fingers

**Keyword Filtering:**
```
Issue: "Left hand slightly elongated with 6 fingers visible"
Keyword match: "slightly" found
Classification: Minor ❌
Result: Image PASSES (wrong!)
```

**LLM Classification:**
```json
{
  "description": "Left hand has 6 fingers instead of 5",
  "severity": "Critical"
}
```
Classification: Critical ✅
Result: Image REJECTED (correct!)

---

### Scenario: Minor Background Noise

**Keyword Filtering:**
```
Issue: "Background has compression artifacts in corner"
Keyword match: None found
Classification: Critical ❌
Result: Image REJECTED (wrong!)
```

**LLM Classification:**
```json
{
  "description": "Background has compression artifacts in corner",
  "severity": "Minor"
}
```
Classification: Minor ✅
Result: Image PASSES (correct!)

---

## Backward Compatibility

The code handles both formats:

```python
for issue in criterion['issues']:
    if isinstance(issue, dict):
        # New format: {"description": "...", "severity": "..."}
        all_issues.append(issue['description'])
        if issue.get('severity') == 'Critical':
            critical_issues.append(issue['description'])
    else:
        # Old format: "issue as plain string"
        all_issues.append(issue)
        # Old format has no severity, so it's not added to critical_issues
```

**Why this matters:**
- Existing logs/tests with old format still work
- Gradual migration (LLM will start returning new format)
- No breaking changes

---

## Real-World Impact

### Before (Keyword Filtering)
```
User: "Generate image of a woman"
→ Image has 7 fingers
→ LLM writes: "Hand slightly deformed with extra fingers"
→ Keyword "slightly" found
→ Classified as Minor
→ Image AUTO-APPROVED ❌
→ User sees nightmare fuel
```

### After (LLM Classification)
```
User: "Generate image of a woman"
→ Image has 7 fingers
→ LLM writes: {"description": "Extra finger on left hand", "severity": "Critical"}
→ Classified as Critical
→ Image REJECTED ✅
→ Automation regenerates
→ User sees clean result
```

---

## Why Gemini Flagged This

**Gemini's Concern:** "Brittle keyword filtering can miss critical issues or reject good images."

**The problem:**
- Keyword matching is context-blind
- Same severity can be described many ways
- False positives and false negatives hurt UX

**Gemini's recommendation:** Have the LLM classify severity in structured JSON.

**Grade impact:**
- **Without:** Unreliable automation = B
- **With:** Robust, context-aware classification = A

---

## Testing Scenarios

### Test 1: Critical Anatomical Issue
```json
{
  "description": "Hand has 6 fingers",
  "severity": "Critical"
}
```
Expected: Image REJECTED ✅

---

### Test 2: Minor Background Artifact
```json
{
  "description": "Small noise in shadows",
  "severity": "Minor"
}
```
Expected: Image PASSES ✅

---

### Test 3: Ambiguous Wording
```json
{
  "description": "Slightly malformed hand with extra finger",
  "severity": "Critical"
}
```
Expected: Image REJECTED ✅ (keyword would classify as Minor ❌)

---

### Test 4: Multiple Issues
```json
{
  "issues": [
    {"description": "Minor noise", "severity": "Minor"},
    {"description": "Extra finger", "severity": "Critical"}
  ]
}
```
Expected: Image REJECTED (has 1 critical issue) ✅

---

## Future Extensions

Now that severity is structured, we can easily add:

### 1. Warning Severity
```json
{
  "severity": "Warning"  // Between Minor and Critical
}
```

### 2. Severity Counts in UI
```
✅ 0 Critical issues
⚠️ 2 Warning issues
ℹ️ 5 Minor issues
```

### 3. Severity-Based Actions
```python
if len(critical_issues) > 0:
    reject_image()
elif len(warning_issues) > 2:
    ask_user_confirmation()
else:
    auto_approve()
```

### 4. Analytics
```python
track_severity_distribution({
    'critical': len(critical_issues),
    'warnings': len(warning_issues),
    'minor': len(minor_issues)
})
```

---

## Key Takeaways

1. **Keyword filtering is brittle** - Can't understand context, misses nuances
2. **LLM classification is robust** - Understands meaning, not just words
3. **Structured data is powerful** - Type-safe, queryable, extendable
4. **Context matters** - "Slightly deformed hand" is still critical!
5. **Trust the LLM's judgment** - It's better at understanding severity than regex

**The rule:** When you need to classify something, ask the LLM to classify it directly. Don't try to parse its natural language output with brittle pattern matching.

---

*This change moves Kindling from "guessing severity from keywords" to "understanding severity from context."*
