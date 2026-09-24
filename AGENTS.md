# Agent Protocol & Rules for AppForge Studio

## 🚀 Mandatory Autonomous Release Rule
Whenever any new feature, bug fix, or enhancement is implemented in this codebase, the assistant MUST autonomously execute the complete end-to-end release lifecycle:

1. **Verify Code & Tests:**
   - Run `python test_appforge.py` to ensure 100% of test cases pass without errors.
2. **Version Bump:**
   - Update `CURRENT_VERSION` in `app/core/update_checker.py`.
   - Update badges/documentation in `README.md` if applicable.
3. **Commit & Tag:**
   - Stage all modified files: `git add .`
   - Create a semantic commit: `git commit -m "feat/fix: <description>"`
   - Create the corresponding git tag: `git tag -a v<X.Y.Z> -m "Release v<X.Y.Z>"`
4. **Push to Remote:**
   - Push commit and tag to GitHub: `git push origin main && git push origin v<X.Y.Z>`
5. **Release Automation:**
   - The repository's GitHub Actions workflow (`.github/workflows/release.yml`) will automatically trigger, build the Windows executable `AppForge.exe`, and publish the GitHub Release with the downloadable binary.
6. **User Notification:**
   - Inform the user of the new version number, commit hash, and GitHub release URL.
