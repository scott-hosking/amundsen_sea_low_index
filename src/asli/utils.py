import contextlib
import joblib
import os
import sys
import configparser
from pathlib import Path


# https://stackoverflow.com/questions/24983493/tracking-progress-of-joblib-parallel-execution
@contextlib.contextmanager
def tqdm_joblib(tqdm_object):
    """Context manager to patch joblib to report into tqdm progress bar given as argument"""

    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        def __call__(self, *args, **kwargs):
            tqdm_object.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old_batch_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_batch_callback
        tqdm_object.close()

def configure_s3_bucket(
        s3_config_filepath: str,
        s3_config_filename: str
        ):
    """
    Configures S3 bucket using a config file.
    
    configfile_filepath(str): location of s3 config file, needs to contain 'secret_key', 'access_key' and 'host_bucket' (without https:// prefix)
    """
    import s3fs
    config = configparser.ConfigParser()
    config_file = os.path.join(s3_config_filepath, s3_config_filename)
    config.read(config_file)
    s3_store_credentials = config['default']

# Populating s3fs s3 connection using the .s3cfg config file
    s3_connection = s3fs.S3FileSystem(
        anon=False,
        secret=s3_store_credentials['secret_key'],
        key=s3_store_credentials['access_key'],
        client_kwargs={'endpoint_url': "https://" + s3_store_credentials['host_bucket']}
    )

    return s3_connection
