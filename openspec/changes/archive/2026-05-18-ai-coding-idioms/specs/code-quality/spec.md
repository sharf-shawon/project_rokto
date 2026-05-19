## ADDED Requirements

### Requirement: AI-Aware Exception Handling

The system SHALL enforce strict exception handling idioms derived from the project's Ruff configuration (`TRY`, `EM`, `BLE`, `SIM`). Specifically:

1. Exception messages SHALL be assigned to a variable before being raised; string literals SHALL NOT be used directly in `raise` statements.
2. `try-except-pass` blocks SHALL NOT be used. The `contextlib.suppress(Exception)` context manager SHALL be used instead.
3. When logging inside an `except` block, `logger.exception()` SHALL be used instead of `logger.error()`.

#### Scenario: Raising an exception

- **WHEN** the system needs to raise an exception
- **THEN** it SHALL assign the error message to a variable first
- **AND** it SHALL use that variable in the `raise` statement

#### Scenario: Suppressing an exception

- **WHEN** the system needs to silently ignore a caught exception
- **THEN** it SHALL use `with contextlib.suppress(Exception):` instead of `try: ... except Exception: pass`

#### Scenario: Logging an exception

- **WHEN** an exception is caught and logged
- **THEN** the system SHALL use `logger.exception("Error message")` rather than `logger.error(...)`

### Requirement: AI-Aware Control Flow

The system SHALL enforce strict control flow idioms derived from the project's Ruff configuration (`FBT`, `SIM`). Specifically:

1. Boolean positional arguments SHALL NOT be used in function or method definitions. Booleans MUST be keyword-only arguments.
2. Ternary operators (`value = a if condition else b`) SHALL be prioritized over multi-line `if-else` blocks for simple assignments.

#### Scenario: Defining a function with a boolean flag

- **WHEN** a function is defined with a boolean parameter
- **THEN** it SHALL be defined as a keyword-only argument (e.g., `def func(arg1, *, flag=False):`)

#### Scenario: Simple conditional assignment

- **WHEN** a variable is assigned one of two values based on a condition
- **THEN** the system SHALL use a ternary operator

### Requirement: AI-Aware Variables and Clean Code

The system SHALL enforce clean code idioms derived from the project's Ruff configuration (`PLR`, `PLC`, `RUF`, `SLF`). Specifically:

1. Numeric literals (magic numbers) SHALL NOT be used directly in application code or test assertions; they MUST be assigned to descriptive constants.
2. All `import` statements SHALL be placed at the top level of the file, not nested inside functions or methods.
3. Unused variables resulting from tuple unpacking SHALL be prefixed with an underscore (e.g., `success, _msg = ...`).
4. Accessing protected/private members (e.g., `_state`) from outside their class SHALL NOT be allowed.

#### Scenario: Using specific numeric values

- **WHEN** the system implements logic relying on specific numeric limits (e.g., `160`, `250`)
- **THEN** these numbers SHALL be defined as constants at the class or module level

#### Scenario: Importing modules

- **WHEN** a module requires an external dependency
- **THEN** the `import` statement SHALL be at the top of the file

#### Scenario: Unpacking tuples with unused values

- **WHEN** unpacking a tuple where not all values are needed
- **THEN** unused variables SHALL be prefixed with `_`
