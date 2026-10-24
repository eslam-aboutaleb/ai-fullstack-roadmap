"""Guided lessons for frontend-foundations chapter covering the 6 major domains:
1. TypeScript
2. React
3. API Integration
4. Window Communication & Iframes
5. Frontend System Design
6. Frontend Security
"""

LESSONS = [
    {
        "Q": "How do TypeScript types, generics, type narrowing and compiler algebra enforce sound contracts?",
        "explain": (
            "TypeScript layers a compile-time structural type system over JavaScript's dynamic runtime semantics. "
            "Unlike nominal type systems where types are differentiated by explicit declaration, TypeScript treats types "
            "as mathematical sets of assignable values. A union `A | B` represents the union of valid values, while an "
            "intersection `A & B` represents the subset of values possessing all properties from both types. "
            "Structural typing dictates that any object possessing the required shape satisfies the contract, regardless "
            "of its construction origin. To enforce nominal guarantees (such as differentiating a validated UserId from "
            "an arbitrary string), developers employ branded or tagged types using unique symbol tags.\n\n"
            "Control flow analysis performs type narrowing across conditional branches. When a discriminator property, "
            "`typeof`, `instanceof`, or user-defined type predicate (`x is T`) is evaluated, the compiler shrinks the "
            "candidate type within that branch. Exhaustiveness checking leverages the bottom type `never`: by passing the "
            "unhandled remainder of a discriminated union to a function accepting only `never`, any unhandled union variant "
            "triggers a compile-time error when new variants are added.\n\n"
            "Generics provide parametric polymorphism, allowing functions and data structures to operate over unknown "
            "types while preserving type relationships. Generic constraints (`T extends Base`) enforce minimal capabilities. "
            "Conditional types (`T extends U ? X : Y`) combined with the `infer` keyword enable type extraction and metaprogramming, "
            "such as unpacking promise resolutions or return types. Strict compiler flags—specifically `strictNullChecks`, "
            "`noImplicitAny`, and `noUncheckedIndexedAccess`—close soundness gaps where undefined dictionary accesses or untyped "
            "variables would otherwise leak runtime runtime exceptions."
        ),
        "example": (
            "Demonstrate discriminated union exhaustiveness checking with never:\n"
            "type Action = { type: 'open'; id: string } | { type: 'close'; id: string };\n"
            "function handle(action: Action): void {\n"
            "    switch (action.type) {\n"
            "        case 'open': return;\n"
            "        case 'close': return;\n"
            "        default: {\n"
            "            const _exhaustive: never = action;\n"
            "            throw new Error(`Unhandled action: ${_exhaustive}`);\n"
            "        }\n"
            "    }\n"
            "}\n"
            "Result: Adding a third action type without updating handle triggers a compile-time exhaustiveness error."
        ),
        "takeaway": (
            "Treat TypeScript types as compile-time set constraints. Use discriminated unions, type predicates and "
            "exhaustive never checks to ensure all runtime variations are handled at compile time."
        ),
        "references": [
            "https://www.typescriptlang.org/docs/handbook/2/narrowing.html",
            "https://www.typescriptlang.org/docs/handbook/2/types-from-types.html"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        }
    },
    {
        "Q": "How do React Fiber reconciliation, concurrent rendering and hook state lifecycles coordinate UI updates?",
        "explain": (
            "React's runtime coordinates declarative UI state with browser DOM mutations through its Fiber architecture. "
            "A Fiber is an internal JavaScript object representing a unit of work and a virtual component instance. Fibers "
            "maintain linked relationships: `child` points to the first child, `sibling` to the next sibling, and `return` "
            "to the parent. This singly-linked tree structure allows React to traverse, pause, resume, and abort rendering work "
            "in small time slices without blocking the browser's main thread.\n\n"
            "Rendering proceeds in two distinct phases: the Render Phase and the Commit Phase. During the Render Phase, "
            "React compares the current Fiber tree (`current`) against newly generated JSX elements to construct an alternative "
            "`workInProgress` Fiber tree. This reconciliation diffing algorithm operates in O(n) time using heuristics: "
            "two elements of different types generate entirely different subtrees, and stable keys preserve component identity "
            "across array reorderings. The Render Phase is purely computational, asynchronous, and interruptible.\n\n"
            "Once reconciliation completes, React executes the synchronous Commit Phase. The host DOM mutations are applied, "
            "the `workInProgress` tree is swapped to become `current` (double buffering), synchronous layout effects (`useLayoutEffect`) "
            "fire to allow layout measurements before browser paint, and passive effects (`useEffect`) execute asynchronously after "
            "paint. Hooks are stored as a singly-linked list on the Fiber's `memoizedState` property; maintaining identical hook call "
            "order on every render is an immutable invariant that ensures state cells align correctly across renders."
        ),
        "example": (
            "Demonstrate concurrent state scheduling using useTransition:\n"
            "import { useState, useTransition } from 'react';\n"
            "function FilterableList({ items }: { items: string[] }) {\n"
            "    const [query, setQuery] = useState('');\n"
            "    const [filtered, setFiltered] = useState(items);\n"
            "    const [isPending, startTransition] = useTransition();\n"
            "    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {\n"
            "        setQuery(e.target.value); // Urgent input update\n"
            "        startTransition(() => {\n"
            "            setFiltered(items.filter(item => item.includes(e.target.value))); // Non-urgent filter update\n"
            "        });\n"
            "    };\n"
            "    return <input value={query} onChange={handleChange} />;\n"
            "}\n"
            "Result: Typing remains responsive at 60fps because filtering work yields to urgent keystroke updates."
        ),
        "takeaway": (
            "Distinguish between interruptible render computation and synchronous commit DOM mutations. Use transitions "
            "for deferred computations and respect the hook call-order invariant."
        ),
        "references": [
            "https://react.dev/reference/react/useTransition",
            "https://react.dev/learn/reconciliation"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        }
    },
    {
        "Q": "How do resilient API integration, streaming fetch, abort controllers and cache synchronization operate?",
        "explain": (
            "Modern web frontends treat network I/O as a volatile asynchronous boundary. The native Fetch API departs from "
            "legacy mechanisms by resolving its promise on any valid HTTP response—including 4xx client errors and 5xx server "
            "failures; it only rejects upon catastrophic network failure or DNS resolution failure. Robust client wrappers must "
            "explicitly evaluate `response.ok`, parse typed JSON payloads safely, and translate non-2xx status codes into "
            "structured application errors with machine-readable codes.\n\n"
            "To prevent memory leaks and wasted bandwidth, long-running or obsolete requests require deterministic cancellation. "
            "`AbortController` provides an `AbortSignal` that binds directly to `fetch`, `addEventListener`, or asynchronous promises. "
            "When component unmounting, tab switching, or rapid query typing supersedes an existing request, calling `abort()` "
            "terminates network transmission immediately. For temporary network partitions, exponential backoff with full randomized "
            "jitter prevents thundering herd congestion on backend services.\n\n"
            "Consuming real-time streaming data—such as token-by-token generative AI responses—requires reading `response.body` "
            "as a `ReadableStream`. Coupling `ReadableStreamDefaultReader` with a `TextDecoderStream` processes chunked server responses "
            "progressively without buffering gigabytes into memory. Finally, caching layers (like TanStack Query or SWR) manage "
            "cache keys, optimistic mutations with rollback snapshots, background revalidation, and request deduplication to keep "
            "local UI state truthful against the remote authority."
        ),
        "example": (
            "Demonstrate streaming token consumption with AbortController:\n"
            "async function streamAIResponse(url: string, signal: AbortSignal, onChunk: (text: string) => void) {\n"
            "    const response = await fetch(url, { signal });\n"
            "    if (!response.ok || !response.body) throw new Error(`HTTP error: ${response.status}`);\n"
            "    const reader = response.body.getReader();\n"
            "    const decoder = new TextDecoder('utf-8');\n"
            "    while (true) {\n"
            "        const { value, done } = await reader.read();\n"
            "        if (done) break;\n"
            "        onChunk(decoder.decode(value, { stream: true }));\n"
            "    }\n"
            "}\n"
            "Result: Text chunks render incrementally as received, and triggering signal abort halts the stream immediately."
        ),
        "takeaway": (
            "Check response.ok on all fetch calls, attach AbortSignal to every asynchronous request, and stream chunked "
            "responses progressively rather than waiting for complete payload termination."
        ),
        "references": [
            "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch",
            "https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        }
    },
    {
        "Q": "How do cross-window messaging, iframe sandboxing and multi-tab coordination maintain origin isolation?",
        "explain": (
            "The browser's Same-Origin Policy (SOP) prohibits scripts on one origin (protocol, host, port) from accessing "
            "DOM or JavaScript objects on a different origin. When legitimate communication across windows, tabs, or embedded "
            "iframes is required, `window.postMessage` serves as the controlled, auditable message-passing channel. Security "
            "hinges on two strict invariants: the sender must specify an explicit `targetOrigin` rather than `'*'`, and the receiver "
            "must verify `event.origin` against an authoritative whitelist before processing the message payload.\n\n"
            "Embedding third-party content safely requires iframe sandboxing. The `sandbox` attribute restricts the embedded "
            "frame by default, removing script execution, form submission, popups, and same-origin privileges. While specific "
            "capabilities can be selectively re-enabled via flags like `allow-scripts` or `allow-forms`, combining `allow-scripts` "
            "with `allow-same-origin` on untrusted content completely destroys the sandbox boundary: an embedded script can "
            "programmatically remove its own sandbox attribute and take over the parent application.\n\n"
            "For multi-tab communication within the same origin, the modern `BroadcastChannel` API provides a 1-to-many publish/subscribe "
            "channel with zero polling overhead. Alternatively, `SharedWorker` offers a shared background execution thread that "
            "can maintain a single persistent WebSocket connection across multiple open tabs. For cross-tab authentication synchronization, "
            "listening to `window.onstorage` events detects token invalidation and triggers immediate multi-tab logout."
        ),
        "example": (
            "Demonstrate secure postMessage receiver validation:\n"
            "window.addEventListener('message', (event: MessageEvent) => {\n"
            "    if (event.origin !== 'https://trusted-auth.example.com') return; // Strict origin filter\n"
            "    if (!event.data || event.data.type !== 'AUTH_SUCCESS') return;\n"
            "    console.log('Received valid auth token:', event.data.token);\n"
            "});\n"
            "Result: Unsolicited messages from malicious or unauthorized third-party origins are ignored without processing."
        ),
        "takeaway": (
            "Never use '*' as postMessage targetOrigin. Always validate event.origin in message handlers and never combine "
            "allow-scripts with allow-same-origin on untrusted iframe embeds."
        ),
        "references": [
            "https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#sandbox"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        }
    },
    {
        "Q": "How do frontend system design, state architecture and Core Web Vitals optimize applications at scale?",
        "explain": (
            "Enterprise frontend system design addresses the architectural challenges of scalability, performance, "
            "and organizational maintainability across large codebases. A robust frontend architecture separates concerns "
            "into clean vertical and horizontal boundaries: domain presentation components, application state management, "
            "data layer abstractions, and reusable design systems. Design tokens govern visual consistency across typography, "
            "spacing, and elevation, while headless UI primitives (such as Radix or React Aria) deliver accessible, keyboard-navigable "
            "behavior without styling constraints.\n\n"
            "State architecture requires matching state to its proper scope. Local component state (`useState`) handles transient "
            "form inputs and toggles. Shared client state (`Zustand` or `Redux Toolkit`) manages cross-cutting UI state like sidebar "
            "toggles and modal managers. Server cache state (`TanStack Query`) governs remote entities, caching, and optimistic updates. "
            "Conflating server cache with local state causes data desynchronization and unnecessary global re-renders.\n\n"
            "Performance optimization is guided by Google's Core Web Vitals: Largest Contentful Paint (LCP < 2.5s), Interaction to "
            "Next Paint (INP < 200ms), and Cumulative Layout Shift (CLS < 0.1). High-performance delivery relies on route-based code "
            "splitting via dynamic `import()`, tree shaking under ES modules with `sideEffects: false`, modern image formats (AVIF/WebP) "
            "with explicit aspect ratios, and DOM list virtualization (`react-window`) to render massive datasets at a steady 60fps."
        ),
        "example": (
            "Demonstrate dynamic code splitting with React.lazy and Suspense:\n"
            "import React, { Suspense, lazy } from 'react';\n"
            "const HeavyAnalyticsChart = lazy(() => import('./HeavyAnalyticsChart'));\n"
            "function Dashboard() {\n"
            "    return (\n"
            "        <Suspense fallback={<div>Loading chart component...</div>}>\n"
            "            <HeavyAnalyticsChart />\n"
            "        </Suspense>\n"
            "    );\n"
            "}\n"
            "Result: Heavy charting libraries are omitted from the main bundle and downloaded on demand when the component mounts."
        ),
        "takeaway": (
            "Architect applications with clear state boundaries: separate server cache from client UI state, split bundles "
            "at route boundaries, and actively monitor LCP, INP, and CLS metrics."
        ),
        "references": [
            "https://web.dev/explore/learn-core-web-vitals",
            "https://react.dev/reference/react/lazy"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        }
    },
    {
        "Q": "How do frontend security defenses against XSS, CSP nonces and CSRF/CORS boundaries protect client applications?",
        "explain": (
            "Client-side security enforces defense-in-depth across the browser runtime. Cross-Site Scripting (XSS) represents "
            "the preeminent threat, occurring whenever untrusted data is rendered into an active DOM execution sink (`innerHTML`, "
            "`eval`, `document.write`, or `href='javascript:'`). Modern frameworks mitigate reflected and stored XSS by escaping "
            "text nodes by default. However, when user-supplied HTML must be rendered (such as rich text or markdown), robust "
            "sanitization libraries like DOMPurify paired with the browser's Trusted Types API are mandatory to strip malicious payloads "
            "and event handlers before insertion.\n\n"
            "A strict Content Security Policy (CSP) provides a cryptographic backstop against script injection. Rather than relying "
            "on vulnerable domain whitelists, modern CSP uses per-request cryptographic nonces (`script-src 'nonce-{RANDOM}' 'strict-dynamic'`) "
            "and disallows `'unsafe-inline'` and `'unsafe-eval'`. Under this policy, injected script tags lack the required random "
            "server nonce and are terminated by the browser engine before execution.\n\n"
            "Cross-Site Request Forgery (CSRF) is mitigated primarily by configuring the `SameSite` cookie attribute. Setting "
            "`SameSite=Lax` or `SameSite=Strict` alongside `Secure` and `HttpOnly` flags prevents the browser from attaching session "
            "cookies to cross-origin state-changing requests. Sensitive authentication tokens must never be stored in `localStorage` "
            "where any XSS vulnerability can extract them; storing tokens in `HttpOnly` cookies or memory-only scoped closures prevents "
            "script-based credential theft."
        ),
        "example": (
            "Demonstrate safe HTML sanitization with DOMPurify before DOM insertion:\n"
            "import DOMPurify from 'dompurify';\n"
            "function renderSafeHTML(untrustedMarkup: string): string {\n"
            "    return DOMPurify.sanitize(untrustedMarkup, {\n"
            "        ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p'],\n"
            "        ALLOWED_ATTR: ['href', 'target', 'rel']\n"
            "    });\n"
            "}\n"
            "const safe = renderSafeHTML('<img src=x onerror=alert(1)><b>Welcome</b>');\n"
            "Result: Malicious script payloads and dangerous onerror event attributes are stripped, leaving only '<b>Welcome</b>'."
        ),
        "takeaway": (
            "Never trust client-rendered markup without DOMPurify and Trusted Types. Deploy strict nonce-based CSP, set "
            "SameSite=Lax on cookies, and avoid storing bearer tokens in localStorage."
        ),
        "references": [
            "https://owasp.org/www-community/attacks/xss/",
            "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        }
    }
]
