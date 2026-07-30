# mh-cemu-enhancements contributor rules

- Treat this as a multi-title Cemu enhancement catalog, not an MH3G-only repository.
- Use `rtk` before every shell command; prefix every command in a shell chain.
- Never distribute game executables, RPX/RPL files, saves, MLC data, keys, or extracted game assets.
- Packs must be fail-closed: exact `moduleMatches` plus a manifest preimage assertion are required for PPC changes.
- Do not call or launch Cemu in this repository's verification workflow. Isolated `graphicPacks` installation is allowed only after a clean verifier result.
- Do not label gameplay behavior `Runtime Verified` without a recorded in-game transcript. `Static Verified` does not imply game-play verification.
