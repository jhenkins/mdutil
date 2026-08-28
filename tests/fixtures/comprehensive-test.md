# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5

###### Heading 6

This is a paragraph with **bold**, *italic*, ***bold and italic***, and ~~strikethrough~~ text.

Here is some `inline code` and a [link](https://example.com).

![Image](https://example.com/image.png "Title")

> This is a blockquote.
>
> It can span multiple lines and include **formatted** text.

---

- Unordered item 1
- Unordered item 2
  - Nested item 2.1
  - Nested item 2.2
    - Deep nested item
- Unordered item 3

1. Ordered item 1
2. Ordered item 2
3. Ordered item 3
   1. Nested ordered 3.1
   2. Nested ordered 3.2
      - Deep nested bullet

- [x] Completed task
- [ ] Pending task

| Feature | Status | Notes |
|---|---|---|
| Headings | ✅ | h1-h6 all working |
| Bold/Italic | ✅ | Bold, italic, both |
| Code blocks | ✅ | Inline and fenced |
| Links | ✅ | Inline and auto |
| Images | ✅ | With title |
| Blockquotes | ✅ | Multi-line |
| Lists | ✅ | Ordered, unordered, nested, task |
| Tables | ✅ | Basic |
| Footnotes | 🔲 | See footnote [^1] |
| Maths | 🔲 | $E = mc^2$ |
| Definition lists | 🔲 | See below |

Here is a fenced code block:

```python
def fibonacci(n: int) -> list[int]:
    """Return the first n Fibonacci numbers."""
    if n <= 0:
        return []
    result = [0, 1]
    for _ in range(2, n):
        result.append(result[-1] + result[-2])
    return result

print(fibonacci(10))
```

```javascript
const greet = (name: string): string => {
    return `Hello, ${name}!`;
};

console.log(greet("World"));
```

Definition lists:

Term 1
:   Definition 1.1
:   Definition 1.2

Term 2
:   Definition 2

Subscript: H~2~O and Superscript: E=mc^2^

Math notation: $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$

Footnote [^1] with [reference](https://example.com).

Here is some text with ~~strikethrough~~ and `inline code` mixed in.

> [!NOTE] This is a callout-style blockquote.

- Item A
- Item B
- Item C

And the final paragraph with **final** *emphasis*.

[^1]: This is the footnote definition.
