# Optional bundled model

Export an image model from Teachable Machine and place these files here before building a release:

- `model.json`
- `metadata.json`
- the exported `.bin` weights file referenced by `model.json`

If these files are absent, the application still works with a hosted model URL or with the three files selected in the browser interface. Do not commit student images or private training data.
