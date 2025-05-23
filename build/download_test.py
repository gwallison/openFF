
# -*- coding: utf-8 -*-
"""
Mar 2024
@author: Gary

This script is used to download a new raw set, and save it, then compare it to a previous
archive.  Summary will be saved in an archive.

This script runs independently of the main build_database set.  It is designed 
to run autonomously.

A new csv zip file is downloaded into test_dir and a new raw_df is created.
We bring up the most recent archive raw (if available; otherwise create one from archived zip)

Then compare the two
Save the results, including to google drive
Move files from today_dir to archives
Clear today_dir
"""
import pandas as pd
import os
import shutil
import requests
from datetime import datetime

import sys
sys.path.insert(0,'c:/MyDocs/integrated/') # adjust to your setup
import ff_archive_tools.Data_reader as dreader
import ff_archive_tools.Meta_reader as mreader

import openFF.build.core.fetch_archive_difference_set as fads

production_computer = 'M2'  # set to the computer name performing production tasks


today = datetime.today()

st = datetime.now() # start timer


# define    
data_dir = r"C:\MyDocs\integrated\openFF_archive"
data_dir = r"G:\My Drive\production\openFF_archive"

bulk_dir = os.path.join(data_dir,'FF_bulk_data')
raw_dir = os.path.join(data_dir,'raw_dataframes')
out_dir = os.path.join(data_dir,'diff_dicts')
test_dir = os.path.join(data_dir,'test')

test_zip_fn = 'test_zip.zip'
test_raw_fn = 'test.parquet'

afile = f'ff_archive_{today.strftime("%Y-%m-%d")}.zip'
rawfn = f'raw_df_{today.strftime("%Y-%m-%d")}.parquet'
outfn = f'diff_dict_{today.strftime("%Y-%m-%d")}.pkl'



class Log_it():
    def __init__(self):
        import platform
        self.log_fn = r"G:\My Drive\webshare\daily_status\current_status.txt"
        self.buffer = f'Logging from {platform.node()}\n'

    def logline(self,txt):
        self.buffer += txt + '\n'
        print(txt)

    def get_online_log(self):
        with open(self.log_fn,'r') as f:
            self.alllog = f.read()
        
    def update_log(self):
        self.get_online_log()
        with open(self.log_fn, 'w') as f:
            f.write(self.buffer)
            f.write('\n*****************\n')
            f.write(self.alllog)

lg = Log_it()
lg.logline(f'\nNew download and comparison: {st}\n')

def fetch_new_archive(lg=lg):
    if os.path.exists(os.path.join(test_dir,test_zip_fn)):
        print(f'{test_zip_fn} already exists; skipping download ')
        return
    url = 'https://www.fracfocusdata.org/digitaldownload/FracFocusCSV.zip' # new as of 2/2024
    lg.logline(f'Downloading data from {url}')
    r = requests.get(url, allow_redirects=True,timeout=20.0)
    open(os.path.join(test_dir,test_zip_fn), 'wb').write(r.content)
    lg.logline(f'Archive written to {test_zip_fn}')

def get_old_df_fn(lg=lg):
    # get previously raw df
    rlst = os.listdir(raw_dir)
    try:
        last_fn =os.path.join(raw_dir,rlst[-1])
        # oldraw = pd.read_parquet(last_fn)  
        return last_fn
    except: 
        last_archive = os.listdir(bulk_dir)[-1]
        rdr = dreader.Make_DF_From_Archive(in_name=last_archive, zipdir=bulk_dir,outset_dir=raw_dir)
        oldraw = rdr.import_raw_FFV4(verbose=True)
        or_fn = 'raw_'+ last_archive[11:-4] + '.parquet'  
        oldraw.to_parquet(os.path.join(raw_dir,or_fn))
        # print(f' "old" data from : {or_fn}')
        return os.path.join(raw_dir,or_fn)


def get_new_df_fn(lg=lg):
    # if raw file already exists, just use it.
    test_fn = os.path.join(test_dir,test_raw_fn)
    if os.path.exists(test_fn):
        print('fetching already existing df')
        return test_fn
    lg.logline(f'Reading data into : {test_fn}')
    rdr = dreader.Make_DF_From_Archive(in_name=test_zip_fn, zipdir=test_dir,outset_dir=test_dir)
    newraw = rdr.import_raw_FFV4(verbose=True)
    newraw_fn = os.path.join(test_dir,test_raw_fn)
    newraw.to_parquet(newraw_fn)
    return newraw_fn

def compare_raw(new_raw_fn,old_raw_fn):
    print('Performing old vs. new comparison')
    return fads.get_difference_set(old_raw_fn,new_raw_fn,df_ver=4)

def archive_test_files(outdict,oldfn,newfn,lg=lg):
    import pickle
    outdict['early_fn'] = oldfn
    outdict['current_fn'] = newfn
    lg.logline(f'Transfering test files to: {rawfn}, {afile}, {outfn}')
    shutil.move(os.path.join(test_dir,test_raw_fn),
                os.path.join(raw_dir,rawfn))
    shutil.move(os.path.join(test_dir,test_zip_fn),
                os.path.join(bulk_dir,afile))
    with open(os.path.join(out_dir,outfn),'wb') as f:
        pickle.dump(outdict,f)

