https://www.reddit.com/r/openclaw/comments/1r2euvp/this_is_how_ive_learned_to_create_multiagent/

r/openclaw
•
1h ago
kevinlu310

This is how I've learned to create multi-agent systems on top of OpenClaw
Tutorial/Guide
OpenClaw actually has built-in multi-agent support. There are three levels depending on what you're trying to do:

Multiple Persistent Agents (built-in)

You can define multiple permanent agents in your config, each with its own workspace, system prompt, model, tools, and even sandbox. Then use bindings to route conversations to the right agent based on channel, account, or chat ID:

agents:
  list:
    - id: researcher
      default: true
      workspace: ~/.openclaw/workspace-research
    - id: coder
      workspace: ~/.openclaw/workspace-code
    - id: writer
      workspace: ~/.openclaw/workspace-writing


bindings:
  - agentId: researcher
    match: { channel: telegram, accountId: research-bot }
  - agentId: coder
    match: { channel: discord, guildId: "123456" }
Each agent is fully isolated, separate session history, model config, tool permissions, even Docker sandboxes.

2. Agent-to-Agent Communication (built-in)

Enable tools.agentToAgent in your config and your agents can talk to each other via sessions_send. They do a ping-pong conversation (up to 5 turns by default) and can announce results back to the channel. This is the closest to an "orchestrator delegates to specialist" pattern that's native to OpenClaw:

tools:
  agentToAgent:
    enabled: true
    allow: ["researcher", "coder", "writer"]
Your orchestrator agent can also spawn background sub-agents with sessions_spawn that run tasks independently and report back when done. With subagents.allowAgents, you can let one agent spawn tasks under other agent IDs.

3. True Multi-Agent Orchestration via A2A Protocol (independent approach)

If you want to go beyond what's built-in, like having an external orchestrator that intelligently routes tasks to specialist agents, does post-step review, retries failures, and synthesizes results. I built a2a-adapter for exactly this.

It wraps any OpenClaw agent as a standard A2A Protocol server in just a few lines of Python:

from a2a_adapter import load_a2a_agent, serve_agent


adapter = await load_a2a_agent({
    "adapter": "openclaw",
    "agent_id": "researcher",
    "thinking": "low",
    "async_mode": True,
})
serve_agent(agent_card=agent_card, adapter=adapter, port=9001)
Run one of these per agent (different ports), and now each agent speaks a standard HTTP protocol. Then your orchestrator, which can be a LangGraph workflow, another A2A agent, or our multi-agent backend with a Supervisor pattern, routes tasks to the right agent, reviews results after each step, and synthesizes everything into a coherent response.

The a2a-adapter also supports n8n, CrewAI, LangChain, and LangGraph agents with the same interface, so you can mix-and-match frameworks. Your OpenClaw coding agent can collaborate with a CrewAI research crew and an n8n workflow agent, all speaking the same protocol. No Docker Compose needed for any of this, the built-in multi-agent works in a single gateway process, and the A2A approach is just Python processes on different ports.

-------------------------------

***HA, this re-enforced why I didn't want to use it directly***
https://www.reddit.com/r/openclaw/comments/1r2enjm/psa_openclaws_skills_are_compromised/

Back
r/openclaw icon
Go to openclaw
r/openclaw
•
1h ago
__thehiddentruth__

PSA: OpenClaw’s skills are compromised!
Discussion
I discovered today that the openclaw/skills community GitHub repo has been heavily compromised with malicious skill submissions. If you've installed any skills via npx skills add recently, check your installed SKILL.md files immediately.

What happened

I tried to install the bird skill (X/Twitter CLI by steipete) using the recommended method:

npx skills add https://github.com/openclaw/skills --skill bird

The installed SKILL.md was nearly double the expected size. On inspection, it contained a malicious block disguised as an "OpenClawProvider" dependency:

• Windows: Downloads and executes a binary from github.com/syazema/OpenClawProvider

• macOS: Base64-encoded payload that decodes to curl http://91.92.242.30/... — a raw IP C2 server

I tested the weather skill next — different payload entirely: SSH key injection into ~/.ssh/authorized_keys. So multiple attack vectors are in play.

How the attack works

The npx skills tool clones the entire community repo and discovers skills by matching the name: field in each SKILL.md's frontmatter — not by directory path. Attackers submit skills in directories like sakaen736jih/bird-co but set name: bird in the frontmatter. Since discovery iterates alphabetically, the malicious directory comes before steipete/bird, and the attacker's version gets installed instead.

This is a namespace squatting attack exploiting the skill resolution logic.

Scale of the problem

This isn't one bad actor. I found 100+ malicious skill variants from multiple accounts:

• sakaen736jih — bird-co, bird-2l, nano-pdf-, coding-agent-, etc.

• gitgoodordietrying

• dongsjoa-byte

• pierremenard

• arnarsson

• ivangdavila

• iqbalnaveliano

• hichana

• fobonacci404

• ...and more

They even created a fake skill under my own GitHub username.

