import os
import shutil
import filecmp
import argparse

IGNORE_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}

def should_ignore(name):
    return name in IGNORE_FILES

def sync_folders(master, target):
    print(f"[init] syncing from '{master}' to '{target}'")
    _sync(master, target)
    _clean(master, target)
    print(f"[done] sync complete")

def _sync(master, target):
    if not os.path.exists(target):
        print(f"[mkdir] creating target directory: {target}")
        os.makedirs(target)

    entries = set(os.listdir(master)) - IGNORE_FILES
    for name in sorted(entries):
        m_path = os.path.join(master, name)
        t_path = os.path.join(target, name)

        if should_ignore(name):
            print(f"[skip] ignoring: {name}")
            continue

        if os.path.isdir(m_path):
            print(f"[descend] entering directory: {m_path}")
            _sync(m_path, t_path)
        else:
            if not os.path.exists(t_path):
                print(f"[copy-new] {m_path} -> {t_path}")
                shutil.copy2(m_path, t_path)
            elif not filecmp.cmp(m_path, t_path, shallow=False):
                print(f"[copy-diff] {m_path} -> {t_path} (was different)")
                shutil.copy2(m_path, t_path)

def _clean(master, target):
    if not os.path.exists(target):
        return

    master_entries = set(os.listdir(master))
    target_entries = set(os.listdir(target))

    for name in sorted(target_entries - master_entries):
        if should_ignore(name):
            print(f"[skip] ignoring extra: {name}")
            continue

        t_path = os.path.join(target, name)
        if os.path.isdir(t_path):
            print(f"[remove-dir] removing extra directory: {t_path}")
            shutil.rmtree(t_path)
        else:
            print(f"[remove-file] removing extra file: {t_path}")
            os.remove(t_path)

    for name in sorted(master_entries & target_entries):
        if should_ignore(name):
            continue
        m_path = os.path.join(master, name)
        t_path = os.path.join(target, name)
        if os.path.isdir(m_path) and os.path.isdir(t_path):
            print(f"[descend-clean] checking common subdir: {name}")
            _clean(m_path, t_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("sync")
    parser.add_argument("master_folder")
    parser.add_argument("target_folder")
    args = parser.parse_args()

    sync_folders(args.master_folder, args.target_folder)