# Moqui Deployment Operations

Use this guide when building, loading, packaging, or deploying a Moqui backend.

## Ground rules

- Confirm the backend root and runtime presence first.
- Choose the narrowest operational task that matches the need.
- Distinguish local load and run tasks from Tomcat deploy tasks.
- Do not describe a production deployment flow the repo does not actually provide.

## Useful Gradle tasks in this codebase

- `./gradlew load`
- `./gradlew loadSeed`
- `./gradlew loadSeedInitial`
- `./gradlew loadProduction`
- `./gradlew addRuntime`
- `./gradlew addRuntimeTomcat`
- `./gradlew deployTomcat`

## Usage guidance

- Use `loadSeed` or `loadSeedInitial` for narrow data initialization when those are sufficient.
- Use `loadProduction` only when the install-level data load is actually intended.
- Use `addRuntime` when the target deployment needs the runtime embedded in the WAR.
- Use `deployTomcat` or `addRuntimeTomcat` only when the deployment target is the Tomcat flow defined in `build.gradle`.

## Verification

- Report the exact command run.
- Report whether runtime setup, data load, or deploy packaging was skipped.
- Call out environment assumptions such as Tomcat home, runtime directory, or external services.
