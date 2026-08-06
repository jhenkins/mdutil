# Test Mermaid Export

## Introduction

This document tests Mermaid diagram rendering in mdutil v4.0.

## Flowchart Example

```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
    Alice->>Bob: Hello Bob, how about you?
    Bob-->>Alice: Good!
```

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
```

## Mixed Content

This paragraph has **bold** and `inline code` mixed with a diagram:

```mermaid
graph LR
    A[Markdown] --> B{Parse}
    B -->|HTML| C[Export]
    B -->|PDF| D[Export]
```

Some text after the diagram.

## Invalid Mermaid (Should Fallback)

```mermaid
this is not valid mermaid syntax @@@
```

## Conclusion

End of test document.
