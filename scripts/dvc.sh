#!/bin/bash
set -e

echo_status() {
	git status
	dvc data status
	dvc status
}

pull_all() {
	git pull
	dvc pull
	dvc exp pull origin
}

push_all() {
	git push
	dvc push
	dvc exp push origin
}

restore_workspace() {
	git checkout .
	dvc checkout
}

commit_workspace() {
	git commit -am "$1"
	push_all
}

run_exp() {
	pull_all
	dvc exp run "$@"
	restore_workspace
}

clear_data() {
	dvc gc -wc
	dvc exp remove -A
	dvc exp remove -A -g origin
}

func="$1"
shift
"$func" "$@"
