# CCI SurveyHUB — Bug Tracking

Bugs encountered during development and the fixes applied to resolve them.

---

## Bug #1 — Flask-Login `is_active` Conflict

**Date:** Day 6 (Authentication)
**Severity:** Critical — login broken
**Component:** `app/models/user.py`

### Description
The User model had a column named `is_active`. Flask-Login's `UserMixin` provides an `is_active` property that checks the user's authentication state. The column name conflicted with the built-in property, causing unexpected behavior when Flask-Login tried to determine if the user was active.

### Cause
Naming collision between a custom database column and Flask-Login's `UserMixin.is_active` property.

### Fix
Renamed the column from `is_active` to `active` in the User model. All references in routes and templates were updated accordingly.

---

## Bug #2 — `Undefined` Not JSON Serializable (Results Page)

**Date:** Day 14 (Results Page)
**Severity:** Critical — 500 error on results page
**Component:** `app/templates/results.html`, `app/routes/surveys.py`

### Description
Opening `/surveys/<id>/results` caused a `TypeError: Object of type Undefined is not JSON serializable`. The error originated from the Jinja2 template attempting to use `|map(attribute='text')` on a dictionary.

### Cause
`choice_counts` was built as a dictionary (keyed by choice ID, with values containing `text`, `count`, `percentage`). Jinja2's `|map(attribute='text')` filter does not work on dictionaries — it produces `Undefined` values which cannot be serialized to JSON.

### Fix
Replaced the dictionary structure with a list of dictionaries (`choice_data`) and pre-computed `labels` and `values` lists in the route. The template now iterates over a list instead of mapping over a dictionary.

**File changed:** `app/routes/surveys.py` (lines 217–235)

---

## Bug #3 — `builtin_function_or_method` Not JSON Serializable

**Date:** Day 14 (Results Page)
**Severity:** Critical — 500 error on results page
**Component:** `app/templates/results.html`

### Description
After fixing Bug #2, a new error appeared: `TypeError: Object of type builtin_function_or_method is not JSON serializable` when serializing `result.values`.

### Cause
In Jinja2, `result.values` resolves to the `dict.values()` method before the `'values'` key. The attribute accessor `result.values` hits the method, not the dictionary key.

### Fix
Renamed the dictionary key from `'values'` to `'counts'` in the route and updated the template reference from `result.values` to `result.counts`.

**Files changed:** `app/routes/surveys.py`, `app/templates/results.html`

---

## Bug #4 — Charts Not Rendering (Blank Space)

**Date:** Day 14 (Results Page)
**Severity:** High — charts invisible
**Component:** `app/static/js/main.js`, `app/templates/results.html`

### Description
The results page showed a large blank gap between question headers and data tables. The Chart.js canvases existed in the DOM but never rendered any charts.

### Cause
The JavaScript selector used `document.querySelectorAll('[data-chart-question]')` but the canvas elements in the template did not have the `data-chart-question` attribute. The selector matched nothing.

### Fix
Added the `data-chart-question` attribute to each `<canvas>` element in `results.html`.

**File changed:** `app/templates/results.html` (line 109)

---

## Bug #5 — `Unexpected end of JSON Input` (Chart Data)

**Date:** Day 14 (Results Page)
**Severity:** Critical — JavaScript error prevents chart rendering
**Component:** `app/templates/results.html`

### Description
Console showed `Uncaught SyntaxError: Unexpected end of JSON input` at `JSON.parse(canvas.dataset.labels)`. The `data-labels` attribute contained invalid JSON when read by the browser.

### Cause
The `|tojson` filter produced JSON with double quotes inside a double-quoted HTML attribute:
```html
data-labels="["Commerce", "Industrie", "Services"]"
```
The browser parsed the attribute as `data-labels="["` (stopping at the first inner double quote), leaving an incomplete JSON string.

### Fix
Changed the attribute delimiter from double quotes to single quotes:
```html
data-labels='{{ result.labels|tojson }}'
```

**File changed:** `app/templates/results.html` (lines 110–111)

---

## Bug #6 — Stale Browser Cache for JavaScript

**Date:** Day 14 (Results Page)
**Severity:** Medium — fixes not loading
**Component:** `app/templates/base.html`

### Description
After applying fixes to `main.js`, the browser continued serving the old cached version. The server logs showed `304 Not Modified` for `main.js?v=3`.

### Cause
The cache-busting query parameter `?v=3` was not changed after modifying the file, so the browser reused its cached copy.

### Fix
Bumped the cache-busting version from `?v=3` to `?v=4` for both `main.css` and `main.js` in `base.html`.

**File changed:** `app/templates/base.html` (lines 14, 136)

---

## Bug #7 — `requirements.txt` UTF-16 Encoding

**Date:** Day 17 (Exports)
**Severity:** Low — file unreadable by tools
**Component:** `requirements.txt`

### Description
`requirements.txt` was encoded in UTF-16 (with BOM), which caused issues with tools that expect UTF-8. The file was essentially broken for `pip install -r requirements.txt` on some systems.

### Cause
The file was likely created or saved by a text editor that defaulted to UTF-16 encoding.

### Fix
Regenerated the file using `pip freeze > requirements.txt` in UTF-8 encoding.

---

## Bug #8 — Settings Sidebar Not Scrollable

**Date:** Day 18 (Password Protection)
**Severity:** Medium — Save button hidden
**Component:** `app/templates/survey_builder.html`

### Description
After adding the Response Password field to the Survey Settings panel, the sidebar content became taller than the viewport. The Save Settings button was cut off at the bottom with no way to scroll to it.

### Cause
The sidebar `<aside>` element used `h-fit` (height: fit-content), which only took the height it needed but did not enable scrolling when the content overflowed the available space.

### Fix
Changed the sidebar class from `h-fit` to `h-full overflow-y-auto`, making it take the full available height and scroll when content overflows.

**File changed:** `app/templates/survey_builder.html` (line 81)

---

## Bug #9 — AI Assistant Markdown Not Rendering

**Date:** Day 19 (AI Assistant)
**Severity:** Medium — poor response formatting
**Component:** `app/templates/base.html`

### Description
The AI assistant responses showed raw markdown syntax (asterisks for bullets, double asterisks for bold) instead of formatted text.

### Cause
The JavaScript used `textContent` to set the message content, which renders everything as plain text without parsing markdown.

### Fix
Added the `marked.js` library via CDN and changed the JavaScript from `textContent` to `innerHTML` using `marked.parse()` to convert markdown to HTML. Added CSS styles for lists, bold, code, and paragraphs within `.ai-message`.

**File changed:** `app/templates/base.html`

---

## Bug #10 — Horizontal Scrollbar in Chat Panel

**Date:** Day 19 (AI Assistant)
**Severity:** Low — unnecessary UI element
**Component:** `app/templates/base.html`

### Description
The AI chat panel displayed a horizontal scrollbar that served no purpose — no content was actually wider than the panel.

### Cause
The `.ai-chat-messages` container did not explicitly prevent horizontal overflow. Some elements (especially after markdown parsing) could trigger a horizontal scrollbar.

### Fix
Added `overflow-x: hidden` to `.ai-chat-messages` and `word-wrap: break-word` with `overflow-wrap: break-word` to `.ai-message` and `.user-message`.

**File changed:** `app/templates/base.html`
