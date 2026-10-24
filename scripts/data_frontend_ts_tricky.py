"""20 Tricky TypeScript Interview Questions covering type algebra, variance, mapped types, satisfies, infer, and polymorphic patterns."""

QUESTIONS = [
    {
        "Q": "What are the exact functional and structural differences between interface and type alias in TypeScript?",
        "A": (
            "**Direct answer:** While both `interface` and `type` can describe object shapes and contracts, they possess fundamental architectural "
            "differences in declaration merging, union representation, inheritance syntax, and compiler performance.\n\n"
            "```typescript\n"
            "// 1. Declaration Merging (Interfaces ONLY):\n"
            "// Two interfaces with the same name in the same scope merge their properties:\n"
            "interface Window {\n"
            "    analytics: AnalyticsService;\n"
            "}\n"
            "interface Window {\n"
            "    authToken?: string;\n"
            "}\n"
            "// window now has BOTH analytics and authToken!\n"
            "// A type alias with the same name throws: 'Duplicate identifier Window'.\n\n"
            "// 2. Unions, Tuples, and Primitives (Type Aliases ONLY):\n"
            "type Status = 'pending' | 'success' | 'failed'; // Union cannot be an interface\n"
            "type Coordinate = [x: number, y: number];       // Tuple cannot be an interface\n"
            "type StringOrNumber = string | number;\n\n"
            "// 3. Inheritance vs Intersection:\n"
            "interface User extends Person { role: string; }\n"
            "type UserType = Person & { role: string; };\n"
            "```\n\n"
            "**Compiler Performance and Best Practices:**\n"
            "- **Interface caching:** The TypeScript compiler caches interface relationships internally by nominal name, making property lookup "
            "and subtype checking faster in large codebases.\n"
            "- **Type intersection costs:** Intersecting multiple type aliases (`A & B & C & D`) creates a flat intersection that must be re-evaluated "
            "repeatedly, increasing compilation times.\n"
            "- **Rule of thumb:** Prefer `interface` for public library APIs and extensible object schemas; use `type` for unions, tuples, primitives, "
            "and complex conditional/mapped transformations."
        ),
        "Why": "Interfaces support declaration merging and cached compiler lookup, whereas type aliases model unions and complex type-level algebra.",
        "Risk": "Accidental declaration merging with identically named interfaces across different files creates silent schema pollution.",
        "Trade": "Interfaces provide faster compiler type-checking but cannot represent union types, tuples, or mapped aliases directly.",
        "Try": "Declare an interface User twice with distinct fields and instantiate an object requiring both fields to verify declaration merging.",
        "worked_case": (
            "Walkthrough scenario: A developer builds a plugin architecture where third-party packages add custom properties to a core Request object. "
            "Defining Request as a type alias prevents plugins from extending it without modifying library source files. Defining Request as an interface "
            "allows third-party plugins to declare interface Request in their own index.d.ts files, seamlessly merging their custom plugin properties "
            "into the global Request contract."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#differences-between-type-aliases-and-interfaces"
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
                "Q": "Can an interface extend a union type alias?",
                "A": "No, an interface can only extend statically known object shapes, not a union type (e.g. interface A extends (B | C) is invalid)."
            }
        ]
    },
    {
        "Q": "How do distributive conditional types operate over naked type parameters, and how do you suppress distribution using tuples?",
        "A": (
            "**Direct answer:** In TypeScript, a conditional type `T extends U ? X : Y` is called **distributive** when `T` is an unadorned, "
            "'naked' type parameter. When a union type `A | B` is supplied to a distributive conditional type, the check automatically distributes "
            "across each constituent member: `(A extends U ? X : Y) | (B extends U ? X : Y)`.\n\n"
            "```typescript\n"
            "// 1. Distributive Conditional Type (Naked T):\n"
            "type ToArray<T> = T extends any ? T[] : never;\n"
            "type Distributed = ToArray<string | number>;\n"
            "// Evaluates as: ToArray<string> | ToArray<number>\n"
            "// Result: string[] | number[]\n\n"
            "// 2. Non-Distributive Conditional Type (Wrapped [T]):\n"
            "// Wrapping T in a single-element tuple prevents distribution:\n"
            "type ToArrayNonDist<T> = [T] extends [any] ? T[] : never;\n"
            "type NonDistributed = ToArrayNonDist<string | number>;\n"
            "// Result: (string | number)[]\n\n"
            "// 3. Implementing NonNullable via distribution:\n"
            "type MyNonNullable<T> = T extends null | undefined ? never : T;\n"
            "type Safe = MyNonNullable<string | null | undefined>; // Result: string (never is pruned from unions)\n"
            "```\n\n"
            "**Suppressing Distribution:**\n"
            "To prevent distribution and check whether the *entire union as a single entity* satisfies a constraint, wrap both the operand "
            "and constraint in a tuple: `[T] extends [U] ? TrueBranch : FalseBranch`. This is mandatory when detecting `never` (since `never` "
            "is an empty union and distributes to `never` without evaluating either branch)."
        ),
        "Why": "Distributive conditional types allow mapping operations across union members, while tuple wrapping tests unions as a collective whole.",
        "Risk": "Checking T extends never directly never executes the true branch because never distributes over zero elements.",
        "Trade": "Distribution is convenient for filtering (pruning never) but requires counter-intuitive tuple syntax [T] when checking exact equality.",
        "Try": "Write an IsNever<T> type and verify that [T] extends [never] ? true : false correctly returns true for never while T extends never fails.",
        "worked_case": (
            "Walkthrough scenario: A developer builds an API response handler and wants to check if a type parameter T is exactly boolean. In TypeScript, "
            "boolean is an alias for the union true | false. When passing boolean to type IsBoolean<T> = T extends boolean ? true : false, naked T "
            "distributes over true and false individually, producing true | true which is true. But if testing type IsExactUnion<T> = T extends any ? ... , "
            "wrapping [T] in a tuple is mandatory to inspect the combined union rather than its isolated branches."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#distributive-conditional-types"
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
                "Q": "Why does type IsNever<T> = T extends never ? true : false evaluate to never when passed never?",
                "A": "never is an empty union of zero types; when a conditional type distributes over zero members, the result is an empty union (never)."
            }
        ]
    },
    {
        "Q": "How does the infer keyword enable type extraction in conditional types, and how do you extract tuple heads, tails, and promise values?",
        "A": (
            "**Direct answer:** The `infer` keyword introduces a type variable inside the `extends` clause of a conditional type to be deduced "
            "dynamically by the TypeScript compiler. It acts as pattern matching for types: rather than providing a type explicitly, you declare "
            "a hole (`infer R`) that the compiler fills with the corresponding matched type.\n\n"
            "```typescript\n"
            "// 1. Recursive Promise Unwrapping (Awaited<T>):\n"
            "type UnpackPromise<T> = T extends Promise<infer U> ? UnpackPromise<U> : T;\n"
            "type DeepResolved = UnpackPromise<Promise<Promise<string>>>; // Result: string\n\n"
            "// 2. Extracting Function Return Types and Parameters:\n"
            "type ExtractReturn<T> = T extends (...args: any[]) => infer R ? R : never;\n"
            "type ExtractParams<T> = T extends (...args: infer P) => any ? P : never;\n\n"
            "// 3. Tuple Head and Tail Extraction (Pattern Matching):\n"
            "type First<T extends any[]> = T extends [infer Head, ...any[]] ? Head : never;\n"
            "type Rest<T extends any[]> = T extends [any, ...infer Tail] ? Tail : [];\n\n"
            "type Names = ['Alice', 'Bob', 'Charlie'];\n"
            "type F = First<Names>; // 'Alice'\n"
            "type R = Rest<Names>;  // ['Bob', 'Charlie']\n"
            "```\n\n"
            "**Co-located Inferences:**\n"
            "- Multiple `infer` declarations in union positions (e.g. arguments of overloaded functions) yield a union type.\n"
            "- Multiple `infer` declarations in contravariant positions (function parameter positions) yield an intersection type."
        ),
        "Why": "The infer keyword enables type-level pattern matching and recursive metaprogramming without manual hardcoding.",
        "Risk": "Unbounded recursive infer types trigger Type instantiation is excessively deep and possibly infinite compiler errors.",
        "Trade": "Enables expressive type extraction at the cost of steep cognitive complexity and slower IDE type-checking performance.",
        "Try": "Implement a Pop<T extends any[]> utility type using infer that strips the last item from a tuple and returns the remaining elements.",
        "worked_case": (
            "Walkthrough scenario: A microservice middleware pipeline passes data through a sequence of transformation functions. The developer needs "
            "to deduce the final output type of a pipe(f1, f2, f3) call. Using infer with recursive tuple tail extraction unwraps the return type "
            "of each function step-by-step, ensuring that the input parameter of f2 matches the output of f1 with strict compile-time verification."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/conditional-types.html#inferring-within-conditional-types"
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
                "Q": "What happens when infer is used multiple times for the same type variable in function parameter positions?",
                "A": "Because function parameters are in contravariant positions, multiple infer candidates for the same variable resolve to an intersection type."
            }
        ]
    },
    {
        "Q": "How do mapped types with key remapping via the as clause filter and transform object keys dynamically?",
        "A": (
            "**Direct answer:** Mapped types construct new object types by iterating over keys with `[K in keyof T]`. TypeScript 4.1 introduced "
            "**key remapping via the `as` clause**, allowing developers to modify, filter, or replace property names dynamically using template "
            "literal types or conditional checks.\n\n"
            "```typescript\n"
            "interface User {\n"
            "    id: string;\n"
            "    name: string;\n"
            "    age: number;\n"
            "    isAdmin: boolean;\n"
            "}\n\n"
            "// 1. Transforming Key Names with Template Literals (Getters):\n"
            "type Getters<T> = {\n"
            "    [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];\n"
            "};\n"
            "type UserGetters = Getters<User>;\n"
            "// Result: { getId: () => string; getName: () => string; getAge: () => number; getIsAdmin: () => boolean; }\n\n"
            "// 2. Filtering Out Keys by Remapping to never:\n"
            "type PickByValueType<T, TargetValue> = {\n"
            "    [K in keyof T as T[K] extends TargetValue ? K : never]: T[K];\n"
            "};\n"
            "type OnlyStringProps = PickByValueType<User, string>;\n"
            "// Result: { id: string; name: string; } (age and isAdmin filtered out!)\n"
            "```\n\n"
            "**Mechanics of `never` in Key Remapping:**\n"
            "When a key in an `as` clause evaluates to `never`, TypeScript completely omits that property from the resulting object type, "
            "providing a native and highly performant alternative to legacy `Omit<T, K>` implementations."
        ),
        "Why": "Key remapping via as enables programmatic mutation and filtering of schema property names using type-level string templates.",
        "Risk": "Remapping symbol keys with template literals that require string can cause unexpected compile errors unless filtered with string & K.",
        "Trade": "Provides type-level schema transformation at compile time without requiring runtime reflection or metadata decorators.",
        "Try": "Write a mapped type that prefixes all methods of an interface with 'rpc_' and transforms return values into Promises.",
        "worked_case": (
            "Walkthrough scenario: An ORM model contains both database columns (id, title, createdAt) and local helper methods (save, validate). "
            "A serializer function needs a type containing only the columns, filtering out any property whose value is a function. Using a mapped type "
            "with [K in keyof T as T[K] extends Function ? never : K] strips all methods cleanly, producing a pure data transfer object schema."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/mapped-types.html#key-remapping-via-as"
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
                "Q": "Why is string & K required when capitalizing keys in template literals?",
                "A": "keyof T can contain number or symbol keys; intersecting with string ensures Capitalize<T> receives only valid string types."
            }
        ]
    },
    {
        "Q": "How does the satisfies operator (TypeScript 4.9+) preserve narrow literal types while validating structural conformance?",
        "A": (
            "**Direct answer:** The `satisfies` operator (introduced in TypeScript 4.9) solves a classic type system trade-off: validating that an "
            "expression matches a defined type contract *without* widening the expression's inferred literal type. Prior to `satisfies`, developers "
            "had to choose between type annotations (which widen) and type assertions (which bypass checks).\n\n"
            "```typescript\n"
            "type RGB = [red: number, green: number, blue: number];\n"
            "type Color = string | RGB;\n\n"
            "// Problem 1: Type annotation widens palette values to string | RGB:\n"
            "const palette1: Record<string, Color> = {\n"
            "    red: [255, 0, 0],\n"
            "    green: '#00ff00',\n"
            "    blue: [0, 0, 255]\n"
            "};\n"
            "// palette1.green.toUpperCase(); // Error: Property 'toUpperCase' does not exist on type 'RGB'!\n\n"
            "// Problem 2: Type assertion (as) suppresses typos:\n"
            "const palette2 = { red: [255, 0] } as Record<string, Color>; // Passes unsafely even though [255, 0] is invalid RGB!\n\n"
            "// Solution: satisfies checks conformance while preserving exact literal shapes!\n"
            "const palette3 = {\n"
            "    red: [255, 0, 0],\n"
            "    green: '#00ff00',\n"
            "    blue: [0, 0, 255]\n"
            "} satisfies Record<string, Color>;\n\n"
            "palette3.green.toUpperCase(); // Allowed! TypeScript knows green is string.\n"
            "palette3.red.slice(0, 2);     // Allowed! TypeScript knows red is [number, number, number].\n"
            "```\n\n"
            "**Comparison Summary:**\n"
            "- `const x: T`: Validates `T`, but widens inferred type to `T`.\n"
            "- `const x = val as T`: Unsafely coerces type to `T`, suppressing excess property checks and type mismatches.\n"
            "- `const x = val satisfies T`: Validates `T` strictly, while retaining the narrow, exact inferred type of `val`."
        ),
        "Why": "satisfies guarantees contract compliance while preserving specific literal property types for autocompletion and method calls.",
        "Risk": "Assuming satisfies prevents mutation: it checks types but does not freeze objects at runtime like Object.freeze.",
        "Trade": "Requires TypeScript 4.9+ and is purely a compile-time assertion with zero emitted JavaScript runtime code.",
        "Try": "Declare a routes config with satisfies Record<string, RouteInfo> and verify typo detection on routes without losing specific path completions.",
        "worked_case": (
            "Walkthrough scenario: A design token configuration defines colors, paddings, and font sizes. Using a type annotation : ThemeConfig widens "
            "theme.colors.primary to string, losing specific hex codes like '#0f172a' and preventing exact CSS color completions in downstream components. "
            "Replacing the annotation with satisfies ThemeConfig verifies that all required theme keys are present, while preserving exact literal hex values "
            "for autocompletion throughout the application."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html#the-satisfies-operator"
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
                "Q": "Can you combine as const with satisfies?",
                "A": "Yes, const config = { ... } as const satisfies Schema deep-freezes literal types while simultaneously validating schema conformance."
            }
        ]
    },
    {
        "Q": "How do covariance, contravariance, and invariance apply to function parameters and return types under strictFunctionTypes?",
        "A": (
            "**Direct answer:** Variance describes how the subtyping relationship of complex types relates to the subtyping relationship of their "
            "component types. In TypeScript with `--strictFunctionTypes` enabled, function return types are **covariant**, while function parameter "
            "types are **contravariant**.\n\n"
            "```\n"
            "Subtype Relationship: Dog extends Animal (Dog is a subtype of Animal)\n"
            "\n"
            "1. Covariance (Return Types - Same Direction):\n"
            "() => Dog is assignable to () => Animal.\n"
            "A caller expecting an Animal will be completely satisfied receiving a Dog.\n"
            "\n"
            "2. Contravariance (Parameter Types - Reversed Direction!):\n"
            "(animal: Animal) => void is assignable to (dog: Dog) => void.\n"
            "A function that can handle ANY Animal can safely be passed where a function expecting a Dog is required!\n"
            "Conversely, (dog: Dog) => void CANNOT be passed where (animal: Animal) => void is expected (it might receive a Cat).\n"
            "```\n\n"
            "```typescript\n"
            "class Animal { name = 'animal'; }\n"
            "class Dog extends Animal { bark() {} }\n\n"
            "type AnimalHandler = (a: Animal) => void;\n"
            "type DogHandler = (d: Dog) => void;\n\n"
            "let handleAnimal: AnimalHandler = (a) => console.log(a.name);\n"
            "let handleDog: DogHandler = (d) => d.bark();\n\n"
            "handleDog = handleAnimal; // Valid under contravariance! handleAnimal can safely process a Dog.\n"
            "// handleAnimal = handleDog; // Compile error under strictFunctionTypes! handleDog might be called with a Cat.\n"
            "```\n\n"
            "**The Method Bivariance Exception:**\n"
            "Methods written with method syntax `{ method(x: string): void }` remain **bivariant** for backward compatibility with `Array.prototype.push`. "
            "To enforce strict contravariant parameter checking, always declare function signatures as properties: `{ method: (x: string) => void }`."
        ),
        "Why": "Contravariant parameter checking prevents passing functions that expect narrow subtypes to callers providing wider supertypes.",
        "Risk": "Declaring methods as object functions using method shorthand enables bivariance, silently allowing unsound argument assignments.",
        "Trade": "Strict contravariance catches runtime type bugs but requires explicit casting when interfacing with older non-strict DOM libraries.",
        "Try": "Write an EventListener interface using method syntax vs property syntax and observe assignability differences under strictFunctionTypes.",
        "worked_case": (
            "Walkthrough scenario: A UI library has an event handler callback: onClick: (e: MouseEvent) => void. A developer attempts to pass a custom "
            "handler expecting a specialized pointer event: onSpecialClick: (e: PointerEvent) => void. Under strictFunctionTypes, parameter contravariance "
            "rejects this assignment with a compiler error, preventing a runtime crash where the caller dispatches a standard MouseEvent lacking PointerEvent properties."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/functions.html#declaring-this-in-a-function",
            "https://github.com/microsoft/TypeScript/pull/18654"
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
                "Q": "Why did TypeScript deliberately keep method syntax bivariant?",
                "A": "Bivariant methods were preserved so Array<Dog> could be assignable to Array<Animal>, allowing existing JavaScript array idioms to pass."
            }
        ]
    },
    {
        "Q": "How do you implement deep immutable types (DeepReadonly), deep partials (DeepPartial), and deep required types recursively?",
        "A": (
            "**Direct answer:** Standard TypeScript utility types like `Readonly<T>` and `Partial<T>` are strictly shallow—they only modify the top-level "
            "properties of an object. In production state management (Redux, Zustand) and configuration engines, applications require **recursive "
            "conditional mapped types** that traverse down nested object hierarchies while leaving primitive leaves and function references intact.\n\n"
            "```typescript\n"
            "// Built-in primitive types that should NOT be recursed into:\n"
            "type Primitive = string | number | boolean | bigint | symbol | undefined | null | Function;\n\n"
            "// 1. Recursive DeepReadonly:\n"
            "export type DeepReadonly<T> = T extends Primitive\n"
            "    ? T\n"
            "    : T extends Map<infer K, infer V>\n"
            "    ? ReadonlyMap<DeepReadonly<K>, DeepReadonly<V>>\n"
            "    : T extends Set<infer M>\n"
            "    ? ReadonlySet<DeepReadonly<M>>\n"
            "    : T extends Array<infer E>\n"
            "    ? ReadonlyArray<DeepReadonly<E>>\n"
            "    : {\n"
            "        readonly [K in keyof T]: DeepReadonly<T[K]>;\n"
            "    };\n\n"
            "// 2. Recursive DeepPartial:\n"
            "export type DeepPartial<T> = T extends Primitive\n"
            "    ? T\n"
            "    : T extends Array<infer E>\n"
            "    ? Array<DeepPartial<E>>\n"
            "    : {\n"
            "        [K in keyof T]?: DeepPartial<T[K]>;\n"
            "    };\n"
            "```\n\n"
            "**Recursion Guardrails:**\n"
            "- Always check for `Primitive` and `Function` first. Recursing into functions breaks their call signatures.\n"
            "- Special-case built-in objects like `Date`, `RegExp`, `Map`, and `Set` to prevent converting internal methods into broken object structures.\n"
            "- To prevent compiler recursion crashes on circular types, limit mapping to JSON-serializable structures."
        ),
        "Why": "Deep mapped types enforce immutability and partial patching across arbitrarily deep nested domain structures.",
        "Risk": "Applying unconstrained recursive mapped types to circular object graphs causes Type instantiation is excessively deep compiler errors.",
        "Trade": "Deep recursive types increase compile times and type-checking latency on massive AST or GraphQL schemas.",
        "Try": "Create a deeply nested state object and verify with DeepReadonly that mutating state.user.address.zip triggers a compile-time error.",
        "worked_case": (
            "Walkthrough scenario: A Redux reducer manages a complex state tree with nested user settings. A developer uses Readonly<AppState>, but "
            "accidentally writes state.settings.theme.colors.primary = '#000' in a reducer. Because Readonly is shallow, TypeScript permits the mutation, "
            "causing silent state mutation bugs. Replacing Readonly with DeepReadonly flags the nested property assignment as an error at compile time."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/mapped-types.html"
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
                "Q": "How do you implement DeepMutable to strip readonly modifiers recursively?",
                "A": "Use the -readonly mapping modifier in the recursive step: { -readonly [K in keyof T]: DeepMutable<T[K]> }."
            }
        ]
    },
    {
        "Q": "How do const type parameters (TypeScript 5.0+) infer exact literal types directly at function call sites?",
        "A": (
            "**Direct answer:** Prior to TypeScript 5.0, functions accepting generic arguments widened object and array literals to general types "
            "(e.g. `string[]` or `{ name: string }`), forcing callers to explicitly append `as const` at every call site. TypeScript 5.0 introduced "
            "**`const` type parameters**, which instruct the compiler to infer the most specific, literal `readonly` type automatically.\n\n"
            "```typescript\n"
            "// Legacy approach (Prior to TS 5.0):\n"
            "function setNamesLegacy<T extends readonly string[]>(names: T): T {\n"
            "    return names;\n"
            "}\n"
            "// Callers HAD to append 'as const' manually:\n"
            "const names1 = setNamesLegacy(['alice', 'bob'] as const); // ['alice', 'bob']\n"
            "const names2 = setNamesLegacy(['alice', 'bob']);          // string[] (Widened!)\n\n"
            "// Modern approach with const type parameter (TS 5.0+):\n"
            "function setNamesModern<const T extends readonly string[]>(names: T): T {\n"
            "    return names;\n"
            "}\n"
            "// Callers pass normal literals, and TypeScript infers the exact readonly tuple!\n"
            "const namesModern = setNamesModern(['alice', 'bob']);\n"
            "// Inferred type of namesModern: readonly ['alice', 'bob']!\n"
            "```\n\n"
            "**Route and Configuration Builders:**\n"
            "`const` type parameters are transformative for API builders, routing tables, and schema definitions. Passing an object literal "
            "`createRouter({ routes: ['/users', '/billing'] })` preserves the exact string union `'/users' | '/billing'` without requiring "
            "clunky `as const` annotations from consuming developers."
        ),
        "Why": "const type parameters automatically deduce narrow literal types for function arguments without requiring callers to annotate as const.",
        "Risk": "const type parameters infer readonly tuples; passing them to functions expecting mutable arrays causes type errors.",
        "Trade": "Results in readonly immutable structures that prevent subsequent in-place array mutations like push or splice.",
        "Try": "Write a createEnum<const T extends readonly string[]>(...values: T) helper and verify values are inferred as exact string literals.",
        "worked_case": (
            "Walkthrough scenario: A library author builds a type-safe form builder: createForm({ fields: ['email', 'password'] }). Callers want "
            "onSubmit: (data: Record<Fields, string>) => void to know the exact field keys. Without const T, fields widens to string[], and data "
            "becomes Record<string, string>. Adding <const T extends readonly string[]> infers readonly ['email', 'password'], giving callers exact "
            "autocompletion for data.email and data.password."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html#const-type-parameters"
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
                "Q": "What happens if a variable previously defined without const is passed to a const type parameter function?",
                "A": "If an already-widened variable (let x = ['a']) is passed, const T respects the variable's existing type (string[]) without narrowing."
            }
        ]
    },
    {
        "Q": "How do declaration merging, module augmentation, and global scope expansion extend third-party library types?",
        "A": (
            "**Direct answer:** TypeScript provides three distinct mechanisms to extend external or ambient type definitions without modifying "
            "third-party source code in `node_modules`: interface declaration merging, module augmentation (`declare module`), and global scope "
            "augmentation (`declare global`).\n\n"
            "```typescript\n"
            "// 1. Module Augmentation: Extending Express Request type\n"
            "// Inside a custom-types.d.ts file:\n"
            "import { UserSession } from './auth';\n\n"
            "declare module 'express-serve-static-core' {\n"
            "    interface Request {\n"
            "        user?: UserSession; // Augment Express Request with authenticated user session\n"
            "        startTime: number;\n"
            "    }\n"
            "}\n\n"
            "// 2. Global Scope Augmentation: Adding properties to window or NodeJS environment\n"
            "declare global {\n"
            "    namespace NodeJS {\n"
            "        interface ProcessEnv {\n"
            "            DATABASE_URL: string;\n"
            "            JWT_SECRET: string;\n"
            "            PORT?: string;\n"
            "        }\n"
            "    }\n"
            "    interface Window {\n"
            "        StripeAnalytics?: (event: string) => void;\n"
            "    }\n"
            "}\n"
            "export {}; // Ensure file is treated as a module\n"
            "```\n\n"
            "**Invariants and Rules:**\n"
            "- **Module requirement:** Module augmentations must occur inside a file that has top-level `import` or `export` statements. If a file has no imports/exports, it is treated as a script, and `declare module` will replace rather than augment the target module.\n"
            "- **Interface matching:** You can only augment `interface` definitions; you cannot augment a `type` alias."
        ),
        "Why": "Module and global augmentation allow applications to type custom middleware extensions and runtime globals safely.",
        "Risk": "Creating a declare module in a file without import/export statements overwrites the entire module with an empty declaration.",
        "Trade": "Augmentations are ambient and global to the compilation context; overusing them can obscure true library dependencies.",
        "Try": "Augment process.env with custom environment variables in a globals.d.ts file and verify autocompletion on process.env.DATABASE_URL.",
        "worked_case": (
            "Walkthrough scenario: An authentication middleware decodes a JWT and attaches req.user = decoded to the Express request object. "
            "In downstream route handlers, accessing req.user triggers TypeScript errors because Express does not define user on Request. "
            "Adding a declare module 'express-serve-static-core' augmentation adds user: UserSession to interface Request, enabling type-safe "
            "access across all controllers."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/declaration-merging.html#module-augmentation"
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
                "Q": "Why is export {}; necessary at the end of a declaration file containing declare global?",
                "A": "It marks the file as an ES module, ensuring declare global operates as an augmentation rather than a global script scope."
            }
        ]
    },
    {
        "Q": "How do noUncheckedIndexedAccess and exactOptionalPropertyTypes eliminate soundness gaps in production codebases?",
        "A": (
            "**Direct answer:** By default, TypeScript contains subtle soundness gaps designed for developer convenience. Enabling "
            "`noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` in `tsconfig.json` closes two of the most prevalent runtime bug vectors "
            "in production JavaScript systems.\n\n"
            "```typescript\n"
            "// 1. noUncheckedIndexedAccess:\n"
            "// Default behavior: Record access is assumed present!\n"
            "const scores: Record<string, number> = { alice: 100 };\n"
            "// Without flag: scores['bob'] has type number! Runtime returns undefined -> Crash on .toFixed()!\n"
            "// With noUncheckedIndexedAccess: scores['bob'] has type number | undefined!\n"
            "const bobScore = scores['bob'];\n"
            "if (bobScore !== undefined) {\n"
            "    console.log(bobScore.toFixed(2)); // Safe!\n"
            "}\n\n"
            "// 2. exactOptionalPropertyTypes:\n"
            "interface UserPreference {\n"
            "    theme?: 'light' | 'dark'; // Means: property may be absent\n"
            "}\n"
            "// Without flag: { theme: undefined } is valid!\n"
            "// With exactOptionalPropertyTypes: You CANNOT explicitly pass undefined unless declared as 'theme?: 'light' | 'dark' | undefined'!\n"
            "const pref: UserPreference = {\n"
            "    // theme: undefined // Compile Error with exactOptionalPropertyTypes!\n"
            "};\n"
            "// Critical for Object.assign or JSON.stringify, where 'theme' in pref is true if theme is undefined!\n"
            "```\n\n"
            "**Production Significance:**\n"
            "In JavaScript, `'key' in obj` and `Object.hasOwn(obj, 'key')` evaluate to `true` even if `obj.key === undefined`. "
            "`exactOptionalPropertyTypes` ensures that optional properties represent *missing* keys, preventing subtle configuration bugs."
        ),
        "Why": "These flags enforce truthful dictionary and optional property typing, eliminating undefined-access crashes in production.",
        "Risk": "Enabling these flags on mature codebases requires extensive refactoring to add nullish checks on array and dictionary lookups.",
        "Trade": "Requires explicit undefined checks when reading array elements by index or dictionary keys by string.",
        "Try": "Enable noUncheckedIndexedAccess in tsconfig.json and observe how accessing array[0] forces a check for undefined before usage.",
        "worked_case": (
            "Walkthrough scenario: An application parses CSV headers into a string[] and reads const id = headers[0].toUpperCase(). If the CSV file "
            "is empty, headers[0] evaluates to undefined at runtime, causing Cannot read properties of undefined (reading toUpperCase). "
            "Enabling noUncheckedIndexedAccess forces headers[0] to be typed as string | undefined, forcing the developer to guard against empty CSVs."
        ),
        "citations": [
            "https://www.typescriptlang.org/tsconfig#noUncheckedIndexedAccess",
            "https://www.typescriptlang.org/tsconfig#exactOptionalPropertyTypes"
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
                "Q": "How do you safely access a guaranteed array element without casting when noUncheckedIndexedAccess is enabled?",
                "A": "Use an explicit non-null assertion array[0]! only when bounds are mathematically proven, or prefer safe array methods like for...of."
            }
        ]
    },
    {
        "Q": "How do user-defined type predicates (x is T) and assertion functions (asserts x is T) narrow types across conditional branches?",
        "A": (
            "**Direct answer:** TypeScript's control flow analysis can automatically narrow types via `typeof` and `instanceof`, but it cannot "
            "inspect custom validation logic inside helper functions without **user-defined type predicates** (`x is T`) or **assertion functions** "
            "(`asserts x is T`).\n\n"
            "```typescript\n"
            "interface AdminUser { role: 'admin'; permissions: string[]; }\n"
            "interface StandardUser { role: 'user'; }\n"
            "type AppUser = AdminUser | StandardUser;\n\n"
            "// 1. Boolean Type Predicate (x is T):\n"
            "// Returns boolean; if true, TypeScript narrows the variable in the if branch:\n"
            "function isAdmin(user: AppUser): user is AdminUser {\n"
            "    return user.role === 'admin' && Array.isArray((user as any).permissions);\n"
            "}\n\n"
            "function handleRequest(user: AppUser) {\n"
            "    if (isAdmin(user)) {\n"
            "        console.log(user.permissions); // Narrows to AdminUser!\n"
            "    }\n"
            "}\n\n"
            "// 2. Assertion Function (asserts x is T):\n"
            "// Throws on invalid input; if it returns normally, TypeScript narrows downstream code unconditionally:\n"
            "function assertIsAdmin(user: AppUser): asserts user is AdminUser {\n"
            "    if (user.role !== 'admin') {\n"
            "        throw new Error('Unauthorized: Admin access required');\n"
            "    }\n"
            "}\n\n"
            "function executeSuperuserAction(user: AppUser) {\n"
            "    assertIsAdmin(user);\n"
            "    // All code below this line is guaranteed to have AdminUser type!\n"
            "    console.log(user.permissions.join(', '));\n"
            "}\n"
            "```\n\n"
            "**Soundness Responsibility:**\n"
            "The TypeScript compiler does *not* verify that the body of a type predicate actually validates `T`. If you return `true` "
            "mistakenly, TypeScript trusts your predicate unconditionally. Write exhaustive property checks inside type guards."
        ),
        "Why": "Type predicates and assertion functions bridge custom runtime validation checks into the compiler's control flow analysis.",
        "Risk": "Writing an inaccurate type guard (e.g. returning true without checking all fields) causes runtime type pollution without compiler errors.",
        "Trade": "Requires authoring and maintaining manual runtime checking code alongside type signatures.",
        "Try": "Write a isNonNullable<T>(val: T): val is NonNullable<T> predicate and filter an array [1, null, 2] verifying the output is number[].",
        "worked_case": (
            "Walkthrough scenario: An array const items = [1, null, 2, undefined, 3]. Calling items.filter(x => x !== null && x !== undefined) "
            "produces an array that TypeScript still types as (number | null | undefined)[]. Passing a type predicate function "
            "items.filter((x): x is number => x != null) instructs TypeScript to narrow the resulting array to number[], eliminating type errors."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates",
            "https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-7.html#assertion-functions"
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
                "Q": "How do you write an assertion function that asserts a condition rather than a specific type?",
                "A": "Use asserts condition: function assert(condition: unknown, msg: string): asserts condition { if (!condition) throw new Error(msg); }."
            }
        ]
    },
    {
        "Q": "How do you type polymorphic React components with an as prop to enforce matching HTML attributes dynamically?",
        "A": (
            "**Direct answer:** A polymorphic component is a reusable component that can render as different HTML elements or React components "
            "via an `as` prop (e.g. `<Button as=\"button\">` vs `<Button as=\"a\" href=\"...\">`), while guaranteeing that HTML attributes and refs "
            "dynamically adapt to the selected element.\n\n"
            "```tsx\n"
            "import React, { ElementType, ComponentPropsWithRef, ReactNode } from 'react';\n\n"
            "// 1. Omit duplicate props to prevent collisions between component props and HTML props:\n"
            "type MergeProps<E extends ElementType, P = {}> = P & Omit<ComponentPropsWithRef<E>, keyof P>;\n\n"
            "// 2. Polymorphic props definition:\n"
            "type BoxProps<E extends ElementType = 'div'> = {\n"
            "    as?: E;\n"
            "    children?: ReactNode;\n"
            "} & MergeProps<E>;\n\n"
            "// 3. Polymorphic Component Implementation:\n"
            "export function Box<E extends ElementType = 'div'>({ as, children, ...rest }: BoxProps<E>) {\n"
            "    const Component = as || 'div';\n"
            "    return <Component {...rest}>{children}</Component>;\n"
            "}\n\n"
            "// USAGE VALIDATION:\n"
            "// Valid: href is allowed on 'a' tag\n"
            "const link = <Box as=\"a\" href=\"https://example.com\">Visit</Box>;\n\n"
            "// Compile Error: href is NOT allowed on 'button' element!\n"
            "// const bad = <Box as=\"button\" href=\"https://example.com\">Click</Box>;\n"
            "```\n\n"
            "**Why `ComponentPropsWithRef` matters:**\n"
            "Using `ComponentPropsWithRef<E>` ensures that passing `ref` to `<Box as=\"button\" ref={btnRef}>` correctly infers `HTMLButtonElement`, "
            "while `<Box as=\"a\" ref={aRef}>` infers `HTMLAnchorElement`."
        ),
        "Why": "Polymorphic typing ensures accessibility and design system flexibility without sacrificing strict HTML attribute safety.",
        "Risk": "Failing to Omit conflicting component prop names from HTML attributes causes type intersection conflicts.",
        "Trade": "Polymorphic generic types are complex to author and require careful ref forwarding configurations.",
        "Try": "Instantiate Box with as='button' and pass href; observe TypeScript red squiggly error indicating href is invalid on button.",
        "worked_case": (
            "Walkthrough scenario: A design system provides a primary Button component styled as a pill. The navigation bar needs a link that looks "
            "like a Button but renders semantically as an HTML anchor tag for SEO and keyboard navigation. Using a polymorphic Button as='a' href='/login' "
            "renders a native anchor tag with full button styling while TypeScript guarantees href, target, and rel props are strictly checked."
        ),
        "citations": [
            "https://react.dev/learn/typescript#typing-dom-events",
            "https://www.typescriptlang.org/docs/handbook/2/generics.html"
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
                "Q": "How do you wrap a polymorphic component with React.forwardRef?",
                "A": "ForwardRef requires a type assertion or helper function because forwardRef does not natively support generic component signatures."
            }
        ]
    },
    {
        "Q": "How do you implement a strongly-typed Event Emitter and Pub/Sub bus with custom event-to-payload maps in TypeScript?",
        "A": (
            "**Direct answer:** A strongly-typed Event Emitter maps event names to their exact payload signatures, guaranteeing that listeners receive "
            "correct argument types and that callers cannot emit unregistered events or invalid payloads.\n\n"
            "```typescript\n"
            "// 1. Declare event-to-payload interface map:\n"
            "export interface AppEventMap {\n"
            "    'user:login': { userId: string; timestamp: number };\n"
            "    'user:logout': { userId: string };\n"
            "    'theme:change': { theme: 'light' | 'dark' };\n"
            "    'session:expired': void; // Events with no payload\n"
            "}\n\n"
            "// 2. Generic Typed EventEmitter Implementation:\n"
            "export class TypedEventEmitter<Events extends Record<string, any>> {\n"
            "    private listeners = new Map<keyof Events, Set<(payload: any) => void>>();\n\n"
            "    on<E extends keyof Events>(event: E, handler: (payload: Events[E]) => void): () => void {\n"
            "        if (!this.listeners.has(event)) this.listeners.set(event, new Set());\n"
            "        this.listeners.get(event)!.add(handler);\n"
            "        return () => this.off(event, handler);\n"
            "    }\n\n"
            "    off<E extends keyof Events>(event: E, handler: (payload: Events[E]) => void): void {\n"
            "        this.listeners.get(event)?.delete(handler);\n"
            "    }\n\n"
            "    emit<E extends keyof Events>(event: E, ...args: Events[E] extends void ? [] : [payload: Events[E]]): void {\n"
            "        const payload = args[0];\n"
            "        this.listeners.get(event)?.forEach(fn => fn(payload));\n"
            "    }\n"
            "}\n\n"
            "// USAGE VALIDATION:\n"
            "const bus = new TypedEventEmitter<AppEventMap>();\n"
            "bus.on('user:login', ({ userId, timestamp }) => console.log(userId)); // Fully typed payload!\n"
            "bus.emit('user:login', { userId: 'usr_1', timestamp: Date.now() });   // Strictly checked payload!\n"
            "bus.emit('session:expired'); // No payload required for void events!\n"
            "```\n\n"
            "**Variadic Args for Void Events:**\n"
            "Using conditional tuple arguments `...args: Events[E] extends void ? [] : [payload: Events[E]]` allows events mapped to `void` "
            "to be emitted without passing dummy arguments, while payload events require their exact object shape."
        ),
        "Why": "Typed event buses replace loose string-based message passing with compile-time checked event-payload contracts.",
        "Risk": "Failing to remove listeners using the returned unsubscribe callback creates long-lived memory leaks.",
        "Trade": "Requires centralized maintenance of the event map interface across distributed micro-frontend packages.",
        "Try": "Add an event with a boolean payload to AppEventMap and verify that calling bus.emit with a number produces a compile error.",
        "worked_case": (
            "Walkthrough scenario: A micro-frontend messaging bus allows decoupled widgets to communicate. Without TypeScript event maps, "
            "Widget A emits 'USER_LOGOUT' with { id: '1' } while Widget B listens for 'user_logout' expecting { userId: '1' }. The typo and "
            "property mismatch cause silent notification failures. A shared TypedEventEmitter<AppEvents> flags the event name mismatch and "
            "property inconsistency at build time."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/generics.html",
            "https://nodejs.org/api/events.html"
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
                "Q": "How do you support once listeners that auto-remove after a single trigger?",
                "A": "Wrap the handler in an internal callback that calls off before invoking the original handler."
            }
        ]
    },
    {
        "Q": "How do template literal types enable type-safe URL route parameter extraction and path validation?",
        "A": (
            "**Direct answer:** Template literal types allow TypeScript to perform type-level string parsing and pattern matching. "
            "By combining template literal types with recursive conditional `infer`, you can parse express-style URL route paths "
            "(e.g. `\"/users/:userId/posts/:postId\"`) and extract a strongly-typed dictionary of URL route parameters.\n\n"
            "```typescript\n"
            "// 1. Recursive String Parser:\n"
            "type ExtractRouteParams<T extends string> =\n"
            "    T extends `${string}:${infer Param}/${infer Rest}`\n"
            "    ? { [K in Param | keyof ExtractRouteParams<`/${Rest}`>]: string }\n"
            "    : T extends `${string}:${infer Param}`\n"
            "    ? { [K in Param]: string }\n"
            "    : {};\n\n"
            "// 2. Type-Safe Route Navigation Function:\n"
            "function navigate<Path extends string>(\n"
            "    path: Path,\n"
            "    params: ExtractRouteParams<Path>\n"
            "): string {\n"
            "    let url: string = path;\n"
            "    for (const [key, value] of Object.entries(params as Record<string, string>)) {\n"
            "        url = url.replace(`:${key}`, value);\n"
            "    }\n"
            "    return url;\n"
            "}\n\n"
            "// USAGE VALIDATION:\n"
            "// Valid: requires both userId and postId\n"
            "const url = navigate('/users/:userId/posts/:postId', {\n"
            "    userId: '101',\n"
            "    postId: '884'\n"
            "});\n\n"
            "// Compile Error: missing postId property!\n"
            "// navigate('/users/:userId/posts/:postId', { userId: '101' });\n"
            "```\n\n"
            "**How the recursion works:**\n"
            "1. Matches `${string}:${infer Param}/${infer Rest}` -> extracts `userId`, recurses on `/posts/:postId`.\n"
            "2. Matches trailing `${string}:${infer Param}` -> extracts `postId`.\n"
            "3. Merges extracted keys into `{ userId: string; postId: string }`."
        ),
        "Why": "Template literal types parse URL paths at compile time, guaranteeing that route navigation calls provide all required parameters.",
        "Risk": "Complex recursive string types can slow down TypeScript Language Server performance on huge routing files.",
        "Trade": "Compile-time route extraction ensures path correctness without requiring external runtime regex engines.",
        "Try": "Pass a path without parameters (e.g. '/dashboard') to navigate and verify the params argument requires an empty object {}.",
        "worked_case": (
            "Walkthrough scenario: A team maintains a web app with 80 routes. A developer updates a link to /organizations/:orgId/members/:memberId "
            "but forgets to provide memberId in the navigation parameters. Without type-safe route parsing, the app navigates to "
            "/organizations/123/members/:memberId, crashing the server with a 404. With ExtractRouteParams, the build immediately fails with "
            "Property memberId is missing in type { orgId: string }."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html"
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
                "Q": "How do you handle optional route parameters like :id?",
                "A": "Add a conditional branch checking if Param ends with '?' and remap to an optional property in the resulting type."
            }
        ]
    },
    {
        "Q": "How do variadic tuple types and tuple index manipulation enable type-safe curry and compose function signatures?",
        "A": (
            "**Direct answer:** Variadic tuple types (introduced in TypeScript 4.0) allow spreading tuple types (`...T`) in arbitrary positions "
            "within array and tuple signatures. This enables full type-safety for higher-order functional programming idioms like `curry`, "
            "`concat`, and `compose`.\n\n"
            "```typescript\n"
            "// 1. Tuple concatenation and slicing:\n"
            "type Concat<T extends readonly any[], U extends readonly any[]> = [...T, ...U];\n"
            "type Combined = Concat<[number, string], [boolean]>; // [number, string, boolean]\n\n"
            "// 2. Prepended and Appended Tuples:\n"
            "type Push<T extends readonly any[], E> = [...T, E];\n"
            "type Unshift<T extends readonly any[], E> = [E, ...T];\n\n"
            "// 3. Type-Safe Function Currying for 2 arguments:\n"
            "function curry2<A, B, R>(fn: (a: A, b: B) => R): (a: A) => (b: B) => R {\n"
            "    return (a: A) => (b: B) => fn(a, b);\n"
            "}\n\n"
            "// 4. Arbitrary Variadic Pipe / Compose:\n"
            "type Tail<T extends any[]> = T extends [any, ...infer Rest] ? Rest : [];\n"
            "```\n\n"
            "**Positional Soundness:**\n"
            "Unlike legacy TypeScript where rest parameters had to be placed at the very end of a tuple, variadic tuples can be placed anywhere: "
            "`[string, ...number[], boolean]`. This accurately models functions that take leading options followed by variadic arguments and "
            "a trailing callback."
        ),
        "Why": "Variadic tuple types preserve element positions and lengths across functional transformations without type widening.",
        "Risk": "Deeply nested currying across unbounded variadic tuples can exceed TypeScript instantiation limits.",
        "Trade": "Unlocks functional composition at the cost of sophisticated recursive type definitions.",
        "Try": "Write a typed concat<T extends any[], U extends any[]>(a: T, b: U): [...T, ...U] function and verify the returned tuple types.",
        "worked_case": (
            "Walkthrough scenario: A functional pipeline takes a database query builder and chains filter, sort, and paginate transformations. "
            "Without variadic tuples, chaining arguments widened positional tuples to Array<string | number>, losing parameter order and count. "
            "Variadic tuples preserve exact argument sequences and types across every piped function step."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-0.html#variadic-tuple-types"
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
                "Q": "Can a tuple have two rest elements like [...T, ...U]?",
                "A": "A tuple can contain multiple rest spreads, but at most one spread may be of an unbounded array type like string[]."
            }
        ]
    },
    {
        "Q": "What are the exact differences between any, unknown, never, and void, and how does type algebra govern their intersections and unions?",
        "A": (
            "**Direct answer:** `any`, `unknown`, `never`, and `void` occupy distinct mathematical positions in TypeScript's type hierarchy lattice:\n\n"
            "- **`unknown` (Top Type):** Represents any value whatsoever. Type-safe: you *cannot* access properties or invoke methods on `unknown` without first narrowing it via `typeof`, `instanceof`, or a type guard.\n"
            "- **`any` (Escape Hatch / Top & Bottom):** Disables type-checking entirely. You can access arbitrary properties, invoke it, and assign it to almost any type, spreading unsoundness throughout the codebase.\n"
            "- **`never` (Bottom Type):** Represents the empty set of values. It is impossible to assign any value to `never`. Returned by functions that never return (throw or infinite loop) or unhandled variants in discriminated unions.\n"
            "- **`void` (Unit-like Type):** Represents the absence of a meaningful return value. A function returning `void` may return `undefined` or return a value that callers must ignore.\n\n"
            "```typescript\n"
            "// Type Algebra Laws:\n"
            "\n"
            "// 1. Unions (Sum Types):\n"
            "type U1 = string | any;     // any (any absorbs everything in unions)\n"
            "type U2 = string | unknown; // unknown (unknown absorbs everything except any)\n"
            "type U3 = string | never;   // string (never is pruned from unions! Identity element)\n"
            "\n"
            "// 2. Intersections (Product Types):\n"
            "type I1 = string & any;     // any\n"
            "type I2 = string & unknown; // string (unknown is identity element in intersections!)\n"
            "type I3 = string & never;   // never (never absorbs everything in intersections!)\n"
            "```\n\n"
            "**Golden Rule:** Always prefer `unknown` over `any` for untrusted API responses, user inputs, and dynamic deserialization."
        ),
        "Why": "Understanding the type lattice ensures proper usage of top and bottom types for safe downcasting and exhaustive matching.",
        "Risk": "Using any silences compiler errors and disables type safety across all downstream variables that consume it.",
        "Trade": "unknown requires explicit type narrowing before usage, adding validation code in exchange for absolute type soundness.",
        "Try": "Write a function accepting unknown and verify you cannot call .trim() without an if (typeof x === 'string') guard.",
        "worked_case": (
            "Walkthrough scenario: An application parses JSON from an untrusted webhook. Typing the payload as any allows code like "
            "payload.user.preferences.theme to compile without error. If preferences is null at runtime, the node server crashes with an unhandled exception. "
            "Typing the payload as unknown forces the developer to validate required fields with runtime checks or Zod schemas before accessing properties."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/narrowing.html",
            "https://www.typescriptlang.org/docs/handbook/2/types-from-types.html"
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
                "Q": "Why does a callback returning void permit the implementation to return a boolean?",
                "A": "void in callback positions indicates the caller will ignore the return value, allowing array.forEach(x => set.add(x)) without compiler errors."
            }
        ]
    },
    {
        "Q": "How does TypeScript execute excess property checks on fresh object literals, and why does intermediate variable assignment bypass them?",
        "A": (
            "**Direct answer:** TypeScript's structural type system normally operates on **duck typing**: if an object has all required properties "
            "of a target type, it is assignable, even if it possesses additional properties. However, when an object is created as a **fresh object "
            "literal** directly at the assignment or argument site, TypeScript applies **Excess Property Checks** to prevent typos and invalid options.\n\n"
            "```typescript\n"
            "interface Options {\n"
            "    color: string;\n"
            "    width?: number;\n"
            "}\n\n"
            "function createBox(opts: Options) {}\n\n"
            "// 1. Fresh Object Literal: Excess property check triggers immediately!\n"
            "// createBox({ color: 'red', widht: 20 });\n"
            "// Error: Object literal may only specify known properties, and 'widht' does not exist in type 'Options'. Did you mean 'width'?\n\n"
            "// 2. Intermediate Variable Assignment: Bypasses excess property check!\n"
            "const rawConfig = { color: 'red', widht: 20, extraSecret: 123 };\n"
            "createBox(rawConfig); // Compiles without error!\n"
            "// Why? rawConfig is not 'fresh'; structural subtyping applies because rawConfig has 'color: string'.\n"
            "```\n\n"
            "**Why Freshness matters:**\n"
            "Passing `{ widht: 20 }` directly is almost always a human developer typo. But passing an existing `rawConfig` object is common when "
            "passing larger domain models to functions that only need a subset of their properties."
        ),
        "Why": "Excess property checks catch accidental typos and misspelled properties when passing inline object literals.",
        "Risk": "Assuming structural typing rejects extra properties everywhere: intermediate variables bypass excess property checks silently.",
        "Trade": "Freshness checks break pure structural typing purity in exchange for practical typo prevention.",
        "Try": "Assign an object literal with an extra field directly to an interface versus assigning via a let variable to observe the check.",
        "worked_case": (
            "Walkthrough scenario: A developer configures an HTTP client with interface RequestOptions { timeout?: number; headers?: Record<string, string> }. "
            "The developer writes fetchClient({ timout: 5000 }). Because this is an inline object literal, TypeScript immediately flags the typo 'timout'. "
            "Without excess property checks, 'timout' would be silently ignored, and the request would run with no timeout, causing production hangs."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/objects.html#excess-property-checks"
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
                "Q": "How can an interface explicitly allow arbitrary extra properties?",
                "A": "Add an index signature: interface Options { color: string; [key: string]: any; } to permit unknown extra keys."
            }
        ]
    },
    {
        "Q": "How do you write ambient declaration files (.d.ts) to provide accurate types for untyped JavaScript libraries?",
        "A": (
            "**Direct answer:** Ambient declaration files (`.d.ts`) describe the shape of existing JavaScript libraries to the TypeScript "
            "compiler without producing emitted JavaScript code. They use the `declare` keyword to assert the existence of variables, functions, "
            "classes, and modules provided by the external runtime environment.\n\n"
            "```typescript\n"
            "// Example: my-analytics-lib.d.ts\n\n"
            "// 1. Declare external CommonJS / ESM Module:\n"
            "declare module 'my-analytics-lib' {\n"
            "    export interface AnalyticsConfig {\n"
            "        apiKey: string;\n"
            "        endpoint?: string;\n"
            "        flushIntervalMs?: number;\n"
            "    }\n\n"
            "    export class AnalyticsTracker {\n"
            "        constructor(config: AnalyticsConfig);\n"
            "        track(event: string, properties?: Record<string, unknown>): void;\n"
            "        identify(userId: string): Promise<boolean>;\n"
            "        flush(): void;\n"
            "    }\n\n"
            "    // Default export:\n"
            "    const defaultTracker: AnalyticsTracker;\n"
            "    export default defaultTracker;\n"
            "}\n\n"
            "// 2. Typing static assets (e.g. SVG imports in bundlers):\n"
            "declare module '*.svg' {\n"
            "    const content: React.FC<React.SVGProps<SVGSVGElement>>;\n"
            "    export default content;\n"
            "}\n"
            "```\n\n"
            "**Crucial Syntax Guidelines:**\n"
            "- Never include implementation bodies inside `.d.ts` files (use `;` instead of `{ ... }`).\n"
            "- Declare types using `export` within `declare module` blocks.\n"
            "- Include your `.d.ts` files in `tsconfig.json` `include` array so the compiler discovers them."
        ),
        "Why": "Ambient declaration files provide type contracts for untyped legacy npm packages and bundler asset imports.",
        "Risk": "Writing ambient definitions that do not match the real JavaScript runtime exports leads to runtime undefined errors.",
        "Trade": "Requires manual maintenance to keep ambient signatures synchronized with external library version updates.",
        "Try": "Create a declaration file for '*.png' and verify that importing a PNG image in TypeScript compiles without module not found errors.",
        "worked_case": (
            "Walkthrough scenario: An application imports an in-house legacy analytics script that is loaded via a script tag onto window.Analytics. "
            "TypeScript throws Cannot find name Analytics. Creating an env.d.ts file with declare const Analytics: { logEvent: (name: string) => void }; "
            "informs the compiler of the global variable, providing autocompletion and eliminating build errors without modifying the legacy script."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/declaration-files/by-example.html"
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
                "Q": "What is the difference between export = and export default in a declaration file?",
                "A": "export = models CommonJS module.exports = value, which callers consume via import x = require('x') or esModuleInterop import x from 'x'."
            }
        ]
    },
    {
        "Q": "What are the known soundness holes and intentional compromises in TypeScript's type system?",
        "A": (
            "**Direct answer:** Unlike pure academic type systems (like Haskell or OCaml), TypeScript was explicitly designed with a pragmatic "
            "balance between safety and developer ergonomics. The official TypeScript Design Goals state: *'Produce a type system that is usable "
            "and idiomatic, not provably sound.'* There are four major intentional soundness compromises in TypeScript:\n\n"
            "```typescript\n"
            "// 1. Mutable Array Covariance (Classic Soundness Hole):\n"
            "class Animal { name = 'animal'; }\n"
            "class Dog extends Animal { bark() {} }\n"
            "class Cat extends Animal { meow() {} }\n\n"
            "let dogs: Dog[] = [new Dog()];\n"
            "let animals: Animal[] = dogs; // Allowed because arrays are covariant!\n"
            "animals.push(new Cat());     // Pushing a Cat into Animal[] modifies dogs underlying array!\n"
            "dogs[1].bark();              // Crash at runtime! Cat does not have bark()!\n\n"
            "// 2. Function Parameter Bivariance on Methods:\n"
            "interface Consumer {\n"
            "    consume(a: Dog): void;\n"
            "}\n"
            "// Method syntax allows assigning (a: Animal) => void or (a: Dog) => void bidirectionally.\n\n"
            "// 3. Array Index Undefined Holes (without noUncheckedIndexedAccess):\n"
            "const empty: number[] = [];\n"
            "const num = empty[0]; // Type is 'number', but runtime value is 'undefined'!\n"
            "\n"
            "// 4. Type Assertions (as) and 'any':\n"
            "const x = 'hello' as unknown as number; // Bypasses type checker completely.\n"
            "```\n\n"
            "**Mitigations:**\n"
            "Enable strict compiler flags (`--strict`, `--noUncheckedIndexedAccess`, `--strictFunctionTypes`) and use `readonly` arrays "
            "(`ReadonlyArray<T>`) to prevent mutable covariant array writes."
        ),
        "Why": "Understanding intentional soundness compromises allows engineers to identify and guard against edge cases where the compiler cannot protect them.",
        "Risk": "Assuming TypeScript guarantees 100 percent runtime correctness: type assertions and covariant arrays can still throw TypeError at runtime.",
        "Trade": "Pragmatic unsoundness enables seamless interop with dynamic JavaScript idioms without excessive type casting ceremonies.",
        "Try": "Push a superclass instance into a subclass array via a covariant reference and observe the runtime method failure.",
        "worked_case": (
            "Walkthrough scenario: A developer has a function modifyList(items: BaseItem[]) that adds a default BaseItem to the list. "
            "The caller passes a SpecializedItem[] array. Because TypeScript arrays are covariant, the code compiles cleanly. At runtime, "
            "the caller iterates over SpecializedItem[] and calls item.specialMethod(), which crashes with a TypeError on the newly added "
            "BaseItem. Refactoring modifyList to accept readonly BaseItem[] prevents the mutation at compile time."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/type-compatibility.html",
            "https://github.com/Microsoft/TypeScript/wiki/TypeScript-Design-Goals"
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
                "Q": "How does ReadonlyArray prevent the covariant array mutation soundness hole?",
                "A": "ReadonlyArray removes push, pop, and index assignment methods, preventing callers from inserting incompatible subtypes."
            }
        ]
    },
    {
        "Q": "How do function overloads differ from generic conditional types, and when is each pattern superior for API design?",
        "A": (
            "**Direct answer:** Both function overloads and generic conditional types allow a function to return different types depending on "
            "its input arguments. However, they differ radically in signature visibility, union argument handling, and implementation complexity.\n\n"
            "```typescript\n"
            "// APPROACH 1: Function Overloads\n"
            "function getItem(id: number): string;\n"
            "function getItem(ids: number[]): string[];\n"
            "// Implementation signature (hidden from callers!):\n"
            "function getItem(arg: number | number[]): string | string[] {\n"
            "    return Array.isArray(arg) ? arg.map(String) : String(arg);\n"
            "}\n\n"
            "const s = getItem(1);    // string\n"
            "const arr = getItem([1]); // string[]\n"
            "// Overload Pitfall: Passing a union parameter FAILS!\n"
            "// const unionArg: number | number[] = 1 as any;\n"
            "// getItem(unionArg); // Error! Neither overload matches number | number[]!\n\n"
            "// APPROACH 2: Generic Conditional Types\n"
            "type ItemResult<T extends number | number[]> = T extends number[] ? string[] : string;\n"
            "function getItemGeneric<T extends number | number[]>(arg: T): ItemResult<T> {\n"
            "    return (Array.isArray(arg) ? arg.map(String) : String(arg)) as ItemResult<T>;\n"
            "}\n"
            "// Generic Handles Unions Gracefully:\n"
            "// getItemGeneric(unionArg) returns string | string[] automatically!\n"
            "```\n\n"
            "**Selection Heuristics:**\n"
            "- **Use Function Overloads** when argument types and return types vary across completely different positional arguments or different arities (e.g. `createElement(tag)` vs `createElement(tag, props, ...children)`).\n"
            "- **Use Generic Conditional Types** when the return type is a direct mathematical projection of a single input argument, especially when callers frequently pass union types."
        ),
        "Why": "Choosing between overloads and conditional types determines whether an API can handle union arguments and multi-arity parameters cleanly.",
        "Risk": "Function overloads reject union arguments because TypeScript evaluates overloads sequentially and matches only exact individual signatures.",
        "Trade": "Overloads provide distinct JSDoc documentation per signature; conditional types handle unions seamlessly with single signatures.",
        "Try": "Call an overloaded function with a union type argument (string | number) and observe why TypeScript requires a union overload or generic conditional.",
        "worked_case": (
            "Walkthrough scenario: A database query helper has overloads query(sql: string): SingleRow and query(sql: string[]): BatchRow[]. "
            "A caller writes a wrapper function that passes sql: string | string[]. Calling query(sql) triggers an error: No overload matches this call. "
            "Refactoring the function to a generic conditional type query<T extends string | string[]>(sql: T): T extends string[] ? BatchRow[] : SingleRow "
            "allows the function to accept both individual inputs and union inputs seamlessly."
        ),
        "citations": [
            "https://www.typescriptlang.org/docs/handbook/2/functions.html#function-overloads",
            "https://www.typescriptlang.org/docs/handbook/2/conditional-types.html"
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
                "Q": "Why is the implementation signature of an overloaded function not visible to outside callers?",
                "A": "TypeScript treats the implementation signature solely as an internal contract to satisfy all declared overload signatures."
            }
        ]
    }
]
