# Rend Asunder — Flag 0 (Hacker101)

**Hints (paraphrased):** What do you have access to? Look around your sandbox. Some places are **D**efinitely m**O**re i**M**portant than others (**DOM**).

## Idea

The challenge page you open in your own browser is still **HTML**. The default script in the textarea is a red herring for this flag: the secret is not inside that snippet—it is in **markup the browser parses but does not execute** the way normal script does.

`<noscript>` is parsed into the DOM; its **children are not treated as HTML** by the parser in the usual sense (they are text until the closing `</noscript>`). That makes it easy to miss with a quick “view source” skim, but it is still reachable from JavaScript via the DOM.

## Steps

1. Open your instance **`BASE`** in a normal browser (not only `curl`).
2. Open DevTools → **Console**.
3. Dump the document and confirm normal tags do not hold the flag:

```javascript
document.write(document.getElementsByTagName('html')[0].innerHTML);
```

4. Check inline script text (usually empty / uninteresting for this flag):

```javascript
document.write(document.getElementsByTagName('script')[0].innerHTML);
```

5. Read the **`noscript`** body from the DOM:

```javascript
document.write(document.getElementsByTagName('noscript')[0].innerHTML);
```

The flag appears in that string (format `^FLAG^…$FLAG$`).

## Why it works

- **`innerHTML` of `<noscript>`** exposes the hidden payload the page author placed for non-JS clients, while JS-enabled clients still run the rest of the app.
- The hint nudges you toward **D**ocument **O**bject **M**odel inspection rather than only iterating on the server-side render pipeline.

## Instance note

Hacker101 flags are **per deployment**. The technique above is stable; the exact flag body changes with each instance.
