#!/usr/bin/env python3
"""根据 git diff 自动生成 CHANGELOG patch

Usage:
    # 生成新版本
    python generate_changelog.py -p packages/rootengine-core/ -o CHANGELOG/ -v 0.5.3

    # 生成新版本并自动 amend 合并到同一 commit
    python generate_changelog.py -p packages/rootengine-core/ -o CHANGELOG/ -v 0.5.3 --commit

    # 指定 commit 区间生成 changelog
    python generate_changelog.py -p packages/rootengine-core/ -o CHANGELOG/ -v 0.5.3 --from abc123 --to def456

    # 指定起始 commit（到 HEAD）
    python generate_changelog.py -p packages/rootengine-core/ -o CHANGELOG/ -v 0.5.3 --from abc123

    # 清空暂存区
    python generate_changelog.py --reset

    # 列出目录下的所有版本
    python generate_changelog.py -p packages/rootengine-core/ -o CHANGELOG/ -l

    # 查看指定版本信息
    python generate_changelog.py -p packages/rootengine-core/ -o CHANGELOG/ -s 0.5.3

    # 删除版本
    python generate_changelog.py -p packages/rootengine-core/ -o CHANGELOG/ -d 0.5.3

    # 重新扫描版本
    python generate_changelog.py -p packages/rootengine-core/ -o CHANGELOG/ -r 0.5.3
"""
version = "0.1.0"
import subprocess
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


def run_git_cmd(cmd):
    """运行 git 命令，处理编码"""
    result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    return result.stdout.strip() if result.stdout else ""


def get_diff(package_path, base_commit=None, use_cached=False, to_commit=None):
    """获取指定 package 的改动

    use_cached=True 时：比较 暂存区 与 base_commit 的差异（用于 git add 后未 commit 的场景）
    use_cached=False 时：比较 base_commit 与 to_commit（默认 HEAD）的差异
    """
    if base_commit:
        if use_cached:
            cmd = ["git", "diff", "--cached", base_commit, "--", package_path]
        else:
            end = to_commit if to_commit else "HEAD"
            cmd = ["git", "diff", base_commit, end, "--", package_path]
    else:
        cmd = ["git", "diff", "--cached", "--", package_path]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.stdout.strip()


def get_commits_details(package_path, base_commit=None, to_commit=None):
    """获取每个 commit 的详细信息"""
    end = to_commit if to_commit else "HEAD"
    if base_commit:
        cmd = ["git", "log", f"{base_commit}..{end}", "--format=%H|%s|%an|%ad", "--date=short"]
    else:
        cmd = ["git", "log", "-10", "--format=%H|%s|%an|%ad", "--date=short"]

    output = run_git_cmd(cmd)
    commits = []

    for line in output.split('\n'):
        if not line.strip():
            continue
        parts = line.split('|')
        if len(parts) >= 4:
            commit_hash = parts[0]
            message = parts[1]
            author = parts[2]
            date = parts[3]

            # 获取单个 commit 的 patch
            patch_cmd = ["git", "diff", f"{commit_hash}^", commit_hash, "--", package_path]
            patch = run_git_cmd(patch_cmd)

            commits.append({
                "hash": commit_hash,
                "short_hash": commit_hash[:8],
                "message": message,
                "author": author,
                "date": date,
                "patch": patch
            })

    return commits


def get_git_info(commit=None):
    """获取指定 commit 的 git 信息，不指定则取当前 HEAD"""
    ref = commit or "HEAD"
    info = {}

    info["commit_hash"] = run_git_cmd(["git", "rev-parse", ref])[:8]
    tags = run_git_cmd(["git", "tag", "--points-at", ref]).split('\n')
    info["tag_name"] = [t for t in tags if t] if tags else []
    info["commit_message"] = run_git_cmd(["git", "log", "-1", "--format=%s", ref])

    return info


