import os
import argparse
import ffmpeg
import pandas as pd


def assemble_movie_file(dg, file_dir):
    fname = "files_to_combine.txt"
    files = []
    with open(fname, "w") as f:
        for kk, row in dg.iterrows():
            directory = os.path.dirname(row["fname"])
            base = os.path.basename(row["fname"])
            final_fname = f"{file_dir}/out/{base.replace('.MOV', '_ac.mp4')}"
            ant = f"""ffmpeg -y -i {row["fname"]} -vf "drawtext=text='{base}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2" -codec:a copy -y {final_fname}"""
            ant = f"""ffmpeg -y -i {row["fname"]} -vf "drawtext=text='{base}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2" -acodec aac -strict -2 -b:a 384k -y {final_fname}"""
            # ant = f"""ffmpeg -y -i {row["fname"]} -acodec aac -strict -2 -b:a 384k -y {final_fname}"""
            if os.path.isfile(final_fname):
                pass
            else:
                if not os.path.isdir(os.path.dirname(final_fname)):
                    os.makedirs(os.path.dirname(final_fname))
                os.system(ant)
            f.write(f"""file {final_fname}\n""")
            files.append(final_fname)
            dg.loc[kk, "final_fname"] = final_fname
            pass
        pass
    return fname, files


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
    # parser.add_argument('--zipfile', dest='zipfile', required=True)

    # args = parser.parse_args()
    for j in range(10):
        print(j)
        pass

    import os
    import glob
    import time
    for j in range(1000):
        zips = glob.glob('/vols/*.zip')
        print("zips", zips)
        for k, z in enumerate(zips):
            # kick off
            file_dir = f"/vols/tmp_{os.path.basename(z).split('.')[0]}"
            cmd = f'unzip -o {os.path.abspath(z)} -d {file_dir}'
            print(cmd)
            ou = os.system(cmd)
            if ou == 0:
                os.system('rm %s' % os.path.abspath(z))
            else:
                raise Exception(f"ou {ou}")

            df = generate_mov_df(file_dir)
            dg = df[(df["nchannels"] == 1) & (df["rotation"] == 90) &
                    (df["duration"] > 0) & (df["duration"] < 5)].copy()
            fname, files = assemble_movie_file(dg, file_dir)

            ee = os.environ["EXCLUSIONS"].split(',')
            print("ee", ee)

            exclusions = [f"{file_dir}/out/IMG_%d.mp4" % i for i in []]
            final_list = []
            for e0 in exclusions:
                e = e0.replace('.mp4', '_ac.mp4')
                final_list.extend([e0, e])
            exclusions = final_list
            dh = dg[~dg["final_fname"].isin(exclusions)].copy()

            files = dh["final_fname"].values
            results = []
            l, u = 0, 500
            import pdb
            pdb.set_trace()
            if len(files) < u:
                u = len(files)+1
                ou = os.system(f"mkvmerge -o out_{l}_{u}.mkv %s" % (r' \+ '.join(files[l:u])))  # noqa
                results.append(ou)
            print("hh")
        time.sleep(5)
