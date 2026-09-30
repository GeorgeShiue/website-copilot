#!/usr/bin/env bash
# 刪除 runs/ 底下今天以前的 run 資料夾（依資料夾名稱 YYYYMMDD_HHMMSS 的日期判斷，本地時間）。
# 不符合此命名格式的項目一律保留。
#
# 用法：./scripts/clean-runs.sh [--dry-run] [--yes]
#   --dry-run  只列出將刪除的資料夾，不實際刪除
#   --yes      略過確認提示直接刪除
# 環境變數 RUNS_DIR 可指定其他 runs 目錄（預設 <專案根目錄>/runs）。
set -euo pipefail
cd "$(dirname "$0")/.."

dry_run=false
assume_yes=false
for arg in "$@"; do
    case "$arg" in
        --dry-run) dry_run=true ;;
        --yes) assume_yes=true ;;
        *) echo "用法：$0 [--dry-run] [--yes]" >&2; exit 2 ;;
    esac
done

runs_dir="${RUNS_DIR:-runs}"
if [[ ! -d "$runs_dir" ]]; then
    echo "找不到 $runs_dir/，無需清理"
    exit 0
fi

today="$(date +%Y%m%d)"
targets=()
for path in "$runs_dir"/*/; do
    name="$(basename "$path")"
    # 只處理 RunManager 產生的 timestamp 資料夾，且日期早於今天
    if [[ "$name" =~ ^([0-9]{8})_[0-9]{6}$ ]] && [[ "${BASH_REMATCH[1]}" < "$today" ]]; then
        targets+=("$runs_dir/$name")
    fi
done

if (( ${#targets[@]} == 0 )); then
    echo "$runs_dir/ 中沒有 $today 以前的 run"
    exit 0
fi

echo "$runs_dir/ 中 $today 以前的 run（共 ${#targets[@]} 個）："
printf '  %s\n' "${targets[@]}"
du -sch "${targets[@]}" | tail -1 | awk '{print "合計大小：" $1}'

if $dry_run; then
    echo "（--dry-run：未刪除任何檔案）"
    exit 0
fi

if ! $assume_yes; then
    read -r -p "確定刪除以上資料夾？[y/N] " answer
    [[ "$answer" =~ ^[Yy]$ ]] || { echo "已取消"; exit 0; }
fi

rm -rf -- "${targets[@]}"
echo "已刪除 ${#targets[@]} 個 run"
