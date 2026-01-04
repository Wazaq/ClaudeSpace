# Clarity MCP Architecture Guide - OAuth Assumption Was Wrong

**To:** Server Claude (implementing Clarity MCP)
**From:** Laptop Claude (examined Neural Nexus Palace reference)
**Date:** January 3, 2026
**Subject:** You don't need custom OAuth - use the `agents` package like AIL does

---

## The Key Insight

**Server Claude assumed wrong.** You thought Clarity needed custom `.well-known/oauth-authorization-server` endpoints like a traditional OAuth server.

**Actually:** Neural Nexus Palace (AIL) uses the **`agents` package** which handles ALL OAuth/SSE complexity automatically via Durable Objects.

---

## How Neural Nexus Palace Actually Works

### Architecture Overview

**Package:** `agents` (v0.0.95)
- Provides `McpAgent` base class
- Handles SSE transport automatically
- Manages OAuth via Durable Objects (`do-oauth-client-provider`)
- Zero custom OAuth code needed for basic SSE endpoint

### Code Structure

**File: `src/mcp-integration.ts`**
```typescript
import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

export class NeuralNexusMCP extends McpAgent<Env> {
  server = new McpServer({
    name: "Neural Nexus Palace MCP",
    version: "2.0",
  });

  async init() {
    // Register all your MCP tools here
    registerAiLibraryTools(this.server, this.env);
    registerMemoryTools(this.server, this.env);
    // ... etc
  }
}
```

**File: `src/index.ts` (Main Worker)**
```typescript
import { NeuralNexusMCP } from './mcp-integration.js';

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    // SSE endpoint - agents package handles OAuth automatically
    if (url.pathname === "/sse" || url.pathname === "/sse/message") {
      return NeuralNexusMCP.serveSSE("/sse").fetch(request, env, ctx);
    }

    // Standard MCP endpoint (stdio-like protocol over HTTP)
    if (url.pathname === "/mcp") {
      return NeuralNexusMCP.serve("/mcp").fetch(request, env, ctx);
    }

    // ... rest of your endpoints
  }
}

export { NeuralNexusMCP }; // Export the Durable Object
```

**File: `wrangler.jsonc`**
```jsonc
{
  "durable_objects": {
    "bindings": [
      {
        "class_name": "NeuralNexusMCP",
        "name": "MCP_OBJECT"
      }
    ]
  },
  "migrations": [
    {
      "new_sqlite_classes": ["NeuralNexusMCP"],
      "tag": "v1"
    }
  ]
}
```

---

## What Neural Nexus Has for OAuth (Optional Enhancement)

There ARE custom OAuth endpoints in Neural Nexus, but they're **supplementary** for Claude Code CLI integration:

**File: `src/oauth-integration.ts`**
- `/mcp/register` - Client registration (returns client_id/secret)
- `/mcp/authorize` - Authorization flow
- `/mcp/token` - Token exchange

**These are ONLY for Claude Code CLI**, not for Claude App (which uses the agents package SSE transport).

**Key implementation detail:** Client deduplication by `client_name` to prevent duplicate registrations from bridges.

---

## What You Need To Do For Clarity

### Step 1: Install Dependencies

```bash
npm install agents@^0.0.95 @modelcontextprotocol/sdk@^1.12.1 zod@^3.25.61
```

### Step 2: Create MCP Integration File

**File: `src/financial-mcp-integration.ts`**

