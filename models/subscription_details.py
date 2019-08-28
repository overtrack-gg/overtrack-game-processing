import time

from pynamodb.attributes import NumberAttribute, UnicodeAttribute, JSONAttribute, BooleanAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

from models.common import OverTrackModel


class SubscriptionIDIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'subscription_id-index'

        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    subscription_id = UnicodeAttribute(hash_key=True)

    def get(self, hash_key) -> 'SubscriptionDetails':
        try:
            return next(self.query(hash_key))
        except StopIteration:
            raise SubscriptionDetails.DoesNotExist('SubscriptionDetails with subscription_id=%s does not exist' % (hash_key,))


class SubscriptionDetails(OverTrackModel):
    class Meta:
        table_name = 'overtrack-subscription-details'
        region = 'us-west-2'

    subscription_id_index = SubscriptionIDIndex()

    user_id = NumberAttribute(hash_key=True)
    timestamp = NumberAttribute(range_key=True, default=time.time)

    version = NumberAttribute()
    type = UnicodeAttribute()
    subscription_id = UnicodeAttribute()

    full_data = JSONAttribute()

    canceled_timestamp = NumberAttribute(null=True)
    canceled_internally = BooleanAttribute(default=False)


def main() -> None:
    # if not SubscriptionDetails.exists():
    #     SubscriptionDetails.create_table(wait=True, read_capacity_units=1, write_capacity_units=1)
    print(SubscriptionDetails.subscription_id_index.get('I-RDXYLX1CY38D'))


if __name__ == '__main__':
    main()