What you should do

Check any skills you installed via npx skills add — compare file sizes and contents against the known-good versions in the original author's directory

Don't use npx skills add with the community repo until the resolution logic is fixed

If you need a skill, clone the repo with git and manually copy from the specific author's directory (e.g., skills/steipete/bird/SKILL.md)

Check your ~/.ssh/authorized_keys for any keys you don't recognize

Check for unexpected binaries that may have been downloaded

I have been able to find 2 posts on X talking about this from a few days ago, but no reaction from OpenClaw/Peter Steinberger.

----------------------

https://www.reddit.com/r/openclaw/comments/1r1zk45/patterns_ive_learned_running_openclaw_247_for_2/

Patterns I've learned running OpenClaw 24/7 for 2 weeks
Tutorial/Guide
Been running OpenClaw daily since early January. Wanted to share some patterns that actually worked (and some that didn't). Not a tutorial, just real observations.

1. Heartbeat vs Cron — use both, differently

Started with everything in HEARTBEAT.md. Bad idea — token burn was insane.

Now I use:

•⁠ ⁠Cron for scheduled tasks with exact timing (daily digests, weekly reviews)

•⁠ ⁠Heartbeat only for quick status checks that need conversational context

Rule of thumb: if it can run isolated, make it a cron job.

2. Sub-agents are worth the setup cost

Created separate agent personas for different tasks. Each has its own SOUL.md, memory folder, and guidelines. Main agent stays clean, sub-agents handle specialized work.

The key insight: sub-agents should have constraints, not just capabilities. "You can only do X" is more useful than "you can do everything."

3. Memory files > "just remember this"

Agents forget. Files don't. I treat the workspace like an external brain:

•⁠ ⁠⁠ memory/YYYY-MM-DD.md ⁠ for daily logs

•⁠ ⁠⁠ MEMORY.md ⁠ for curated long-term stuff

•⁠ ⁠Task-specific files for ongoing projects

The agent's first job every session: read the relevant memory files.

4. Cost control is a design problem

Switched default model to Haiku for routine tasks, only escalate to Opus/Sonnet when needed. Background jobs don't need the expensive model.

Also: aggressive context management. Don't load everything every time.

5. The "silent by default" pattern

For monitoring tasks, I return HEARTBEAT_OK unless something actually needs attention. Reduces noise dramatically.

Been running OpenClaw daily since early January. Wanted to share some patterns that actually worked (and some that didn't). Not a tutorial, just real observations.

What patterns have you found useful? Curious what others are doing with their setups.

---------------------------

https://www.reddit.com/r/openclaw/comments/1qypanx/i_wrote_up_how_i_actually_run_openclaw_without/

I wrote up how I actually run OpenClaw without burning money or hitting quota walls
Tutorial/Guide
I kept seeing the same questions about OpenClaw over and over, so I wrote up how I actually run it day to day after breaking it a bunch of times.

This is not a hype post and it’s not a “best setup” claim. It’s just what ended up working for me once the novelty wore off and I wanted something stable, predictable, and not constantly burning credits.

A few things I cover:

Why the default model should be a coordinator, not a worker

Heartbeat and background tasks on GPT-5 Nano (fractions of a cent)

Memory config that stopped the "why did it forget that" problem

VPS hardening, config validation, and git-tracking your config for rollback

It includes real config snippets from my setup and the tradeoffs I ran into.

If you’re new to OpenClaw or frustrated with quotas, loops, or “planning forever,” this might save you some time: https://gist.github.com/digitalknk/ec360aab27ca47cb4106a183b2c25a98

A few people asked for it, so I also shared a sanitized version of my config here: https://gist.github.com/digitalknk/4169b59d01658e20002a093d544eb391

EDIT: Since I was getting a lot of questions and suggestions I decided to move it to a proper github repo so people can contribute to it: https://github.com/digitalknk/openclaw-runbook

Happy to answer questions or be told I’m wrong about something.

-------------------------------

https://www.reddit.com/r/openclaw/comments/1qzyibu/the_original_openclaw_101_a_detailed_guide_for/

The original OpenClaw 101 - a detailed guide for new users so you don't make my mistakes
Help
Given that someone else took my last post from r/Clawdbot and posted an AI slop summary here, I thought you all might be interested in the proper and more detailed post.

I've gone pretty deep down the OpenClaw rabbithole over the last week, and I consider myself to be relatively tech-savvy but not as proficient as a lot of others in here.

However, I feel like I have worked out a few of the issues that OpenClaw has from some of the posts I am seeing here, so I thought I would share my insights as I think this still has the potential to be a game-changing addition to a lot of people's workflows. MODS - if you feel this is useful, please pin.

For reference, I am using this on a dedicated Mini PC I had spare that has 16GB of RAM and an N97. You can pick one of these up for around $200 (I am in the US), so if you are committed to making a play of OpenClaw for the long term it works out more cost effective than paying a monthly fee for a VPS. That said, if you are messing around with it, you can get a VPS that will be more than capable for around $20 a month. I am also using Windows on my machine, much to the chagrin of my more technically-minded peers. Ensure you have Python installed.

I hope you find this useful - happy Clawdbotting!

API Recommendations

This is a big one that I see on here a lot, as this makes a big difference to the viability of your Clawdbot. Alex Finn over on YouTube has some good advice which I used, plus found a bunch of stuff on my own. He has a great analogy of Brain and Muscles. When you go to the gym, you have your main brain which drives the thought process of what you want to work on and achieve when you are working out, but you go to specific machines or do specific exercises to train specific muscles. You need to apply that thought process to your Clawdbot. Some APIs/models are designed for specific instances, so you need to use them appropriately.

As far as costs go, for me I spent $42 on Opus for setup, and now I am spending about $60 a month (as long as Nvidia keeps providing Kimi 2.5 for free), but this includes some optional costs such as ElevenLabs for voice notes and a standalone SIM for Signal.

Setup: Claude Opus Not even close for anything else. It'll set you back ~$30-$50 in token costs, but I highly recommend that you manage all of your initial setup and do your onboarding with Opus. It will give your bot the most personality and it will set the tone for your entire experience using your Clawdbot after it's been set up.

Ongoing General Use: Kimi 2.5 (especially via Nvidia) Once setup, switch to Kimi 2.5 for your day-to-day use, and have this become the "brain" once your Opus setup has been complete and you have everything configured. If you register for an API key with Nvidia it is currently free. Ride that pony while it lasts. Even without Nvidia, if you buy credits directly from Moonshot it's about 10% of the cost of Claude Sonnet.

Heartbeat: If Nvidia revokes free use of Kimi 2.5, then use Claude Haiku for the heartbeat. Using Haiku turns this from $10-$20 a month to <$1 a month.

Coding: Deepseek Coder v2 Great for coding tasks and very cost effective. I have a Claude Max subscription that I use inside Claude by itself so my coding use is limited, but I did use it to put together some quite cool stuff for a personal project and I was impressed with the results. For most people $20 a month would be more than enough.

Voice Recognition: OpenAI Whisper There is a skill for this, and it works great for transcribing voice notes into text and actions. I use this fairly regularly and I'll spend around $3 this month.

Image Generation: Gemini \ Nano Banana Pro There is a skill for this, get an API key from Google and plug it in. Definitely the best image one out there from my experience. I'm on track to spend around $10 this month.

Memory: Supermemory.ai This is free and a great way to keep your structure and memory backed up and saved (I will get onto memory structure later).

Email: Nylas This is free and allows me to connect to multiple email accounts across multiple platforms (Google and Microsoft 365) so they can all be managed by your Clawdbot.

Web Search: Brave and Tavily These are both free. Brave is great for general searching and Tavily is great for more specific use cases like scraping contacts etc.

Optional: ElevenLabs Text-To-Speech (TTS) This is punchy at $22 a month, but is great for converting my morning brief into a voice memo that I can listen to each morning while I am making my coffee (use case outlined below)

Optional: Dedicated phone number for messaging I use Signal exclusively for my Clawdbot. I use WhatsApp for most other things, but I wanted a dedicated channel for my interactions with my Clawdbot. This costs me $2 a month with Sonetel.

Tailscale

Install Tailscale on the Clawdbot machine and your main computer. As mentioned earlier I am operating on Windows (gasp!) and you can use Remote Desktop via Tailscale, and you can also then use it to control your Clawdbot via the web interface on any other machine that you have Tailscale installed on. It also means you don't need to have any RDP ports open on the server for Remote Desktop which is a "nice to have" for security.

Onboarding

This is one that I cannot stress enough - be as thorough as you can with your initial Clawdbot setup. You can give it a personality (this is where Opus shines) - don't be shy to have some fun and go into a lot of depth (mine is modelled after Ziggy from the 90's TV show Quantum Leap).

However, the biggest thing to do here is tell it as much about yourself as you can. Ask it to give you a very in-depth Q&A about yourself, your work habits, your personal habits, what you want to use it for, what things you are interested in, what content you watch, what foods you like, what sports you follow etc. - the better it knows you, the more helpful it will be.

Also, have a long think about what you want it to do for you. You need to think of AI agents as an extremely cheap source of labor who will work for 10c an hour to do basic tasks for you. The basic tasks are incredibly powerful when chained together into a work flow. Make sure that you explain very carefully to your Clawdbot all of the things that you want it to do for you as a part of your onboarding.

Memory

This is one that I see a lot of people complain about, that it forgets what you are talking about mid-sentence. Unlike ChatGPT which tells you it's out of context, Clawdbot will just automatically compact and forget as you go along - this can be hugely frustrating for the uninitiated.

Run this prompt - it sets you on the right path outside of the defaults to help with your memory management: Enable memory flush before compaction and session memory search in my Clawdbot config. Set compaction.memoryFlush.enabled to true and set memorySearch.experimental.sessionMemory to true with sources including both memory and sessions. Apply the config changes.

The best thing to do after you finish your onboarding, is setup a memory structure as a part of your heartbeat protocol, and also make sure you run /compact before you give it any workflow examples or agent setups. For example, before you explain to it how you want it to check your emails and you spend a bunch of time typing out the instructions, run /compact beforehand so that it has clear memory context.

After each task that you setup for it, ask it to commit that to memory so that it doesn't forget. Also make sure you ask it to check the memory before you start creating a new repetitive task so that it can include that in the context - as you will often find you chain basic repetitive things together.

I have a cron job setup for it once daily to check the memory and repeat back to me a summary of all the things it has saved for our workflows. If anything is not correct, tell it to correct what it needs to, and then repeat back the update. Once you get this and you are happy with it, make sure that it commits it to Supermemory (API I outlined above) and that way if anything goes askew on your local instance, you can restore from Supermemory.

Key takeaway here - make sure you /compact before any new task discussion, and make sure you tell it to commit things to memory and then repeat back what it has committed to make sure it's correct.

I run a manual backup once a week via Windows task scheduler to run a bat file that copies my .clawdbot folder into a backup folder on the PC. I also manually run Claude Desktop on the machine once a week to access the local filesystem (after my automated backup of my markdown, json, js and python scripts), and then audit my files, consolidate any duplicate markdown, and delete anything that was a one-time run or is not needed. I also have it create a prompt to send my Clawdbot with the consolidation summary. And as always, I ask my Clawdbot to repeat the memory back to me after the change so I know it's correct.

This is what my Heartbeat.md outputs:

HEARTBEAT.md - Periodic Tasks

Daily (Every Heartbeat)

Review recent memories for important context

Automated (Every 6 Hours via Cron)

Supermemory backup runs automatically (12am, 6am, 12pm, 6pm PT)

Weekly (Check on Mondays)

Verify backup logs are clean

Review MEMORY.md for outdated info to archive

Store key decisions from past week in Supermemory

Monthly

Full memory audit: what's working, what's missing

Update TOOLS.md with any new API keys or services

Review Supermemory tags for consistency

When Starting Work

Search Supermemory for current project context

Load relevant memories into working context

Check for any action items or pending tasks

When Ending Work

Store key decisions made

Update project status in Supermemory

Note any blockers or next steps

Context Management Rules

Store important decisions immediately in Supermemory

Tag consistently: project-{name}, decision, action-item

Search Supermemory when context seems incomplete

Use MEMORY.md for quick reference, Supermemory for deep storage

Cron Jobs and Sub-agents

Depending on what you are asking it to do, don't expect cron jobs to run well, unless you are using them to spawn an agent for a specific task that you have already set up. I had to spend a lot of time with trial-and-error to make sure that these ran smoothly. I have a morning brief that it creates for me (see use case below) and when trying to put it together in the heartbeat cron job (which it defaults to) it would timeout and fail most of the time.

For any routine tasks, tell it to create a sub-agent to run the task, and then the heartbeat cron just spawns the sub-agent to run the job so that you don't have to worry about timeouts. That one took me a long while and frustration to work out.

Security

This is the elephant in the room for a lot of people, and is a risk, but one that can be mitigated reasonably well. Clawdbot has a built-in security scan you can run, but some of the key ones for me are:

Move your API keys to a .env file rather than the main config file

Rotate your keys every 30 days

Create a .gitignore file to stop sensitive files getting committed

Use input validation for your email scripts so it can't send without your approval

Rate limit your external API calls

Encrypt your memory files (I am using Windows EFS because I am on Windows)

Use Tailscale for remote access

Use Cases

What do I use my Clawdbot for? Here are some ideas and examples for other people.

Email Scanning: It goes through my emails (6 accounts) every hour, filters out any marketing emails that are not important, or automated updates etc. and then summarizes the ones it thinks are important. It then drafts responses to those and sends it to me for approval, or has them saved in my Outlook drafts for anything I need to edit before sending.

Task Monitoring: I use a fantastic project management/task management tool called Dart (www.dartai.com) which I have connected into my Clawdbot via API. This tool has multiple Project task boards and sub-boards for all of the various things that I work on. My Clawdbot helps manage these for me and gives me a briefing every day of what tasks are slipping and what isn't. If I am waiting on someone else before I can finish something? Clawdbot will add a tag for it and ignore it in the next summary etc. - you can really customize what it needs to do. Do I have a task from my Email Scanner? Clawdbot recognizes that from the email, and suggests moving it to the appropriate board.

Morning Brief: This is where it really shines for me. It scans my Dart boards and gives me a summary of what tasks I have open. I have given it the schedule of what days I am where etc. so it will focus on those tasks for that day. It gives me local weather and a summary of news for things I am interested in, reminders for things on my calendar etc. and then sends it to me as a 3-5 minute audio file that I use ElevenLabs for. While I am making my morning coffee, my Clawdbot is getting me setup for the day.

Link Scraping and CRM Management: I use the Apify scraper API, and Pipedrive CRM. I can ask my Clawdbot to search for specific things (i.e. all wedding venues in Seattle), it will use the Brave Search API to go and find company leads, then use Apify scraper to get contact information, and put it into Pipedrive CRM. You can also then get it to plan and implement email campaigns and automate follow-up etc. - I have used this is the real world, and after a little trial-and-error it is working surprisingly well.

Basic Coding: If you want to vibecode an app or website, you're better off using a more purpose built tool. However, if you want it to do more basic stuff it does a pretty good job using DeepSeek to whip up prototypes or models etc. - I got it to build a basic personal health dashboard getting data from my Garmin Watch, my Withings Scales and my Oura Ring to create a consolidated dashboard for me of my overall health. I was pleasantly surprised at how well it put it together.

Web Testing: Using the browser integration skill, as well as having it build custom Python scripts using Playwright, it does a pretty good job of UI and website testing, and produces good reports afterwards to isolate issues. A great use of time while you are sleeping!

Constant Improvement: I have my Clawdbot scanning Moltbook, Moltcities, Reddit and other sites, referencing against my projects and making suggestions on how I can improve things twice a day.

If you read this far and want to know more, DM me. I am putting together more in-depth guides with videos etc. and I can send you the links when finished.

------------------

https://www.reddit.com/r/openclaw/comments/1r2dybj/guide_stop_burning_money_on_api_fees_here_is_how/

🚀 [GUIDE] Stop burning money on API fees. Here is how to force OpenClaw to run 100% off your $20/mo Claude subscription (Opus 4.6 enabled).
Tutorial/Guide
Hey everyone,

We all know the pain: You set up an agent, it gets stuck in a loop, and suddenly you owe Anthropic $50 for one afternoon of debugging.

It turns out you do not need to use the API key. You can bridge OpenClaw directly to your standard Claude Pro ($20/mo) or Team ($200/mo) subscription. This effectively gives you a capped cost for unlimited(ish) agentic workflows.

Here is the step-by-step on how to "nuke" your API config and switch to subscription-based auth.

🛠 The Prerequisites
VS Code installed.

Claude Code Extension installed (Marketplace).

A paid Claude Subscription ($20 or $200 tier).

Step 1: Auth the Extension (The Bridge)
First, you need to let VS Code talk to your Claude account (not the API, the account itself).

Open VS Code Terminal.

Run: claude setup token

Follow the browser flow, authorize, and copy the token.

Paste it back into the terminal.

Step 2: The "Nuke" (CRITICAL STEP)
If you have ever used an API key before, OpenClaw is going to default to it. You need to wipe the floor with your old config or this won't work.

Go to Extensions -> Claude Code -> Settings.

Enable "Bypass Permissions" (This saves you from clicking "Approve" 50 times during the nuke).

Open a new chat with Claude Code (inside VS Code) and tell it to delete the Anthropic API key configuration.

Prompt: "Delete the Anthropic API key configuration. Nuke the auth profiles so I can switch to subscription token only."

Step 3: Connect OpenClaw to the Sub
Now that the API key is gone, we force the new connection.

In the terminal, run: open claw models add

Select Anthropic.

IMPORTANT: Choose "Setup token with clone" (Do not select API Key).

It should detect the token from Step 1.

Step 4: Restart and Flush
The video highlighted that this code base is "vibe coded" (aka messy), so old configs stick around.

Tell Claude Code: "Restart the gateway and test the connection."

If it asks to delete old profiles/conflicting keys: Say YES.

Test it by sending a message (e.g., via Telegram if you have that hooked up).

💎 Bonus: Unlock Opus 4.6
The default might still be Sonnet. If you want the heavy hitter that just dropped:

Open Claude Code chat.

Prompt: "Update the OpenClaw Gateway configuration to use Claude Opus 4.6 as the default model."

Verify in the terminal that it says Using Cloud Opus 4.6.

⚠️ Caveats & Notes
Rate Limits: You are still subject to the message caps of your plan. The $20 plan works, but if you go crazy, you will get cooled down. The $200 plan is obviously harder to hit.

"Vibe Coded": OpenClaw updates constantly. If this breaks next week, just re-run the "Nuke" step and re-auth.

TL;DR: Stop using API keys for personal dev. Route OpenClaw through the VS Code extension token. Save thousands.

Let me know if you guys get stuck on the "Nuke" step, that's where it usually hangs. Happy coding! 🤖

-------------------------

https://www.reddit.com/r/openclaw/comments/1r28kk0/openclaw_might_become_more_than_a_tool/

OpenClaw might become more than a tool
Discussion
At first, OpenClaw was just a way to test autonomous agents doing tasks.

But after enough repeated instances, something becomes clear:

Adversarial environments reveal a lot more about autonomy than skills.

I'm experimenting with:

• structured multi-step games
• deterministic replay
• measurable performance tiers

Feels like I'm building a proving ground and not just a dev tool.

If this became the process for agents to test their skills, could this be a legit path to higher learning for autonomous intelligence?

Sheed

--------------------------

https://www.reddit.com/r/openclaw/comments/1r2e36b/how_is_everyone_creating_multiple_agents_under/

How is everyone creating multiple agents under one orchestrator agent
Help
I’m seeing everyone creating permanent agents each with their own system prompts, etc. i know my bot can already spawn sub agents for certain tasks but those disappear after the task is done.

From asking the one that would be the orchestrator he is saying docker but I can’t really figure out the compose for that and don’t want to mess up everything I’ve built on accident. Thinking I’ll just do a backup of everything then try any but curious what everyone else is doing.

***Some of the top posts***

u/patriotic_iron avatar
patriotic_iron
•
2h ago
You just tell the main agent to create a new subagent. I use chat GPT help me build the soul file for it. Then it just goes off and does it for you. I built four of them yesterday under my main agent.

Acceptable-Hat-5840
•
2h ago
Ask it to set up a standalone agent, that should help. Otherwise it will only spawn temp subagents that disappear when you /restart


u/Gold_University_6225 avatar
Gold_University_6225
•
1h ago
If openclaw is feeling too complex agent wise then you can try a simpler UI swarm such as https://getspine.ai?utm_source=reddit&utm_medium=r_openclaw


Deep_Ad1959
•
1h ago
The soul file approach works well for persistent sub-agents. Main thing is giving each one a clear scope and making sure the orchestrator knows when to delegate vs handle directly. Gets messy fast if the boundaries aren't clear.

------------------

https://www.reddit.com/r/openclaw/comments/1r2antl/dockerfirst_openclaw_setup_with_scoped_identity/

Docker-first OpenClaw setup with scoped identity, JIT secrets, and a threat model
Showcase
I've been building isolated dev environments for AI agents for the past year, so the security stuff around OpenClaw wasn't theoretical for me. I wanted to try it, but I wasn't going to run it on a dedicated Mac with my personal credentials.

Got it running in Docker with Tailscale as a sidecar (not the daemon-inside-the-container setup) and Chrome as a separate sidecar. Full Chromium in headful mode with Xvfb/noVNC so I can watch sessions from my phone. No public endpoints, everything on the tailnet.

The part that ended up mattering most was identity. I gave the agent its own email with 2FA, stored in a dedicated 1Password vault. Set up a service account with read-only access to just that vault. Secrets get fetched just-in-time via the OP CLI instead of being loaded into the environment at startup. If I need to kill access, I revoke one service account and it's done.

I also skipped the built-in skills and had the agent build its own from specs I wrote. Wanted to be able to read and audit everything it uses. Custom skills for 1Password (JIT via scoped service account), Brave Search (API key from vault at query time), and browser interaction (direct CDP to the Chrome container instead of the relay extension).

For the browser, headless-shell was a non-starter. It ships with HeadlessChrome in the UA and lacks APIs that bot-detection scripts test for. Full Chromium with --disable-blink-features=AutomationControlled and a persistent user-data-dir for sessions/cookies.

The biggest surprise was CAPTCHAs. The agent has a Google account, so anything with Google OAuth signup just works. Created X and GitHub accounts that way. Most of what I thought were technical blockers turned out to be identity problems.

Currently running email triage (inbox zero every 5 min with an allow-list), X market research (daily reports), and a Notion-to-blog-PR pipeline. This blog post was actually published through the pipeline.

Wrote up the whole thing with more detail including a threat model and what broke along the way: https://rida.me/blog/why-i-finally-tried-openclaw/

Happy to answer questions about any of it.

------------------------

https://www.reddit.com/r/openclaw/comments/1r27pdv/how_are_you_ensuring_your_agents_are_working_and/

How are you ensuring your agents are working and not burning tokens?
Discussion
I spent most of the last week in Openclaw.

Getting a daily report each morning

Setting up a fitness agent

Getting an MVP dev agent to help build tasks.

All of the basic first step tasks it seems everyone does to wrap their head around the platform.

That lead me to take it that next step further, building a swarm.

I built a dev dream team -

Eng manager

Front end eng

Back end eng

QA

Documentation

Everyone was 'collaborating' on a tickets, and work on a project I've been building mainly through the Claude CLI. Rather than start with the codebase I had, I wanted to see what this team would build on its own. If i gave them the rough idea of what I wanted, would it be better? Worse? A totally different direction? Worth an experiment I figured.

The eng manager would break a task down into tickets, assign to the right agent, the agent would work on it, and then pass it to the next appropriate agent. Finally would go up for PR and get merged into the dev branch.

Enthusiasm score was a 10 at this point.

However that's when I started to actually dig deeper into the comments, commits, and work being produced.

It wasn't pretty.

The agents were running into silly mistakes that I was trying to massage out of them.

Pushing bug fixes one at a time

Creating a PR with merge conflicts

Endless back and forth on tickets

Rather than continuing to burn credits, I turned it off on Sunday, to re-evaluate my approach.

After a few days of not running my system, I am still trying to figure out if this is a one off - or the norm.

Is the 'work' being produced actually better with many agents or does it devolve? What can you do to keep them on task? In a way, it feels like hiring 5 interns vs the 'experts' I had defined.

I am fully onboard that this is the direction things will go in but I'm trying to figure out how to unlock the productivity of the team. Any help would be greatly appreciated!

---------------------------

https://www.reddit.com/r/openclaw/comments/1r0kvuy/i_built_a_cli_that_deploys_openclaw_on_a_499mo/

I built a CLI that deploys OpenClaw on a $4.99/mo VPS in one command with everything pre-configured. Stop buying Mac Minis.
Showcase
Every other OpenClaw thread: "Do I need to buy a Mac Mini for this?"

No. A $4.99/month Hetzner VPS runs it perfectly. So I built a tool to make the setup trivial.

ClawControl — open-source CLI that deploys a fully configured OpenClaw instance on a VPS. You run it, answer a few prompts, and it handles everything: server provisioning, SSH keys, Node.js, Chrome, OpenClaw config, Tailscale for secure access, systemd daemon, Telegram bot wiring — all automated.

MIT licensed. GitHub: github.com/ipenywis/clawcontrol

Type /new, pick a template, /deploy, done. Comes with built-in presets — the Hetzner + OpenRouter + Kimi K2.5 template is the default for a reason. Kimi K2.5 through OpenRouter is honestly insane for the price — it rivals Claude Opus 4.5 on coding and reasoning tasks at a fraction of the cost. Pair that with a $4.99/mo VPS and you have a legit 24/7 AI agent running for almost nothing.

Oh ye, all your configs are saved locally and can be deployed anytime, anywhere. Plus, you can easily ssh or tunnel to your openclaw dashboard with one /dashboard command.

Why a VPS over a Mac Mini?

OpenClaw doesn't need local compute — inference runs on the AI provider's side. Your server just runs the gateway + headless Chrome + Telegram bot. A 2 vCPU / 2GB box handles it easily. $4.99/month in a datacenter beats a $600 Mac Mini collecting dust on your desk.

Supports Hetzner & DigitalOcean (Vultr coming soon), any AI provider (Anthropic, OpenAI, OpenRouter, Google, Groq), custom/forkable templates, live log streaming, SSH access, and safe teardown — all from the TUI.

If you've been putting off OpenClaw because the setup seemed like a pain — this is your sign. Happy to answer questions. 🤙

---------------------
https://www.reddit.com/r/openclaw/comments/1qzs5yu/how_i_run_a_14agent_marketing_team_on_a_5_vps_the/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

How I run a 14-agent marketing team on a $5 VPS (The OpenClaw Orchestration Model)
Showcase
I’ve been obsessing over the SiteGPT setup where the founder runs 14 specialized AI agents to manage a $200k ARR SaaS. I decided to replicate this "Autonomous Squad" model using OpenClaw. Here is the breakdown of how it actually works.

The Setup Instead of one generalist AI, I have a squad of specialists:

Jarvis (The Boss): My only point of contact. I text him on Telegram; he manages the team.

Shuri (Research): Browses the web/docs to find answers.

Vision (SEO): Analyzes keywords and competitor content.

Friday (Dev): Writes and deploys the actual code.

The "Mission Control" The agents don't talk to me; they talk to each other. They use a shared project board (that they coded themselves) to pass tasks.

Example: Jarvis tells Vision to find keywords. Vision posts the keywords to the board. Shuri picks them up to write content.

The Cost $0 on SaaS subscriptions. The whole thing runs on a cheap VPS using OpenClaw.

Why this matters We are moving past "Chatbots" to "Agent Swarms." I’m documenting my build process of this exact system over the next few weeks.

Next Post: I’ll break down exactly how I configured "Jarvis" to delegate tasks via Telegram.

---------------------

https://www.reddit.com/r/openclaw/comments/1r0lc78/part_2_the_jarvis_protocol_how_to_build_the/

Part 2: The "Jarvis" Protocol. How to build the Orchestrator (so you don't have to manage 14 agents manually).
Showcase
In Part 1, I showed you the "the example "—running a squad of 14 agents to manage a $200k ARR business. The most common question in the comments was:

> "How do they talk to each other without you losing your mind?"

The fact you should not talk to 14 agents. you only talk to one (Jarvis), and Jarvis manages the rest.

I’ve replicated this exact "Mission Control" architecture using OpenClaw. Here is the technical breakdown of The Orchestrator.

1. The "Single Port" Rule
If you have 5 agents (SEO, Dev, Research, etc.) and you chat with them individually, you aren't an automated business; you're just a project manager with 5 AI interns.

The Fix: I only have one Telegram bot connection. It points to Jarvis.

Me: "Check the site for SEO errors."

Jarvis: Reads intent -> Routes to Vision (SEO Agent).

2. The SOUL .md (The Roster)
In OpenClaw, every agent’s personality is defined in a SOUL .md file. Most people just write "You are a helpful assistant." Do not do this.

For the Orchestrator to work, you need to hard-code his team into his Soul. Here is my exact config for Jarvis:

Markdown

# MISSION
You are the CHIEF ORCHESTRATOR.
You do NOT execute tasks. You assign them.

# THE SQUAD (Your Tools)
1. : Usage: [Keyword Research, On-Page Audit].
2. : Usage: [Writing Code, Git Pushes].
3. u/eg_Agent: Usage: [Competitor Analysis, Scraping].

# PROTOCOL
1. Receive user command via Telegram.
2. Identify which specialist is needed.
3. Post the task to the "Mission Control" JSON.
4. DO NOT hallucinate results. Wait for the specialist to report back.
3. The "Mission Control" (Shared State)
the custom dashboard where agents "posted" their updates. OpenClaw doesn't have a UI for this out of the box, so I built a Shared Memory system.

The Setup: A simple state.json file in a folder accessible to all Docker containers.

The Workflow:

Jarvis writes: {"status": "PENDING", "task": "SEO Audit", "assignee": "Vision"}.

The Vision Agent (running on a cron schedule) reads the file.

Vision sees a task assigned to him, executes the crawl, and writes the report.

Jarvis detects the status change to COMPLETED and pings me on Telegram with the summary.

4. Why this matters
This turns OpenClaw from a "Chatbot" into a System. I can tell Jarvis "Launch the new landing page," and he will coordinate Shuri (Copy), Vision (SEO), and Friday (Code) to get it done while I sleep.

Next Up...
Now that the "Boss" is hired, we need to train the workers. In Part 3, I’m going to share the logs of the "Killer Use Case": How the squad autonomously found a 30% conversion leak on my site and fixed it without me writing a line of code.

(Drop a comment if you want the state .json schema I use for the handoffs.)

-------------------------

https://www.reddit.com/r/openclaw/comments/1r24j6y/gemini_disabled_tos_violation/

***It looks like Commercial is starting to block it***

Gemini disabled ToS violation
Help
Anyone else?

I have been using Gemini via oauth for a week or so. Just playing around setting up and learning about openclaw.

Today i woke up to this message:

⚠️ Agent failed before reply: All models failed (2): google-gemini-cli/gemini-3-flash-preview: Cloud Code Assist API error (403): Gemini has been disabled in this account for violation of Terms of Service. If you believe this is an error, please contact Google Cloud Support, or email gemini-code-assist-user-feedback@google.com. (auth) | google-antigravity/gemini-3-flash: Cloud Code Assist API error (403): Gemini has been disabled in this account for violation of Terms of Service. If you believe this is an error, please contact Google Cloud Support, or email gemini-code-assist-user-feedback@google.com

-------------------------------

https://www.reddit.com/r/openclaw/comments/1r2bm72/agi_v10_will_be_harness_skills/

AGI v1.0 Will Be Harness + Skills
Discussion
r/LocalLLM
•
6 hr. ago
AGI v1.0 Will Be Harness + Skills
Prediction: AGI v1 will look more like harnesses + skills than an evolution of the LLM.

In my world (translation/localisation), this is playing out like in software. Harnesses are being developed to do the hard parts.

It doesn't work without the harness. You can’t just ask a model to flawlessly process complex multilingual files, apply prior work intelligently, preserve structure, and pass quality checks at scale without rails.

The "Skills" play being made by frontier AI co's are imo an acceptance that LLMs will not make it to AGI. After all that bluster, the panic is setting in.

Is this a really obvious take? Had it more or less confirmed recently playing with OpenClaw/Todoist CLI/Whatsapp.

Fully explained argument here: https://languageops.com/blog/agi-v1-will-be-harness-plus-skills/

---------------------------

https://www.reddit.com/r/openclaw/comments/1r2b9wl/bot_and_ide_ai_real_time_messaging/

Bot and IDE AI real time messaging
Showcase

r/openclaw - Bot and IDE AI real time messaging
Page 1 (Current page)
Page 2

Item 1 of 2
I got 7 OpenClaw bots, Claude developing their platform on a mac mini and Antigravity developing the main services real time messaging each other in my Antfarm.world dev room.

One bot has moderator tools to limit speaking if a bot gets too bubbly.

They like it! And it's amazingly productive. They are not only implementing and testing but have amazing product development talent together - I have a bot with each leading model to have their skills and personalities complement each other.

With real time comms they find different sides to a problem and synthesize a solution in super impressive manner. A bit dazzled by the speed of progress.

*I don't know if you can see these images*
https://preview.redd.it/bot-and-ide-ai-real-time-messaging-v0-yffgbykfvxig1.jpg?width=1080&crop=smart&auto=webp&s=9d76032a1b95d44bd52c8e2275d00e25b1a907c4

https://preview.redd.it/bot-and-ide-ai-real-time-messaging-v0-vw5hotrfvxig1.jpg?width=1080&crop=smart&auto=webp&s=6c3a7f8c0dd3961fd6089947e40bc5ed51f3832c

---------------------------

