from osbot_aws.aws.s3.S3__DB_Base                       import S3__DB_Base
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_aws.aws.s3.S3__Virtual_Storage               import Virtual_Storage__S3
from mgraph_ai_service_llms.config                      import LLM__CACHE__DEFAULT__ROOT_FOLDER, LLM__CACHE__BUCKET_NAME__PREFIX, LLM__CACHE__BUCKET_NAME__SUFFIX


class LLM__Cache(Virtual_Storage__S3):
    root_folder: Safe_Str__File__Path = LLM__CACHE__DEFAULT__ROOT_FOLDER                     # Prefix for all stored files in S3
    s3_db      :  S3__DB_Base

    def __init__(self):
        super().__init__()
        with self.s3_db as _:
            _.bucket_name__prefix = LLM__CACHE__BUCKET_NAME__PREFIX
            _.bucket_name__suffix = LLM__CACHE__BUCKET_NAME__SUFFIX

    def setup(self):
        self.s3_db.setup()
        return self
