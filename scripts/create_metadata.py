from sentinel_preprocess.crop_manager import crop_manager
from pathlib import Path
from glob import glob
import os


def main(root_in, root_out):
    safe_list = glob(os.path.join(root_in, '*.SAFE'))
    if len(safe_list) > 0:
        df_meta = crop_manager().create_metada(safe_list[0])

        Path(root_out).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(root_out, 'metadata.json'), 'w') as file:
            file.write(df_meta.to_json())
            print('Finish!')
    else:
        print('Empty folder!')


if __name__ == "__main__":
    root_data_in = '/storage2/0/Sentinel/2/T32TMQ'
    root_data_out = '/storage2/1/Sentinel2-crops/T32TMQ'

    main(root_data_in, root_data_out)
