"""Config loader for train/test splits. Usage: get_split('70') returns (train_files, test_files)"""

import os, yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).parent
with open(CONFIG_DIR / "data_splits.yaml") as f:
    _cfg = yaml.safe_load(f)
DATA_DIR = CONFIG_DIR.parent / _cfg['data_dir']

def _expand(file_ids):
    """Expand file IDs to full file paths."""
    return [str(DATA_DIR / _cfg['files'][fid]) for fid in file_ids]

def get_split(pct: str):
    """Get (train_files, test_files) for split '30', '50', or '70'."""
    return _expand(_cfg['splits'][pct]), _expand(_cfg['test'])

def get_split_with_labels(pct: str):
    """Get ((path, label), ...) tuples. Label: 'malicious' if CF, else 'benign'."""
    label = lambda f: 'malicious' if '_CF_' in f else 'benign'
    train, test = get_split(pct)
    return [(f, label(f)) for f in train], [(f, label(f)) for f in test]

if __name__ == "__main__":
    for p in ['30', '50', '70']:
        tr, te = get_split(p)
        print(f"{p}%: train={len(tr)} test={len(te)}")
        tr_lab, te_lab = get_split_with_labels(p)
        print(f"{p}% labeled:")
        print(f"  train (count={len(tr_lab)}):")
        for path, label in tr_lab:
            print(f"    {path} {label}")
        print(f"  test (count={len(te_lab)}):")
        for path, label in te_lab:
            print(f"    {path} {label}")
