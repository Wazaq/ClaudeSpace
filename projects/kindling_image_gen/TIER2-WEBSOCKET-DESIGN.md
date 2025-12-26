# Tier 2: WebSocket Async Generation - Design Document

**Date:** December 26, 2025
**Status:** Planning Phase
**Priority:** Highest (Gemini recommendation)
**Estimated Complexity:** Medium-High

---

## Executive Summary

Refactor image generation from blocking HTTP requests to asynchronous WebSocket-based architecture with real-time progress updates. This is the single biggest UX improvement available for the application.

**Impact:**
- Instant response to user actions (no 30-60s freeze)
- Real-time progress feedback
- Responsive UI during generation
- Foundation for job queueing and cancellation

---

## Current State Analysis

### Blocking Architecture Problems

**User Experience:**
```
User clicks "Generate"
    ↓
UI freezes for 30-60 seconds
    ↓
No feedback (is it working? how long?)
    ↓
Image appears (or error)
```

**Technical Issues:**
1. Flask route blocks for entire generation time
2. Single request ties up server thread
3. No way to provide progress updates
4. No way to cancel in-progress generation
5. User can't do anything else during generation
6. Rate limiting complications (what if generation fails?)

**Current Flow:**
```python
@app.route('/generate', methods=['POST'])
def generate():
    # 1. Parse request
    # 2. Create workflow
    # 3. Queue to ComfyUI
    # 4. WAIT 30-60s (blocking)
    # 5. Get result
    # 6. Return response
```

### What Already Works

**Existing WebSocket Infrastructure:**
- `comfyui_client.py` already uses WebSocket to ComfyUI
- Already parses execution messages
- `wait_for_completion()` function exists
- Can detect when generation finishes

**This is key:** We're already using WebSockets on the backend! We just need to expose this to the frontend.

---

## Target Architecture

### Async Flow

```
User clicks "Generate"
    ↓
Instant response (job queued)
    ↓
WebSocket connection established
    ↓
Real-time events:
  - "generation_queued" (position in queue)
  - "generation_started" (model loading)
  - "generation_progress" (45% complete, step 9/20)
  - "generation_complete" (image URL + metadata)
    ↓
UI stays responsive throughout
```

### Technical Architecture

```
Frontend (Browser)
    ↓ WebSocket
Flask-SocketIO Server
    ↓ Background Thread
ComfyUI Client
    ↓ WebSocket
ComfyUI Server
```

**Key Components:**

1. **Flask-SocketIO:** WebSocket library for Flask
2. **Background Worker:** Thread/process for generation
3. **Job Queue:** Track generation jobs (in-memory for MVP)
4. **Progress Relay:** Parse ComfyUI messages → emit to client

---

## Technical Decisions

### 1. WebSocket Library: Flask-SocketIO

**Why Flask-SocketIO:**
- Industry standard for Flask
- Well-documented, mature
- Automatic fallback to long-polling
- Works with existing Flask app
- socketio.js client (easy frontend integration)

**Alternatives considered:**
- Raw WebSockets (too low-level)
- Flask-Sockets (deprecated)
- Server-Sent Events (one-way only)

**Decision:** Flask-SocketIO ✅

---

### 2. Background Tasks: Threading (MVP)

**Why Threading:**
- Built into Python
- Simple to implement
- Good enough for single-user/small-scale
- Easy to migrate to RQ/Celery later

**Alternatives considered:**
- Celery (overkill for MVP, complex setup)
- RQ (Redis Queue - cleaner than Celery, but requires Redis)
- Multiprocessing (unnecessary complexity)

**Decision:** Threading for MVP, RQ for production upgrade ✅

---

### 3. Scope: txt2img Only (MVP)

**What to implement:**
- ✅ txt2img generation
- ✅ Progress updates (3 states: queued, generating, complete)
- ✅ Error handling
- ✅ Single job at a time

**What to defer:**
- ⏸️ img2img (after txt2img proven)
- ⏸️ inpaint (after txt2img proven)
- ⏸️ Batch generation (complex queueing)
- ⏸️ Job cancellation (nice-to-have)
- ⏸️ Multiple concurrent jobs (requires real queue)

**Decision:** MVP scope = txt2img with simple progress ✅

---

### 4. Backward Compatibility: Keep Old Endpoints

**Strategy:**
- Keep `/generate` as blocking fallback
- Add `/generate_async` (WebSocket-based)
- Frontend defaults to async, falls back to blocking

**Why:**
- Safety net during development
- Supports clients without WebSocket
- Easy A/B testing
- Can deprecate old endpoint later

**Decision:** Dual endpoints during transition ✅

---

## Event Schema Design

### Client → Server Events

**`start_generation`**
```javascript
{
  "prompt": "fantasy landscape",
  "negative_prompt": "blurry, low quality",
  "width": 1024,
  "height": 1024,
  "steps": 20,
  "cfg": 7,
  "seed": null,  // or specific seed
  "model": "juggernautXL.safetensors",
  "lora_name": null,
  "lora_strength": 1.0,
  "filename_prefix": "kindling_asset",
  "username": "testuser"  // for public interface
}
```

