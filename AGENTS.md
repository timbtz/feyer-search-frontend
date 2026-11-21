# Frontend collaboration

This repository owns a read-only search visualization. Read `docs/ARCHITECTURE_BRIEFING.md` and `docs/API_CONTRACT.md` before changing integration behavior. Host placement and launcher configuration are changeable snapshots, not fixed frontend assumptions.

- Use `python3 serve.py --demo` for independent frontend work. Synthetic data must stay visibly labelled.
- Preserve scientific candidate parents separately from Git ancestry and grouping. Do not invent worker-to-candidate links or infer successful validation from process completion.
- Do not add agent launching, queue submission, host administration, or credentials to the browser. Those responsibilities belong to the experiment coordinator and host owner.
- Keep production snapshots, transcripts, `.env` files, and host credentials out of Git. `.local/` is ignored for local observations.
- Keep the graph automatically positioned; do not turn it into a drag-and-drop workflow editor.
- Run `npm run check`, `npm test`, and `python3 -m unittest discover -s tests -p 'test_*.py'` for relevant code changes. Check desktop/mobile interactions after graph UI changes.
- Keep the pinned Porsche assets and their license/notice. Preserve generated assets unless intentionally regenerating them with `build-pds.cjs`.
