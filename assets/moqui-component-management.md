# Moqui Component Management

Use this guide when creating, retrieving, updating, or packaging components.

## Component principles

- Keep domain logic inside the owning component whenever possible.
- Use `component.xml` as the canonical declaration of the component boundary.
- Preserve the existing component naming and directory conventions before introducing a new component.

## Useful Gradle tasks in this codebase

- `./gradlew getRuntime`
- `./gradlew getComponent -Pcomponent=<name>`
- `./gradlew getComponentSet -PcomponentSet=<set>`
- `./gradlew getDepends`
- `./gradlew createComponent -Pcomponent=<name>`
- `./gradlew gitPullAll`
- `./gradlew zipComponent -Pcomponent=<name>`
- `./gradlew zipComponents`

## Workflow

1. Inventory existing components before adding a new one.
2. If the component already exists, preserve its package and folder strategy.
3. If a new component is needed, prefer the framework’s `createComponent` flow over hand-rolled scaffolding.
4. Check dependencies before assuming a component is standalone.
5. Package or retrieve components through Gradle tasks instead of manual zip or clone steps when possible.