def parse_diff(diff_text):
    """解析 diff，保留完整格式供 git 使用"""
    changes = []
    current_file = None
    current_content = []
    in_hunk = False

    for line in diff_text.split('\n'):
        if line.startswith('diff --git'):
            if current_file and current_content:
                changes.append((current_file, '\n'.join(current_content)))
            parts = line.split(' b/')
            if len(parts) == 2:
                current_file = parts[1]
            current_content = [line]
            in_hunk = False
        elif line.startswith('index '):
            current_content.append(line)
        elif line.startswith('--- ') or line.startswith('+++ '):
            current_content.append(line)
        elif line.startswith('@@'):
            current_content.append(line)
            in_hunk = True
        elif in_hunk:
            current_content.append(line)

    if current_file and current_content:
        changes.append((current_file, '\n'.join(current_content)))

    return changes


def format_changes(changes):
    """格式化改动"""
    lines = []
    for file_path, content in changes:
        lines.append(content)
        lines.append("")
    return '\n'.join(lines)


def generate_changelog(package_path):
    """生成 patch 内容"""
    diff_text = get_diff(package_path)
    if not diff_text:
        return ""
    changes = parse_diff(diff_text)
    return format_changes(changes)


def read_index(changelog_dir):
    """读取项目根目录的 index.json"""
    index_file = changelog_dir / "index.json"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    return {"versions": [], "commits": {}}


def write_index(changelog_dir, data):
    """写入项目根目录的 index.json"""
    index_file = changelog_dir / "index.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def list_versions(changelog_dir):
    """列出所有版本"""
    data = read_index(changelog_dir)
    if not data["versions"]:
        print("暂无版本记录")
        return

    print(f"{'版本':<12} {'patch文件':<20} {'提交hash':<10} {'创建时间'}")
    print("-" * 60)
    for entry in data["versions"]:
        version = entry.get("version", "")
        patch_file = entry.get("patch_file", "")
        commit_hash = entry.get("commit_hash", "")
        created_at = entry.get("created_at", "")
        print(f"{version:<12} {patch_file:<20} {commit_hash:<10} {created_at}")


def show_version(changelog_dir, version):
    """显示指定版本信息"""
    data = read_index(changelog_dir)
    for entry in data["versions"]:
        if entry["version"] == version:
            print(json.dumps(entry, indent=2, ensure_ascii=False))
            return

    print(f"[ERROR] 版本 {version} 不存在")
    sys.exit(1)


