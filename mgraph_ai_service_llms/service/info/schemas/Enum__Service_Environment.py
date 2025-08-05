from enum import Enum


class Enum__Service_Environment(Enum):
    aws_lambda : str = 'aws-lambda'
    local      : str = 'local'