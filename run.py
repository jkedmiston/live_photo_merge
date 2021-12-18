import os
import argparse
import ffmpeg
import pandas as pd
import glob
import time


def assemble_movie_df(df, file_dir, annotations=True):
    """
    Converts the MOV files into mp4, plus optionally adding the annotation
    in the middle of the movie with the filename, so that it 
    can be excluded in final runs (see .env file)

    The writing of paths to files in files_to_combine is for debugging
    """
    fname = "files_to_combine.txt"
    files = []
    with open(fname, "w") as f:
        for kk, row in df.iterrows():
            base = os.path.basename(row["fname"])
            if annotations:
                final_fname = f"{file_dir}/out/{base.replace('.MOV', '_ac.mp4')}"
            else:
                final_fname = f"{file_dir}/out/{base.replace('.MOV', '.mp4')}"

            if annotations:
                ant = f"""ffmpeg -y -i {row["fname"]} -vf "drawtext=text='{base}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2" -acodec aac -strict -2 -b:a 384k -y {final_fname}"""
            else:
                ant = f"""ffmpeg -y -i {row["fname"]} -acodec aac -strict -2 -b:a 384k -y {final_fname}"""

            if os.path.isfile(final_fname):
                pass
            else:
                if not os.path.isdir(os.path.dirname(final_fname)):
                    os.makedirs(os.path.dirname(final_fname))
                os.system(ant)
            f.write(f"""file {final_fname}\n""")
            files.append(final_fname)
            df.loc[kk, "final_fname"] = final_fname

    return fname, files


def remove_excluded_files_from_df(file_dir, dg, annotations):
    """
    Look in the environ variable EXCLUSIONS (a comma separated list of ints)
    for exclusion list and remove them from the dataframe. 
    """
    exclusion_list = os.environ["EXCLUSIONS"].split(',')
    exclusions = [f"{file_dir}/out/IMG_%s.mp4" %
                  i for i in exclusion_list]
    final_list = []
    for e0 in exclusions:
        if annotations:
            e = e0.replace('.mp4', '_ac.mp4')
        else:
            e = e0
            pass
        final_list.extend([e0, e])
    exclusions = final_list
    dh = dg[~dg["final_fname"].isin(exclusions)].copy()
    return dh


def generate_mov_df(file_dir):
    movs = glob.glob(os.path.join(file_dir, '*.MOV'))
    mov_df = []
    for m in movs[:]:
        out = ffmpeg.probe(m)
        if "rotate" in out["streams"][0]["tags"]:
            rotation = int(out["streams"][0]["tags"]["rotate"])
        else:
            rotation = 0

        if "channels" in out["streams"][0]:
            nchannels = int(out["streams"][0]["channels"])
        elif "channels" in out["streams"][1]:
            nchannels = int(out["streams"][1]["channels"])
        else:
            nchannels = 1

        duration = float(out["format"]["duration"])
        dt = pd.to_datetime(out["format"]["tags"]["creation_time"])
        pst = dt.tz_convert('US/Pacific').replace(tzinfo=None)
        mov_df.append([pst, m, duration, rotation, nchannels])

    df = pd.DataFrame.from_records(
        mov_df, columns=["pst", "fname", "duration", "rotation", "nchannels"])
    df = df.sort_values(by="pst", ascending=True)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser('')
    annotations = int(os.environ["ANNOTATIONS"])
    while 1:
        print("scanning for new zip files")
        zips = glob.glob('/home/videos/*.zip')
        for k, z in enumerate(zips):
            # unzip the file, and process all the videos inside it
            zipf = os.path.basename(z).split('.')[0].replace(' ', '_')

            # delete any existing files
            base_file_dir = f"/home/videos/tmp_{zipf}"
            if os.path.isdir(base_file_dir):
                os.system(f"rm -rf {base_file_dir}")

            zpath = os.path.abspath(z).replace(' ', '\ ')
            cmd = f"unzip -o {zpath} -d {base_file_dir}"
            print(cmd)
            ou = os.system(cmd)
            if os.path.isdir(os.path.join(base_file_dir, 'iCloud Photos')):
                iclouddir = os.path.join(
                    base_file_dir, 'iCloud Photos').replace(' ', '\ ')
                cmd = f"mv {iclouddir} {os.path.join(base_file_dir, 'iCloudPhotos')}"
                os.system(cmd)
                print(cmd)
                file_dir = os.path.join(base_file_dir, 'iCloudPhotos')
            else:
                file_dir = base_file_dir

            if ou == 0:
                os.system('rm %s' % zpath)
            else:
                raise Exception(f"ou {ou}")

            df = generate_mov_df(file_dir)
            # filter for live photos or short videos in the portrait format
            dg = df[(df["nchannels"] == 1) & (df["rotation"] == 90) &
                    (df["duration"] > 0) & (df["duration"] < 5)].copy()
            _, _ = assemble_movie_df(dg, file_dir, annotations=annotations)

            dh = remove_excluded_files_from_df(
                file_dir, dg, annotations=annotations)
            files = dh["final_fname"].values
            # I don't know the exact upper limit here, set to 500 for now.
            l, u = 0, 500
            if len(files) > 500:
                raise Exception("Too many videos for mkvmerge")

            u = len(files)+1
            mkvfile = os.path.join(
                os.path.dirname(base_file_dir), f"out_{zipf}.mkv")
            cmd = f"mkvmerge -o {mkvfile} %s" % (r' \+ '.join(files[l:u]))
            ou = os.system(cmd)  # noqa
            print(f"wrote {mkfile}")

        time.sleep(5)
