#!/bin/bash
set -e

pre-commit install

if pre-commit run --all-files; then
	echo "All pre-commit checks passed."
	exit 0
fi

echo "Some pre-commit checks failed."

if ! pre-commit run --all-files; then
	echo "Some files were not fixed automatically."
	exit 1
fi

echo "All files were fixed automatically."

git config user.email "$GITLAB_USER_EMAIL"
git config user.name "pre-commit bot for $GITLAB_USER_NAME"
git commit --no-verify -am "Apply pre-commit fixes from $CI_JOB_URL"

base_url="https://gitlab-ci-token:${PRE_COMMIT_ACCESS_TOKEN:-$CI_JOB_TOKEN}@${CI_SERVER_HOST}"
if [[ -n "$CI_COMMIT_BRANCH" ]]; then
	git remote set-url origin "${base_url}/${CI_PROJECT_PATH}.git"
	git push origin HEAD:"$CI_COMMIT_BRANCH"
elif [[ -n "$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME" ]]; then
	git remote set-url origin "${base_url}/${CI_MERGE_REQUEST_SOURCE_PROJECT_PATH}.git"
	git push origin HEAD:"$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME"
else
	echo "This is not a branch or merge request pipeline."
	exit 1
fi

echo "Pushed fixes as new commit. Cancelling this pipeline."
exit 1
