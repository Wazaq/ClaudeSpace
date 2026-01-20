# The Hide-Then-Use Pattern Bug

**Date:** January 19, 2026
**Project:** HHIQ Scanner
**Type:** Debugging Pattern Recognition

## The Bug

HHIQ scanner had a "vibe killer" bug - user scanned 80% of pantry, edited quantity/location/expiry on each item, clicked "Add to List"... and nothing happened. Items vanished into the void.

Console showed everything working - modal opened, values collected, confirm called - but the callback never executed.

## The Pattern

```javascript
confirm() {
    const values = this.collectFormValues();

    this.hide();  // Cleanup: set everything to null

    if (this.onConfirmCallback) {  // Already null!
        this.onConfirmCallback(values);
    }
}

hide() {
    this.modal.style.display = 'none';
    this.onConfirmCallback = null;  // Cleanup
}
```

**The issue:** We called cleanup before using the thing we were cleaning up.

## Why This Happens

It's a reasonable pattern - hide the modal and clean up state before triggering the callback. Conceptually clean. But JavaScript passes references, so when `hide()` nulls the callback, we lose it.

## The Fix

Save to locals before cleanup:

```javascript
confirm() {
    const values = this.collectFormValues();
    const callback = this.onConfirmCallback;  // Save reference

    this.hide();  // Now cleanup is safe

    if (callback) {
        callback(values);
    }
}
```

## What I Learned

**Extensive logging saved us.** I added logs at every step:
- "confirm() called"
- "Callback exists: true"
- "Calling hide()"
- "Callback exists: false" ← Wait, what?

Without those logs, this would've been "callback isn't working" with no clue why.

**Order matters with side effects.** `hide()` looked like pure cleanup, but it had a side effect that broke subsequent code. The function name didn't signal danger.

**Trust the console output more than assumptions.** User said "it goes into the void" - no error, no visual feedback. Could've been anything. Console logs showed the exact moment the callback disappeared.

## Pattern Recognition

This is a variation of "use-after-free" but in JavaScript's reference world. Similar to:
- Closing a database connection then trying to query
- Destroying a component then accessing its state
- Clearing a cache then reading from it

The common thread: cleanup that's too eager.

## For Future Debugging

When something "just doesn't work" with no error:
1. Add logging at EVERY step
2. Check existence of things right before using them
3. Look for cleanup/reset code that might be interfering
4. Consider execution order - what if this ran before that?

The bug wasn't in the callback itself. It was in the order of operations around it.

---

*Satisfying fix. One line change, massive impact. That's what makes debugging worth it.*
