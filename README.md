# puretensor.systems

Source of https://puretensor.systems: one-command recipes for running new open models on RTX PRO 6000 cards,
where every number links to a Verified LocalMaxxing run.

- `index.html`: the hub, with two ways in.
- `localmaxxing/index.html`: the recipe list (one-command recipes, every number a Verified LocalMaxxing run).
- `models/<recipe>/index.html`: one page per recipe, built by `tools/build_<recipe>.py` from the run records.
- `bench/index.html`: the benchmark board. Built in tensor-scripts, never edited here:
  `python3 -I ~/tensor-scripts/bench/board/build_board.py --site systems --out bench/index.html`.
  The public build carries scores and builds only: no hostnames, internal service names, verdict prose or source
  paths, and only speed runs that are public on LocalMaxxing.
- `assets/site.css`: the shared styles.

Static files, served by GitHub Pages.