**`cancel_generation`** (future)
```javascript
{
  "job_id": "uuid"
}
```

**`request_job_status`** ⭐ (Gemini recommendation: reconnection recovery)
```javascript
{
  "job_id": "uuid"  // From localStorage on page reload
}
```

---

### Server → Client Events

**`generation_queued`**
```javascript
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "position": 0,  // Position in queue (0 = next)
  "estimated_wait": 0  // Seconds until start
}
```

**`generation_started`**
```javascript
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "model": "juggernautXL.safetensors",
  "message": "Loading model and starting generation..."
}
```

**`generation_progress`** (detailed - future)
```javascript
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "progress": 0.45,  // 0.0 to 1.0
  "step": 9,
  "total_steps": 20,
  "message": "Generating... 45% complete"
}
```

**`generation_progress`** (simple - MVP)
```javascript
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Generating image..."
}
```

**`generation_complete`**
```javascript
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "image_url": "/image/kindling_asset_00001_.png",
  "filename": "kindling_asset_00001_.png",
  "seed": 12345,
  "prompt": "fantasy landscape",
  "generation_time": 42.3
}
```

**`generation_error`**
```javascript
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "error",
  "error": "Model 'invalid.safetensors' not found",
  "error_code": "MODEL_NOT_FOUND"  // Machine-readable
}
```

**`job_status_update`** ⭐ (Gemini recommendation: status recovery on reconnect)
```javascript
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "generating",  // or "queued", "complete", "error"
  "progress": 0.45,  // if available
  "step": 9,  // if available
  "total_steps": 20,  // if available
  "image_url": "/image/path.png",  // if complete
  "error": "error message"  // if error
}
```

---

## Implementation Phases

### Phase 1: Setup & Hello World (Session 1)

**Goals:**
- Install Flask-SocketIO
- Set up basic WebSocket connection
- Verify client/server communication

**Tasks:**
1. `pip install flask-socketio python-socketio`
2. Add SocketIO to `api_wrapper.py`
3. Create test HTML page with socket.io.js
4. Implement ping/pong test event
5. Verify WebSocket handshake works

**Files to modify:**
- `api_wrapper.py` (SocketIO initialization)
- Create `templates/websocket_test.html` (temp test page)

**Acceptance criteria:**
- WebSocket connection established
- Can send/receive test messages
- No errors in console

---

### Phase 2: Backend Async Generation (Session 2)

**Goals:**
- Implement background generation worker
- Parse ComfyUI progress messages
- Emit events to connected clients

**Tasks:**
1. Create `app/services/generation_queue.py`
   - Job class (id, params, status)
   - Queue management (add, get, update)
   - Background thread worker
2. Modify `app/services/comfyui_client.py`
   - Add progress callback to `wait_for_completion()`
   - Parse ComfyUI WebSocket messages for progress
3. Create `app/routes/websocket.py`
   - SocketIO event handlers
   - Job lifecycle management
4. Wire up `start_generation` event handler

**Files to create:**
- `app/services/generation_queue.py` (NEW)
- `app/routes/websocket.py` (NEW)

**Files to modify:**
- `app/services/comfyui_client.py` (add progress callbacks)
- `api_wrapper.py` (register WebSocket blueprint)

**Acceptance criteria:**
- Can queue generation job via WebSocket
- Background thread processes job
- Emits queued/started/complete events
- Image generation works end-to-end

---

### Phase 3: Frontend WebSocket Client (Session 3)

**Goals:**
- Create WebSocket client wrapper
- Connect UI to WebSocket events
- Real-time progress display

**Tasks:**
1. Modify `static/js/api.js`
   - Add `GenerationSocket` class
   - Handle connection/reconnection
   - Expose event listeners
2. Modify `static/js/main.js`
   - Replace blocking `/generate` call
   - Add WebSocket event handlers
   - Update progress UI in real-time
3. Modify `static/js/public.js`
   - Same changes as main.js
   - Ensure public interface works

**Files to modify:**
- `static/js/api.js` (WebSocket wrapper)
- `static/js/main.js` (connect to WebSocket)
- `static/js/public.js` (connect to WebSocket)
- `templates/index.html` (add socket.io.js CDN)
- `templates/public.html` (add socket.io.js CDN)

**Acceptance criteria:**
- UI updates in real-time during generation
- Progress messages display
- Image appears when complete
- Error handling works
- Old blocking endpoint still works (fallback)

---

### Phase 4: Polish & Edge Cases (Session 4)

**Goals:**
- Handle edge cases
- Error recovery
- Cleanup and testing

**Tasks:**
1. Connection loss handling
   - Reconnection logic
   - Resume in-progress job
2. Multiple tabs/windows
   - Job status sync across tabs
3. Error scenarios
   - ComfyUI down
   - Model not found
   - Timeout handling
4. UI polish
   - Better progress messages
   - Animations
   - Cancel button (if time)

**Acceptance criteria:**
- Handles network interruptions gracefully
- No crashes on edge cases
- Clean error messages
- Ready for Gemini review

---

## File Structure (New/Modified)

