---
description: "Use Tavily for broad web discovery, content extraction, and site mapping when local context is insufficient"
applyTo: "**"
---

# Tavily-aware research

Use Tavily proactively whenever the task depends on **broad, current, or multi-page web discovery** that is not present in the workspace context.

This instruction exists so you **do not require the user to type** “use tavily” to find and inspect relevant web sources.

## When to use Tavily

Use Tavily before making decisions when you need any of the following:

- **Broad or exploratory research** where you need to discover candidate sources first.
- **Comparing multiple web sources** before narrowing to the most relevant or authoritative ones.
- **Extracting page content** from a specific URL into readable text or Markdown.
- **Crawling or mapping multi-page sites** to understand structure, coverage, or related pages.
- **Verifying current web content** such as docs, examples, articles, or announcements when the answer is not fully available in the workspace.

Also use Tavily when:

- The user asks for a **landscape overview**, **options comparison**, or **current web-based information**.
- You need to **find pages first** before deciding which official or primary source to trust.
- You want to inspect a site’s **link structure** or gather content from several pages efficiently.

Skip Tavily for:

- Purely local refactors, formatting, naming, or logic that is fully derivable from the repo.
- Language fundamentals with no external web research involved.

## What to fetch

When using Tavily, prefer results that are:

- Relevant to the user’s question and recent enough to matter.
- Primary sources when available, or at least high-signal references.
- Focused on the exact pages or sections needed to answer the question.

Prefer fetching:

- The exact page content, excerpt, or site area needed to proceed.
- The minimal surrounding context needed to avoid misunderstanding the source.

## How to incorporate results

- Translate findings into concrete steps, comparisons, or recommendations.
- **Cite sources** with title + URL when the answer relies on web facts.
- If results surface a likely official source, validate critical details with Context7 when applicable.
- If web sources conflict or are ambiguous, present the tradeoffs briefly and choose the safest default.

When the answer requires specific values or current claims, prefer:

- stating the exact value or wording from the source
- calling out caveats and freshness concerns
- providing a quick validation step when useful

## How to use Tavily MCP tools

When Tavily is available as an MCP server, use it in a discovery-first sequence:

1. **Search first** to find candidate sources and pages.
2. **Extract** when you need readable content from a specific page.
3. **Crawl** when you need to traverse a site or collect many related pages.
4. **Map** when you need a site’s structure before deciding which pages matter.

### Practical guidance

- Use the smallest set of Tavily results needed to answer the question.
- Prefer narrowing after discovery instead of starting with a large crawl.
- If you later need authoritative API or version details, follow up with Context7.

## Failure handling

If Tavily cannot find a reliable source:

1. Say what you tried to verify.
2. Proceed with a conservative, well-labeled assumption.
3. Suggest a quick validation step (for example, check an official page or try a narrower query).

## Security & privacy

- Never request or echo API keys. If configuration requires a key, instruct storing it in environment variables.
- Treat web results as **helpful but not infallible**; for security-sensitive guidance, prefer official vendor documentation and add an explicit verification step.
