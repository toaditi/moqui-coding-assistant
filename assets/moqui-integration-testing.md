# Moqui Integration Testing

How to write a native Moqui integration test — a Spock spec that boots the framework and
exercises real services against a real database — so it actually runs and actually
authenticates. Both failure modes below are silent: the suite stays green while testing
nothing, or a service refuses to run for a reason the error message misdescribes.

Applies to `src/test/groovy/*` specs that call `Moqui.getExecutionContext()` and invoke
services or entity finds (not pure-unit Groovy with no framework boot).

## Wiring — a spec that exists is not a spec that runs

Two independent gates decide whether a spec executes. Miss either and `gradle test`
reports **BUILD SUCCESSFUL** having run **zero** of your tests.

### 1. The component needs its own `build.gradle`

`settings.gradle`'s `getDirectoryProjects()` only includes a `runtime/component/<name>`
directory as a Gradle subproject if that directory contains a `build.gradle`. A component
with none is invisible to Gradle — `:runtime:component:<name>:test` does not exist, and a
whole-repo `gradle test` skips it entirely. There is no warning; the task simply is not there.

- **Symptom:** you add specs under `src/test/groovy/`, `gradle test` is green, and nothing
  you wrote ever ran (no log lines from your spec, `tests completed` count unchanged).
- **Fix:** add a `build.gradle` to the component. For a pure XML/data component with no
  `src/main`, it exists only to wire `src/test/groovy` into Gradle: `apply plugin: 'groovy'`,
  `implementation project(':framework')`, the JUnit-Platform + Spock test deps, and a `test`
  block with `useJUnitPlatform()`, `include '**/*MoquiSuite.class'`, and the
  `systemProperty` datasource overrides (mirror an existing component such as `moqui-gql`).

### 2. The spec must be listed in the suite

The `test` block runs only `**/*MoquiSuite.class` — a JUnit-Platform `@Suite` class with
`@SelectClasses([...])`. A spec class that compiles but is **not** in that list never runs,
and again the suite stays green.

- **Fix:** add every new spec to `@SelectClasses`. Treat the suite class as the registry;
  a spec not registered is dead.
- The suite's `@AfterAll` should call `Moqui.destroyActiveExecutionContextFactory()` so the
  ECF is torn down once after all specs.

**Rule: green ≠ ran.** After adding or moving a spec, confirm its own log lines and a
changed `tests completed` count — never trust a green build alone.

## Authenticating in an integration test

A service with `authenticate="true"` (the default) needs a logged-in user. A raw test JVM
has none, so the call fails before running. Getting a user logged in has one non-obvious
requirement on the HotWax/Maarg stack.

### The realm authenticates against OFBiz `UserLogin`, not `UserAccount` username

The active realm on this stack is `co.hotwax.auth.OfbizShiroRealm`. It resolves the login
against the OFBiz **`org.apache.ofbiz.security.login.UserLogin`** model. A
`moqui.security.UserAccount` row whose `username` matches is **not** enough — if there is no
corresponding `UserLogin`, login throws **"No account found for username …"**, which reads
like the account is missing even though a direct `find("moqui.security.UserAccount")` locates it.

- **Symptom:** `internalLoginUser("john.doe")` fails with "No account found", yet the
  `UserAccount` row plainly exists in the DB. The realm looked in `UserLogin`, where the row
  was absent.

### Use the demo admin with `internalLoginUser` — no password, no fabricated user

- `internalLoginUser(username)` is a **force-login**: it establishes the user without a
  password. Prefer it in tests — no credential is embedded in the repo.
- Log in as an **existing demo account**, not one the test fabricates. On this stack the demo
  Administrator is **`hotwax.user`** (`COMMERCE_SUPER` / `ADMIN` / `ADMIN_ADV`), defined in
  `oms/data/JA_Demo_AJ_HCUserData.xml` — it has the required `Party` / `UserLogin` /
  `UserAccount` rows already. Do **not** hand-build a `Party`/`UserLogin`/`UserAccount` per
  test; that duplicates data the demo file already owns and drifts from it.
- **Make the suite self-contained:** load that demo file in `setupSpec` before logging in, so
  the spec passes on a fresh or CI database, not only on a dev DB that happens to have demo
  data. It is idempotent (fixed PKs), so a re-run just re-applies the same rows:

  ```groovy
  ec.artifactExecution.disableAuthz()
  ec.transaction.runRequireNew(30, "demo user load",
          { ec.entity.makeDataLoader().location("component://oms/data/JA_Demo_AJ_HCUserData.xml").load() })
  ((org.moqui.impl.context.UserFacadeImpl) ec.user).internalLoginUser("hotwax.user")
  ec.artifactExecution.enableAuthz()
  ```

### Two more mechanics that bite

- **`disableAuthz` for raw entity access.** `EntityValueBase.create()` (and finds outside a
  service) run their own authz check regardless of any `authenticate="false"`. Wrap raw
  entity reads/writes in a **paired** `boolean was = ec.artifactExecution.disableAuthz(); try
  { … } finally { if (!was) ec.artifactExecution.enableAuthz() }`. This is separate from
  authentication — logging in does not remove the need for it when you touch entities directly.
- **A stuck error poisons later calls.** Once `ec.message` holds an error, the service engine
  refuses subsequent calls with *"Found error(s) before service …, so not running service"* —
  so one failure cascades into unrelated later assertions. In a `@Shared`-context spec, clear
  errors at the start of each feature: `ec.message.clearErrors()` in Spock's `setup()`.

## References

- Framework silent-failure catalog: `moqui-framework-pitfalls.md`
- Verification procedure (run the audit, then the narrowest test): `moqui-quality-checklist.md`