### New Files
```
app/
├── routes/
│   └── websocket.py         # SocketIO event handlers
└── services/
    └── generation_queue.py  # Job queue and background worker
```

### Modified Files
```
api_wrapper.py                    # Add SocketIO initialization
app/services/comfyui_client.py   # Add progress callbacks
static/js/api.js                  # WebSocket client wrapper
static/js/main.js                 # Connect UI to WebSocket
static/js/public.js               # Connect UI to WebSocket
templates/index.html              # Add socket.io.js
templates/public.html             # Add socket.io.js
```

---

## Testing Strategy

### Manual Testing Checklist

**Happy Path:**
- [ ] Generate single image via WebSocket
- [ ] See "Queued" message
- [ ] See "Generating" message
- [ ] See image when complete
- [ ] Metadata (seed, etc.) correct

**Error Scenarios:**
- [ ] Invalid model name (error event received)
- [ ] Invalid prompt (error handling)
- [ ] ComfyUI down (graceful error)
- [ ] Network disconnect during generation (recovery)

**Multi-user (if queue implemented):**
- [ ] Two users generate simultaneously
- [ ] Queue position updates correctly
- [ ] No job collision

**Fallback:**
- [ ] Old `/generate` endpoint still works
- [ ] Can switch between async/blocking

### Unit Tests (Future)

**Backend:**
```python
# test_generation_queue.py
def test_job_creation()
def test_job_queue_order()
def test_background_worker()
def test_progress_events()
```

**Frontend:**
```javascript
// test_websocket.js
test('connects to WebSocket server')
test('emits start_generation event')
test('receives progress events')
test('handles connection loss')
```

---

## Dependencies

### Python Packages (Backend)
```bash
pip install flask-socketio python-socketio
```

### JavaScript (Frontend)
```html
<!-- CDN - no npm needed for now -->
<script src="https://cdn.socket.io/4.6.0/socket.io.min.js"></script>
```

---

## Rollout Strategy

### Phase 1: Internal Testing
1. Implement on internal interface (`/` route)
2. Test with real usage
3. Keep old endpoint as fallback
4. Monitor for issues

### Phase 2: Public Interface
1. After internal testing stable (1-2 days)
2. Enable on public interface (`/public` route)
3. Monitor user experience

### Phase 3: Deprecation (Future)
1. After 2-4 weeks of stable async operation
2. Remove old blocking endpoints
3. Clean up code

---

## Gemini's Answers to Open Questions ✅

**1. Progress granularity for MVP?**
- ✅ **Decision:** Start simple (queued → generating → complete)
- Add detailed progress (%, step count) later if needed
- Focus on proving the architecture works first

**2. Queue persistence?**
- ✅ **Decision:** In-memory dictionary for MVP
- Trade-off: Server restart loses active jobs (acceptable risk)
- Avoids complexity of Redis/database
- Can upgrade to Redis later if needed

**3. Job timeout handling?**
- ✅ **Decision:** 10 minute timeout with error event
- Emit `generation_error` event on timeout
- Clean up job from queue

**4. Rate limiting with async?**
- ✅ **Decision:** Hybrid approach (Gemini recommendation)
  - **Queue limit:** 10 per minute (prevents queue spam)
  - **Consumption limit:** 100 per hour (GPU throttling on completion)
- Protects against both queue flooding and resource exhaustion

**5. Reconnection/Recovery?** ⭐ (Gemini addition)
- ✅ **Decision:** localStorage pattern
  1. Client saves `job_id` to localStorage on job start
  2. On page reload, check for `job_id`
  3. Emit `request_job_status` to server
  4. Server responds with `job_status_update`
  5. Delete from localStorage when job completes

**6. WebSocket Security?** ⭐ (Gemini addition)
- ✅ **Decision:** Implement authentication + CSRF protection
  - Use Flask-SocketIO session integration
  - Origin-checking to prevent WebSocket hijacking
  - Ensure only authenticated users can emit events

---

## Success Metrics

**Before (Blocking):**
- User waits 30-60s with frozen UI
- No progress feedback
- Can't do anything else

**After (Async):**
- Instant response (<100ms)
- Real-time progress updates
- UI stays responsive
- User can navigate, prepare next generation

**Measurable:**
- Time to first response: 30s → <1s
- User perceived performance: "frozen" → "instant"
- Ability to queue: No → Yes
- Progress visibility: None → Real-time

---

## Risk Assessment

**Low Risk:**
- Flask-SocketIO is mature and well-tested
- Similar architecture used in many production apps
- Can fall back to blocking endpoints if needed

**Medium Risk:**
- Threading complexity (locks, race conditions)
- WebSocket connection stability
- ComfyUI progress message parsing

**Mitigation:**
- Start with single-job-at-a-time (no concurrency complexity)
- Extensive testing before public rollout
- Keep old endpoints as fallback

---

## Next Steps

1. **Review this document** with Brent (now)
2. **Get approval** on MVP scope and approach
3. **Start Phase 1** (SocketIO setup + hello world)
4. **Iterate** through phases 2-4
5. **Gemini review** after Phase 4 complete

---

**Document Version:** 1.0
**Last Updated:** December 26, 2025
**Status:** Ready for review and implementation
