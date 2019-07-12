import datetime
import os
import time
from typing import Union, cast

from pynamodb.attributes import BooleanAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model


class SupportsGet(GlobalSecondaryIndex):
    def get(self, hash_key: Union[str, int]) -> 'Stream':
        ...

def make_user_id_index() -> SupportsGet:
    class UserIDIndex(SupportsGet):
        class Meta:
            index_name = 'user_id_index'
            projection = AllProjection()
            read_capacity_units = 1
            write_capacity_units = 1

        user_id = NumberAttribute(attr_name='user_id', hash_key=True)

        def get(self, hash_key: Union[str, int]) -> 'Stream':
            """ :rtype: User """
            try:
                # noinspection PyTypeChecker
                return cast('Stream', next(self.query(hash_key)))
            except StopIteration:
                raise Stream.DoesNotExist(f'Stream with user_id={hash_key} does not exist')
    return UserIDIndex()

class Stream(Model):
    class Meta:
        table_name = os.environ.get('STREAM_TABLE', 'overtrack_ingest_streams')
        region = os.environ.get('DYNAMODB_REGION', 'us-west-2')

    user_id_index = make_user_id_index()

    key = UnicodeAttribute(hash_key=True)
    user_id = NumberAttribute()
    stream_name = UnicodeAttribute()
    time = NumberAttribute()

    # latest connection or disconnection from the client streaming
    latest_connection = NumberAttribute()
    # ip of the client streaming
    ip = UnicodeAttribute()
    # whether the client is currently streaming (published)
    live = BooleanAttribute()
    type = UnicodeAttribute(default='rtmp')

    # latest heartbeat from the worker processing this stream
    latest_heartbeat = NumberAttribute()
    # id of the current worker
    current_worker = NumberAttribute(null=True)
    worker_log_name = UnicodeAttribute(null=True)

    files_uploaded = NumberAttribute(default=0)
    bytes_uploaded = NumberAttribute(default=0)

    @property
    def user(self) -> str:
        return self.key.split('/')[0]

    @property
    def timestamp(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(self.time)

    def archive(self, reason: str) -> None:
        StreamArchive(
            key=self.key,
            user_id=self.user_id,
            stream_name=self.stream_name,
            time=self.time,
            latest_connection=self.latest_connection,
            ip=self.ip,
            live=self.live,
            latest_heartbeat=self.latest_heartbeat,
            current_worker=self.current_worker,
            worker_log_name=self.worker_log_name,
            files_uploaded=self.files_uploaded,
            bytes_uploaded=self.bytes_uploaded,

            disconnect_reason=reason,
            duration=time.time() - self.time
        ).save()
        self.delete()


class StreamArchive(Model):
    class Meta:
        table_name = os.environ.get('STREAM_ARCHIVE_TABLE', 'overtrack_ingest_streams_archive')
        region = os.environ.get('DYNAMODB_REGION', 'us-west-2')

    user_id_index = make_user_id_index()
    key = UnicodeAttribute(hash_key=True)
    user_id = NumberAttribute()
    stream_name = UnicodeAttribute()
    time = NumberAttribute()
    latest_connection = NumberAttribute()
    ip = UnicodeAttribute()
    live = BooleanAttribute()
    latest_heartbeat = NumberAttribute()
    current_worker = NumberAttribute(null=True)
    worker_log_name = UnicodeAttribute(null=True)
    files_uploaded = NumberAttribute(default=0)
    bytes_uploaded = NumberAttribute(default=0)

    duration = NumberAttribute()
    disconnect_reason = UnicodeAttribute()


def main() -> None:
    # StreamArchive.create_table(read_capacity_units=1, write_capacity_units=1)
    for u in Stream.user_id_index.query(303577352):
        print(u)
    print(Stream.user_id_index.get(303577352))


if __name__ == '__main__':
    main()
