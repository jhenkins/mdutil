# CommonMark & GFM Specification Test Cases

## Block Elements

### Paragraphs

This is a paragraph.

    This is a code block (4 spaces indent).

### Headers

# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5

###### Heading 6

### Blockquotes

> This is a blockquote.
>
> It can span multiple lines.
>
> > This is a nested blockquote.

### Horizontal Rules

---

***

___

### Lists

- Unordered item 1
- Unordered item 2
    - Nested item
        - Deeply nested

1. Ordered item 1
2. Ordered item 2
    1. Nested ordered
    2. Nested ordered
        1. Deeply nested

### Code Blocks

Inline `code` in a paragraph.

```
Fenced code block
with multiple lines
and `backticks` inside.
```

````
A code block with `` inside.
````

### Tables (GFM)

| Syntax | Description |
|--------|-------------|
| Header | Title |
| -------- | :---: |
| Paragraph | Text |

| Left | Center | Right |
|:-----|:------:|------:|
| 1    | 2      | 3     |
| 4    | 5      | 6     |

## Inline Elements

### Emphasis

*single asterisks*

_single underscores_

**double asterisks**

__double underscores__

***both***

___both___

### Links

[A link](https://example.com "Title")

<https://example.com>

auto-linked

### Images

![alt text](https://example.com/image.jpg "Title")

### Strikethrough (GFM)

~~delete me~~

~~multiple~~ ~~strikethroughs~~

### Task Lists (GFM)

- [x] Implement feature A
- [ ] Implement feature B
- [x] Write tests
- [ ] Deploy to production

### Footnotes

Here is a footnote reference[^1].

Another reference[^note].

[^1]: Here is the footnote.
[^note]: Here is another footnote with `code`.

### Highlight (GFM)

==highlighted text==

This is ==important== information.

### Math Notation

The equation $E = mc^2$ is famous.

The quadratic formula is $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$.

## Edge Cases

### Escaped Characters

\*not emphasized\*

\[not a link\](/url)

\~\~not deleted\~\~

==not highlighted==

\\$not math\\$

### Line Breaks

This line  
has a hard break.

This line  
has two trailing spaces.

### Autolinks

Visit <https://example.com> for more info.

### Email

Contact <user@example.com> for support.

### Soft Breaks

Line one
Line two
Line three

### Hard Breaks

Line one  
Line two  
  
Line three

### Code Span Edge Cases

``code with ` backtick``

`code with "quotes"`

### HTML Blocks

<p>This is an HTML block.</p>

```html
<div class="container">
    <p>HTML inside code block</p>
</div>
```

### Definition Lists (Custom)

Term 1
:   Definition 1

Term 2
:   Definition 2a
:   Definition 2b

Multiple terms sharing a definition
:   Shared definition here

### Subscript and Superscript

H~2~O is water.

The formula x^2^ + y^2^ = r^2^.

E=mc^2^

### Link with Title

[Visit Example](https://example.com "Example Website")

[API Docs](https://api.example.com "API Reference Documentation")

### Nested Formatting

**bold and *italic***

*italic and **bold***

~~**deleted and bold**~~

==**highlighted bold**==

### Backslashes in Code

`backslash: \`\``

### Empty Elements

[empty link]()

[empty image](![])

### Unicode in Various Contexts

日本語のテキスト

日本語のテキスト with **bold**

日本語のテキスト with ~~strikethrough~~

日本語のテキスト with $math$

日本語のテキスト with [^1] footnote
