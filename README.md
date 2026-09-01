# Adastra Marketing Assets

## The AI-Powered Bank

`adastra-ai-powered-bank.html` is a single self-contained page (open it directly
in a browser, no server needed) presenting Adastra's AI-in-retail-banking value
map, with a deep dive into Hyperpersonalization and real case studies pulled
from adastracorp.com.

To rebuild it after editing `page.template.html`:

```
python build.py
```

`build.py` inlines fonts, icons and the logo from `ds/` (a trimmed subset of
the Adastra Design System: Figtree fonts, the icon set, the red wordmark) and
images from `web-assets/` (client logos and case-study photos downloaded from
adastracorp.com) as base64 data URIs, so the output has zero external
dependencies.
