"""16 Frontend System Design Interview Questions with comprehensive answers, code examples and worked cases."""

QUESTIONS = [
    {
        "Q": "How do you architect a frontend application for scale using layered architecture and separation of concerns?",
        "A": (
            "**Direct answer:** Enterprise frontend applications fail to scale when business logic, network I/O, and UI presentation are tangled "
            "inside monolithic React components. A robust, scalable frontend architecture adopts a **Layered Architecture** with unidirectional "
            "dependencies divided into four distinct layers:\n"
            "1. **Presentation Layer (UI):** Pure, declarative components responsible solely for rendering DOM elements and receiving user interactions. Components are agnostic of HTTP endpoints or global stores.\n"
            "2. **Application Layer (Hooks/Controllers):** Coordinates state, orchestrates business flows, and connects presentation to domain logic (e.g., custom hooks like `useCheckoutFlow()`).\n"
            "3. **Domain Layer (Entities & Rules):** Framework-agnostic pure TypeScript classes, types, and validation rules (e.g., `calculateCartTax(cart)`). Zero dependencies on React or DOM.\n"
            "4. **Infrastructure Layer (Data & Network):** Implements HTTP clients, WebSocket connections, IndexedDB, and analytics adapters.\n\n"
            "```typescript\n"
            "// 1. DOMAIN LAYER (Pure TypeScript, Zero Framework Dependencies)\n"
            "export interface CartItem { id: string; price: number; quantity: number; }\n"
            "export function calculateCartTotal(items: CartItem[]): number {\n"
            "    return items.reduce((sum, item) => sum + item.price * item.quantity, 0);\n"
            "}\n"
            "\n"
            "// 2. INFRASTRUCTURE LAYER (Network Client)\n"
            "export const cartApi = {\n"
            "    checkout: async (items: CartItem[]) => apiFetch('/api/checkout', { method: 'POST', body: items })\n"
            "};\n"
            "\n"
            "// 3. APPLICATION LAYER (React Hook Orchestration)\n"
            "export function useCheckout() {\n"
            "    const [items, setItems] = useState<CartItem[]>([]);\n"
            "    const total = useMemo(() => calculateCartTotal(items), [items]);\n"
            "    const checkout = async () => cartApi.checkout(items);\n"
            "    return { items, total, checkout };\n"
            "}\n"
            "\n"
            "// 4. PRESENTATION LAYER (Pure Component View)\n"
            "export function CartView({ total, onCheckout }: { total: number; onCheckout: () => void }) {\n"
            "    return (\n"
            "        <div>\n"
            "            <p>Total: ${total}</p>\n"
            "            <button onClick={onCheckout}>Checkout</button>\n"
            "        </div>\n"
            "    );\n"
            "}\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **Testability:** Domain logic is unit-tested without React testing libraries or DOM mocks in milliseconds.\n"
            "- **Framework portability:** If the UI migrates from React to Vue or React Native, the entire Domain and Infrastructure layers are reused with zero modifications.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Enforce dependency boundaries using ESLint rules (like `eslint-plugin-import` or `nx` boundaries) to prevent Presentation components "
            "from directly importing Infrastructure network clients."
        ),
        "Why": "Layered architecture isolates business rules from UI frameworks, enabling independent unit testing and long-term maintainability.",
        "Risk": "Allowing presentation components to make raw fetch calls directly creates tight coupling that makes UI refactoring impossible.",
        "Trade": "Introduces more files and architectural discipline compared to rapid monolithic component prototyping.",
        "Try": "Write unit tests for a pure domain pricing function without importing React or testing-library and observe sub-millisecond execution.",
        "worked_case": (
            "Walkthrough scenario: An enterprise fintech app needs to support both a Web client (React) and a Mobile client (React Native). "
            "Because tax calculations, interest rates, and loan validation were written as pure TypeScript domain functions in a shared package, "
            "the mobile team reused 100% of the domain calculations, reducing the mobile development timeline from 6 months to 6 weeks."
        ),
        "citations": [
            "https://martinfowler.com/bliki/PresentationDomainDataLayering.html",
            "https://khalilstemmler.com/articles/client-side-architecture/introduction/"
        ],
        "follow_ups": [
            {
                "Q": "How do you enforce architectural layer boundaries automatically in CI?",
                "A": "Use ESLint import boundary rules (e.g. eslint-plugin-import or Nx module boundaries) that throw build errors if domain layers import presentation code."
            }
        ]
    },
    {
        "Q": "How do you evaluate and select state management solutions across local state, Context, Zustand, Redux, and server cache?",
        "A": (
            "**Direct answer:** State in modern frontend applications is not uniform; choosing a state management tool requires categorizing "
            "state into four distinct categories and selecting the lightest tool that solves the problem:\n"
            "1. **Local Component State (`useState`, `useReducer`):** Ephemeral UI state confined to a single component (form inputs, toggle state, accordion open/close). Default to this for 80% of state.\n"
            "2. **Server Cache State (TanStack Query / SWR):** Remote database state that is asynchronous, shared, and requires caching, revalidation, and optimistic updates. Never store server data in Redux or global stores manually.\n"
            "3. **Global Client State (`Zustand` / `Redux Toolkit`):** Complex synchronous client-side UI state shared across disparate components (active theme, user preferences, audio player playback queue, canvas shape selection).\n"
            "4. **Low-Frequency Static Context (`React Context`):** Values that change rarely and are needed everywhere (current authenticated user object, locale string).\n\n"
            "```typescript\n"
            "// Modern Lightweight Global Store with Zustand (supports selectors):\n"
            "import { create } from 'zustand';\n"
            "\n"
            "interface PlayerStore {\n"
            "    isPlaying: boolean;\n"
            "    volume: number;\n"
            "    togglePlay: () => void;\n"
            "    setVolume: (v: number) => void;\n"
            "}\n"
            "\n"
            "export const usePlayerStore = create<PlayerStore>((set) => ({\n"
            "    isPlaying: false,\n"
            "    volume: 80,\n"
            "    togglePlay: () => set(state => ({ isPlaying: !state.isPlaying })),\n"
            "    setVolume: (volume) => set({ volume })\n"
            "}));\n"
            "\n"
            "// Consumer component using selective re-rendering:\n"
            "function PlayButton() {\n"
            "    // Only re-renders when isPlaying changes, ignores volume changes!\n"
            "    const isPlaying = usePlayerStore(s => s.isPlaying);\n"
            "    const togglePlay = usePlayerStore(s => s.togglePlay);\n"
            "    return <button onClick={togglePlay}>{isPlaying ? 'Pause' : 'Play'}</button>;\n"
            "}\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **Selector performance:** Zustand uses `useSyncExternalStore` with equality checks, ensuring components only re-render when their selected slice changes.\n"
            "- **Redux comparison:** Redux Toolkit is suited for massive enterprise applications requiring strict time-travel debugging, serialization middleware, and complex saga side-effects.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "The biggest anti-pattern in modern React is using Redux to fetch and store server data manually with `FETCH_START`, `FETCH_SUCCESS`, "
            "`FETCH_ERROR` actions. Migrating server state to TanStack Query eliminates 90% of legacy Redux boilerplate."
        ),
        "Why": "Properly partitioning state categories prevents monolithic store bloat and stops cascading re-renders across consumers.",
        "Risk": "Duplicating server response data into a global Redux store causes cache desynchronization and stale UI bugs.",
        "Trade": "Zustand provides zero-boilerplate selector stores; Redux Toolkit offers structured governance and middleware for huge teams.",
        "Try": "Replace a complex React Context holding state with a Zustand store and verify that unselected state changes cause zero re-renders.",
        "worked_case": (
            "Walkthrough scenario: An application with 200 components stored all backend data in a Redux store with 15,000 lines of boilerplate. "
            "The team migrated server data to TanStack Query. The Redux codebase shrank by 85%, leaving only a 150-line Zustand store "
            "for managing the persistent audio player state and sidebar collapse toggle."
        ),
        "citations": [
            "https://tanstack.com/query/latest/docs/framework/react/overview",
            "https://github.com/pmndrs/zustand"
        ],
        "follow_ups": [
            {
                "Q": "Why is React Context ill-suited for high-frequency state updates like mouse coordinates or animations?",
                "A": "Context lacks fine-grained selectors; updating a context value forces every component calling useContext() to re-render, creating severe CPU bottlenecks."
            }
        ]
    },
    {
        "Q": "How do Micro-Frontends work using Webpack/Vite Module Federation, and what are the trade-offs vs a monolith?",
        "A": (
            "**Direct answer:** Micro-Frontends extend microservices principles to the web frontend: decomposing a large monolithic frontend "
            "into smaller, semi-independent micro-applications owned by distinct vertical feature teams (e.g., Team Checkout, Team Catalog, Team Search). "
            "While early micro-frontends used clunky iframes, modern micro-frontends use **Module Federation** (supported in Webpack 5 and Vite via plugins). "
            "Module Federation allows a 'Host' container application to dynamically import remote JavaScript bundles at runtime across different domains, "
            "while sharing singleton dependencies (like `react` and `react-dom`) so libraries are downloaded only once.\n\n"
            "```javascript\n"
            "// webpack.config.js for Remote Application (Team Checkout)\n"
            "new ModuleFederationPlugin({\n"
            "    name: 'checkoutApp',\n"
            "    filename: 'remoteEntry.js',\n"
            "    exposes: {\n"
            "        './CheckoutWidget': './src/CheckoutWidget.tsx'\n"
            "    },\n"
            "    shared: {\n"
            "        react: { singleton: true, requiredVersion: '^18.0.0' },\n"
            "        'react-dom': { singleton: true, requiredVersion: '^18.0.0' }\n"
            "    }\n"
            "});\n"
            "\n"
            "// Inside Host Container (Shell Application):\n"
            "import React, { Suspense, lazy } from 'react';\n"
            "// Dynamically loads bundle from checkout.enterprise.com at runtime!\n"
            "const RemoteCheckout = lazy(() => import('checkoutApp/CheckoutWidget'));\n"
            "\n"
            "function Shell() {\n"
            "    return (\n"
            "        <Suspense fallback={<div>Loading checkout...</div>}>\n"
            "            <RemoteCheckout orderId=\"123\" />\n"
            "        </Suspense>\n"
            "    );\n"
            "}\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **Independent deployment:** Team Checkout can deploy bug fixes to `checkout.enterprise.com/remoteEntry.js` without recompiling or redeploying the Shell.\n"
            "- **Shared Singleton:** `singleton: true` prevents loading duplicate copies of React in memory, avoiding hook runtime crashes.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Trade-offs are substantial: Micro-frontends introduce operational complexity, runtime version mismatch risks, CSS style pollution "
            "(requiring CSS modules or Shadow DOM), and slower initial page loads. Only adopt micro-frontends when organizational scale "
            "(>50 developers across distinct teams) makes monolithic builds a deployment bottleneck."
        ),
        "Why": "Module Federation enables independent CI/CD deployments across large engineering organizations without full app redeploys.",
        "Risk": "Incompatible dependency versions between Host and Remote (e.g. React 18 vs 17) can trigger hook dispatcher runtime crashes.",
        "Trade": "Grants team deployment autonomy at the expense of significant build configuration complexity and increased runtime debugging difficulty.",
        "Try": "Configure a Module Federation remote entry and verify the Host dynamically fetches remoteEntry.js in the browser network tab.",
        "worked_case": (
            "Walkthrough scenario: An enterprise e-commerce platform has 200 developers. Monolithic builds take 45 minutes, creating a CI bottleneck. "
            "Decomposing into Shell, Product, and Checkout micro-frontends via Module Federation allows Team Checkout to build and deploy its remote "
            "in 2 minutes. When Checkout pushes a critical payment bug fix, users see the updated widget immediately on the next navigation without a shell release."
        ),
        "citations": [
            "https://webpack.js.org/concepts/module-federation/",
            "https://martinfowler.com/articles/micro-frontends.html"
        ],
        "follow_ups": [
            {
                "Q": "What happens if a Host and a Remote declare incompatible versions of React in Module Federation?",
                "A": "If singleton: true is set and versions conflict, the host emits a console warning and picks the highest compatible version, or fails if strictVersion: true is configured."
            }
        ]
    },
    {
        "Q": "How do you diagnose and optimize Largest Contentful Paint (LCP) in modern web applications?",
        "A": (
            "**Direct answer:** **Largest Contentful Paint (LCP)** is a Core Web Vital measuring perceived loading speed. It marks the point in the "
            "page load timeline when the main content of a page (typically a hero image, video poster, or large text heading block) has likely "
            "rendered on screen. A good LCP score is **2.5 seconds or less**.\n\n"
            "LCP time breaks down into four sub-parts:\n"
            "1. **Time to First Byte (TTFB):** Server response latency.\n"
            "2. **Resource Load Delay:** Time between page start and browser discovering the LCP resource.\n"
            "3. **Resource Load Duration:** Time taken to download the LCP resource bytes.\n"
            "4. **Element Render Delay:** Time between resource download completion and visual painting.\n\n"
            "```html\n"
            "<!-- 1. Preload Hero Image to eliminate Resource Load Delay -->\n"
            "<link rel=\"preload\" fetchpriority=\"high\" as=\"image\" href=\"/hero.avif\" type=\"image/avif\">\n"
            "\n"
            "<!-- 2. Optimized Hero Image Markup -->\n"
            "<img\n"
            "    src=\"/hero.avif\"\n"
            "    fetchpriority=\"high\"  <!-- Instructs browser to download image immediately -->\n"
            "    decoding=\"async\"\n"
            "    width=\"1200\"\n"
            "    height=\"600\"\n"
            "    alt=\"Product Hero\"\n"
            ">\n"
            "<!-- CRITICAL RULE: NEVER put loading=\"lazy\" on the LCP image! -->\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **`fetchpriority=\"high\"`:** Boosts the network priority of the image above scripts and non-critical stylesheets.\n"
            "- **Format compression:** Converting PNG/JPEG to modern AVIF or WebP cuts resource load duration by 50–70%.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "The most common engineering mistake is adding `loading=\"lazy\"` to all images via a generic component. Placing `loading=\"lazy\"` "
            "on the LCP hero image forces the browser to wait until layout is calculated before starting the download, adding 1–2 seconds of delay to LCP!"
        ),
        "Why": "Optimizing LCP directly improves user conversion rates and search engine rankings by delivering visible hero content in under 2.5s.",
        "Risk": "Applying loading='lazy' to the LCP hero image delays its network request until after layout, severely degrading LCP scores.",
        "Trade": "Preloading hero assets consumes early bandwidth that could otherwise download scripts; only preload the single true LCP candidate.",
        "Try": "Run Lighthouse in Chrome DevTools on a page with and without fetchpriority='high' on the hero image and compare LCP timings.",
        "worked_case": (
            "Walkthrough scenario: An e-commerce product page has an LCP of 4.8 seconds. DevTools diagnostics reveal the hero image is referenced "
            "in a background CSS url() inside a client bundle and marked loading='lazy'. Removing loading='lazy', adding <link rel=\"preload\" fetchpriority=\"high\">, "
            "and converting the image to AVIF brings LCP down from 4.8s to 1.8s, entering the 'Good' Core Web Vitals threshold."
        ),
        "citations": [
            "https://web.dev/articles/lcp",
            "https://web.dev/articles/optimize-lcp"
        ],
        "follow_ups": [
            {
                "Q": "What is the threshold for a 'Good' Largest Contentful Paint score according to Google?",
                "A": "An LCP of 2.5 seconds or less for at least 75% of page visits measured in the field."
            }
        ]
    },
    {
        "Q": "How does Interaction to Next Paint (INP) measure web responsiveness, and how do you reduce long main-thread tasks?",
        "A": (
            "**Direct answer:** **Interaction to Next Paint (INP)** replaced First Input Delay (FID) as the official Core Web Vital for "
            "measuring page responsiveness. While FID measured only the *first* input delay, INP measures the latency of **all user interactions** "
            "(clicks, taps, key presses) throughout the entire page lifecycle and reports the 98th percentile worst latency. A good INP score is "
            "**200 milliseconds or less**.\n\n"
            "INP latency consists of three phases:\n"
            "1. **Input Delay:** Waiting for background main-thread tasks to finish before the event handler can even start.\n"
            "2. **Processing Time:** Time spent executing the JavaScript event handler code.\n"
            "3. **Presentation Delay:** Time taken by React and the browser to recalculate layout and paint the next visual frame.\n\n"
            "```typescript\n"
            "// 1. Yielding to the Main Thread via scheduler.yield() (modern standard):\n"
            "async function processLargeBatch(items: string[]) {\n"
            "    for (let i = 0; i < items.length; i++) {\n"
            "        heavyCalculation(items[i]);\n"
            "\n"
            "        // Every 50 items, yield control to allow browser to process clicks/paint:\n"
            "        if (i % 50 === 0) {\n"
            "            if ('scheduler' in window && 'yield' in (window as any).scheduler) {\n"
            "                await (window as any).scheduler.yield();\n"
            "            } else {\n"
            "                // Fallback for older browsers:\n"
            "                await new Promise(resolve => setTimeout(resolve, 0));\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "// 2. Offloading to Web Workers (Zero main-thread blocking):\n"
            "// worker.postMessage({ items });\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **Long Tasks:** Any task exceeding 50ms is classified as a Long Task by the browser profiler.\n"
            "- **`scheduler.yield()`:** Unlike `setTimeout(0)` (which puts the task at the end of the entire macrotask queue), `scheduler.yield()` yields to urgent input and paint, and immediately resumes the computation as a continuation task.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Optimizing INP also requires reducing React re-render scope: avoiding massive re-renders across the whole page when an input field "
            "or hover state changes. Use `useTransition` to split urgent visual input updates from non-urgent heavy processing."
        ),
        "Why": "INP reflects real-world user frustration with lagging clicks, dropped keystrokes, and frozen web interfaces.",
        "Risk": "Executing synchronous loops over 50ms locks the main thread, queuing clicks and causing severe INP regressions.",
        "Trade": "Yielding to the main thread slightly increases overall task completion time in exchange for keeping the UI responsive to user input.",
        "Try": "Profile a heavy button click handler in Chrome DevTools Performance panel and identify Long Tasks exceeding 50ms.",
        "worked_case": (
            "Walkthrough scenario: A data table with 10,000 rows sorts rows synchronously on header click, taking 450ms. When users click, "
            "the button freezes in a depressed state and the browser stops responding (INP: 450ms). Refactoring the sorting algorithm into "
            "a Web Worker off the main thread brings main-thread processing time down to 12ms, achieving an INP of 48ms."
        ),
        "citations": [
            "https://web.dev/articles/inp",
            "https://web.dev/articles/optimize-long-tasks"
        ],
        "follow_ups": [
            {
                "Q": "Why is scheduler.yield() superior to setTimeout(0) for breaking up long tasks?",
                "A": "scheduler.yield() yields to allow input handling and paints, then resumes the task immediately without being demoted behind unrelated macrotasks."
            }
        ]
    },
    {
        "Q": "What causes Cumulative Layout Shift (CLS), and what engineering practices guarantee visual layout stability?",
        "A": (
            "**Direct answer:** **Cumulative Layout Shift (CLS)** is the Core Web Vital that measures visual stability. It quantifies unexpected "
            "layout shifts where visible page elements move position from one rendered frame to the next without user interaction (e.g., text jumping "
            "downward just as a user attempts to tap a button, causing them to click an ad instead). A good CLS score is **0.1 or less**.\n\n"
            "Primary causes of CLS and their engineering remedies:\n"
            "1. **Images & Videos without dimensions:** Always specify explicit `width` and `height` attributes or CSS `aspect-ratio` on `<img>` and `<video>` tags so the browser reserves the exact layout space before bytes download.\n"
            "2. **Dynamic ads, embeds, and iframes:** Reserve slot dimensions using min-height containers before ad scripts inject.\n"
            "3. **Web Fonts causing FOIT/FOUT:** When custom web fonts load, the text reflows if the fallback system font has different metrics. Use `font-display: optional` or CSS `@font-face` metric overrides (`size-adjust`, `ascent-override`, `descent-override`) to match fallback dimensions.\n\n"
            "```html\n"
            "<!-- 1. Explicit Aspect Ratio on Responsive Images (ZERO CLS) -->\n"
            "<img\n"
            "    src=\"/product.webp\"\n"
            "    width=\"800\"\n"
            "    height=\"450\"\n"
            "    style=\"width: 100%; height: auto; aspect-ratio: 16 / 9;\"\n"
            "    alt=\"Product preview\">\n"
            "\n"
            "<!-- 2. Reserved Container for Dynamic Banner / Ad -->\n"
            "<div style=\"min-height: 250px; background: #f0f0f0;\">\n"
            "    <!-- Dynamic banner injects here without pushing content down -->\n"
            "    <DynamicBanner />\n"
            "</div>\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **CLS formula:** $\text{Layout Shift Score} = \text{Impact Fraction} \times \text{Distance Fraction}$.\n"
            "- **User exclusion:** Layout shifts that occur within 500ms of a direct user interaction (like clicking an accordion) are excluded from the CLS score.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Injecting non-sticky banner alerts or cookie consent banners at the top of the DOM after page load causes 100% of the entire page content "
            "to shift downward, producing massive CLS penalties. Always render cookie banners with `position: fixed` or `position: sticky`."
        ),
        "Why": "Eliminating CLS prevents accidental clicks, improves user trust, and achieves optimal Google search ranking criteria.",
        "Risk": "Injecting dynamic content above the fold pushes text downward, causing users to misclick destructive buttons.",
        "Trade": "Reserving layout space for dynamic ads can leave temporary blank boxes while advertisements load.",
        "Try": "Inspect the Layout Shifts track in Chrome DevTools Performance panel to pinpoint the exact DOM element triggering shifts.",
        "worked_case": (
            "Walkthrough scenario: A news article displays a 300x250 ad banner between paragraphs without a reserved container. "
            "When the ad script loads 1.5 seconds later, the entire article text jumps downward by 250px, producing a poor CLS of 0.35. "
            "Adding style=\"min-height: 250px\" to the ad wrapper reserves the exact space on initial paint, dropping CLS to 0.00."
        ),
        "citations": [
            "https://web.dev/articles/cls",
            "https://web.dev/articles/optimize-cls"
        ],
        "follow_ups": [
            {
                "Q": "How does CSS aspect-ratio solve layout shift for responsive images?",
                "A": "aspect-ratio allows the browser to calculate the container's height immediately based on its width, reserving layout space before image bytes download."
            }
        ]
    },
    {
        "Q": "How does list virtualization (windowing) render thousands of dynamic items smoothly at 60fps?",
        "A": (
            "**Direct answer:** In web browsers, maintaining thousands of DOM nodes consumes vast amounts of memory, slows style recalculation, "
            "and causes severe layout thrashing. **List Virtualization (Windowing)** renders *only the visible items* currently within the "
            "viewport (plus a small overscan buffer above and below). As the user scrolls, virtualization libraries (like `react-window` or "
            "`@tanstack/react-virtual`) dynamically recycle and swap out off-screen DOM nodes while maintaining an outer container with the "
            "correct total scroll height.\n\n"
            "```tsx\n"
            "import { useRef } from 'react';\n"
            "import { useVirtualizer } from '@tanstack/react-virtual';\n"
            "\n"
            "export function VirtualList({ items }: { items: string[] }) {\n"
            "    const parentRef = useRef<HTMLDivElement>(null);\n"
            "\n"
            "    const virtualizer = useVirtualizer({\n"
            "        count: items.length, // e.g. 100,000 items!\n"
            "        getScrollElement: () => parentRef.current,\n"
            "        estimateSize: () => 50, // estimated row height in px\n"
            "        overscan: 5 // render 5 extra rows above/below to prevent blank flashes\n"
            "    });\n"
            "\n"
            "    return (\n"
            "        <div ref={parentRef} style={{ height: '500px', overflowY: 'auto' }}>\n"
            "            {/* Total height container maintains correct scrollbar position */}\n"
            "            <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>\n"
            "                {virtualizer.getVirtualItems().map(virtualRow => (\n"
            "                    <div\n"
            "                        key={virtualRow.index}\n"
            "                        style={{\n"
            "                            position: 'absolute',\n"
            "                            top: 0,\n"
            "                            left: 0,\n"
            "                            width: '100%',\n"
            "                            height: `${virtualRow.size}px`,\n"
            "                            transform: `translateY(${virtualRow.start}px)`\n"
            "                        }}>\n"
            "                        {items[virtualRow.index]}\n"
            "                    </div>\n"
            "                ))}\n"
            "            </div>\n"
            "        </div>\n"
            "    );\n"
            "}\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **DOM Node Count:** Bounded to $O(V)$ where $V$ is visible rows (~20–30 nodes), completely independent of total dataset size (e.g. 500,000 items).\n"
            "- **Memory usage:** Drops DOM tree memory from gigabytes to megabytes, sustaining 60fps scrolling.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "For items with dynamic, unpredictable heights (e.g. expandable cards), use a `ResizeObserver` inside the row item that reports "
            "measured heights back to the virtualizer (`virtualizer.measureElement`), dynamically recalculating offset positions on the fly."
        ),
        "Why": "Virtualization allows rendering datasets with hundreds of thousands of items with zero DOM performance degradation.",
        "Risk": "Virtualization breaks browser native text search (Cmd+F / Ctrl+F) because off-screen text is not present in the DOM tree.",
        "Trade": "Dramatically improves memory and scroll FPS at the cost of breaking native browser Ctrl+F find-in-page search.",
        "Try": "Render 20,000 unvirtualized div rows in a list and observe memory usage and scrolling frame rate collapse.",
        "worked_case": (
            "Walkthrough scenario: A financial log viewer renders 50,000 server log events. Rendering all 50,000 rows creates 250,000 DOM nodes, "
            "freezing the browser for 8 seconds and consuming 1.2GB of RAM. Implementing @tanstack/react-virtual reduces active DOM elements to 25, "
            "reducing initial render time to 40ms and memory consumption to 35MB with fluid 60fps scrolling."
        ),
        "citations": [
            "https://tanstack.com/virtual/latest",
            "https://github.com/bvaughn/react-window"
        ],
        "follow_ups": [
            {
                "Q": "What is the purpose of the overscan parameter in list virtualizers?",
                "A": "Overscan renders a small number of buffer items just outside the visible viewport, preventing users from seeing blank flashes during fast flick scrolling."
            }
        ]
    },
    {
        "Q": "How do code splitting, dynamic imports, and route-based chunking reduce initial JavaScript bundle size?",
        "A": (
            "**Direct answer:** In traditional single-page applications, all JavaScript across all routes and features is bundled into a single "
            "monolithic `main.js` file (often 2–5MB). Users on the login page are forced to download code for the admin dashboard, charting libraries, "
            "and checkout flows before seeing the page. **Code Splitting** breaks this monolith into smaller, on-demand chunks using ECMAScript "
            "dynamic `import('./Module')` syntax, which instructs bundlers (Webpack, Vite, Rollup) to emit separate chunk files downloaded "
            "only when the user navigates to that specific route or triggers that feature.\n\n"
            "```tsx\n"
            "import React, { Suspense, lazy } from 'react';\n"
            "import { BrowserRouter, Routes, Route } from 'react-router-dom';\n"
            "\n"
            "// 1. Route-based chunk splitting via React.lazy and dynamic import:\n"
            "const HomePage = lazy(() => import('./routes/HomePage'));\n"
            "const AdminDashboard = lazy(() => import('./routes/AdminDashboard')); // 500KB chunk only loaded by admins!\n"
            "const SettingsPage = lazy(() => import('./routes/SettingsPage'));\n"
            "\n"
            "export function AppRoutes() {\n"
            "    return (\n"
            "        <BrowserRouter>\n"
            "            <Suspense fallback={<div className=\"route-spinner\">Loading page...</div>}>\n"
            "                <Routes>\n"
            "                    <Route path=\"/\" element={<HomePage />} />\n"
            "                    <Route path=\"/admin\" element={<AdminDashboard />} />\n"
            "                    <Route path=\"/settings\" element={<SettingsPage />} />\n"
            "                </Routes>\n"
            "            </Suspense>\n"
            "        </BrowserRouter>\n"
            "    );\n"
            "}\n"
            "\n"
            "// 2. Feature-level code splitting on user interaction:\n"
            "function ExportButton({ data }: { data: any }) {\n"
            "    const handleExport = async () => {\n"
            "        // Download 200KB xlsx library only when user clicks export!\n"
            "        const { utils, writeFile } = await import('xlsx');\n"
            "        const ws = utils.json_to_sheet(data);\n"
            "        const wb = utils.book_new();\n"
            "        utils.book_append_sheet(wb, ws, 'Data');\n"
            "        writeFile(wb, 'export.xlsx');\n"
            "    };\n"
            "    return <button onClick={handleExport}>Export to Excel</button>;\n"
            "}\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **Initial load reduction:** Slashes initial JavaScript payload by 60–80%, directly improving Time to Interactive (TTI) and First Contentful Paint (FCP).\n"
            "- **Network prefetching:** Modern routers prefetch lazy chunks on link hover (`<Link onMouseEnter={preloadRoute}>`), eliminating navigation delay.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "When deploying new versions to production with hashed filenames (`admin.8f3a.js` replaced by `admin.9b2c.js`), users on an open tab "
            "attempting to navigate to `/admin` can experience chunk load failures (HTTP 404). Handle chunk loading errors with an Error Boundary "
            "that executes `window.location.reload()` to fetch the updated asset manifest."
        ),
        "Why": "Route-based code splitting ensures users only download the exact JavaScript needed for the screen they are viewing.",
        "Risk": "Deploying new builds can invalidate old hashed chunk URLs, causing lazy route navigations to fail with chunk load errors.",
        "Trade": "Introduces minor latency during route transitions unless paired with intelligent link prefetching.",
        "Try": "Run Vite build or Webpack analyzer and observe how dynamic import() splits single output bundles into multiple numbered chunks.",
        "worked_case": (
            "Walkthrough scenario: A SaaS app's initial bundle is 3.8MB due to an integrated PDF generator and admin analytics panel. "
            "Splitting admin routes into separate chunks and lazy-loading the PDF generator with import('jspdf') on button click "
            "drops the initial landing page bundle to 180KB, reducing mobile load time from 6.2s to 0.9s."
        ),
        "citations": [
            "https://react.dev/reference/react/lazy",
            "https://web.dev/articles/reduce-javascript-payloads-with-code-splitting"
        ],
        "follow_ups": [
            {
                "Q": "How do you prefetch a lazy-loaded route chunk before the user clicks the navigation link?",
                "A": "Trigger the dynamic import function inside an onMouseEnter or onFocus event on the link: const Component = lazy(...); <Link onMouseEnter={() => import('./route')} />."
            }
        ]
    },
    {
        "Q": "How does JavaScript tree shaking work under ES modules, and why do package sideEffects flags matter?",
        "A": (
            "**Direct answer:** **Tree Shaking** is a dead-code elimination optimization performed by modern bundlers (Webpack, Rollup, esbuild) "
            "that removes unused exports from the final production bundle. Tree shaking relies on the static structure of **ES Modules (ESM)** "
            "(`import` and `export` statements must appear at the top level and cannot be dynamic), enabling the compiler to construct a complete "
            "dependency graph and eliminate unused functions.\n\n"
            "The **`\"sideEffects\"`** property in a package's `package.json` is the single most critical flag for effective tree shaking. "
            "By default, bundlers must assume that imported files might execute global side effects (modifying prototypes, setting global variables, "
            "injecting polyfills) when evaluated. Setting `\"sideEffects\": false` informs the bundler that no files in the package contain "
            "side effects, allowing the bundler to safely drop entirely unused imported modules.\n\n"
            "```json\n"
            "// package.json for an enterprise utility library:\n"
            "{\n"
            "  \"name\": \"my-enterprise-utils\",\n"
            "  \"version\": \"1.0.0\",\n"
            "  \"sideEffects\": [\n"
            "    \"*.css\",\n"
            "    \"./src/polyfills.js\"\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "```typescript\n"
            "// In application code:\n"
            "import { formatDate } from 'my-enterprise-utils';\n"
            "// If sideEffects: false, the other 50 functions in my-enterprise-utils are completely omitted from bundle!\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **CommonJS vs ESM:** CommonJS (`require()`, `module.exports`) cannot be reliably tree-shaken because `require()` is dynamic and can be called inside `if` statements.\n"
            "- **Pure annotations:** `/*#__PURE__*/` comments tell the minifier that a top-level function invocation (e.g. `const StyledDiv = /*#__PURE__*/ styled('div')`) has no side effects and can be dropped if unused.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Importing barrel files (`import { x } from './components'`) where `components/index.ts` exports 500 components frequently defeats tree "
            "shaking unless `sideEffects: false` is configured, because the bundler evaluates all 500 module exports."
        ),
        "Why": "Tree shaking eliminates dead, unused library code, shrinking production bundles by hundreds of kilobytes.",
        "Risk": "Omitting sideEffects: false causes bundlers to bundle entire libraries even if you only use a single utility function.",
        "Trade": "Accidentally marking a package with sideEffects: false can strip necessary CSS imports or global polyfills from the build.",
        "Try": "Import a single function from lodash-es vs legacy lodash in a Vite project and compare resulting bundle sizes in build output.",
        "worked_case": (
            "Walkthrough scenario: A developer imports import { debounce } from 'lodash'. The legacy lodash package uses CommonJS and lacks sideEffects flags, "
            "forcing Webpack to bundle all 300KB of lodash into the bundle. Switching to import { debounce } from 'lodash-es' with sideEffects: false "
            "allows Rollup to tree-shake away 295KB, bundling only the 5KB debounce function and its immediate dependencies."
        ),
        "citations": [
            "https://webpack.js.org/guides/tree-shaking/",
            "https://web.dev/articles/reduce-javascript-payloads-with-tree-shaking"
        ],
        "follow_ups": [
            {
                "Q": "Why must CSS files be exempted in the sideEffects array (e.g. sideEffects: ['*.css'])?",
                "A": "CSS imports (import './styles.css') have no exported JavaScript identifiers; if sideEffects: false is unexempted, the bundler considers the CSS file unused and drops it entirely."
            }
        ]
    },
    {
        "Q": "How do you implement a progressive web app (PWA) with Service Worker caching strategies (Cache-First vs Network-First)?",
        "A": (
            "**Direct answer:** A Progressive Web App (PWA) uses a **Service Worker**—a programmable network proxy running in a background "
            "thread independent of the web page—to intercept outgoing HTTP requests and manage local storage via the `CacheStorage` API. "
            "Production PWAs combine two primary caching strategies based on asset mutability:\n"
            "1. **Cache-First (Fastest, for Static Assets):** Checks `CacheStorage` first. If present, returns cached asset in 0ms. If not, fetches from network, populates cache, and returns. Used for content-hashed assets (images, fonts, hashed JS/CSS bundles).\n"
            "2. **Network-First (Freshest, for Dynamic HTML/API):** Attempts network fetch first. If successful, updates the cache. If offline or network fails, falls back to the latest cached copy. Used for HTML documents and API endpoints.\n\n"
            "```javascript\n"
            "// service-worker.js\n"
            "const CACHE_NAME = 'app-v1';\n"
            "const STATIC_ASSETS = ['/', '/index.html', '/style.css', '/app.js'];\n"
            "\n"
            "// 1. Install Event: Pre-cache core app shell\n"
            "self.addEventListener('install', (event) => {\n"
            "    event.waitUntil(\n"
            "        caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))\n"
            "    );\n"
            "    self.skipWaiting(); // Activate immediately\n"
            "});\n"
            "\n"
            "// 2. Fetch Event: Intercept network traffic\n"
            "self.addEventListener('fetch', (event) => {\n"
            "    const url = new URL(event.request.url);\n"
            "\n"
            "    // Cache-First for static assets:\n"
            "    if (url.pathname.match(/\\.(js|css|png|jpg|svg|woff2)$/)) {\n"
            "        event.respondWith(\n"
            "            caches.match(event.request).then(cached => cached || fetch(event.request))\n"
            "        );\n"
            "        return;\n"
            "    }\n"
            "\n"
            "    // Network-First for HTML and API routes:\n"
            "    event.respondWith(\n"
            "        fetch(event.request)\n"
            "            .then(networkRes => {\n"
            "                const resClone = networkRes.clone();\n"
            "                caches.open(CACHE_NAME).then(cache => cache.put(event.request, resClone));\n"
            "                return networkRes;\n"
            "            })\n"
            "            .catch(() => caches.match(event.request)) // Offline fallback!\n"
            "    );\n"
            "});\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **Lifecycle stages:** `install` -> `activate` (cleans up old cache buckets) -> `fetch`.\n"
            "- **Cloning required:** A `Response` body can only be read once; `networkRes.clone()` is mandatory before saving to cache.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Never cache Service Worker files (`service-worker.js`) in HTTP caches (`Cache-Control: no-cache, no-store`). If the service worker file "
            "is cached by the browser, you will be unable to deploy updates to users."
        ),
        "Why": "Service Workers grant complete control over network offline caching, making web apps load instantaneously even on flaky networks.",
        "Risk": "Serving index.html Cache-First can permanently lock users into an outdated app shell that never updates.",
        "Trade": "Delivers full offline capability at the cost of managing background worker update lifecycles and cache invalidations.",
        "Try": "Register a Service Worker, go offline in Chrome DevTools Network panel, reload the page, and verify it renders from CacheStorage.",
        "worked_case": (
            "Walkthrough scenario: A field sales rep enters an underground parking garage with zero cell reception. The rep opens the PWA. "
            "The Service Worker intercepts the navigation request, detects network failure, and returns the pre-cached app shell and latest "
            "cached customer catalog from CacheStorage. The rep completes orders offline, which queue in IndexedDB for syncing upon exit."
        ),
        "citations": [
            "https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API",
            "https://web.dev/explore/progressive-web-apps"
        ],
        "follow_ups": [
            {
                "Q": "What happens if you do not call networkRes.clone() before passing it to cache.put()?",
                "A": "The browser throws a TypeError: Response body already consumed when returning the response to the web page, breaking the render."
            }
        ]
    },
    {
        "Q": "How do you design a scalable Design System with design tokens, headless component primitives, and theme switching?",
        "A": (
            "**Direct answer:** A scalable enterprise Design System decouples visual design decisions from technical component behavior. "
            "It consists of three architectural tiers:\n"
            "1. **Design Tokens:** The single source of truth for raw visual values (colors, spacing, typography, elevation, border-radii) exported from design tools (Figma) as JSON and compiled into **CSS Custom Properties** (variables). Theming is implemented by swapping CSS variable values at the `:root` or `[data-theme]` level.\n"
            "2. **Headless Component Primitives:** Unstyled, fully accessible behavioral components (e.g. Radix UI, React Aria, Headless UI) that manage complex ARIA attributes, keyboard navigation (roving tabindex, arrow keys), focus traps, and modal lifecycles with zero CSS styling.\n"
            "3. **Styled Domain Components:** The union of headless behavior and design token styling (e.g. `<Button>`, `<Select>`, `<Dialog>`), styled via Tailwind CSS, CSS Modules, or vanilla CSS variables.\n\n"
            "```css\n"
            "/* 1. Design Tokens as CSS Variables */\n"
            ":root {\n"
            "    --color-bg-primary: #ffffff;\n"
            "    --color-text-primary: #111827;\n"
            "    --color-accent: #2563eb;\n"
            "}\n"
            "[data-theme=\"dark\"] {\n"
            "    --color-bg-primary: #0f172a;\n"
            "    --color-text-primary: #f8fafc;\n"
            "    --color-accent: #38bdf8;\n"
            "}\n"
            "```\n\n"
            "```tsx\n"
            "// 2. Combining Headless Radix Dialog with Design Tokens:\n"
            "import * as Dialog from '@radix-ui/react-dialog';\n"
            "\n"
            "export function AccessibleModal({ title, children }: { title: string; children: React.ReactNode }) {\n"
            "    return (\n"
            "        <Dialog.Root>\n"
            "            <Dialog.Trigger className=\"btn-primary\">Open Dialog</Dialog.Trigger>\n"
            "            <Dialog.Portal>\n"
            "                <Dialog.Overlay className=\"modal-overlay\" />\n"
            "                <Dialog.Content className=\"modal-content\">\n"
            "                    <Dialog.Title>{title}</Dialog.Title>\n"
            "                    {children}\n"
            "                    <Dialog.Close className=\"btn-close\">Close</Dialog.Close>\n"
            "                </Dialog.Content>\n"
            "            </Dialog.Portal>\n"
            "        </Dialog.Root>\n"
            "    );\n"
            "}\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **Theme switching performance:** Toggling `document.documentElement.setAttribute('data-theme', 'dark')` recalculates styles in 0ms without re-rendering React component trees.\n"
            "- **Accessibility (a11y):** Headless primitives guarantee WCAG 2.1 AA compliance out of the box without manual keyboard event handling.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Prevent dark mode flashing on initial page load by embedding a tiny synchronous inline `<script>` in the document `<head>` that reads "
            "`localStorage.getItem('theme')` and sets `data-theme` on `<html>` *before* CSS renders."
        ),
        "Why": "Headless primitives guarantee bulletproof accessibility while design tokens enable instantaneous runtime theme switching.",
        "Risk": "Writing custom modal keyboard focus traps from scratch usually misses edge cases, trapping screen reader users in infinite focus loops.",
        "Trade": "Adopting headless libraries adds an external dependency compared to writing raw unstyled HTML elements.",
        "Try": "Toggle data-theme='dark' on document.documentElement and observe all CSS variable colors transition instantly.",
        "worked_case": (
            "Walkthrough scenario: An enterprise company rebrands 8 separate web products. Previously, rebranding required updating 400 CSS files "
            "across 8 codebases, taking 4 months. Because products share a Design Token pipeline, designers updated colors in Figma. "
            "Tokens compiled to updated JSON, CI regenerated the CSS Custom Properties, and all 8 products rebranded in a single afternoon."
        ),
        "citations": [
            "https://www.radix-ui.com/primitives",
            "https://m3.material.io/foundations/design-tokens/overview"
        ],
        "follow_ups": [
            {
                "Q": "How do you prevent theme flashing (FOUC) when loading dark mode in SSR applications?",
                "A": "Execute an inline blocking script in the HTML <head> that reads localStorage or prefers-color-scheme and applies the dark attribute before the body paints."
            }
        ]
    },
    {
        "Q": "How do browser resource hints (preload, prefetch, preconnect, dns-prefetch) optimize critical rendering paths?",
        "A": (
            "**Direct answer:** Browser Resource Hints provide declarative directives informing the browser's preload scanner about external resources "
            "and network connections before they are encountered in the document body:\n"
            "1. **`dns-prefetch`:** Resolves DNS lookup for a cross-origin domain in the background (`<link rel=\"dns-prefetch\" href=\"https://api.com\">`), saving 50–100ms.\n"
            "2. **`preconnect`:** Performs DNS resolution, TCP handshake, and TLS negotiation ahead of time (`<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>`), saving 100–300ms on initial API or font connections.\n"
            "3. **`preload`:** Instructs the browser to download a high-priority critical resource needed for the **current page** immediately (`<link rel=\"preload\" as=\"font\" href=\"/font.woff2\" crossorigin>`).\n"
            "4. **`prefetch`:** Downloads a low-priority resource needed for **future navigations** in the background during browser idle time (`<link rel=\"prefetch\" href=\"/dashboard-chunk.js\">`).\n\n"
            "```html\n"
            "<!-- 1. Warm up TLS connection to external API domain -->\n"
            "<link rel=\"preconnect\" href=\"https://api.enterprise.com\">\n"
            "\n"
            "<!-- 2. Preload critical web font (MANDATORY: crossorigin for fonts!) -->\n"
            "<link rel=\"preload\" href=\"/fonts/inter.woff2\" as=\"font\" type=\"font/woff2\" crossorigin>\n"
            "\n"
            "<!-- 3. Preload LCP hero image with high fetch priority -->\n"
            "<link rel=\"preload\" href=\"/hero.avif\" as=\"image\" type=\"image/avif\" fetchpriority=\"high\">\n"
            "\n"
            "<!-- 4. Prefetch next likely page chunk during idle time -->\n"
            "<link rel=\"prefetch\" href=\"/settings-page.js\">\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **`crossorigin` attribute on fonts:** Fonts must be fetched anonymously according to web standards. Omitting `crossorigin` on a font `<link rel=\"preload\">` causes the browser to download the font **twice** (once without credentials, and again with credentials)!\n"
            "- **Unused preload warning:** If a preloaded resource is not used within 3 seconds of load, Chrome logs a console warning: *The resource was preloaded using link preload but not used within a few seconds*.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Do not preload everything. Overusing `preload` saturates network bandwidth and starves critical CSS and JavaScript bundles, "
            "ironically worsening First Contentful Paint. Reserve `preload` strictly for 1 font, 1 LCP image, or critical route bundles."
        ),
        "Why": "Resource hints eliminate connection handshakes and pre-warm assets before the browser discovery parser finds them in CSS or JS.",
        "Risk": "Omitting crossorigin on font preloads causes the browser to download the exact same font file twice.",
        "Trade": "Preloading consumes upfront bandwidth; prefetching future pages consumes mobile data for pages the user may never visit.",
        "Try": "Preload a font without crossorigin and inspect DevTools Network tab to observe the duplicate download.",
        "worked_case": (
            "Walkthrough scenario: An application uses Google Fonts. By default, the browser downloads the CSS, parses it, finds the font URL, "
            "resolves DNS, completes TLS handshake, and downloads the font (400ms delay causing FOUT). Adding <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin> "
            "negotiates the TLS connection in parallel with initial HTML streaming, reducing font load latency from 400ms to 80ms."
        ),
        "citations": [
            "https://web.dev/articles/preconnect-and-dns-prefetch",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/preload"
        ],
        "follow_ups": [
            {
                "Q": "Why does Chrome emit a warning if a preloaded resource is not used within 3 seconds?",
                "A": "Preload is intended exclusively for immediate current-page critical assets; unused preloads indicate wasted bandwidth that delayed other critical resources."
            }
        ]
    },
    {
        "Q": "How do modern image optimization techniques (srcset, sizes, AVIF, WebP, aspect-ratio, lazy loading) minimize load times?",
        "A": (
            "**Direct answer:** Images account for over 50% of total web page weight. Modern frontend engineering applies a five-part optimization "
            "strategy to deliver crisp visual assets with minimal byte transfer:\n"
            "1. **Modern Formats (AVIF & WebP):** AVIF offers ~50% better compression than JPEG; WebP offers ~30%. Use the HTML `<picture>` element to serve AVIF with WebP and JPEG fallbacks.\n"
            "2. **Responsive Resolutions (`srcset` and `sizes`):** Serve smaller image files to mobile screens and larger files to 4K desktops based on viewport width.\n"
            "3. **Native Lazy Loading (`loading=\"lazy\"`):** Defers image downloading until the element is within a threshold distance of the viewport.\n"
            "4. **Layout Reservation (`aspect-ratio`):** Prevents Cumulative Layout Shift by enforcing container proportions.\n"
            "5. **Asynchronous Decoding (`decoding=\"async\"`):** Moves image byte decompression off the browser's main thread to prevent scrolling hitch.\n\n"
            "```html\n"
            "<picture>\n"
            "    <!-- Next-gen format: AVIF (Smallest bytes) -->\n"
            "    <source type=\"image/avif\" srcset=\"/hero-400.avif 400w, /hero-800.avif 800w, /hero-1200.avif 1200w\">\n"
            "    <!-- Modern fallback: WebP -->\n"
            "    <source type=\"image/webp\" srcset=\"/hero-400.webp 400w, /hero-800.webp 800w, /hero-1200.webp 1200w\">\n"
            "    <!-- Fallback image tag with responsive sizes and layout reservation -->\n"
            "    <img\n"
            "        src=\"/hero-800.jpg\"\n"
            "        srcset=\"/hero-400.jpg 400w, /hero-800.jpg 800w, /hero-1200.jpg 1200w\"\n"
            "        sizes=\"(max-width: 768px) 100vw, 800px\"\n"
            "        width=\"800\"\n"
            "        height=\"450\"\n"
            "        style=\"width: 100%; height: auto; aspect-ratio: 16 / 9;\"\n"
            "        loading=\"lazy\"\n"
            "        decoding=\"async\"\n"
            "        alt=\"Product Overview\">\n"
            "</picture>\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **`sizes` attribute:** Tells the browser's preload scanner how wide the image will render *before CSS styles are parsed*, allowing it to pick the optimal `srcset` candidate immediately.\n"
            "- **Bandwidth reduction:** Combining AVIF + responsive widths reduces mobile image downloads from 2MB to ~70KB.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Never apply `loading=\"lazy\"` to above-the-fold hero images or LCP elements. Lazy loading delays image discovery until layout completes, "
            "severely damaging Largest Contentful Paint."
        ),
        "Why": "AVIF compression and responsive srcset cut page transfer weight by up to 80% without sacrificing visual sharpness.",
        "Risk": "Omitting sizes when using srcset causes browsers to assume 100vw width, downloading oversized desktop images on mobile screens.",
        "Trade": "Generating multiple image formats and resolutions requires an automated image CDN or build-time asset processing pipeline.",
        "Try": "Inspect Network tab on mobile emulation vs desktop for a picture element and observe different srcset candidate selection.",
        "worked_case": (
            "Walkthrough scenario: An e-commerce product catalog page loads 24 product cards. Originally, it downloaded 24 uncompressed 1MB JPEGs (24MB total). "
            "Implementing AVIF compression, responsive srcset (300px on mobile), and loading=\"lazy\" on cards below the fold reduced total page transfer "
            "to 480KB. Page load time dropped from 8.5s to 1.1s on cellular networks."
        ),
        "citations": [
            "https://web.dev/articles/serve-images-webp",
            "https://developer.mozilla.org/en-US/docs/Learn/HTML/Multimedia_and_embedding/Responsive_images"
        ],
        "follow_ups": [
            {
                "Q": "What does decoding='async' do on an HTML image tag?",
                "A": "It instructs the browser to decompress and decode image raster bytes on a background thread, preventing frame drops and main-thread scrolling jank."
            }
        ]
    },
    {
        "Q": "How do you design client-side error telemetry, performance monitoring (RUM), and distributed trace propagation?",
        "A": (
            "**Direct answer:** Real User Monitoring (RUM) and client observability capture real-world user performance and production errors "
            "without degrading the application's runtime. A production telemetry architecture consists of three pillars:\n"
            "1. **Error Telemetry:** Centralized capture via `window.onerror`, `window.onunhandledrejection`, and React Error Boundaries, sanitizing PII before batching.\n"
            "2. **Performance Instrumentation:** Measuring Core Web Vitals via `web-vitals` library and `PerformanceObserver` API (reporting LCP, INP, CLS, TTFB).\n"
            "3. **Distributed Trace Propagation:** Injecting W3C Trace Context headers (`traceparent`, `tracestate`) into outgoing `fetch` calls so backend microservices can trace a database query back to the initiating frontend click.\n\n"
            "```typescript\n"
            "// 1. W3C Distributed Trace Injection in API Client:\n"
            "export function createTraceparent(): string {\n"
            "    const version = '00';\n"
            "    const traceId = crypto.randomUUID().replace(/-/g, '');\n"
            "    const spanId = crypto.randomUUID().replace(/-/g, '').slice(0, 16);\n"
            "    const flags = '01'; // Sampled\n"
            "    return `${version}-${traceId}-${spanId}-${flags}`;\n"
            "}\n"
            "\n"
            "export async function telemetryFetch(url: string, init?: RequestInit) {\n"
            "    const traceparent = createTraceparent();\n"
            "    return fetch(url, {\n"
            "        ...init,\n"
            "        headers: { ...init?.headers, 'traceparent': traceparent }\n"
            "    });\n"
            "}\n"
            "\n"
            "// 2. Reliable Beaconing on Page Unload:\n"
            "export function sendTelemetry(endpoint: string, payload: any) {\n"
            "    const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });\n"
            "    // navigator.sendBeacon guarantees transmission even if tab is closing!\n"
            "    if (navigator.sendBeacon) {\n"
            "        navigator.sendBeacon(endpoint, blob);\n"
            "    } else {\n"
            "        fetch(endpoint, { method: 'POST', body: blob, keepalive: true });\n"
            "    }\n"
            "}\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **`navigator.sendBeacon`:** Standard fetch requests are cancelled when a tab closes. `sendBeacon()` queues data in the browser process itself, guaranteeing transmission with zero unmount delay.\n"
            "- **PII sanitization:** Error stack traces and URLs must strip auth tokens, query parameters (`?token=...`), and credit card numbers before transmission.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Sample telemetry at high traffic volumes (e.g. log 100% of errors, but sample only 5% of successful performance events) to prevent "
            "overwhelming telemetry ingest collectors."
        ),
        "Why": "Distributed tracing and beaconing connect frontend user actions directly to backend microservice logs without dropping unload events.",
        "Risk": "Sending telemetry using standard synchronous XHR during page unload freezes the browser and delays tab closing.",
        "Trade": "sendBeacon payloads are restricted in size (typically 64KB max) and cannot receive server responses.",
        "Try": "Send an event with navigator.sendBeacon in a beforeunload listener, close the tab, and verify the network request reached the server.",
        "worked_case": (
            "Walkthrough scenario: A customer reports an order failed. The support engineer searches the customer's trace ID. "
            "The traceparent header links the frontend button click directly to the backend API gateway, payment service, and database lock timeout, "
            "pinpointing the exact failure within 60 seconds without reproducing on local machines."
        ),
        "citations": [
            "https://www.w3.org/TR/trace-context/",
            "https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon"
        ],
        "follow_ups": [
            {
                "Q": "Why is keepalive: true used in fetch when sendBeacon is unsupported?",
                "A": "keepalive: true allows a fetch request to outlive the document that initiated it, ensuring data is sent even if the tab closes."
            }
        ]
    },
    {
        "Q": "How do web workers offload heavy computational tasks (e.g., encryption, large data parsing) from the main thread?",
        "A": (
            "**Direct answer:** JavaScript in web browsers executes in a single-threaded event loop shared by DOM manipulation, style layout, "
            "user input events, and script execution. Running a heavy computational task (e.g. parsing 50MB of CSV data, image manipulation, "
            "crypto hashing, or sorting 100,000 objects) on the main thread freezes the entire browser tab, dropping animation frames and causing "
            "severe INP penalties. **Web Workers** run scripts in a completely separate OS background thread, communicating with the main thread "
            "via message passing without touching or blocking the DOM.\n\n"
            "```typescript\n"
            "// 1. parser.worker.ts (Background Thread - Zero DOM Access)\n"
            "self.onmessage = (event: MessageEvent<{ rawCSV: string }>) => {\n"
            "    const rows = event.data.rawCSV.split('\\n').map(line => line.split(','));\n"
            "    // Perform heavy data transformations, regex parsing, sorting...\n"
            "    const parsedData = rows.map(r => ({ id: r[0], val: parseFloat(r[1]) }));\n"
            "    self.postMessage({ result: parsedData });\n"
            "};\n"
            "\n"
            "// 2. main.ts (Main UI Thread)\n"
            "const worker = new Worker(new URL('./parser.worker.ts', import.meta.url), { type: 'module' });\n"
            "\n"
            "export function parseLargeDataset(rawCSV: string): Promise<any[]> {\n"
            "    return new Promise((resolve) => {\n"
            "        worker.onmessage = (event) => resolve(event.data.result);\n"
            "        worker.postMessage({ rawCSV }); // Dispatched to worker thread!\n"
            "    });\n"
            "}\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **Thread isolation:** Web Workers have no access to `window`, `document`, or DOM nodes; they have their own `self`, `fetch`, `IndexedDB`, and `crypto`.\n"
            "- **Transferable Objects:** Large binary data (`ArrayBuffer`, `ImageBitmap`) can be transferred rather than copied using `postMessage(buffer, [buffer])`, achieving zero-copy 0ms transfer time.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Copying massive JSON objects across `postMessage` incurs structured clone serialization serialization cost. For multi-megabyte payloads, "
            "convert data into typed arrays (`Uint8Array`) and pass them as **Transferable Objects** to avoid cloning latency."
        ),
        "Why": "Web Workers keep the main thread completely free of computational strain, sustaining smooth 60fps animations.",
        "Risk": "Structured cloning of massive objects across postMessage can itself take tens of milliseconds; use Transferable Objects for large binaries.",
        "Trade": "Web Workers cannot touch the DOM directly and communicate strictly through asynchronous message passing.",
        "Try": "Run a 2-second while(true) loop on the main thread (page freezes) vs inside a Web Worker (page stays 100% responsive).",
        "worked_case": (
            "Walkthrough scenario: A web spreadsheet application recalculates 50,000 financial formulas on every cell edit. "
            "Executing calculations on the main thread freezes typing for 600ms on every keystroke. Moving formula calculation to a Web Worker "
            "allows the user to continue typing smoothly at 60fps while formula results stream back asynchronously in the background."
        ),
        "citations": [
            "https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers",
            "https://developer.mozilla.org/en-US/docs/Web/API/Transferable"
        ],
        "follow_ups": [
            {
                "Q": "What happens to an ArrayBuffer when passed as a Transferable Object in postMessage(buf, [buf])?",
                "A": "Its ownership is transferred to the worker; the buffer in the sending thread is neutered (byteLength becomes 0) with zero memory copy."
            }
        ]
    },
    {
        "Q": "How do you architect an accessible, keyboard-navigable component library conforming to WAI-ARIA authoring practices?",
        "A": (
            "**Direct answer:** Building an accessible component library conforming to WCAG 2.1 AA and WAI-ARIA authoring practices requires "
            "treating keyboard navigation and assistive technology (screen readers) as primary architectural constraints. Core patterns include:\n"
            "1. **Roving Tabindex vs aria-activedescendant:** Managing keyboard focus in composite widgets (menus, toolbars, grids). Using roving tabindex, the currently selected item has `tabIndex={0}` while all other items have `tabIndex={-1}`. Arrow keys move focus and update tabindex.\n"
            "2. **Accessible Names:** Ensuring every interactive control has a computed accessible name via `<label>`, `aria-label`, or `aria-labelledby`.\n"
            "3. **Focus Trapping:** In modal dialogs, trapping focus so pressing Tab on the last element cycles to the first, and pressing Escape dismisses the modal and returns focus to the trigger element.\n"
            "4. **ARIA Roles & States:** Explicitly declaring states (`aria-expanded`, `aria-selected`, `aria-disabled`, `aria-checked`, `role=\"tablist\"`).\n\n"
            "```tsx\n"
            "// Roving Tabindex Accessible Tab List:\n"
            "function TabList({ tabs, selectedIndex, onSelect }: {\n"
            "    tabs: string[];\n"
            "    selectedIndex: number;\n"
            "    onSelect: (index: number) => void;\n"
            "}) {\n"
            "    const handleKeyDown = (e: React.KeyboardEvent, index: number) => {\n"
            "        let next = index;\n"
            "        if (e.key === 'ArrowRight') next = (index + 1) % tabs.length;\n"
            "        if (e.key === 'ArrowLeft')  next = (index - 1 + tabs.length) % tabs.length;\n"
            "        if (next !== index) {\n"
            "            e.preventDefault();\n"
            "            onSelect(next);\n"
            "            // Programmatically focus the new tab element\n"
            "        }\n"
            "    };\n"
            "\n"
            "    return (\n"
            "        <div role=\"tablist\" aria-label=\"Account Sections\">\n"
            "            {tabs.map((tab, i) => (\n"
            "                <button\n"
            "                    key={tab}\n"
            "                    role=\"tab\"\n"
            "                    aria-selected={i === selectedIndex}\n"
            "                    tabIndex={i === selectedIndex ? 0 : -1} // Roving tabindex!\n"
            "                    onClick={() => onSelect(i)}\n"
            "                    onKeyDown={(e) => handleKeyDown(e, i)}>\n"
            "                    {tab}\n"
            "                </button>\n"
            "            ))}\n"
            "        </div>\n"
            "    );\n"
            "}\n"
            "```\n\n"
            "**Complexity analysis and mechanics:**\n"
            "- **Single Tab Stop:** Entire composite widgets (like a 10-tab list or 50-row menu) represent exactly **one single Tab stop** in the overall document flow.\n"
            "- **Focus Restoration:** Storing `document.activeElement` before opening a dialog and calling `.focus()` on it when the dialog unmounts.\n\n"
            "**Algorithmic mechanics and edge cases:**\n"
            "Never use `role=\"button\"` on a `<div>` if a native `<button>` can be used. Native buttons natively support Space and Enter activation, "
            "disabled state semantics, and form submission without writing custom keyboard listeners."
        ),
        "Why": "Conforming to WAI-ARIA authoring practices guarantees usability for keyboard users and screen reader accessibility.",
        "Risk": "Failing to restore focus when closing modal dialogs disorients blind screen reader users back to the top of the document.",
        "Trade": "Requires implementing keyboard event handlers (Arrow keys, Home, End, Escape) alongside standard click interactions.",
        "Try": "Navigate your application using only the Tab and Arrow keys with your mouse unplugged and verify all controls can be operated.",
        "worked_case": (
            "Walkthrough scenario: A dropdown menu has 8 items. Originally, all 8 items had tabIndex=0. Tabbing through the page required pressing Tab "
            "8 times just to get past the dropdown. Refactoring to a roving tabindex menu makes the entire menu a single Tab stop. "
            "Pressing Tab enters the menu, Arrow Down navigates items, and pressing Tab exits immediately to the next section."
        ),
        "citations": [
            "https://www.w3.org/WAI/ARIA/apg/",
            "https://web.dev/explore/learn-accessibility"
        ],
        "follow_ups": [
            {
                "Q": "What is the difference between aria-hidden='true' and the inert attribute?",
                "A": "aria-hidden hides elements from assistive screen readers but leaves them keyboard focusable; inert removes elements from both accessibility trees and keyboard focus."
            }
        ]
    }
]
