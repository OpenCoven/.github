# Agent guide: OpenCoven/.github

This repository holds the OpenCoven organization profile and the default community health files GitHub applies to every OpenCoven repository that lacks its own. It contains no application code and has nothing to build.

## Rules

- **A change here affects many repositories at once.** Default issue forms, PR templates, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `SUPPORT.md` apply organization-wide. Keep them generic; repository-specific rules belong in that repository.
- **Do not invent facts.** Project descriptions, install commands, platform support, and status labels must match the owning repository's current README, About text, or release assets. Do not claim packages, downloads, guarantees, certifications, or response times that don't exist.
- **Security language follows `SECURITY.md`.** Never weaken the private-reporting instruction or add guarantees the policy disclaims.
- **Keep `PATENTS` and `PROVENANCE.md` factual.** They are public records; change them only with maintainer direction.
- **Issue forms must be valid YAML.** GitHub silently drops an invalid form. Parse every changed `ISSUE_TEMPLATE/*.yml` before committing.
- **Commits** need a DCO sign-off (`git commit -s`) and should be signed.

## Verification

1. Parse YAML: `ruby -ryaml -e 'ARGV.each { |f| YAML.load_file(f) }' ISSUE_TEMPLATE/*.yml`
2. Check that every repository linked from `profile/README.md` exists and is public and not archived (unless labeled legacy).
3. Preview the Markdown and confirm relative links resolve.
