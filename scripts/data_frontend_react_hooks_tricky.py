"""20 Advanced React Interview Questions covering all hooks with examples, custom hook design, and tricky interview topics."""

QUESTIONS = [
    {
        "Q": "How do useState and useReducer differ in state transition guarantees, lazy initialization, and dispatch stability?",
        "A": (
            "**Direct answer:** `useState` and `useReducer` are React's primary state primitives, with `useReducer` actually serving as "
            "the foundational engine under the hood (`useState` is implemented internally using `useReducer`). While `useState` is ideal "
            "for simple, independent state cells, `useReducer` provides architectural guarantees for complex state objects with interdependent "
            "sub-properties and predictable transitions guided by state machine actions.\n\n"
            "```typescript\n"
            "// 1. Lazy initialization in useState vs useReducer\n"
            "// Expensive computation runs ONLY on initial mount, not on every re-render:\n"
            "const [state, setState] = useState(() => calculateExpensiveInitialState(props.seed));\n\n"
            "// useReducer with init function to defer initial state creation:\n"
            "function init(initialSeed: number) {\n"
            "    return { count: initialSeed, history: [initialSeed] };\n"
            "}\n"
            "const [state, dispatch] = useReducer(reducer, props.seed, init);\n"
            "```\n\n"
            "**Mechanics and Dispatch Stability:**\n"
            "- **Dispatch reference identity:** Both `setState` and `dispatch` identity are guaranteed to remain referentially stable "
            "across all re-renders for the lifetime of the component. You do not need to include `dispatch` or `setState` in `useEffect` "
            "or `useCallback` dependency arrays.\n"
            "- **Functional updates in useState:** When next state depends on current state, passing an updater callback `setCount(prev => prev + 1)` "
            "prevents stale closure capture during concurrent batching.\n"
            "- **Atomic transitions in useReducer:** In `useReducer`, action dispatches decouple the *what happened* (the action event) from "
            "*how the state updates* (the reducer function). When an action requires updating multiple related fields (e.g. `isLoading`, `error`, `data`), "
            "`useReducer` applies the update atomically in a single pass, eliminating intermediate inconsistent renders."
        ),
        "Why": "useReducer provides predictable state transitions and eliminates race conditions across complex interdependent fields.",
        "Risk": "Mutating state directly inside a reducer function instead of returning fresh objects breaks reconciliation and memoization.",
        "Trade": "useReducer introduces more boilerplate code and action ceremonies compared to inline useState setters.",
        "Try": "Convert three interdependent useState booleans into a useReducer state machine and verify impossible states are eliminated.",
        "worked_case": (
            "Walkthrough scenario: An async fetch uses three useState calls: setLoading, setData, and setError. Under rapid user toggling, "
            "a resolved fetch sets loading false and data, but an earlier errored request resolves late and sets error true. The UI renders "
            "both data and error simultaneously. Refactoring to useReducer with explicit actions (FETCH_INIT, FETCH_SUCCESS, FETCH_FAILURE) "
            "ensures loading, data, and error transitions are mutually exclusive and atomic."
        ),
        "citations": [
            "https://react.dev/reference/react/useState",
            "https://react.dev/reference/react/useReducer"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "What changes when you pass state and dispatch through React Context?",
                "A": "Separating state and dispatch into two distinct contexts prevents components that only need dispatch from re-rendering when state changes."
            }
        ]
    },
    {
        "Q": "How do useRef and useImperativeHandle manage mutable escape hatches and imperative component handles?",
        "A": (
            "**Direct answer:** `useRef` returns a persistent, mutable container object whose `.current` property holds an arbitrary value "
            "that survives across all re-renders of a component. Unlike `useState`, mutating `ref.current` is a synchronous side-effect that "
            "does *not* notify React or trigger a re-render. `useImperativeHandle` works in tandem with `forwardRef` to customize and restrict "
            "the imperative methods exposed to parent components, preserving encapsulation.\n\n"
            "```typescript\n"
            "import { forwardRef, useImperativeHandle, useRef } from 'react';\n\n"
            "export interface VideoPlayerHandle {\n"
            "    play(): void;\n"
            "    pause(): void;\n"
            "    seekTo(seconds: number): void;\n"
            "}\n\n"
            "export const VideoPlayer = forwardRef<VideoPlayerHandle, { src: string }>((props, ref) => {\n"
            "    const internalVideoRef = useRef<HTMLVideoElement>(null);\n\n"
            "    // Restrict parent access to only play, pause, and seekTo instead of exposing full DOM node\n"
            "    useImperativeHandle(ref, () => ({\n"
            "        play() { internalVideoRef.current?.play(); },\n"
            "        pause() { internalVideoRef.current?.pause(); },\n"
            "        seekTo(sec) { if (internalVideoRef.current) internalVideoRef.current.currentTime = sec; }\n"
            "    }), []);\n\n"
            "    return <video ref={internalVideoRef} src={props.src} />;\n"
            "});\n"
            "```\n\n"
            "**Core mechanics and usage boundaries:**\n"
            "- **DOM measurement and focus:** Accessing actual HTML elements for focus management, scroll positioning, canvas manipulation, and third-party DOM libraries.\n"
            "- **Instance variables:** Storing timer IDs (from `setTimeout`/`setInterval`), animation frame IDs, previous prop/state values, or abort controllers.\n"
            "- **Golden rule:** Never read or write `ref.current` during rendering computation. Only mutate and read refs inside event handlers or `useEffect`/`useLayoutEffect`."
        ),
        "Why": "Refs provide an escape hatch for non-rendering values and imperative DOM operations without causing re-render loops.",
        "Risk": "Reading or modifying ref.current during rendering introduces non-deterministic bugs in concurrent and strict mode.",
        "Trade": "Imperative handles break purely declarative data flow and should be restricted to media, canvas, or focus behaviors.",
        "Try": "Wrap an input element in forwardRef with useImperativeHandle exposing only a focusAndSelectAll method, and invoke it from a parent.",
        "worked_case": (
            "Walkthrough scenario: A parent form component needs to focus and highlight an invalid custom input inside a complex child widget upon submit. "
            "Exposing the raw input DOM node breaks abstraction and lets the parent mutate arbitrary attributes. Implementing useImperativeHandle exposes only "
            "a validateAndFocus imperative method. When the parent calls ref.current.validateAndFocus, the child triggers internal validation animations and focuses "
            "the native input cleanly."
        ),
        "citations": [
            "https://react.dev/reference/react/useRef",
            "https://react.dev/reference/react/useImperativeHandle"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "What happens if you read or write ref.current directly during the render phase?",
                "A": "Reading or writing refs during render makes component output unpredictable, as concurrent React can pause, discard, or re-execute render passes."
            }
        ]
    },
    {
        "Q": "How does useSyncExternalStore eliminate tearing in concurrent React and integrate external subscriptions safely?",
        "A": (
            "**Direct answer:** `useSyncExternalStore` was introduced in React 18 to solve 'tearing'—a visual inconsistency bug where different "
            "components on the screen read different values from an external mutable store during a single concurrent render pass. "
            "Because React 18 can yield execution in the middle of rendering a component tree, an external store mutation between time slices "
            "would cause already-rendered components to show old data while subsequently-rendered components show new data.\n\n"
            "```typescript\n"
            "import { useSyncExternalStore } from 'react';\n\n"
            "// Custom hook subscribing to browser network online status:\n"
            "function subscribe(callback: () => void) {\n"
            "    window.addEventListener('online', callback);\n"
            "    window.addEventListener('offline', callback);\n"
            "    return () => {\n"
            "        window.removeEventListener('online', callback);\n"
            "        window.removeEventListener('offline', callback);\n"
            "    };\n"
            "}\n\n"
            "function getSnapshot() {\n"
            "    return navigator.onLine;\n"
            "}\n\n"
            "function getServerSnapshot() {\n"
            "    return true; // Default true during SSR\n"
            "}\n\n"
            "export function useOnlineStatus() {\n"
            "    return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);\n"
            "}\n"
            "```\n\n"
            "**Requirements and Invariants:**\n"
            "- **Immutable snapshots:** The `getSnapshot` function must return an immutable value or referentially stable object if the underlying data has not changed. Returning a new object literal every time triggers an infinite re-render loop.\n"
            "- **Synchronous checks:** React inspects the external store before and after concurrent renders; if a mismatch is detected, React discards the concurrent tree and synchronously re-renders the entire tree to guarantee consistency."
        ),
        "Why": "useSyncExternalStore coordinates non-React external stores with React concurrent scheduling without visual tearing.",
        "Risk": "Returning a new object reference from getSnapshot on every invocation causes an infinite re-render loop.",
        "Trade": "External store mutations force synchronous de-optimizations when conflicts arise during concurrent background rendering.",
        "Try": "Write a useWindowDimensions hook with useSyncExternalStore and verify resize events do not tear across sibling widgets.",
        "worked_case": (
            "Walkthrough scenario: A financial trading dashboard renders 50 stock tickers using a global Redux store. During a non-urgent transition, "
            "React renders the first 25 tickers with price 100 USD. An incoming WebSocket message updates the store price to 105 USD. Traditional "
            "useEffect subscriptions would render tickers 26 to 50 at 105 USD while tickers 1 to 25 remain at 100 USD (tearing). useSyncExternalStore "
            "detects the snapshot change mid-render and forces a synchronized atomic re-render so all 50 tickers display 105 USD simultaneously."
        ),
        "citations": [
            "https://react.dev/reference/react/useSyncExternalStore",
            "https://github.com/reactwg/react-18/discussions/86"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "Why is useEffect and useState subscription insufficient for concurrent external state?",
                "A": "useEffect runs after the browser paint, meaning intermediate frames are visible with inconsistent state before the synchronization effect runs."
            }
        ]
    },
    {
        "Q": "How does the useId hook generate hydration-stable unique identifiers for accessible form controls?",
        "A": (
            "**Direct answer:** `useId` generates unique, deterministic, and hydration-stable identifiers formatted as `:r0:`, `:r1:`, etc. "
            "Prior to `useId`, developers relied on random numbers (`Math.random()`) or global counters (`id++`). Random numbers guarantee "
            "a hydration mismatch because server and client generate different random values. Global counters fail because server-rendered streams "
            "and asynchronous client component hydration arrive in non-deterministic orders.\n\n"
            "```tsx\n"
            "import { useId } from 'react';\n\n"
            "export function AccessibleFormField({ label, hint }: { label: string; hint: string }) {\n"
            "    const id = useId();\n"
            "    const hintId = `${id}-hint`;\n"
            "\n"
            "    return (\n"
            "        <div className=\"field-group\">\n"
            "            <label htmlFor={id}>{label}</label>\n"
            "            <input id={id} type=\"text\" aria-describedby={hintId} />\n"
            "            <p id={hintId} className=\"hint\">{hint}</p>\n"
            "        </div>\n"
            "    );\n"
            "}\n"
            "```\n\n"
            "**Underlying mechanics:**\n"
            "- **Hierarchical tree position:** `useId` derives IDs from the position of the component in React's Fiber tree hierarchy. "
            "Because the tree structure is identical on the server and client, the generated IDs match perfectly across HTML generation and client hydration.\n"
            "- **Prefixing for multiple elements:** A single `useId()` call per component can generate multiple related IDs by appending suffixes (e.g. `${id}-firstName`, `${id}-lastName`), saving Fiber memory.\n"
            "- **Anti-pattern:** Never use `useId` to generate keys for mapping over arrays in list rendering. Keys must come from your data."
        ),
        "Why": "useId calculates deterministic identifiers based on component tree coordinates, eliminating SSR hydration mismatches.",
        "Risk": "Using useId to generate list reconciliation keys causes state corruption and remount thrashing on data reorders.",
        "Trade": "IDs are opaque strings with colons (:r0:) and cannot be styled as simple CSS class names or target CSS selectors directly.",
        "Try": "Inspect server-rendered HTML and client DOM for a form with useId, verifying identical IDs across the boundary without console warnings.",
        "worked_case": (
            "Walkthrough scenario: An accessible password input uses Math.random() to connect label htmlFor to input id. In server-rendered HTML, "
            "the input receives id='pwd-4821'. During client hydration, Math.random() produces 'pwd-9134'. React logs a hydration mismatch error, "
            "discards the server DOM node, and screen readers fail to associate the label with the input control until full client remounting. "
            "Switching to useId produces deterministic ':r1:' on both server and client, resolving the error instantly."
        ),
        "citations": [
            "https://react.dev/reference/react/useId",
            "https://github.com/reactwg/react-18/discussions/111"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "Can you use useId to generate CSS selectors?",
                "A": "useId generates tokens containing colons (:r0:), which require backslash escaping in querySelector but work natively in getElementById."
            }
        ]
    },
    {
        "Q": "How do useDebugValue and custom DevTools formatting inspect internal hook state during development?",
        "A": (
            "**Direct answer:** `useDebugValue` is a developer-experience hook designed specifically for authoring custom hooks. "
            "It allows a custom hook to display custom, readable labels and diagnostics inside the React DevTools Component Inspector tab. "
            "In production builds, `useDebugValue` compiles away into a no-op, adding zero overhead to the production bundle.\n\n"
            "```typescript\n"
            "import { useState, useEffect, useDebugValue } from 'react';\n\n"
            "export function useFriendStatus(friendId: string) {\n"
            "    const [isOnline, setIsOnline] = useState<boolean | null>(null);\n\n"
            "    // Simple string formatting:\n"
            "    // useDebugValue(isOnline ? 'Online' : 'Offline');\n\n"
            "    // Deferred formatting: formatter function is ONLY executed if React DevTools is actively open\n"
            "    useDebugValue(isOnline, status => status === null ? 'Connecting...' : status ? 'Active (Online)' : 'Idle (Offline)');\n\n"
            "    useEffect(() => {\n"
            "        // Subscription logic...\n"
            "    }, [friendId]);\n\n"
            "    return isOnline;\n"
            "}\n"
            "```\n\n"
            "**Key Best Practices:**\n"
            "- **Only for shared custom hooks:** Do not add `useDebugValue` to every custom hook. Reserve it for complex, widely shared libraries (e.g. animation libraries, query caches, form frameworks).\n"
            "- **Lazy formatting function:** Always pass a secondary formatting function `useDebugValue(date, d => d.toISOString())` when formatting is computationally expensive, ensuring it only executes when developer tools inspect the node."
        ),
        "Why": "useDebugValue surfaces internal custom hook diagnostics directly within React DevTools without littering console logs.",
        "Risk": "Executing heavy synchronous formatting logic without the deferred function argument degrades developer experience in DevTools.",
        "Trade": "Adds minor code footprint to custom hook definitions for developer-facing introspection only.",
        "Try": "Implement useDebugValue with a formatting function in a custom useDebounce hook and inspect the live timer status in React DevTools.",
        "worked_case": (
            "Walkthrough scenario: A shared animation hook useSpring coordinates velocity and friction across hundreds of elements. Without "
            "useDebugValue, inspecting a component in React DevTools only displays three raw anonymous useState numbers. Adding useDebugValue "
            "with a deferred formatter displays 'Spring: { velocity: 12.4, target: 100, settled: false }', enabling immediate visualization "
            "of physics calculations without cluttering the browser console."
        ),
        "citations": [
            "https://react.dev/reference/react/useDebugValue"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "Does useDebugValue execute or affect performance in production builds?",
                "A": "No, React strips out useDebugValue logic in production builds, ensuring zero runtime or memory overhead for end users."
            }
        ]
    },
    {
        "Q": "How does the React 19 use hook unwrap promises and context conditionally inside loops and branching logic?",
        "A": (
            "**Direct answer:** The `use` hook (introduced in React 19) is a fundamentally unique React API that breaks the traditional "
            "'Rules of Hooks' invariant. While all standard hooks (`useState`, `useEffect`, etc.) must be called unconditionally at the top level "
            "of a component, `use` can be called conditionally inside `if` statements, ternary operators, and loops. It can read both Promises "
            "and React Context values.\n\n"
            "```tsx\n"
            "import { use, Suspense } from 'react';\n\n"
            "// 1. Reading Context conditionally:\n"
            "function UserGreeting({ showFull, themeContext }: { showFull: boolean; themeContext: React.Context<Theme> }) {\n"
            "    if (!showFull) {\n"
            "        return <span>Welcome!</span>;\n"
            "    }\n"
            "    // Conditionally read context without breaking hook rules!\n"
            "    const theme = use(themeContext);\n"
            "    return <span style={{ color: theme.color }}>Welcome back, authenticated user!</span>;\n"
            "}\n\n"
            "// 2. Unwrapping Promises in streaming components:\n"
            "function MessageFeed({ messagePromise }: { messagePromise: Promise<string[]> }) {\n"
            "    // Suspends component until messagePromise resolves:\n"
            "    const messages = use(messagePromise);\n"
            "    return <ul>{messages.map((m, i) => <li key={i}>{m}</li>)}</ul>;\n"
            "}\n"
            "```\n\n"
            "**Mechanics with Suspense and Error Boundaries:**\n"
            "- When reading a Promise that is pending, `use` suspends the component, causing the nearest parent `<Suspense fallback={<Spinner />}>` to display.\n"
            "- If the Promise rejects, `use` throws the rejection error, which is caught and displayed by the nearest `<ErrorBoundary>`.\n"
            "- The Promise passed to `use` must be cached (e.g. via Next.js cache or a query client); creating a new Promise inside render causes an infinite suspension loop."
        ),
        "Why": "use enables asynchronous data streaming and conditional context reads directly inside JSX without render-prop gymnastics.",
        "Risk": "Creating a new un-memoized Promise during render and passing it to use triggers an infinite suspension loop.",
        "Trade": "Requires wrapping consumers in Suspense and Error Boundaries to handle pending and rejected promise states.",
        "Try": "Pass a fetch promise from a server action into a client component with use, rendering a skeleton fallback with Suspense.",
        "worked_case": (
            "Walkthrough scenario: An application dashboard renders an optional comments section only when a user toggles an accordion. Traditional "
            "useContext required lifting context or unconditionally subscribing to comments, triggering re-renders even when collapsed. With React 19 use, "
            "the component only calls use(CommentsContext) if isExpanded is true. When collapsed, the component incurs zero subscription overhead."
        ),
        "citations": [
            "https://react.dev/reference/react/use"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "Can the use hook be invoked inside standard JavaScript helper functions?",
                "A": "No, like other hooks, use can only be called inside React component functions or custom hook functions, never in plain utility functions."
            }
        ]
    },
    {
        "Q": "How do you design and architect robust custom React hooks, and when should you return a tuple versus an object?",
        "A": (
            "**Direct answer:** Custom hooks are JavaScript functions whose names begin with `use` and that compose built-in React hooks to "
            "encapsulate reusable, stateful business logic. Custom hooks share *stateful logic*, not physical state itself: each component instance "
            "calling a custom hook receives an isolated, independent state allocation. Choosing between returning a tuple `[state, actions]` "
            "versus an object `{ state, actions }` is a fundamental API design decision.\n\n"
            "```typescript\n"
            "// 1. Tuple Return (Convention like useState):\n"
            "// Best for 1-2 elements where callers frequently rename values:\n"
            "export function useToggle(initial = false): [boolean, () => void] {\n"
            "    const [on, setOn] = useState(initial);\n"
            "    const toggle = useCallback(() => setOn(v => !v), []);\n"
            "    return [on, toggle];\n"
            "}\n"
            "// Usage allows clean renaming:\n"
            "// const [isModalOpen, toggleModal] = useToggle();\n"
            "// const [isNavOpen, toggleNav] = useToggle();\n\n"
            "// 2. Object Return (Convention for complex hooks):\n"
            "// Best for 3+ properties, optional destructuring, and future-proof extensibility:\n"
            "export interface AsyncState<T> {\n"
            "    data: T | null;\n"
            "    isLoading: boolean;\n"
            "    error: Error | null;\n"
            "    refetch: () => Promise<void>;\n"
            "}\n"
            "```\n\n"
            "**Key Architecture Invariants:**\n"
            "- **Stable action references:** All action callbacks returned from a custom hook must be memoized with `useCallback` or functional updates to prevent breaking consumer `useEffect` dependencies.\n"
            "- **Cleanups:** If the custom hook sets up subscriptions, intervals, or observers, it *must* return a cleanup function in `useEffect`.\n"
            "- **Strict naming:** Prefix with `use` so React ESLint linters enforce top-level call order rules."
        ),
        "Why": "Custom hooks extract stateful coordination logic while guaranteeing encapsulation and independent lifecycle instances.",
        "Risk": "Returning un-memoized object or function references from custom hooks causes continuous re-render cascades in consuming components.",
        "Trade": "Tuples offer frictionless renaming for 1-2 items; objects provide clear self-documenting property names and easy extensibility for 3+ items.",
        "Try": "Write a useToggle hook returning a tuple [boolean, () => void], and use it in two separate components verifying isolated state.",
        "worked_case": (
            "Walkthrough scenario: A developer writes a useUser hook returning [user, loading, error, refetch, mutate]. Consuming components that "
            "only need mutate must write const [, , , , mutate] = useUser(), which is fragile and error-prone. Refactoring the return signature "
            "to an object { user, loading, error, refetch, mutate } allows clean destructuring: const { mutate } = useUser(), while allowing future "
            "properties (e.g. isStale) to be added without breaking existing callers."
        ),
        "citations": [
            "https://react.dev/learn/reusing-logic-with-custom-hooks"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "How do you achieve TypeScript tuple types that do not widen to union arrays?",
                "A": "Use an explicit return type annotation like [boolean, () => void] or the as const assertion on the returned array."
            }
        ]
    },
    {
        "Q": "How do you implement a production-grade useDebounce and useThrottle custom hook with cleanup and immediate execution flags?",
        "A": (
            "**Direct answer:** Debouncing and throttling limit the rate of expensive computations (e.g. API search queries, layout calculations, "
            "or window resize handlers). A production-grade `useDebounce` hook defers updating a value until a specified delay has elapsed since "
            "the last change, canceling any pending timers when new inputs arrive or when the component unmounts.\n\n"
            "```typescript\n"
            "import { useState, useEffect, useRef, useCallback } from 'react';\n\n"
            "// 1. Debounced Value Hook (ideal for search inputs)\n"
            "export function useDebounce<T>(value: T, delayMs: number): T {\n"
            "    const [debouncedValue, setDebouncedValue] = useState<T>(value);\n\n"
            "    useEffect(() => {\n"
            "        const handler = setTimeout(() => {\n"
            "            setDebouncedValue(value);\n"
            "        }, delayMs);\n\n"
            "        // Cleanup cancels timer if value or delay changes before delayMs elapsed\n"
            "        return () => {\n"
            "            clearTimeout(handler);\n"
            "        };\n"
            "    }, [value, delayMs]);\n\n"
            "    return debouncedValue;\n"
            "}\n\n"
            "// 2. Throttled Callback Hook (ideal for scroll / resize events)\n"
            "export function useThrottleCallback<T extends (...args: any[]) => void>(callback: T, limitMs: number): T {\n"
            "    const lastRun = useRef<number>(0);\n"
            "    const timer = useRef<ReturnType<typeof setTimeout> | null>(null);\n"
            "    const savedCallback = useRef(callback);\n"
            "    savedCallback.current = callback;\n\n"
            "    return useCallback(((...args: any[]) => {\n"
            "        const now = Date.now();\n"
            "        if (now - lastRun.current >= limitMs) {\n"
            "            lastRun.current = now;\n"
            "            savedCallback.current(...args);\n"
            "        }\n"
            "    }) as T, [limitMs]);\n"
            "}\n"
            "```\n\n"
            "**Memory and Lifecycle Invariants:**\n"
            "- Always invoke `clearTimeout` in the `useEffect` cleanup function. Omitting cleanup triggers memory leaks and state updates on unmounted components.\n"
            "- Using `useRef` to hold the latest callback (`savedCallback.current`) allows the throttled callback to read fresh state without re-creating the wrapper function on every render."
        ),
        "Why": "Rate-limiting hooks prevent API spam and main-thread layout thrashing during rapid user typing or scroll interactions.",
        "Risk": "Failing to clear setTimeout in the cleanup return handler causes state updates on unmounted components.",
        "Trade": "Debouncing introduces intentional visual delay (latency) in exchange for dramatic reductions in network and CPU load.",
        "Try": "Connect useDebounce to a text input wired to an external API fetch effect, verifying that typing 10 characters triggers only 1 HTTP request.",
        "worked_case": (
            "Walkthrough scenario: An auto-complete search bar fires an HTTP query on every keystroke. Typing 'react components' generates 16 rapid "
            "requests that arrive out-of-order, overwriting the final search results with stale responses. Integrating useDebounce(query, 300) "
            "buffers intermediate keystrokes and only fires a single HTTP request 300ms after the user pauses typing, completely eliminating race conditions."
        ),
        "citations": [
            "https://react.dev/reference/react/useEffect#connecting-to-an-external-system"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "How do you add a cancel or flush method to a debounced callback hook?",
                "A": "Attach cancel and flush functions to the returned function using Object.assign or a returned controller object with ref-held timer IDs."
            }
        ]
    },
    {
        "Q": "How do you build a resilient useLocalStorage custom hook that syncs across multiple browser tabs via window storage events?",
        "A": (
            "**Direct answer:** A resilient `useLocalStorage` hook synchronizes component state with the browser's `window.localStorage` "
            "engine while providing three critical production capabilities: safe JSON serialization/deserialization with fallbacks, SSR safety "
            "when `window` is undefined, and cross-tab multi-window synchronization via the native `window` `'storage'` event.\n\n"
            "```typescript\n"
            "import { useState, useEffect, useCallback } from 'react';\n\n"
            "export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((prev: T) => T)) => void] {\n"
            "    // 1. SSR-safe lazy initialization\n"
            "    const [storedValue, setStoredValue] = useState<T>(() => {\n"
            "        if (typeof window === 'undefined') return initialValue;\n"
            "        try {\n"
            "            const item = window.localStorage.getItem(key);\n"
            "            return item ? (JSON.parse(item) as T) : initialValue;\n"
            "        } catch (error) {\n"
            "            console.warn(`Error reading localStorage key '${key}':`, error);\n"
            "            return initialValue;\n"
            "        }\n"
            "    });\n\n"
            "    // 2. Wrapped setter that writes to localStorage and component state\n"
            "    const setValue = useCallback((value: T | ((prev: T) => T)) => {\n"
            "        setStoredValue(prev => {\n"
            "            const next = value instanceof Function ? value(prev) : value;\n"
            "            if (typeof window !== 'undefined') {\n"
            "                try {\n"
            "                    window.localStorage.setItem(key, JSON.stringify(next));\n"
            "                } catch (e) { console.error('LocalStorage quota exceeded', e); }\n"
            "            }\n"
            "            return next;\n"
            "        });\n"
            "    }, [key]);\n\n"
            "    // 3. Cross-tab synchronization via window 'storage' event\n"
            "    useEffect(() => {\n"
            "        function handleStorageChange(e: StorageEvent) {\n"
            "            if (e.key === key && e.newValue !== null) {\n"
            "                try { setStoredValue(JSON.parse(e.newValue)); } catch {}\n"
            "            }\n"
            "        }\n"
            "        window.addEventListener('storage', handleStorageChange);\n"
            "        return () => window.removeEventListener('storage', handleStorageChange);\n"
            "    }, [key]);\n\n"
            "    return [storedValue, setValue];\n"
            "}\n"
            "```\n\n"
            "**Crucial Caveat:** The native `'storage'` event only fires on *other* open tabs, not the tab that made the mutation. "
            "Updating local state in `setValue` handles the active tab, while the event listener syncs background tabs."
        ),
        "Why": "useLocalStorage bridges persistent client storage with reactive state while maintaining multi-tab cache consistency.",
        "Risk": "Failing to handle quota errors or private-browsing restrictions causes unhandled runtime exceptions during setItem.",
        "Trade": "Synchronous localStorage I/O can block the main thread if storing large multi-megabyte payloads.",
        "Try": "Open an application in two browser tabs and change a theme or cart item in tab A; verify tab B updates instantly via storage events.",
        "worked_case": (
            "Walkthrough scenario: A user opens an e-commerce dashboard in two adjacent browser tabs. In Tab 1, the user logs out, clearing authentication "
            "keys from localStorage. Without a storage event listener, Tab 2 continues rendering the active user session and allows sensitive actions "
            "until page refresh. Implementing useLocalStorage with a storage listener notifies Tab 2 immediately upon Tab 1's logout, resetting Tab 2 to "
            "the login screen automatically."
        ),
        "citations": [
            "https://developer.mozilla.org/en-US/docs/Web/API/Window/storage_event",
            "https://react.dev/reference/react/useState"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "Why does window.addEventListener('storage') not trigger in the active tab that invoked setItem?",
                "A": "The HTML storage specification intentionally dispatches storage events only to other documents sharing the origin to prevent redundant local updates."
            }
        ]
    },
    {
        "Q": "How do you create a performant useIntersectionObserver custom hook for infinite scrolling and lazy asset loading?",
        "A": (
            "**Direct answer:** A custom `useIntersectionObserver` hook observes when a target DOM node enters or exits the browser viewport "
            "(or an ancestor container) using the browser's asynchronous `IntersectionObserver` API. This completely replaces expensive "
            "and laggy `window.onscroll` listeners with off-thread platform intersection checks.\n\n"
            "```typescript\n"
            "import { useState, useEffect, useRef } from 'react';\n\n"
            "export interface IntersectionOptions extends IntersectionObserverInit {\n"
            "    freezeOnceVisible?: boolean;\n"
            "}\n\n"
            "export function useIntersectionObserver(\n"
            "    elementRef: React.RefObject<Element | null>,\n"
            "    { threshold = 0, root = null, rootMargin = '0px', freezeOnceVisible = false }: IntersectionOptions = {}\n"
            "): IntersectionObserverEntry | null {\n"
            "    const [entry, setEntry] = useState<IntersectionObserverEntry | null>(null);\n"
            "    const frozen = entry?.isIntersecting && freezeOnceVisible;\n\n"
            "    useEffect(() => {\n"
            "        const node = elementRef?.current;\n"
            "        if (!node || frozen || typeof IntersectionObserver === 'undefined') return;\n\n"
            "        const observer = new IntersectionObserver(([firstEntry]) => {\n"
            "            setEntry(firstEntry);\n"
            "        }, { threshold, root, rootMargin });\n\n"
            "        observer.observe(node);\n\n"
            "        // Cleanup: disconnect observer when target node changes or component unmounts\n"
            "        return () => {\n"
            "            observer.disconnect();\n"
            "        };\n"
            "    }, [elementRef, threshold, root, rootMargin, frozen]);\n\n"
            "    return entry;\n"
            "}\n"
            "```\n\n"
            "**Performance Features:**\n"
            "- **`freezeOnceVisible`:** For image lazy-loading, once an image enters the viewport (`isIntersecting === true`), the observer is disconnected permanently, preventing redundant re-renders when the user scrolls past it again.\n"
            "- **`rootMargin` pre-fetching:** Setting `rootMargin: '200px'` triggers pagination or image loading 200px *before* the sentinel element reaches the viewport edge, creating a seamless infinite scroll experience."
        ),
        "Why": "IntersectionObserver offloads visibility detection to browser layout threads, avoiding main-thread scroll event bottlenecks.",
        "Risk": "Failing to disconnect the observer on unmount leads to orphaned DOM element retainment and memory leaks.",
        "Trade": "Intersection checks run asynchronously on the next animation frame, making them unsuitable for synchronous zero-frame layout locking.",
        "Try": "Attach useIntersectionObserver to a sentinel div at the bottom of a list to trigger fetchNextPage() when entry.isIntersecting is true.",
        "worked_case": (
            "Walkthrough scenario: An infinite feed binds a window scroll listener with getBoundingClientRect() to check if the user reached "
            "the bottom. On low-end mobile devices, rapid scrolling triggers continuous forced synchronous reflows, dropping frame rates to 15fps. "
            "Refactoring to useIntersectionObserver on a sentinel div at the list bottom eliminates scroll event handlers entirely; the browser "
            "asynchronously notifies the hook when the sentinel appears, maintaining a steady 60fps."
        ),
        "citations": [
            "https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API",
            "https://react.dev/reference/react/useEffect"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "How do you observe multiple elements without instantiating hundreds of IntersectionObserver instances?",
                "A": "Maintain a singleton IntersectionObserver in a module-level map, registering individual DOM nodes and their respective callbacks."
            }
        ]
    },
    {
        "Q": "How do you build an accessible useClickOutside custom hook to dismiss modals and dropdowns without event race conditions?",
        "A": (
            "**Direct answer:** A `useClickOutside` custom hook detects pointer interactions occurring outside a referenced container "
            "element to dismiss dropdown menus, dialogs, and popovers. Building a resilient version requires listening to `pointerdown` "
            "(or `mousedown`) rather than `click`, and carefully verifying DOM node containment while ignoring clicks on trigger elements.\n\n"
            "```typescript\n"
            "import { useEffect, useRef } from 'react';\n\n"
            "export function useClickOutside<T extends HTMLElement>(\n"
            "    handler: (event: MouseEvent | TouchEvent) => void\n"
            "): React.RefObject<T | null> {\n"
            "    const containerRef = useRef<T>(null);\n"
            "    const savedHandler = useRef(handler);\n"
            "    savedHandler.current = handler; // Avoid handler re-subscription\n\n"
            "    useEffect(() => {\n"
            "        const listener = (event: MouseEvent | TouchEvent) => {\n"
            "            const target = event.target as Node | null;\n"
            "            // Do nothing if container does not exist or click occurred inside container\n"
            "            if (!containerRef.current || containerRef.current.contains(target)) {\n"
            "                return;\n"
            "            }\n"
            "            savedHandler.current(event);\n"
            "        };\n\n"
            "        // Use pointerdown to capture initial touch/mouse press before focus switches\n"
            "        document.addEventListener('mousedown', listener);\n"
            "        document.addEventListener('touchstart', listener);\n\n"
            "        return () => {\n"
            "            document.removeEventListener('mousedown', listener);\n"
            "            document.removeEventListener('touchstart', listener);\n"
            "        };\n"
            "    }, []);\n\n"
            "    return containerRef;\n"
            "}\n"
            "```\n\n"
            "**Race Condition Defenses:**\n"
            "- **`mousedown` vs `click`:** If you listen to `click`, dragging text inside a modal and releasing the mouse outside it will trigger a `click` event on the body, prematurely closing the modal. Listening to `mousedown` accurately records where the gesture originated.\n"
            "- **Portal containment:** When components render into React Portals outside the root container, `containerRef.current.contains(target)` evaluates to `false` for portal children unless the portal node is also explicitly checked."
        ),
        "Why": "useClickOutside handles modal dismissal by detecting when gestures originate outside the component container.",
        "Risk": "Listening to click instead of mousedown causes modal closure when users release a text selection drag outside modal bounds.",
        "Trade": "Global document event listeners run on every click on the page, requiring fast early-exit containment checks.",
        "Try": "Attach useClickOutside to a dropdown menu and verify clicking inside keeps it open while clicking anywhere outside closes it.",
        "worked_case": (
            "Walkthrough scenario: A user opens a dropdown menu and tries to select text inside an input field in the dropdown. As the user drags the "
            "selection cursor, the mouse button is released outside the dropdown boundary. A naive click listener interprets this as a click outside "
            "and unmounts the dropdown, wiping the user's input. Using mousedown with node containment checks ensures the gesture that started inside "
            "does not close the dropdown."
        ),
        "citations": [
            "https://developer.mozilla.org/en-US/docs/Web/API/Node/contains",
            "https://react.dev/learn/reusing-logic-with-custom-hooks"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "How do you prevent the click that opens the dropdown from immediately triggering the click-outside handler?",
                "A": "Ensure the toggle button click event does not bubble or check if event.target is contained within the toggle button ref."
            }
        ]
    },
    {
        "Q": "How do you implement a useMediaQuery custom hook with SSR hydration safety and matchMedia listeners?",
        "A": (
            "**Direct answer:** A `useMediaQuery` custom hook evaluates CSS media queries (e.g. `(min-width: 768px)`, `(prefers-color-scheme: dark)`) "
            "in JavaScript, re-rendering the component when the viewport or user preferences cross breakpoint thresholds. "
            "In SSR frameworks (Next.js, Remix), the server has no window or device viewport dimensions, so the hook must provide a predictable "
            "initial default to prevent hydration layout mismatches.\n\n"
            "```typescript\n"
            "import { useState, useEffect } from 'react';\n\n"
            "export function useMediaQuery(query: string, defaultValue = false): boolean {\n"
            "    const [matches, setMatches] = useState<boolean>(() => {\n"
            "        if (typeof window === 'undefined') return defaultValue;\n"
            "        return window.matchMedia(query).matches;\n"
            "    });\n\n"
            "    useEffect(() => {\n"
            "        if (typeof window === 'undefined') return;\n"
            "        const mediaQueryList = window.matchMedia(query);\n"
            "        setMatches(mediaQueryList.matches);\n\n"
            "        const listener = (event: MediaQueryListEvent) => {\n"
            "            setMatches(event.matches);\n"
            "        };\n\n"
            "        // Modern EventTarget API on MediaQueryList\n"
            "        mediaQueryList.addEventListener('change', listener);\n"
            "        return () => {\n"
            "            mediaQueryList.removeEventListener('change', listener);\n"
            "        };\n"
            "    }, [query]);\n\n"
            "    return matches;\n"
            "}\n"
            "```\n\n"
            "**Hydration Invariant:**\n"
            "On the server, `defaultValue` is rendered into the HTML. If the client device has a different viewport on initial mount, "
            "the `useEffect` synchronizes the true client value *after* the initial hydration commit, avoiding a hydration markup mismatch error."
        ),
        "Why": "useMediaQuery lets components programmatically adapt to viewport and device preference changes without polling resize events.",
        "Risk": "Switching DOM trees during SSR hydration based on immediate window.innerWidth reads causes hydration mismatch errors.",
        "Trade": "Using JavaScript media queries instead of CSS media queries (@media) causes a brief flash of default layout if values differ.",
        "Try": "Toggle device simulation mode in browser DevTools across 768px width and verify useMediaQuery updates without page reload.",
        "worked_case": (
            "Walkthrough scenario: A responsive navigation bar renders a desktop menu or mobile hamburger. Using window.innerWidth < 768 on the server "
            "crashes with window is not defined. Using window.matchMedia on client initial state causes HTML from server (desktop) to mismatch "
            "client initial render on mobile (hamburger), causing React to dump the server DOM. Providing a default SSR fallback and syncing via "
            "useEffect allows clean hydration followed by a smooth single-pass layout update."
        ),
        "citations": [
            "https://developer.mozilla.org/en-US/docs/Web/API/Window/matchMedia",
            "https://react.dev/reference/react/useSyncExternalStore"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "How can useSyncExternalStore be applied to useMediaQuery?",
                "A": "Pass mediaQueryList.addEventListener as subscribe and () => mediaQueryList.matches as getSnapshot for zero-lag concurrent reads."
            }
        ]
    },
    {
        "Q": "How does the useLatest or useEvent ref pattern eliminate stale closures in effects without triggering re-subscriptions?",
        "A": (
            "**Direct answer:** A frequent architectural dilemma in React occurs when an effect needs to call a callback that reads fresh "
            "props or state, but adding that callback to the `useEffect` dependency array would cause the effect to unbind and re-bind "
            "expensive subscriptions (like WebSocket connections or event listeners) on every render. The `useLatest` pattern uses a mutable "
            "ref to hold the most recent callback, allowing effects to invoke the latest logic with stable dependencies.\n\n"
            "```typescript\n"
            "import { useRef, useLayoutEffect, useCallback } from 'react';\n\n"
            "// 1. The useLatest hook:\n"
            "export function useLatest<T>(value: T): React.RefObject<T> {\n"
            "    const ref = useRef<T>(value);\n"
            "    useLayoutEffect(() => {\n"
            "        ref.current = value;\n"
            "    });\n"
            "    return ref;\n"
            "}\n\n"
            "// 2. The useEventCallback hook:\n"
            "export function useEventCallback<T extends (...args: any[]) => any>(fn: T): T {\n"
            "    const ref = useRef<T>(fn);\n"
            "    useLayoutEffect(() => {\n"
            "        ref.current = fn;\n"
            "    });\n"
            "    return useCallback(((...args: any[]) => {\n"
            "        return ref.current(...args);\n"
            "    }) as T, []);\n"
            "}\n"
            "```\n\n"
            "**Why useLayoutEffect?**\n"
            "Updating `ref.current` inside `useLayoutEffect` guarantees the ref is updated synchronously before any passive `useEffect` "
            "fires anywhere in the component tree, ensuring that background timers and subscriptions never invoke a stale function.\n\n"
            "**Restriction:** Event callbacks generated this way should only be called inside effects or event handlers, never during render computation."
        ),
        "Why": "useLatest breaks the coupling between callback freshness and effect re-execution dependencies.",
        "Risk": "Invoking an event callback created with useEventCallback during render computation reads uncommitted mutable state.",
        "Trade": "Sacrifices purely declarative dependency tracking in exchange for stable subscription lifetimes.",
        "Try": "Create a timer interval effect that reads a fast-updating state counter using useLatest, verifying the interval timer ID never resets.",
        "worked_case": (
            "Walkthrough scenario: A chat widget connects to a WebSocket in useEffect. Inside the onMessage handler, it calls onNewMessage(msg, currentRoomId). "
            "Because currentRoomId changes as the user navigates, adding onNewMessage to useEffect dependencies drops and re-establishes the WebSocket "
            "connection on every room change. Wrapping onNewMessage with useEventCallback provides a referentially stable callback that reads fresh "
            "currentRoomId without ever disconnecting the socket."
        ),
        "citations": [
            "https://react.dev/reference/react/useRef",
            "https://github.com/reactjs/rfcs/blob/useevent/text/0000-useevent.md"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "Why is useLayoutEffect preferred over useEffect for updating ref.current in useLatest?",
                "A": "useLayoutEffect runs synchronously before browser paint, ensuring the ref is populated before any child or sibling useEffect executes."
            }
        ]
    },
    {
        "Q": "How do React's synthetic event system and native DOM event delegation differ between React 16, 17, and 18?",
        "A": (
            "**Direct answer:** React wraps browser native events in cross-browser `SyntheticEvent` instances for unified behavior across platforms. "
            "A monumental architectural shift occurred between React 16 and React 17/18 in how events are attached and delegated.\n\n"
            "```\n"
            "React 16 Delegation Architecture:\n"
            "[ Document Node ] <--- All React event listeners attached here!\n"
            "       |\n"
            "[ App Root Container #root ]\n"
            "       |\n"
            "[ Target Button: <button onClick={...}> ]\n\n"
            "React 17+ Delegation Architecture:\n"
            "[ Document Node ]\n"
            "       |\n"
            "[ App Root Container #root ] <--- React listeners attached here per root!\n"
            "       |\n"
            "[ Target Button: <button onClick={...}> ]\n"
            "```\n\n"
            "**Crucial Differences:**\n"
            "- **Attachment Point:** In React 16, React attached listeners to `document`. In React 17 and 18, React attaches listeners to the root DOM container (`rootNode`, e.g. `<div id=\"root\">`). This allows multiple micro-frontend React apps to safely co-exist on the same page without cross-app event interference.\n"
            "- **Event Pooling Removal:** In React 16, `SyntheticEvent` objects were pooled and wiped after the event callback executed (accessing `e.target` in an async `setTimeout` threw `null` unless `e.persist()` was called). In React 17+, event pooling was completely removed; synthetic event properties remain accessible in async code.\n"
            "- **Propagation Order:** When mixing native `document.addEventListener` with React `onClick`, in React 16 native document listeners fired *after* React handlers. In React 17+, native document listeners fire *after* the event bubbles out of `#root`."
        ),
        "Why": "Root container delegation enables micro-frontend multi-version co-existence and aligns React event bubbling with native DOM order.",
        "Risk": "Calling e.stopPropagation() in a React 17+ handler stops bubbling to root, but native listeners on child DOM nodes still fire.",
        "Trade": "Synthetics introduce an allocation wrapper layer in exchange for cross-browser normalization and consistent bubbling across portals.",
        "Try": "Attach a native click listener to document.body and a React onClick to a button, logging order to verify bubbling from root to document.",
        "worked_case": (
            "Walkthrough scenario: A micro-frontend host running React 18 embeds a legacy React 16 checkout widget. In React 16, clicking inside "
            "the legacy widget bubbled to document, where both apps had global listeners that collided and broke dropdowns. With React 17+ root delegation, "
            "calling e.stopPropagation() inside the child micro-frontend stops the event at the child root boundary, preventing it from reaching the host "
            "root container cleanly."
        ),
        "citations": [
            "https://legacy.reactjs.org/blog/2020/08/10/react-v17-rc.html#changes-to-event-delegation",
            "https://react.dev/learn/responding-to-events"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "Why was synthetic event pooling removed in React 17?",
                "A": "Modern JavaScript engines optimize small object allocations efficiently, making pooling benefits negligible compared to the async confusion it caused."
            }
        ]
    },
    {
        "Q": "Why does React StrictMode render components and invoke effects twice in development, and how do you write idempotent effects?",
        "A": (
            "**Direct answer:** In development mode, `React.StrictMode` intentionally double-invokes component render functions, constructor functions, "
            "state updater functions, and effect setup/cleanup cycles (`mount -> unmount -> mount`). This is not a bug; it is an aggressive stress test "
            "designed to surface side-effects placed in pure render functions and prove that `useEffect` cleanups are fully idempotent.\n\n"
            "```typescript\n"
            "// VULNERABLE NON-IDEMPOTENT EFFECT (Broke in StrictMode):\n"
            "useEffect(() => {\n"
            "    // Missing cleanup! StrictMode mount -> unmount -> mount adds two listeners:\n"
            "    window.addEventListener('resize', handleResize);\n"
            "}, []);\n\n"
            "// SECURE IDEMPOTENT EFFECT (Succeeds in StrictMode & Concurrent Mode):\n"
            "useEffect(() => {\n"
            "    window.addEventListener('resize', handleResize);\n"
            "    // Cleanup restores system to pristine baseline:\n"
            "    return () => {\n"
            "        window.removeEventListener('resize', handleResize);\n"
            "    };\n"
            "}, []);\n"
            "```\n\n"
            "**Why Concurrent React requires this:**\n"
            "React 18 introduces Fast Refresh and features like Offscreen (Activity), where React can hide a component, unmount its DOM and layout effects "
            "to save memory, and remount it later with preserved state. If your effect cannot survive an unmount/remount cycle without leaking sockets, "
            "timers, or duplicate DOM elements, it will fail in production concurrent scenarios."
        ),
        "Why": "Double-mounting in StrictMode verifies that components and effects can safely survive concurrent pauses, resumes, and tab unmounting.",
        "Risk": "Omitting cleanup handlers causes duplicate subscriptions, multiple network requests, and runaway memory leaks in development and production.",
        "Trade": "Doubles initial development render and network calls, causing developer confusion unless intentional idempotency is understood.",
        "Try": "Add an AbortController to a fetch effect in StrictMode and verify the network tab aborts the first request cleanly and completes the second.",
        "worked_case": (
            "Walkthrough scenario: A developer connects to a chat room in useEffect without cleanup. In development with StrictMode, the user notices "
            "they receive every message twice. The developer thinks React has a bug, but StrictMode exposed that navigating away and back to the chat "
            "room would have leaked a persistent connection in production. Adding return () => socket.disconnect() ensures the first connection closes "
            "cleanly and only one active connection remains."
        ),
        "citations": [
            "https://react.dev/reference/react/StrictMode",
            "https://react.dev/learn/synchronizing-with-effects#how-to-handle-the-effect-firing-twice-in-development"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "Does StrictMode double-render in production builds?",
                "A": "No, StrictMode double-renders and double-invokes effects strictly in development mode; production builds mount exactly once."
            }
        ]
    },
    {
        "Q": "How do controlled and uncontrolled components differ in form state management, and how do you build a useControllableState hook?",
        "A": (
            "**Direct answer:** A **controlled component** derives its form value directly from React props (`value={props.value}`) and notifies "
            "the parent of changes via a callback (`onChange={props.onChange}`), making React the single source of truth. An **uncontrolled component** "
            "stores its form value natively in the DOM (`defaultValue={props.defaultValue}`), queried imperatively via a `ref`.\n\n"
            "High-grade UI component libraries (such as Radix UI and Headless UI) implement hybrid components that support *both* modes seamlessly "
            "using a `useControllableState` hook.\n\n"
            "```typescript\n"
            "import { useState, useCallback, useRef } from 'react';\n\n"
            "export function useControllableState<T>({\n"
            "    value: propValue,\n"
            "    defaultValue,\n"
            "    onChange\n"
            "}: {\n"
            "    value?: T;\n"
            "    defaultValue: T;\n"
            "    onChange?: (val: T) => void;\n"
            "}): [T, (nextVal: T | ((prev: T) => T)) => void] {\n"
            "    const isControlled = propValue !== undefined;\n"
            "    const [uncontrolledState, setUncontrolledState] = useState<T>(defaultValue);\n"
            "    const currentValue = isControlled ? propValue : uncontrolledState;\n\n"
            "    const setValue = useCallback((next: T | ((prev: T) => T)) => {\n"
            "        const resolved = next instanceof Function ? next(currentValue) : next;\n"
            "        if (!isControlled) {\n"
            "            setUncontrolledState(resolved);\n"
            "        }\n"
            "        onChange?.(resolved);\n"
            "    }, [isControlled, currentValue, onChange]);\n\n"
            "    return [currentValue, setValue];\n"
            "}\n"
            "```\n\n"
            "**Critical Anti-Pattern:** A component must never switch from uncontrolled (`value=undefined`) to controlled (`value='text'`) mid-lifecycle. "
            "Doing so triggers React's warning: *'A component is changing an uncontrolled input to be controlled.'*"
        ),
        "Why": "useControllableState allows design system components to support both frictionless drop-in uncontrolled use and strict parent-controlled state.",
        "Risk": "Passing value={undefined} initially and later passing a string triggers React uncontrolled-to-controlled console errors.",
        "Trade": "Controlled state incurs a re-render per keystroke; uncontrolled state eliminates typing lag on massive forms but complicates validation.",
        "Try": "Build a Switch toggle component with useControllableState that can operate standalone or controlled by a parent state variable.",
        "worked_case": (
            "Walkthrough scenario: A design system team builds an Accordion component. Consumer A wants quick drop-in usage without managing state: "
            "<Accordion defaultValue='item-1' />. Consumer B wants to synchronize the open accordion with a URL query parameter: <Accordion value={activeTab} onChange={setActiveTab} />. "
            "Implementing useControllableState allows the exact same Accordion component to serve both consumers flawlessly without duplicate implementations."
        ),
        "citations": [
            "https://react.dev/learn/sharing-state-between-components#controlled-and-uncontrolled-components"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "How do you avoid the uncontrolled-to-controlled warning when initializing controlled state from asynchronous data?",
                "A": "Provide a fallback value (e.g. value={data?.name ?? ''}) so the controlled input value is never passed as undefined."
            }
        ]
    },
    {
        "Q": "What is the exact reconciliation behavior when swapping component types versus toggling reconciliation keys?",
        "A": (
            "**Direct answer:** React's reconciliation diffing heuristic operates on two fundamental assumptions to achieve O(n) performance: "
            "1. Two elements of different types produce entirely different subtrees. "
            "2. Keys identify which child elements remain stable across different renders.\n\n"
            "```tsx\n"
            "// 1. Swapping Component Types: Completely destroys and remounts subtree\n"
            "// When isEditing toggles between true and false:\n"
            "{isEditing ? <EditProfileForm /> : <ViewProfileDisplay />}\n"
            "// React unmounts ViewProfileDisplay (clearing DOM, refs, state) and mounts EditProfileForm.\n\n"
            "// 2. Swapping Same Component Type with Same Key: Preserves internal state!\n"
            "<Counter key=\"counter\" />\n"
            "// State is preserved even if surrounding props change.\n\n"
            "// 3. Changing Key on Same Component Type: Forces complete teardown and re-initialization!\n"
            "<UserProfile key={userId} userId={userId} />\n"
            "```\n\n"
            "**Strategic Use of Keys to Reset State:**\n"
            "A common React bug is retaining old form state when switching selected users. Instead of writing complex `useEffect` cleanup "
            "functions to reset 10 different `useState` fields when `userId` changes, changing the reconciliation `key` (`key={userId}`) "
            "instructs React to tear down the old component Fiber and mount a fresh instance with clean default state automatically."
        ),
        "Why": "Keys determine component identity; changing keys signals React to discard previous state and re-initialize the subtree.",
        "Risk": "Using array indices as keys causes React to preserve old component state in the wrong items when list items are deleted or inserted.",
        "Trade": "Tearing down a component via key change resets internal state cleanly but loses uncommitted scroll and focus positions.",
        "Try": "Render a stateful Form with a key={userId} prop; change userId and verify all input fields reset to initial defaults without useEffect.",
        "worked_case": (
            "Walkthrough scenario: A master-detail admin panel displays user profiles. User A has draft text in a bio input. The admin clicks User B "
            "in the sidebar. Because the UserProfile component did not change type and had no key, React kept the existing Fiber and preserved the "
            "draft bio state, accidentally saving User A's draft bio into User B's profile. Adding key={user.id} forces React to unmount User A and "
            "mount User B with fresh empty state, preventing data corruption."
        ),
        "citations": [
            "https://react.dev/learn/preserving-and-resetting-state"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "What happens if two sibling elements in an array share the exact same key?",
                "A": "React emits a console warning, and updates to the duplicate elements will improperly clobber and overwrite each other during diffing."
            }
        ]
    },
    {
        "Q": "Why do Error Boundaries require class components, and what specific categories of runtime errors can they not catch?",
        "A": (
            "**Direct answer:** In React, Error Boundaries catch JavaScript errors anywhere in their child component tree during rendering, "
            "lifecycle methods, and constructor execution, logging the error and displaying a fallback UI instead of crashing the entire page. "
            "Error Boundaries *must* be implemented as class components because there are no hook equivalents for `componentDidCatch` or "
            "`static getDerivedStateFromError`.\n\n"
            "```typescript\n"
            "import React, { Component, ErrorInfo, ReactNode } from 'react';\n\n"
            "interface Props { children: ReactNode; fallback: ReactNode; }\n"
            "interface State { hasError: boolean; error: Error | null; }\n\n"
            "export class ErrorBoundary extends Component<Props, State> {\n"
            "    state: State = { hasError: false, error: null };\n\n"
            "    // Synchronously update state to render fallback UI on next render:\n"
            "    static getDerivedStateFromError(error: Error): State {\n"
            "        return { hasError: true, error };\n"
            "    }\n\n"
            "    // Log error telemetry asynchronously:\n"
            "    componentDidCatch(error: Error, errorInfo: ErrorInfo) {\n"
            "        console.error('Captured by ErrorBoundary:', error, errorInfo.componentStack);\n"
            "    }\n\n"
            "    render() {\n"
            "        if (this.state.hasError) return this.props.fallback;\n"
            "        return this.props.children;\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "**What Error Boundaries CANNOT catch:**\n"
            "1. **Event Handlers:** Errors thrown inside `onClick` or `onSubmit` happen outside rendering. Catch these with standard `try/catch`.\n"
            "2. **Asynchronous Callbacks:** Errors in `setTimeout`, `requestAnimationFrame`, or uncaught `Promise` rejections.\n"
            "3. **Server-Side Rendering (SSR):** Errors occurring during server HTML rendering; SSR fails closed.\n"
            "4. **Errors inside the Error Boundary itself:** An error boundary only catches errors in its *children*, not in its own render method."
        ),
        "Why": "Error boundaries isolate sub-tree crashes so a widget failure in a sidebar does not crash the entire web application.",
        "Risk": "Assuming error boundaries catch asynchronous event handler failures leaves unhandled promise rejections silent.",
        "Trade": "Class components require older lifecycle syntax and cannot use hooks directly (though children can).",
        "Try": "Wrap a buggy component in an ErrorBoundary with a Retry button that resets state.hasError to false upon user click.",
        "worked_case": (
            "Walkthrough scenario: A user clicks a Buy button that throws an error inside an async fetch. The developer expected the ErrorBoundary "
            "surrounding the checkout form to catch it. Instead, the screen remained stuck with a spinning button because ErrorBoundaries do not catch "
            "event handler errors. Refactoring the event handler to try/catch with a local setError state allows the form to display an inline error message."
        ),
        "citations": [
            "https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "How can an event handler pass an async error to the nearest Error Boundary?",
                "A": "Invoke a state setter with a function that throws: const [, setError] = useState(); setError(() => { throw error; });."
            }
        ]
    },
    {
        "Q": "How does React prevent concurrent mode starvation across priority lanes, and how does lane expiration upgrade work?",
        "A": (
            "**Direct answer:** In React 18's concurrent scheduler, units of work are assigned to **Lanes** represented as a 31-bit integer bitmask. "
            "High-priority lanes include `SyncLane` (discrete user gestures like clicks) and `InputContinuousLane` (typing and dragging), "
            "while low-priority lanes include `DefaultLane` (normal data fetching updates) and `TransitionLane` (background transitions).\n\n"
            "```\n"
            "Lane Priority Hierarchy (from highest to lowest):\n"
            "SyncLane (1)                <-- Discrete clicks, keypresses\n"
            "InputContinuousLane (2)     <-- Dragging, scroll tracking\n"
            "DefaultLane (4)             <-- Normal state updates (fetch resolution)\n"
            "TransitionLane (8...64)     <-- startTransition, useDeferredValue\n"
            "IdleLane (1073741824)       <-- Offscreen rendering\n"
            "```\n\n"
            "**Preventing Starvation via Expiration:**\n"
            "If a user continuously types at 120 words per minute, high-priority `SyncLane` tasks enter the queue incessantly. Without a starvation "
            "protection mechanism, low-priority `TransitionLane` renders would be deferred indefinitely and never commit.\n\n"
            "- **Expiration Timestamp:** When a transition task is scheduled, React assigns it an expiration deadline (typically ~5000ms in the future).\n"
            "- **Priority Upgrade:** On each scheduler tick, React checks if any pending task's deadline has passed. If expired, React immediately upgrades the task from `TransitionLane` to `SyncLane`, forcing it to render synchronously without yielding until committed."
        ),
        "Why": "Lane expiration ensures low-priority background transitions are guaranteed to complete even under continuous high-priority user interaction.",
        "Risk": "Setting too short a transition timeout or heavy background computation causes UI stutters when expired tasks block the main thread.",
        "Trade": "Bitmask lanes provide extremely fast 32-bit bitwise comparison and scheduling operations at the cost of framework internal complexity.",
        "Try": "Dispatch a rapid loop of urgent state updates while a transition is pending and observe in Profiler how the transition eventually forces completion.",
        "worked_case": (
            "Walkthrough scenario: A dashboard user types continuously into a filter box while a heavy 5000-row table re-renders in startTransition. "
            "Because keystrokes arrive every 50ms, React keeps interrupting the table render to process the keystroke. After 5000ms, the transition's "
            "expiration timer lapses. React marks the table render as expired, elevates it to Sync priority, completes the render synchronously, "
            "and commits the updated table to the screen, preventing indefinite starvation."
        ),
        "citations": [
            "https://github.com/facebook/react/blob/main/packages/react-reconciler/src/ReactFiberLane.js",
            "https://react.dev/reference/react/useTransition"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "Why did React replace expiration times with bitmask lanes in React 17/18?",
                "A": "Lanes allow expressing multiple independent priority batches simultaneously using bitwise operators (lanes & -lanes), decoupling priority from sequence."
            }
        ]
    },
    {
        "Q": "How do you profile, identify, and eliminate unnecessary re-renders using the React DevTools Profiler and WhyDidYouRender?",
        "A": (
            "**Direct answer:** Performance profiling in React requires empirical measurement rather than speculative memoization. "
            "The **React DevTools Profiler** records commit phases, measuring component render duration, commit counts, and why a specific "
            "component rendered.\n\n"
            "```tsx\n"
            "// 1. Profiler Component for programmatic telemetry:\n"
            "import { Profiler, ProfilerOnRenderCallback } from 'react';\n\n"
            "const onRender: ProfilerOnRenderCallback = (\n"
            "    id, phase, actualDuration, baseDuration, startTime, commitTime\n"
            ") => {\n"
            "    if (actualDuration > 16) {\n"
            "        console.warn(`[Slow Render] ${id} in ${phase} took ${actualDuration.toFixed(2)}ms`);\n"
            "    }\n"
            "};\n\n"
            "export function MonitoredFeed() {\n"
            "    return (\n"
            "        <Profiler id=\"FeedList\" onRender={onRender}>\n"
            "            <LargeFeed />\n"
            "        </Profiler>\n"
            "    );\n"
            "}\n"
            "```\n\n"
            "**Identifying Re-render Culprits:**\n"
            "- **Flamegraph vs Ranked Chart:** The Flamegraph shows tree hierarchy with color-coded durations (yellow = expensive, blue = fast, gray = skipped). The Ranked Chart sorts components strictly by `actualDuration` to pinpoint bottlenecks.\n"
            "- **'Why did this render?':** Enable 'Record why each component rendered while profiling' in DevTools settings. Common triggers: `props changed: onClick` (un-memoized inline callback) or `state changed`.\n"
            "- **WhyDidYouRender library:** Automatically hooks into React to notify the console when a component wrapped in `React.memo` re-renders due to equal-by-value but unequal-by-reference props."
        ),
        "Why": "Systematic profiling prevents premature memoization while exposing real prop instability and render bottlenecks.",
        "Risk": "Wrapping every component in React.memo and useMemo indiscriminately introduces memory overhead that exceeds the cost of re-rendering.",
        "Trade": "The Profiler adds profiling overhead in development and requires specialized profiling production bundles to measure accurately in production.",
        "Try": "Enable 'Highlight updates when components render' in React DevTools and identify components that re-render without visual changes.",
        "worked_case": (
            "Walkthrough scenario: A developer wrapped a 100-item TableRow component in React.memo, but noticed in Profiler that every row still re-rendered "
            "when a top-level counter changed. Hovering over TableRow in DevTools revealed: 'Props changed: (onDelete)'. The parent passed onDelete={() => deleteItem(item.id)} "
            "as an inline arrow function, generating a brand new reference on every render and defeating React.memo completely. Passing a stable useCallback "
            "or passing id to the child eliminated all 100 re-renders."
        ),
        "citations": [
            "https://react.dev/reference/react/Profiler",
            "https://legacy.reactjs.org/blog/2018/09/10/introducing-the-react-profiler.html"
        ],
        "reviewer_status": {
            "status": "reviewed",
            "reviewer": "Codex AI technical review (user-delegated verdict; authored/self-reviewed)",
            "reviewed_at": "2026-10-24"
        },
        "answer_format": "conceptual",
        "difficulty": "interview",
        "follow_ups": [
            {
                "Q": "What is the difference between actualDuration and baseDuration in the Profiler?",
                "A": "actualDuration is time spent rendering the current commit; baseDuration estimates how long the subtree would take without memoization."
            }
        ]
    }
]
