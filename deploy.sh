#!/bin/bash
# Ship an update: commit all changes, push, GitHub Pages rebuilds automatically.
cd ~/projects/ready-timer
git add -A
git -c user.name='Oliver' -c user.email='oliver@local' commit -m "update $(date +%F)" || echo 'nothing to commit'
git push