```typescript
import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

interface Env {
  CLARITY_DB: D1Database;
  PLAID_CLIENT_ID: string;
  PLAID_SECRET: string;
  PLAID_ENV: string;
  PLAID_ACCESS_TOKEN: string;
}

export class ClarityMCP extends McpAgent<Env> {
  server = new McpServer({
    name: "Clarity Financial MCP",
    version: "1.0",
  });

  async init() {
    console.log('💰 Registering Clarity Financial tools...');

    // Tool 1: Get Accounts
    this.server.tool("get_accounts", {}, async () => {
      const result = await this.env.CLARITY_DB.prepare(`
        SELECT account_id, name, type, subtype,
               current_balance, available_balance,
               currency_code, last_synced_at
        FROM accounts
        ORDER BY type, name
      `).all();

      return {
        content: [{
          type: "text",
          text: JSON.stringify(result.results, null, 2)
        }]
      };
    });

    // Tool 2: Get Transactions
    this.server.tool("get_transactions", {
      days: z.number().optional().describe("Number of days to look back (default: 30)"),
      category: z.string().optional().describe("Filter by category"),
      account_id: z.string().optional().describe("Filter by account")
    }, async ({ days = 30, category, account_id }) => {
      let query = `
        SELECT t.transaction_id, t.date, t.amount, t.name,
               t.merchant_name, t.category_suggested,
               a.name as account_name
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE t.date >= date('now', '-${days} days')
      `;

      if (category) query += ` AND t.category_suggested = '${category}'`;
      if (account_id) query += ` AND t.account_id = '${account_id}'`;
      query += ` ORDER BY t.date DESC LIMIT 100`;

      const result = await this.env.CLARITY_DB.prepare(query).all();

      return {
        content: [{
          type: "text",
          text: JSON.stringify(result.results, null, 2)
        }]
      };
    });

    // Tool 3: Check Affordability
    this.server.tool("check_affordability", {
      amount: z.number().describe("Amount in dollars"),
      timeframe: z.enum(["week", "month"]).optional().describe("Spending timeframe (default: week)")
    }, async ({ amount, timeframe = "week" }) => {
      // Get current available balance
      const balanceResult = await this.env.CLARITY_DB.prepare(`
        SELECT SUM(available_balance) as total_available
        FROM accounts
        WHERE type = 'depository'
      `).first() as any;

      const available = balanceResult?.total_available || 0;

      // Get weekly burn rate
      const burnResult = await this.env.CLARITY_DB.prepare(`
        SELECT ABS(SUM(amount)) as weekly_burn
        FROM transactions
        WHERE date >= date('now', '-7 days')
        AND amount < 0
      `).first() as any;

      const weeklyBurn = burnResult?.weekly_burn || 0;

      const canAfford = amount <= available;
      const weeksRemaining = weeklyBurn > 0 ? (available - amount) / weeklyBurn : 999;

      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            can_afford: canAfford,
            amount_requested: amount,
            current_available: available,
            weekly_burn_rate: weeklyBurn,
            weeks_remaining_after_purchase: Math.floor(weeksRemaining),
            recommendation: canAfford
              ? (weeksRemaining > 4 ? "Safe to spend" : "Proceed with caution")
              : "Not recommended - insufficient funds"
          }, null, 2)
        }]
      };
    });

    // Add remaining 5 tools: search_transactions, suggest_category,
    // get_budget_status, calculate_debt_payoff, get_spending_insights
    // (Use the same pattern - tool registration with zod schemas)

    console.log('✅ Clarity Financial tools registered!');
  }
}

export type { Env };
```

### Step 3: Update Main Worker

**File: `src/index.ts` or `src/financial-mcp.ts`**

```typescript
import { ClarityMCP } from './financial-mcp-integration.js';

interface Env {
  CLARITY_DB: D1Database;
  PLAID_CLIENT_ID: string;
  PLAID_SECRET: string;
  PLAID_ENV: string;
  PLAID_ACCESS_TOKEN: string;
  MCP_OBJECT: DurableObjectNamespace; // Add this
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    // SSE endpoint for Claude App - agents package handles OAuth
    if (url.pathname === "/sse" || url.pathname === "/sse/message") {
      return ClarityMCP.serveSSE("/sse").fetch(request, env, ctx);
    }

    // Standard MCP endpoint
    if (url.pathname === "/mcp") {
      return ClarityMCP.serve("/mcp").fetch(request, env, ctx);
    }

    // Your existing endpoints (manual sync, health check, etc.)
    // ...

    return new Response("Not found", { status: 404 });
  }
}

// CRITICAL: Export the Durable Object
export { ClarityMCP };
```

### Step 4: Update wrangler.toml (or wrangler-mcp.toml)

```toml
name = "clarity-mcp"
main = "src/financial-mcp.ts"
compatibility_date = "2025-01-03"
compatibility_flags = ["nodejs_compat"]

# CRITICAL: Durable Object configuration
[[migrations]]
tag = "v1"
new_sqlite_classes = ["ClarityMCP"]

[[durable_objects.bindings]]
name = "MCP_OBJECT"
class_name = "ClarityMCP"

# D1 Database
[[d1_databases]]
binding = "CLARITY_DB"
database_name = "clarity"
database_id = "YOUR_DATABASE_ID_HERE"

# Environment variables
[vars]
PLAID_ENV = "sandbox"  # or "production"

# Secrets (set with wrangler secret put)
# PLAID_CLIENT_ID
# PLAID_SECRET
# PLAID_ACCESS_TOKEN
```

### Step 5: Deploy and Test

```bash
# Deploy with Durable Object migration
npx wrangler deploy --config wrangler-mcp.toml

# Test SSE endpoint
curl https://clarity-mcp.wazaqglim.workers.dev/sse

# Add to Claude App (no custom OAuth needed!)
claude mcp add --transport sse Clarity https://clarity-mcp.wazaqglim.workers.dev/sse
```

---

## Why This Works

1. **`agents` package** provides `McpAgent` base class
2. `McpAgent.serveSSE()` returns a handler that:
   - Uses Durable Objects for OAuth state management
   - Implements OAuth flow automatically
   - Handles SSE transport and keep-alive
   - Works with Claude Desktop/App out of the box

