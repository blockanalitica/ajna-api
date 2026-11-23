BIGINT_MAX = 2**63 - 1


class BucketIndexConverter:
    regex = "[0-9]+"

    def to_python(self, value):
        bucket_index = int(value)
        if bucket_index > BIGINT_MAX:
            raise ValueError("bucket_index out of range")
        return bucket_index

    def to_url(self, value):
        return str(value)
