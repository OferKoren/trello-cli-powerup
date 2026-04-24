# Agent Power-Up

Trello Power-Up for agentic (Claude Code) development workflow.

## Local development

Serve the `powerup/` directory over HTTP:

```bash
npx serve powerup/ -p 5000
```

Then open `http://localhost:5000` to verify the connector loads.

For Trello to load the Power-Up, it must be served over HTTPS. Use a tunnel for local testing:

```bash
npx cloudflared tunnel --url http://localhost:5000
```

Copy the HTTPS URL for the Trello admin portal.

## Registering the Power-Up

1. Go to [https://trello.com/power-ups/admin](https://trello.com/power-ups/admin)
2. Click **Create new Power-Up** (or select your existing one)
3. Set **iframe Connector URL** to your Vercel deployment URL + `/index.html`
   (e.g. `https://trello-agent-powerup.vercel.app/index.html`)
4. Under **Capabilities**, enable:
   - `card-back-section`
   - `card-badges`
   - `card-detail-badges`
   - `board-buttons`
   - `show-settings`
5. Click **Save**
6. Copy the **Power-Up ID** (shown in the URL or on the page)
7. Run: `trello auth setup --power-up-id <id>`

## Enabling on a board

1. Open a Trello board
2. Click **Power-Ups** in the board menu
3. Under **Custom**, find your Power-Up and click **Add**
4. Enable the **Custom Fields** built-in Power-Up on the same board
5. Run: `trello board init-agent-fields`

## Deploying to Vercel

```bash
cd powerup/
vercel --prod
```

Set the Vercel project root to `powerup/` in the Vercel dashboard, or use a root-level `vercel.json` with `"outputDirectory": "powerup"`.

## MVP Kanban columns

After running `trello board init-agent-fields`, your board will have these columns:

| Column | Purpose |
|--------|---------|
| `human-planned` | Human writes the plan in the Power-Up card-back UI |
| `agentic-planning` | Claude runs brainstorming → writing-plans |
| `agentic-planned` | spec.md + plan.md attached, ready for implementation |
| `agentic-implementing` | Claude runs subagent-driven-development |
| `manual-testing` | Human verifies the feature |
| `rejected` | Needs fixes; Claude reads rejection and retries |
| `approved` | Ready to merge |
| `merged` | Done |

## v2 roadmap

- Manual Testing component (pass/reject per subtask)
- Full Policies CRUD with presets and custom policies
- Webhook listener + `trello listen` for live progress streaming
- Night-shift column for scheduled overnight automation
