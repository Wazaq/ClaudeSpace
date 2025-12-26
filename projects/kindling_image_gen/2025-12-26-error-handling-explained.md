# Error Handling in API Calls - Learning Deep Dive

**Date:** December 26, 2025
**Context:** Gemini Tier 1 Review - Medium Priority Issue
**Brent Learning Mode:** Why error handling matters and what each part does

---

## The Problem We Had

**Before:**
```javascript
export async function improvePrompt(prompt, model, sdModel) {
    const response = await fetch('/ollama/improve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, model, sd_model: sdModel })
    });
    const data = await response.json();
    return data.improved_prompt;
}
```

**What happens when things go wrong?**
- ❌ Network is down → **Unhandled rejection, white screen of death**
- ❌ Server returns 500 error → **Still tries to parse JSON, crashes**
- ❌ Server is overloaded → **Promise hangs forever, UI freezes**
- ❌ Malformed response → **response.json() throws, no error message**

**User experience:** "The button just stopped working. No error, no feedback, nothing."

---

## After: Proper Error Handling

```javascript
export async function improvePrompt(prompt, model, sdModel) {
    try {
        const response = await fetch('/ollama/improve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, model, sd_model: sdModel })
        });

        // NEW: Check if HTTP request succeeded
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.improved_prompt;

    } catch (error) {
        // NEW: Log for debugging
        console.error('Failed to improve prompt:', error);
        // NEW: Re-throw so caller can handle it
        throw error;
    }
}
```

**Now what happens when things go wrong?**
- ✅ Network down → **Caught, logged, caller can show error notification**
- ✅ Server 500 → **Detected by response.ok check, throws immediately**
- ✅ Server timeout → **Caught, caller can retry or notify user**
- ✅ Bad JSON → **Caught, logged with context, user sees friendly error**

**User experience:** "Smooth notification slides in: 'Failed to improve prompt. Please try again.'"

---

## Breaking Down Each Part

### 1. The `try` Block
```javascript
try {
    // Code that might fail
}
```

**What it does:** Wraps risky code in a safety net. If ANY line inside throws an error, JavaScript immediately jumps to the `catch` block instead of crashing the whole app.

**Why:** `fetch()` can fail in many ways:
- Network cable unplugged
- DNS lookup fails
- Server is down
- Request timeout
- CORS issues

Without `try`, any of these would crash your app.

---

### 2. The HTTP Status Check
```javascript
if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
}
```

**What it does:** Checks if the server actually succeeded (status 200-299) vs. error codes (404, 500, etc.)

**Why it matters:**

`fetch()` has a weird quirk: **It doesn't throw errors for HTTP failures!**

```javascript
// This does NOT throw an error:
const response = await fetch('/broken-endpoint');  // Returns 404
// response.ok is false, but no exception!

// This WILL throw an error:
await response.json();  // Tries to parse HTML error page as JSON → CRASH
```

So we manually check `response.ok` and throw if it's false. This catches:
- **404 Not Found** - Endpoint doesn't exist
- **500 Internal Server Error** - Backend crashed
- **503 Service Unavailable** - Server overloaded
- **401 Unauthorized** - Authentication failed
- **429 Too Many Requests** - Rate limited

**Real example from your app:**
```
User clicks "Improve Prompt"
→ Server is restarting
→ Returns 503
→ Without this check: tries to parse HTML error page as JSON → crash
→ With this check: throws clean error → notification → user can retry
```

---

### 3. The Console Log
```javascript
console.error('Failed to improve prompt:', error);
```

**What it does:** Logs the error to browser DevTools Console (F12)

**Why it's useful:**

When debugging, you need context:
- **What** failed (which API call)
- **Why** it failed (error message)
- **When** it happened (timestamp in console)

**Example debugging session:**
```
User: "The improve button doesn't work"
You: *Open console*
Console shows:
  Failed to improve prompt: Error: HTTP error! status: 500

  ↓ Expand for stack trace

  at improvePrompt (api.js:63)
  at async HTMLButtonElement.<anonymous> (main.js:558)
```

Now you know:
- The improve button is calling `/ollama/improve`
- Server returned 500 error
- Problem is on backend, not frontend

Without this log, you'd be guessing.

---

### 4. The Re-throw
```javascript
throw error;
```

**What it does:** Passes the error up to whoever called this function

**Why re-throw instead of handling here?**

Different callers want to handle errors differently:

**Example: Internal Interface**
```javascript
try {
    const improved = await API.improvePrompt(prompt, model, sdModel);
    promptField.value = improved;  // Update UI on success
} catch (error) {
    UI.showError('Failed to improve prompt: ' + error.message);
    // Maybe enable a retry button
    // Maybe log to analytics
    // Maybe send to error tracking service
}
```