def delete_version(changelog_dir, version, force=False):
    """删除指定版本"""
    data = read_index(changelog_dir)

    target_entry = None
    for entry in data["versions"]:
        if entry["version"] == version:
            target_entry = entry
            break

    if target_entry is None:
        print(f"[ERROR] 版本 {version} 不存在")
        sys.exit(1)

    # 确认删除（force=True 时跳过）
    if not force:
        print(f"即将删除版本: {version}")
        print(f"  版本目录: {changelog_dir / f'v{version}'}")
        confirm = input("确认删除? (y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            sys.exit(0)

    # 删除版本文件夹
    version_dir = changelog_dir / f"v{version}"
    if version_dir.exists():
        import shutil
        shutil.rmtree(version_dir)
        print(f"[OK] Deleted: {version_dir}")

    # 更新 index.json
    new_versions = [v for v in data["versions"] if v["version"] != version]
    data["versions"] = new_versions

    # 删除 commits 中该版本的记录
    if version in data.get("commits", {}):
        del data["commits"][version]

    write_index(changelog_dir, data)
    print(f"[OK] Updated index.json")


def add_version_by_range(changelog_dir, package_path, version, from_commit, to_commit=None):
    """根据 commit 区间添加新版本"""
    data = read_index(changelog_dir)

    # 检查版本号是否已存在
    for v in data["versions"]:
        if v["version"] == version:
            print(f"[ERROR] 版本 {version} 已存在，请使用 -r 重新扫描或先删除再生成")
            sys.exit(1)

    end = to_commit if to_commit else "HEAD"

    # 生成原始 patch
    changelog = get_diff(package_path, from_commit, use_cached=False, to_commit=end)
    git_info = get_git_info(end)

    # 创建版本文件夹
    version_dir = changelog_dir / f"v{version}"
    version_dir.mkdir(parents=True, exist_ok=True)

    # 写入原始 patch
    patch_file = f"v{version}.patch"
    patch_path = version_dir / patch_file
    with open(patch_path, 'w', encoding='utf-8') as f:
        f.write(changelog)

    # 写入 commits.json
    commits_info = get_commits_details(package_path, from_commit, to_commit)
    commits_file = "commits.json"
    commits_path = version_dir / commits_file
    with open(commits_path, 'w', encoding='utf-8') as f:
        json.dump(commits_info, f, indent=2, ensure_ascii=False)

    # 写入版本 index.json
    version_index = {
        "version": version,
        "patch_file": patch_file,
        "commits_file": commits_file,
        "tag_name": git_info.get("tag_name"),
        "commit_hash": git_info.get("commit_hash"),
        "commit_message": git_info.get("commit_message"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(version_dir / "index.json", 'w', encoding='utf-8') as f:
        json.dump(version_index, f, indent=2, ensure_ascii=False)

    # 更新项目根目录 index.json
    new_entry = {
        "version": version,
        "version_dir": f"v{version}",
        "patch_file": patch_file,
        "tag_name": git_info.get("tag_name"),
        "commit_hash": git_info.get("commit_hash"),
        "commit_message": git_info.get("commit_message"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    data["versions"].insert(0, new_entry)

    # commits 按版本分组存到根级别（合并）
    existing_commits = data.get("commits", {})
    existing_commits[version] = [
        {"hash": c["hash"], "short_hash": c["short_hash"], "message": c["message"]}
        for c in commits_info
    ]
    data["commits"] = existing_commits

    write_index(changelog_dir, data)

    print(f"[OK] Created: {patch_path}")
    print(f"[OK] Created: {commits_path}")
    print(f"[OK] Updated index.json")
    print()
    print(json.dumps(new_entry, indent=2, ensure_ascii=False))


def add_version(changelog_dir, package_path, version, auto_commit=False):
    """添加新版本"""
    # 读取上次记录的 commit
    data = read_index(changelog_dir)

    # 检查版本号是否已存在
    for v in data["versions"]:
        if v["version"] == version:
            print(f"[ERROR] 版本 {version} 已存在，请使用 -r 重新扫描或先删除再生成")
            sys.exit(1)

    # --commit 时直接取最新 commit 作为基准
    base_commit = run_git_cmd(["git", "rev-parse", "HEAD"])

    # 生成原始 patch（--commit 时用 cached 取暂存区改动）
    changelog = get_diff(package_path, base_commit, use_cached=auto_commit)
    git_info = get_git_info()

    # 创建版本文件夹
    version_dir = changelog_dir / f"v{version}"
    version_dir.mkdir(parents=True, exist_ok=True)

    # 写入原始 patch
    patch_file = f"v{version}.patch"
    patch_path = version_dir / patch_file
    with open(patch_path, 'w', encoding='utf-8') as f:
        f.write(changelog)

    # 写入 commits.json
    commits_info = get_commits_details(package_path, base_commit)
    commits_file = "commits.json"
    commits_path = version_dir / commits_file
    with open(commits_path, 'w', encoding='utf-8') as f:
        json.dump(commits_info, f, indent=2, ensure_ascii=False)

    # 写入版本 index.json
    version_index = {
        "version": version,
        "patch_file": patch_file,
        "commits_file": commits_file,
        "tag_name": git_info.get("tag_name"),
        "commit_hash": git_info.get("commit_hash"),
        "commit_message": git_info.get("commit_message"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(version_dir / "index.json", 'w', encoding='utf-8') as f:
        json.dump(version_index, f, indent=2, ensure_ascii=False)

    # 更新项目根目录 index.json
    new_entry = {
        "version": version,
        "version_dir": f"v{version}",
        "patch_file": patch_file,
        "tag_name": git_info.get("tag_name"),
        "commit_hash": git_info.get("commit_hash"),
        "commit_message": git_info.get("commit_message"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    data["versions"].insert(0, new_entry)

    # commits 按版本分组存到根级别（合并，不是替换）
    existing_commits = data.get("commits", {})
    existing_commits[version] = [
        {"hash": c["hash"], "short_hash": c["short_hash"], "message": c["message"]}
        for c in commits_info
    ]
    data["commits"] = existing_commits

    # --commit 时：生成 changelog 后 amend 合并
    if auto_commit:
        write_index(changelog_dir, data)

        subprocess.run(["git", "add", str(changelog_dir)], check=True)

        # 撤销上一次的 commit，保留暂存区的代码+changelog
        subprocess.run(["git", "reset", "--soft", "HEAD^"], check=False)

        # 重新提交，合并代码和 changelog
        subprocess.run(["git", "commit", "--amend", "--no-edit"], check=False)

        print(f"[OK] Created: {patch_path}")
        print(f"[OK] Created: {commits_path}")
        print(f"[OK] Updated index.json")
        print(f"[OK] Git reset soft + commit amend done")
    else:
        # 非 --commit 时，只生成 changelog，不自动 amend
        write_index(changelog_dir, data)
        print(f"[OK] Created: {patch_path}")
        print(f"[OK] Created: {commits_path}")
        print(f"[OK] Updated index.json")

    print()
    print(json.dumps(new_entry, indent=2, ensure_ascii=False))


def get_previous_commit(commit_hash):
    """获取指定 commit 的前一个 commit hash"""
    cmd = ["git", "log", "--format=%H", "-1", f"{commit_hash}^"]
    return run_git_cmd(cmd) or None


def rescan_version(changelog_dir, package_path, version):
    """重新扫描指定版本"""
    data = read_index(changelog_dir)

    # 查找版本
    target_entry = None
    for entry in data["versions"]:
        if entry["version"] == version:
            target_entry = entry
            break

    if target_entry is None:
        print(f"[ERROR] 版本 {version} 不存在")
        sys.exit(1)

    version_dir = changelog_dir / f"v{version}"

    # 读取版本自身的 index.json（获取 commits_file 等字段）
    version_index_file = version_dir / "index.json"
    if version_index_file.exists():
        with open(version_index_file, 'r', encoding='utf-8') as f:
            version_index_data = json.load(f)
    else:
        version_index_data = {}

    # 用版本自身的 commit_hash 的前一个 commit 作为基准
    base_commit = get_previous_commit(target_entry["commit_hash"])
    if not base_commit:
        print("[WARNING] 该版本为仓库首个 commit，无前一个 commit，patch 将为空")
        changelog = ""
    else:
        changelog = get_diff(package_path, base_commit, use_cached=False)
        if not changelog:
            print("[WARNING] patch 为空，可能是该版本没有对应目录的改动")

    patch_path = version_dir / target_entry["patch_file"]
    with open(patch_path, 'w', encoding='utf-8') as f:
        f.write(changelog)

    # 重新生成 commits.json
    commits_info = get_commits_details(package_path, base_commit)
    commits_path = version_dir / "commits.json"
    with open(commits_path, 'w', encoding='utf-8') as f:
        json.dump(commits_info, f, indent=2, ensure_ascii=False)

    # 更新版本自身的 index.json（tag_name 取版本 commit 上的标签）
    version_index = {
        "version": version,
        "patch_file": target_entry["patch_file"],
        "commits_file": version_index_data.get("commits_file", "commits.json"),
        "tag_name": get_git_info(target_entry["commit_hash"]).get("tag_name"),
        "commit_hash": target_entry["commit_hash"],
        "commit_message": target_entry["commit_message"],
        "created_at": target_entry["created_at"],
    }
    with open(version_dir / "index.json", 'w', encoding='utf-8') as f:
        json.dump(version_index, f, indent=2, ensure_ascii=False)

    # 更新根目录 index.json 的版本条目 tag_name（改为列表）
    for entry in data["versions"]:
        if entry["version"] == version:
            entry["tag_name"] = get_git_info(target_entry["commit_hash"]).get("tag_name")
            break

    # 更新根目录 commits 列表，改为按版本分组
    # 兼容旧格式（列表）和新格式（字典）
    raw_commits = data.get("commits", {})
    if isinstance(raw_commits, list):
        existing_commits = {}
    else:
        existing_commits = raw_commits
    existing_commits[version] = [
        {"hash": c["hash"], "short_hash": c["short_hash"], "message": c["message"]}
        for c in commits_info
    ]
    data["commits"] = existing_commits

    write_index(changelog_dir, data)

    print(f"[OK] Rescanned: {patch_path}")
    print(f"[OK] Rescanned: {commits_path}")
    print(f"[OK] Updated index.json")


def main():
    parser = argparse.ArgumentParser(description="根据 git diff 自动生成 CHANGELOG patch")
    parser.add_argument('--path', '-p', required=True, help='指定检测路径')
    parser.add_argument('--output', '-o', required=True, help='指定 CHANGELOG 目录')
    parser.add_argument('--version', '-v', help='生成新版本')
    parser.add_argument('--commit', action='store_true', help='生成 changelog 后自动 amend 合并到同一 commit')
    parser.add_argument('--reset', action='store_true', help='清空 git 暂存区（git reset HEAD）')
    parser.add_argument('--yes', '-y', action='store_true', help='删除时跳过确认提示')
    parser.add_argument('--from', dest='from_commit', help='指定起始 commit（配合 --to 使用）')
    parser.add_argument('--to', dest='to_commit', help='指定结束 commit（配合 --from 使用）')
    parser.add_argument('--delete', '-d', help='删除版本')
    parser.add_argument('--rescan', '-r', help='重新扫描版本')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有版本')
    parser.add_argument('--show', '-s', help='显示指定版本信息')

    args = parser.parse_args()

    root = Path(__file__).parent
    package_path = args.path.rstrip('/') + '/'
    changelog_dir = root / args.path.rstrip('/') / args.output.rstrip('/')

    # 确保目录存在
    changelog_dir.mkdir(parents=True, exist_ok=True)

    # 列表模式
    if args.list:
        list_versions(changelog_dir)
        return

    # 显示指定版本
    if args.show:
        show_version(changelog_dir, args.show)
        return

    # 清空 git 暂存区
    if args.reset:
        subprocess.run(["git", "reset", "HEAD"], check=False)
        print("[OK] Git reset HEAD (staging cleared)")
        return

    # 删除版本
    if args.delete:
        delete_version(changelog_dir, args.delete, force=args.yes)
        return

    # 重新扫描版本
    if args.rescan:
        rescan_version(changelog_dir, package_path, args.rescan)
        return

    # 生成新版本（指定 commit 区间）
    if args.version and args.from_commit:
        add_version_by_range(changelog_dir, package_path, args.version, args.from_commit, args.to_commit)
        return

    # 生成新版本
    if args.version:
        add_version(changelog_dir, package_path, args.version, auto_commit=args.commit)
        return

    # 没有指定操作
    print("错误：必须指定 -v、-d、-r、-l 或 -s")
    print()
    print("用法示例：")
    print("  生成版本: -v 0.5.3")
    print("  生成版本并自动 amend: -v 0.5.3 --commit")
    print("  指定 commit 区间: -v 0.5.3 --from abc123 --to def456")
    print("  指定起始 commit（到 HEAD）: -v 0.5.3 --from abc123")
    print("  删除版本: -d 0.5.3")
    print("  重新扫描: -r 0.5.3")
    print("  清空暂存区: --reset")
    print("  列出版本: -l")
    print("  显示版本: -s 0.5.3")
    sys.exit(1)


if __name__ == "__main__":
    main()
