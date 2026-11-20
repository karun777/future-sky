# Character and player resources

FS-W3-F4 authoring convention v0.1. No runtime file-serving capability is introduced.

`registry.json` maps stable resource IDs to stable subject IDs and private manifests. Cast records reference resource IDs, never machine-specific absolute paths. Resolve manifest paths relative to the repository root. Private manifests resolve their file paths relative to their own directory. Reject absolute paths, traversal and symlinks escaping the resource root in any future resolver; do not expose this directory through a static web server.

Character layout: `resources/private/characters/<character_id>/manifest.json` and `source/<original_filename>`. Future player resources use `resources/private/players/<stable_player_id>/`; do not use display names or Discord account IDs as storage keys. No player identity or account binding has been created here. Characters, resource provenance and controller assignments remain separate.

The tracked registry carries routing metadata only. Personal source files, person-to-character associations, original source paths and checksums live in gitignored private manifests. These are author-only resources, not character knowledge or player-visible assets. Gitignore prevents routine Git inclusion; it is not an access-control or backup system.

The first resource is copied into this isolated worktree and verified byte-for-byte. A fresh clone will contain the registry but not its private sources. Treat a missing manifest as unavailable; do not fabricate data or search unrelated folders. Dropbox retains the original. Before moving/deleting the worktree, explicitly migrate and verify the private resource directory; a shared private store and backup policy remain future work.

To add a resource: allocate an unused stable resource ID, preserve the supplied original, create a private manifest with source, media type, size, SHA-256, date and access, then register the reference against its subject. Preserve old source versions when replacing reports. Generated interpretations must be separate derived resources identifying their input and framework versions. Review derived content before publishing it.
