import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

parser = argparse.ArgumentParser(
    description="Parses each log file in specified directory "
                "and creates graphs to summarize results"
)
parser.add_argument("-d", "--directory", type=str, default=None,
                    help="Directory in which log files are "
                         "contained. All log files in the "
                         "directory will be parsed and visualized")
parser.add_argument("-f", "--file", type=str, default=None,
                    help="Path to a single log file")
parser.add_argument("-doh", "--datetime-one-hot", type=int, default=None,
                    help="Let the date & time features be loaded as one-hot")
parser.add_argument("-woh", "--weekdays-one-hot", type=int, default=None,
                    help="Let the week-of-the-day feature be loaded as one-hot")
parser.add_argument("--loc-id", dest='loc_id', type=int, default=None,
                    help="Let the zone IDs be excluded from the dataset")

def num_or_str(string):
    tokens = string.split(".")
    if len(tokens) == 1 and tokens[0].isnumeric():
        return int(string)
    else:
        is_float = True
        for item in tokens:
            if not item.isnumeric():
                is_float = False
                break
        if is_float:
            return float(string)
    return string

def parse_config(cfg_strings):
    cfg_dict = {}
    cfg_str = ", ".join(cfg_strings)
    cfg_dict['str'] = cfg_str
    configs = cfg_str.split(", ")
    for cfg in configs:
        cfg_name, cfg_val = cfg.split(": ")
        if cfg_val == "True":
            cfg_val = 1
        elif cfg_val == "False":
            cfg_val = 0
        else:
            cfg_val = num_or_str(cfg_val)
        cfg_dict[cfg_name] = cfg_val
    return cfg_dict

def parse_losses(loss_strings):
    loss_tuples = []
    for loss_str in loss_strings:
        tokens = loss_str.split()
        if len(tokens) == 9:
            iter_idx = int(tokens[2][:-1])
            val_loss = float(tokens[5][:-1])
            train_loss = float(tokens[8])
        elif len(tokens) == 8:
            iter_idx = int(tokens[1][1:-1])
            val_loss = float(tokens[4][:-1])
            train_loss = float(tokens[7])
        else:
            raise ValueError
        loss_tuples.append((iter_idx,train_loss,val_loss))
    return np.asarray(loss_tuples)

def read_file_by_line_and_close(fp):
    lines = []
    line = fp.readline()
    while line:
        lines.append(line.rstrip())
        line = fp.readline()
    fp.close()
    return lines

def parse_stats_in_dir(dir_path):
    stats = []
    for fname in os.listdir(dir_path):
        fpath = os.path.join(dir_path,fname)
        if os.path.isfile(fpath):
            fp = open(fpath,'r')
            lines = read_file_by_line_and_close(fp)
            stats.append(
                [parse_config(lines[:4]), parse_losses(lines[5:-1]), fname]
                )
            
    return stats

def return_smallest(stats, doh=None, woh=None, loc_id=None):
    min_val_loss = 1000000
    min_cfg = None
    min_idx = -1
    min_iter = -1
    min_name = None
    check = doh is not None or woh is not None \
            or loc_id is not None
    for idx, (cfg, losses, fname) in enumerate(stats):
        min_it = np.argmin(losses[:,-1])
        if losses[min_it,-1] < min_val_loss:
            if check and (cfg['datetime_one_hot'] != doh or \
                cfg['weekdays_one_hot'] != woh or \
                cfg['loc_id'] != loc_id):
                continue
            min_val_loss = losses[min_it,-1]
            min_cfg = cfg
            min_idx = idx
            min_iter = min_it
            min_name = fname
    return min_val_loss, min_idx, min_iter, min_cfg, min_name

def main():
    args = parser.parse_args()
    if args.file is not None:
        fp = open(args.file,'r')
        lines = read_file_by_line_and_close(fp)
        print(parse_config(lines[:4]))
        print(parse_losses(lines[5:-1]))
    if args.directory is not None:
        stats = parse_stats_in_dir(args.directory)
        min_val_loss, min_idx, min_iter, min_cfg, min_name \
            = return_smallest(stats,
                              doh=args.datetime_one_hot,
                              woh=args.weekdays_one_hot,
                              loc_id=args.loc_id,)
        print(f"[{min_name}]: {min_val_loss} at {min_iter+1}")
        print(min_cfg)

if __name__ == "__main__":
    main()