def update_pub_delay(lg=lg):
    obj = mreader.Make_Meta_From_Archive(zipdir = bulk_dir)
    _ = obj.update_pub_delay_df(archive_dirs=[bulk_dir],
                                verbose=False)
    lg.logline('Completed update of publication date dataframe')
    
# def eval_gsutil_command(command):
#   """Evaluates a gsutil command and returns the output.
#   Args:
#     command: The gsutil command to evaluate.
#   Returns:
#     The output of the gsutil command.
#   """
#   import subprocess
#   process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
#   output, _ = process.communicate()
#   return output.decode('utf-8')

def upload_file_to_bucket(bucket_name, blob_name, file_path,lg=lg):
    """Uploads a file to the specified bucket."""
    from google.cloud import storage
    from time import sleep  
    # Set the project ID as an environment variable
    os.environ["GOOGLE_CLOUD_PROJECT"] = "open-FF-catalog"
    try:      
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
          
        lg.logline(f"File {file_path} uploaded to {bucket_name}/{blob_name}")
    except:
        lg.logline(f"Upload problem with {file_path}, trying again:")
        try:      
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(file_path)
              
            lg.logline(f"File {file_path} uploaded to {bucket_name}/{blob_name}")
        except:
            lg.logline("Didn't work again.  Moving on after pause...")
            sleep(3)
    
def notebook_to_google_drive(lg=lg,move_to_storage=True):
    import openFF.common.nb_helper as nbh
    import openFF.common.handles as hndl 
    import os
    import platform
    
    if platform.node() == production_computer:           
        lg.logline('Performing generation of Raw_disclosures.html')
        fn = 'Raw_disclosures.html'
        fulloutfn = os.path.join(r"G:\My Drive\webshare\daily_status",fn)
        nbh.make_notebook_output(nb_fn=os.path.join(hndl.browser_nb_dir,'Raw_disclosures.ipynb'),
                                    output_fn=fulloutfn)
    else:
        print(f'No notebook generation for computer: {platform.node()}')

    # Now let's move that same file to the google storage spot
    if move_to_storage:
        upload_file_to_bucket(bucket_name='open-ff-browser', 
                              blob_name='Raw_disclosures.html', 
                              file_path=fulloutfn)

def difflib_to_google_drive(lg=lg):
    """This routine moves all files from google drive location to browser space
    It is presumed that each file is a new file, so that we don't upload the
    whole set every day."""
    import openFF.common.handles as hndl 
    import os
    import shutil
    import platform
    
    drive_dir = r"G:\My Drive\webshare\daily_status\diff_files"
    drive_bu = r"G:\My Drive\webshare\daily_status\diff_files_backup"
    storage_prefix = 'difflib/'
    
    if platform.node() == production_computer:           
        lg.logline('Performing move of difflib files to google storage')
        flst = os.listdir(drive_dir)
        cntr = 0
        for f in flst:
            if (f[-5:] == '.html'):
                fn = os.path.join(drive_dir,f)
                bname = storage_prefix+f
                upload_file_to_bucket(bucket_name='open-ff-browser', 
                                      blob_name=bname, 
                                      file_path=fn)
                # now move drive file to the backup drive dir to clear out diff dir
                shutil.move(fn,
                            os.path.join(drive_bu,f))
                cntr += 1

        lg.logline(f'  -- number of files uploaded: {cntr}')
    else:
        print(f'No moving difflib files for computer: {platform.node()}')

    
    
def main_run():
        old_raw_fn = get_old_df_fn()
        fetch_new_archive()
        new_raw_fn = get_new_df_fn()
        lg.logline(f'OLD: {old_raw_fn}')
        lg.logline(f'NEW: {new_raw_fn}')
    
        out = compare_raw(new_raw_fn,old_raw_fn)
        lg.logline(f'\n\n  Column status: {out["columns"]}')
        lg.logline(f'  Number of differing records: {out["num_diff_records"]}')
        lg.logline(f'  New disclosures:     {len(out["added_disc"])}')
        lg.logline(f'  Changed disclosures: {len(out["changed_disc"])}')
        lg.logline(f'  Removed disclosures: {len(out["removed_disc"])}')
        archive_test_files(out, old_raw_fn,new_raw_fn)
        update_pub_delay()
        
        # make Raw_disclosures html
        notebook_to_google_drive()
        
        # move new difflib files to google storage
        difflib_to_google_drive()

    

if __name__ == '__main__':
    use_exception = True
    if use_exception:
        try:
            main_run()
        except:
            lg.logline('***EXCEPTION THROWN***')
    else:
        main_run()
        
    endit = datetime.now()
    lg.logline(f'\nProcess completed in {endit-st}\n')
    lg.update_log()