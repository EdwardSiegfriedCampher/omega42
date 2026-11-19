# Setting up the Ω42 portal on GitHub

Steps for the person who publishes this repository. Each takes a few minutes.

1. **Create the repository** (public) and push this tree. Suggested name: `omega42/omega42`.
2. **Point the links at the repository:** `python3 tools/setup_repo.py OWNER/REPO`, then commit.
3. **Enable GitHub Pages:** Settings → Pages → Source: *GitHub Actions*. The `pages` workflow builds `site/` with `tools/site_build.py` and deploys it on every push to `main`. A custom domain can be set there.
4. **Enable Discussions:** Settings → Features → Discussions. Create the categories listed in `community/FORUM.md` (the forms in `.github/DISCUSSION_TEMPLATE/` attach automatically by name). Make *Announcements* an announcement-type category.
5. **Labels:** run the `setup-labels` workflow once (Actions → setup-labels → Run). It creates the labels the intake uses.
6. **Permissions for the intake bot:** Settings → Actions → General → Workflow permissions: *Read and write*, and allow GitHub Actions to create pull requests.
7. **Private vulnerability reporting:** Settings → Security → enable.
8. **Archive:** connect the repository to Zenodo (zenodo.org → GitHub) so each release receives a DOI.
9. **Newsletter:** choose a provider, then set `newsletter.form_action` in `site/config.json`.
10. **Contacts:** set the contact, privacy and verification addresses in `site/config.json`.
11. **Branch protection** on `main`: require the `omega42-ci` checks and one review, and require review from code owners (`.github/CODEOWNERS`) for the Core, the Companion and the tools that check them. Keep the development stream on a `dev` branch (`RELEASES.md` §2).
12. **Immutable releases:** Settings → General → Releases → enable immutable releases, and add a tag ruleset protecting `v*` tags, so a published release and its tag cannot be changed (`RELEASES.md` §4).

After step 3 the site is live at `https://<owner>.github.io/<repo>/`. The build replaces `{{REPO}}` in the site with the repository's own name, so every link to forms, Discussions and files points to the right place.