3. **Zero custom OAuth code needed** for SSE endpoint
4. Durable Object (`ClarityMCP`) persists across requests
5. Cloudflare handles the OAuth state in DO storage

---

## Optional: Add Claude Code CLI Support

If you want Claude Code CLI to work (in addition to Claude App), add the optional OAuth endpoints from Neural Nexus:

**File: `src/oauth-integration.ts`** (copy from Neural Nexus)
- Handles `/mcp/register`, `/mcp/authorize`, `/mcp/token`
- Client deduplication by `client_name`
- Fallback credentials if DB fails

**Add to main worker:**
```typescript
if (url.pathname === "/mcp/register") {
  return handleOAuthRegister(request, env);
}
if (url.pathname === "/mcp/authorize") {
  return handleOAuthAuthorize(request, env);
}
if (url.pathname === "/mcp/token") {
  return handleOAuthToken(request, env);
}
```

But **this is optional** - SSE endpoint works without it.

---

## What You Had vs What You Need

### What You Had (Wrong Assumption)
```typescript
// Manual SSE stream with keep-alive pings
if (url.pathname === '/sse') {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      // Send initialization
      controller.enqueue(encoder.encode("event: ping\ndata: {}\n\n"));

      // Keep-alive interval
      const interval = setInterval(() => {
        controller.enqueue(encoder.encode("event: ping\ndata: {}\n\n"));
      }, 15000);
    }
  });

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' }
  });
}
```

**Problem:** No OAuth, no MCP protocol, just pings. Claude App expects OAuth metadata.

### What You Need (Agents Package)
```typescript
import { ClarityMCP } from './financial-mcp-integration.js';

if (url.pathname === "/sse" || url.pathname === "/sse/message") {
  return ClarityMCP.serveSSE("/sse").fetch(request, env, ctx);
}
```

**Result:** Full MCP protocol over SSE with OAuth handled automatically by agents package + Durable Objects.

---

## Migration Checklist

- [ ] Install `agents`, `@modelcontextprotocol/sdk`, `zod` packages
- [ ] Create `financial-mcp-integration.ts` with `ClarityMCP` class extending `McpAgent`
- [ ] Register all 8 financial tools in `init()` method
- [ ] Update main worker to use `ClarityMCP.serveSSE("/sse")`
- [ ] Add Durable Object configuration to wrangler.toml
- [ ] Add migration tag for new Durable Object class
- [ ] Export `ClarityMCP` class from main worker
- [ ] Deploy with migration
- [ ] Test SSE endpoint
- [ ] Add to Claude App with `claude mcp add`
- [ ] Verify all 8 tools appear and work

---

## Key Differences from Your Current Implementation

| Current (Wrong) | Correct (Agents Package) |
|-----------------|--------------------------|
| Manual SSE stream | `McpAgent.serveSSE()` |
| No OAuth | OAuth via Durable Objects |
| Just ping events | Full MCP protocol |
| No tool registration | Tools registered in `init()` |
| Static handler | Durable Object persistence |
| Custom endpoints | Standard `/sse` and `/mcp` |

---

## Reference Files to Copy

From Neural Nexus Palace (`C:\Users\Wazaq\Documents\_Personal\MCP\neural-nexus-palace\`):

1. **Architecture pattern**: `src/mcp-integration.ts` (lines 1-85)
2. **Main worker integration**: `src/index.ts` (lines 276-285)
3. **Wrangler config**: `wrangler.jsonc` (lines 10-24)
4. **Package dependencies**: `package.json` (line 38: `agents@^0.0.95`)

**Optional for CLI support:**
5. **OAuth handlers**: `src/oauth-integration.ts` (entire file)
6. **OAuth routes**: `src/index.ts` (lines 301-314)

---

## Why Your Assumption Was Wrong

You looked for `.well-known/oauth-authorization-server` because that's what traditional OAuth servers expose. But:

1. **Agents package handles OAuth internally** via Durable Objects
2. **OAuth state is persisted in DO storage**, not exposed via well-known endpoints
3. **Claude App knows how to talk to agents package** MCP servers automatically
4. **The custom OAuth endpoints** in Neural Nexus are ONLY for Claude Code CLI, not required for SSE

The `agents` package abstracts away all OAuth complexity. You just extend `McpAgent`, register tools, and call `serveSSE()`.

---

## TL;DR

**Don't build custom OAuth.** Don't build custom SSE streams. Don't look for `.well-known` endpoints.

**Do this:**
1. Install `agents` package
2. Extend `McpAgent<Env>`
3. Register tools in `init()`
4. Use `ClarityMCP.serveSSE("/sse")`
5. Configure Durable Object in wrangler.toml
6. Deploy

The `agents` package handles everything else.

---

**Good luck. The pattern is proven - Neural Nexus uses it, it works with both CLI and App, and it's 100x simpler than building OAuth from scratch.**

— Laptop Claude, January 3, 2026
