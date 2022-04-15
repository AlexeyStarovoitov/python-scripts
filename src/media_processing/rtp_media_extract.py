import os
import sys
import pyshark
import subprocess
import pathlib

if __name__ == "__main__":
    media_aligned = 0
    strm_type = "a"
    output_dir = pathlib.Path("../", "output_vectors")

    argc = len(sys.argv)
    if argc < 3:
        print("There is no filename")
        exit()
    argv_iter = iter(sys.argv)
    for arg in argv_iter:
        if arg == "-i":
            filename = next(argv_iter)
        elif arg == "-dst":
            dst_ip = next(argv_iter)
        elif arg == "-a":
            media_aligned = 1
        elif arg == "-s":
            strm_type = next(argv_iter)
        elif arg == "-o":
            output_dir = pathlib.Path(next(argv_iter))

    ifilename = str(pathlib.Path(filename))
    print(ifilename)

    if output_dir.is_dir() == False:
        output_dir.mkdir(output_dir, mode=0o666)

    tshark_cmd=f"tshark -r {ifilename} -q -p -o rtp.heuristic_rtp:TRUE -z rtp,streams -Y udp"
    tshark_stat_file = "tshark_stat.txt"
    f = open(tshark_stat_file, "w")
    subprocess.call(tshark_cmd, stdout=f)
    f.close()
    f = open(tshark_stat_file, "r")
    tshark_stat = f.readlines()
    f.close()
    os.remove(tshark_stat_file)

    header = "".join((tshark_stat[1].split()))
    header = header.upper()
    header_template = ['STARTTIME', 'ENDTIME', 'SRCIPADDR',  'PORT', 'DESTIPADDR',  'PORT', 'SSRC', 'PAYLOAD', 'PKTS', 'LOST', 'MAXDELTA(MS)', 'MAXJITTER(MS)', 'MEANJITTER(MS)',  'PROBLEMS?']
    header_fields = []
    while len(header):
        for tmpl in header_template:
            if header.find(tmpl)==0:
                break
        header_fields.append(tmpl)
        header = header.replace(tmpl, "", 1)

    av_stream_params = []


    acodecs_init = ['AAC', 'G711A', 'G711U', 'G719', 'G722', 'G7221', 'G7231', 'G726', 'G729A', 'OPUS']
    acodecs_ffmpeg = ['aac', 'alaw', 'mulaw', 'none', 'adpcm_g722', 'none', 'g723_1', 'adpcm_g726', 'none', 'libopus']
    acodecs = list(zip(acodecs_init, acodecs_ffmpeg))
    av_strt_times = []
    for rtp_str in tshark_stat:
        if rtp_str in (tshark_stat[0:2] + [tshark_stat[-1]]):
            continue
        rtp_str_fields = rtp_str.split()
        lost_field_index = header_fields.index('LOST')
        rtp_str_fields = rtp_str_fields[0:lost_field_index]+["".join(rtp_str_fields[lost_field_index:lost_field_index+2])]+rtp_str_fields[lost_field_index+2:]
        payload_type = rtp_str_fields[header_fields.index('PAYLOAD')].upper()
        if rtp_str_fields[header_fields.index('DESTIPADDR')] == dst_ip:
            if strm_type == "a" and (payload_type not in acodecs_init or acodecs[acodecs_init.index(payload_type)][1] == 'none'):
                continue
            dst_port = int(rtp_str_fields[header_fields.index('DESTIPADDR')+1])
            av_media_file_type = "aligned" if media_aligned == 1 else "init"
            av_media_file_name = f"av_{dst_ip}_{dst_port}_{rtp_str_fields[header_fields.index('SSRC')]}_{av_media_file_type}.{payload_type}"
            av_media_file_path = str(pathlib.Path(str(output_dir), av_media_file_name))
            f = open(av_media_file_path, "wb")
            av_media_decfile_path = f"{av_media_file_path}_s16le_{av_media_file_type}.raw"
            strt_time = float(rtp_str_fields[header_fields.index('STARTTIME')])
            av_strt_times.append(strt_time)
            av_cur_params = dict(ssrc=rtp_str_fields[header_fields.index('SSRC')], strt_time=strt_time, dst_port=dst_port, payload=payload_type, f=f, fpath=av_media_file_path, fdecpath=av_media_decfile_path)
            av_stream_params.append(av_cur_params)

    max_strt_time = max(av_strt_times) if media_aligned == 1 else min(av_strt_times)
    for i, av_stream in enumerate(av_stream_params):
        cap = pyshark.FileCapture(
            input_file=ifilename,
            display_filter=f'ip.dst=={dst_ip} && udp.dstport=={av_stream["dst_port"]} && rtp.ssrc=={av_stream["ssrc"]} && frame.time_relative >= {max_strt_time}')
        for pkt in cap:
            av_stream['f'].write(pkt.rtp.payload.main_field.binary_value)
        av_stream['f'].close()
        cap.close()
        if strm_type == "a":
            if av_stream['payload'] in [acodecs_init[acodecs_init.index('G711A')], acodecs_init[acodecs_init.index('G711U')]]:
                acodec_cmd = f"-f {acodecs[acodecs_init.index(av_stream['payload'])][1]} -ar 8000 -ac 1"
            else:
                acodec_cmd = f"-c:a {acodecs[acodecs_init.index(av_stream['payload'])][1]}"
            ffmpeg_cmd = f"ffmpeg -y {acodec_cmd} -i {av_stream['fpath']} -ar 48000 -ac 1 -f s16le {av_stream['fdecpath']}"
            subprocess.call(ffmpeg_cmd)
            #av_stream['fdeclen'] = pathlib.Path(av_stream['fdecpath']).stat().st_size
            #av_stream_params[i] = av_stream
            #pathlib.Path(av_stream['fpath']).unlink()