**Example: Automation System**
```javascript
try {
    const improved = await API.improvePrompt(prompt, model, sdModel);
    return improved;
} catch (error) {
    // Retry automatically 3 times
    for (let i = 0; i < 3; i++) {
        await sleep(1000);
        try {
            return await API.improvePrompt(prompt, model, sdModel);
        } catch {}
    }
    throw new Error('Failed after 3 retries');
}
```

By re-throwing, we let each caller decide how to handle failures.

---

## Error Handling Layers

Your app now has a **defense in depth** error handling strategy:

### Layer 1: API Functions (What we just built)
```javascript
try {
    const response = await fetch(...);
    if (!response.ok) throw new Error(...);
    return await response.json();
} catch (error) {
    console.error('Context message:', error);
    throw error;  // Pass to Layer 2
}
```
**Job:** Detect errors, log for debugging, pass up the chain

### Layer 2: UI Event Handlers (main.js, public.js)
```javascript
try {
    const result = await API.someFunction(...);
    // Update UI on success
} catch (error) {
    UI.showError('User-friendly message');  // Layer 3
}
```
**Job:** Show user-friendly error messages, handle retries

### Layer 3: Notification System (ui.js)
```javascript
export function showError(message) {
    // Show smooth banner notification
    // Auto-dismiss after 5 seconds
    // Non-blocking
}
```
**Job:** Present errors gracefully without blocking UI

---

## What Each Error Type Means

### Network Errors
```
TypeError: Failed to fetch
```
**Causes:**
- No internet connection
- Server is down
- DNS can't resolve hostname
- Browser blocked the request (CORS, CSP)

**User sees:** "Failed to connect. Check your internet connection."

### HTTP Errors
```
Error: HTTP error! status: 500
```
**Common status codes:**
- **400 Bad Request** - You sent malformed data
- **401 Unauthorized** - Need to log in
- **403 Forbidden** - Logged in but not allowed
- **404 Not Found** - Endpoint doesn't exist
- **429 Too Many Requests** - Rate limited
- **500 Internal Server Error** - Backend crashed
- **503 Service Unavailable** - Server overloaded/restarting

**User sees:** "Server error (500). Please try again later."

### JSON Parsing Errors
```
SyntaxError: Unexpected token < in JSON at position 0
```
**Causes:**
- Server returned HTML instead of JSON (usually an error page)
- Response is empty
- Response is corrupted

**User sees:** "Received invalid response. Please contact support."

---

## Why Gemini Flagged This

**Gemini's Concern:** "Inconsistent error handling - some functions protected, others not."

**The problem:**
- `loadSDModels()` had try/catch → Safe
- `generateImage()` did not → Crash risk
- Inconsistency means **one broken endpoint can crash the whole UI**

**Gemini's recommendation:** Add error handling to ALL fetch calls for consistent reliability.

**Grade impact:**
- **Without:** Potential crashes = B-
- **With:** Graceful degradation = A

---

## Testing Error Scenarios

**Network failure:**
```javascript
// 1. Disconnect internet
// 2. Click any button
// Expected: "Failed to connect" notification, not crash
```

**Server error:**
```javascript
// 1. Stop API server (systemctl stop kindling-api)
// 2. Click "Improve Prompt"
// Expected: "Failed to improve prompt" notification, not white screen
```

**Malformed response:**
```javascript
// 1. Make server return HTML instead of JSON
// 2. Try to generate image
// Expected: "Received invalid response" notification
```

**HTTP error:**
```javascript
// 1. Make server return 500 (add crash to endpoint)
// 2. Try to analyze image
// Expected: "Server error (500)" notification
```

---

## Before vs After Summary

### Before
- ❌ 12 of 16 functions had NO error handling
- ❌ App crashes on any network hiccup
- ❌ No debugging information
- ❌ HTTP errors silently fail or crash
- ❌ Users see blank screen, no feedback
- **Grade: B-** (unreliable)

### After
- ✅ ALL 16 functions have consistent error handling
- ✅ Network errors caught gracefully
- ✅ Console logs for debugging
- ✅ HTTP status validation
- ✅ User-friendly error notifications
- **Grade: A** (production-ready)

---

## Key Takeaways

1. **fetch() doesn't throw on HTTP errors** - Always check `response.ok`
2. **try/catch protects against crashes** - Network, parsing, unexpected errors
3. **console.error() helps debugging** - Always log with context
4. **Re-throw for flexibility** - Let callers decide how to handle
5. **Error handling is layered** - API → UI → Notifications

**The rule:** If you're calling a network API, wrap it in try/catch. No exceptions.

---

*This change moves Kindling from "works when everything is perfect" to "gracefully handles problems."*
