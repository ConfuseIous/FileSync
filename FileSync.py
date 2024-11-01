import os
import shutil
import filecmp
import argparse

def sync_folders(master_folder, target_folder):
    # Compare the directory trees
    comparison = filecmp.dircmp(master_folder, target_folder)

    # Copy missing or different files and folders from master to target
    copy_items(master_folder, target_folder, comparison)
    
    # Remove files and folders from target that are not in master
    remove_extra_items(target_folder, comparison)

def copy_items(master_folder, target_folder, comparison):
    # Copy files that are in master but not in target
    for file in comparison.left_only:
        master_path = os.path.join(master_folder, file)
        target_path = os.path.join(target_folder, file)
        if os.path.isdir(master_path):
            if not os.path.exists(target_path):  # Check if target directory already exists
                shutil.copytree(master_path, target_path)
                print(f"Directory copied from {master_path} to {target_path}")
            else:
                # Recursively copy contents if the folder exists
                sub_comparison = filecmp.dircmp(master_path, target_path)
                copy_items(master_path, target_path, sub_comparison)
        else:
            shutil.copy2(master_path, target_path)
            print(f"File copied from {master_path} to {target_path}")
    
    # For music, there's no need to diff files
    # # Update files that are different between master and target
    # for file in comparison.diff_files:
    #     master_path = os.path.join(master_folder, file)
    #     target_path = os.path.join(target_folder, file)
    #     shutil.copy2(master_path, target_path)
    #     print(f"File updated from {master_path} to {target_path}")
    
    # Recursively process subdirectories that are common between master and target
    for sub_dir in comparison.common_dirs:
        new_master_folder = os.path.join(master_folder, sub_dir)
        new_target_folder = os.path.join(target_folder, sub_dir)
        sub_comparison = filecmp.dircmp(new_master_folder, new_target_folder)
        copy_items(new_master_folder, new_target_folder, sub_comparison)

def remove_extra_items(target_folder, comparison):
    # Remove files and directories that are only in the target folder
    for file in comparison.right_only:
        target_path = os.path.join(target_folder, file)
        if os.path.isdir(target_path):
            shutil.rmtree(target_path)
            print(f"Extra directory removed: {target_path}")
        else:
            os.remove(target_path)
            print(f"Extra file removed: {target_path}")
    
    # Recursively process common subdirectories for further extra items
    for sub_dir in comparison.common_dirs:
        new_target_folder = os.path.join(target_folder, sub_dir)
        new_comparison = filecmp.dircmp(os.path.join(comparison.left, sub_dir), new_target_folder)
        remove_extra_items(new_target_folder, new_comparison)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("FileSync")
    parser.add_argument("master_folder", help="Path to the master folder")
    parser.add_argument("target_folder", help="Path to the target folder")
    args = parser.parse_args()

    sync_folders(args.master_folder, args.target_folder)
