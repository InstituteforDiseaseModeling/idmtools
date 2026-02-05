# Recommended real-world flow (matches what you described)

## Develop & test on feature / dev branch
Work on feature/xyz or dev branch
When you want to test the package:
Go to GitHub → Actions → "Deploy Packages" → Run workflow
Select your feature/dev branch
Choose target: test

This builds + uploads to TestPyPI (only manual, no automatic runs)
Install from TestPyPI and test thoroughly (pip install -i https://test.pypi.org/simple/ toy-package-a==0.1.0.postX.devY)

## Merge to main when tests pass
Merge your feature branch into main (via PR)
main now contains the "ready to publish" code

## Tag from main → real release
git checkout main
git pull origin main
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
Your workflow automatically builds clean 0.2.0 and uploads to real PyPI with approver