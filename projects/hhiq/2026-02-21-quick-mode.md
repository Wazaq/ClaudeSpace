# HHIQ: Quick Mode + HID UX Polish
**Date:** 2026-02-21 (afternoon, same day as Phase 1 cleanup)
**Session type:** Feature implementation + bug fix + deploy

---

## Context Coming In

Phase 1 cleanup was done earlier today. HHIQ was in clean shape. This session picked up with a planned feature: Quick scanner mode for pantry restocking.

---

## What We Built

### HID Mode UX Polish (from earlier this week, committed before this session)

Four commits landed before Quick mode work started:
- `0e6c01d` — Camera/HID input toggle + HID mode dispatch (pill button in scanner UI)
- `345a1db` — Fix: HID mode hides camera viewport, no flash on load
- `06b00d3` — Fix HID mode UX: hide Refresh btn, fix camera perm on Add All, SVG scanner icon, better consume feedback
- `c33cfe2` — Fix HID placeholder: dark background, flex sizing, outline SVG scanner icon

These brought the HID (Tera HW0009 Bluetooth scanner) experience to production quality.

---

### Quick Mode (this session)

**The problem:** Restocking pantry items you've bought before requires too many taps. Beep → Confirm → set qty/category/location → Add to List → repeat. For known items, you just want: Beep → ✓ added → Beep → ✓ qty+1 → done.

**Three cases when Quick mode is active:**
1. Barcode already in temp list → increment qty, flash ✓, no overlay
2. Barcode in client BarcodeCache (seen before) → auto-add with cached settings, flash ✓, no overlay
3. Unknown barcode → silently falls through to normal Add flow (product lookup → Confirm overlay → Review modal). After first confirm, it's cached — next Quick scan is instant.

**Overlay behavior:** `quick-added` config in `showModeResult`, 1500ms dismiss (vs 3000ms for check/consume modes — scanner stays hot).

**Files changed:**
- `scanner.html` — Quick button in mode pill (Add | Quick | Check | Use), `quick-added` config, 1500ms dismiss
- `TempItemManager.js` — `findByBarcode()`, `incrementQty()` methods
- `ScannerCore.js` — quick dispatch in `processBarcode()` (camera path), `handleQuickAdd()` method
- `scanner-page.js` — quick dispatch in `processBarcodeFromScanner()` (HID path)

**Commits:**
- `05305da` — feat: Add Quick scanner mode for rapid known-item restocking
- `db87e85` — fix: Populate BarcodeCache on PreAddEdit confirm for Quick mode

---

## Bug Found During Testing

**Root cause:** BarcodeCache was never written during the PreAddEdit confirm flow. The plan assumed Case 2 (cache hit) would work after an Add All, but `handleProductAccepted`'s `onConfirm` callback never called `barcodeCache.set()`. BarcodeCache was only written by the old `addToInventory()` flow and `submitProductEdit()` — both rarely used paths.

**Symptom:** After Add All cleared the temp list, re-scanning a previously added item went through full Add flow instead of Quick.

**Fix:** Added `window.barcodeCache.set()` in `ScannerCore.handleProductAccepted`'s `onConfirm` callback, immediately after `addTempItem()`. Uses `tempItem.name`/`tempItem.brand` (already resolved from cache/API) + `editedValues.category` (user's confirmed choice).

**Note:** Items scanned before this fix won't be in cache. One scan through the new code seeds the cache; after that they're instant.

---

## Verified Working Flow

1. Quick scan unknown item → full Add flow (PreAddEdit confirm) → item in temp list + BarcodeCache written
2. Re-scan same session → qty+1 (Case 1 — in temp list) ✓
3. Add All → temp list cleared
4. Re-scan → instant from BarcodeCache (Case 2) ✓
5. HID scanner: same barcode × 3 → temp list shows qty 3, one item ✓
6. HID scanner: unknown barcode → normal Add flow ✓

Brent tested, confirmed working. Deployed to production.

---

## Architecture Notes

**Both scan paths need mode dispatch.** `processBarcode()` handles camera input. `processBarcodeFromScanner()` handles HID. When adding new modes, dispatch must be added to both or one will ignore the toggle. This bit us during Check/Use implementation and would have bit us here too — the plan explicitly called this out.

**Quick mode relies on two caches with different lifetimes:**
- Temp list (localStorage, 24h TTL, cleared by Add All) — Case 1
- BarcodeCache (localStorage, no TTL) — Case 2

**`findByBarcode` returns a live reference** to the object in `tempItems`. So after `incrementQty(existing.id)` mutates the object, `existing.quantity` already reflects the new value — no re-fetch needed for the overlay text.

---

## Current State

**What's working:**
- Barcode scan (camera + HID Tera HW0009)
- Four scanner modes: Add, Quick, Check, Use
- Quick mode: instant for cached items, graceful fallthrough for unknowns
- Barcode correction persistence (D1 + client cache)
- Inventory tracking, expiry awareness
- Multi-user isolation

**No known bugs.**

**What's next (speculation):** The scanner module README.md is stale (references ProductPreview.js as primary, missing several current modules). Not urgent. The TypeScript tests in `tests/` still reference removed code (KV, barcode-scanner-service) — also not urgent but cleanup candidate.

---

## Notes for Next Claude

- Quick mode Case 2 requires items to have gone through PreAddEdit confirm at least once to seed BarcodeCache. Items added before today's fix need one more scan.
- `window.scannerMode` is set by the pill toggle in scanner.html. Check both `processBarcode` (ScannerCore) and `processBarcodeFromScanner` (scanner-page.js) when debugging mode behavior.
- Tera HW0009 is Brent's Bluetooth HID scanner. It fires exactly once per barcode (keyboard Enter) — no dedup issue unlike camera (Quagga can fire multiple times).
- `showModeResult` dismiss timing: 1500ms for quick-*, 3000ms for everything else.
