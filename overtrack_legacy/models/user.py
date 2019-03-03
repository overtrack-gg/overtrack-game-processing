import os

from pynamodb.attributes import BooleanAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex

try:
    from .util import OverTrackModel, TupleAttribute
except (SystemError, ModuleNotFoundError):
    from util import OverTrackModel, TupleAttribute


class UserIDIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user-id-index'

        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    user_id = NumberAttribute(attr_name='user-id', hash_key=True)

    def get(self, hash_key):
        """ :rtype: User """
        try:
            return next(self.query(hash_key))
        except StopIteration:
            raise User.DoesNotExist('User with user-id=%d does not exist' % (hash_key, ))


# noinspection PyAbstractClass
class User(OverTrackModel):

    class Meta:
        table_name = os.environ.get('USERS_TABLE', 'overtrack_users')
        region = 'us-west-2'

    user_id_index = UserIDIndex()

    battletag = UnicodeAttribute(attr_name='battletag', hash_key=True, null=False)
    username = UnicodeAttribute(attr_name='username', null=True)
    user_id = NumberAttribute(attr_name='user-id', default=0)
    current_sr = NumberAttribute(attr_name='current-sr', null=True)
    twitch_account = UnicodeAttribute(attr_name='twitch-account', null=True)

    nonce = UnicodeAttribute(attr_name='nonce', null=True)
    games_parsed = NumberAttribute(attr_name='games-parsed', null=True)

    daily_upload_limit = NumberAttribute(attr_name='daily-upload-limit', null=True)
    game_uploads_today = NumberAttribute(attr_name='game-uploads-today', null=True, default=0)
    telemetry_uploads_today = NumberAttribute(attr_name='telemetry-uploads-today', null=True, default=0)
    last_day_uploaded = NumberAttribute(attr_name='last-day-uploaded', null=True, default=0)

    current_upload_requested = NumberAttribute(attr_name='current-upload-requested', null=True)

    type = UnicodeAttribute(attr_name='type', null=True)
    demo = BooleanAttribute(attr_name='demo', null=True)
    superuser = BooleanAttribute(attr_name='superuser', null=True)
    record_states = BooleanAttribute(attr_name='record-states', null=True)

    account_created = NumberAttribute(attr_name='account-created', null=True)
    free = BooleanAttribute(attr_name='free', default=False, null=True)
    free_custom_games = BooleanAttribute(attr_name='free-custom-games', null=True, default=None)

    subscription_active = BooleanAttribute(attr_name='subscription-active', default=False)
    subscription_type = UnicodeAttribute(attr_name='subscription-type', null=True, default=None)

    stripe_customer_id = UnicodeAttribute(attr_name='stripe-customer-id', null=True, default=None)
    stripe_customer_email = UnicodeAttribute(attr_name='stripe-customer-username', null=True, default=None)
    stripe_subscription_id = UnicodeAttribute(attr_name='stripe-subscription-id', null=True, default=None)

    paypal_payer_email = UnicodeAttribute(attr_name='paypal-payer-email', null=True, default=None)
    paypal_payer_id = UnicodeAttribute(attr_name='paypal-payer-id', null=True, default=None)
    paypal_subscr_id = UnicodeAttribute(attr_name='paypal-subscr-id', null=True, default=None)
    paypal_subscr_date = UnicodeAttribute(attr_name='paypal-subscr-date', null=True, default=None)
    paypal_cancel_at_period_end = BooleanAttribute(attr_name='paypal-cancel-at-period-end', null=True, default=None)

    used_trial = BooleanAttribute(attr_name='used-trial', default=False, null=True)
    trial_active = BooleanAttribute(attr_name='trial-active', default=False, null=True)
    trial_games_remaining = NumberAttribute(attr_name='trial-games-remaining', null=True)
    trial_end_time = NumberAttribute(attr_name='trial-end-time', null=True)

    stream_key = UnicodeAttribute(attr_name='stream-key', null=True)
    twitch_overlay = UnicodeAttribute(attr_name='twitch-overlay', null=True)

    @classmethod
    def get(cls, hash_key, **kwargs):
        """ :rtype: User """
        return super(User, cls).get(hash_key, **kwargs)

    def increment_game_uploads_today(self):
        return self.update({
            'game_uploads_today': {
                'action': 'add',
                'value': 1
            }
        })

    def increment_telemetry_uploads_today(self):
        return self.update({
            'telemetry_uploads_today': {
                'action': 'add',
                'value': 1
            }
        })

    @property
    def account_valid(self):
        return self.free or self.subscription_active or self.trial_valid

    @property
    def trial_valid(self):
        if not self.trial_active:
            return False
        else:
            if self.trial_games_remaining > 0 or self.trial_end_time > time.time():
                return True
            else:
                return False


if __name__ == '__main__':
    import logging
    import time
    import string
    import shortuuid

    ALLOWED = string.ascii_letters + string.digits + '_-'

    logging.basicConfig()
    log = logging.getLogger("pynamodb")
    log.setLevel(logging.WARNING)
    log.propagate = True

    u = User.get('EeveeA#1716')
    # u = User.user_id_index.get(71245935)
    # u.stream_key = shortuuid.uuid()
    # u.save()

    u.twitch_overlay = 'eeveea_'

    # u.battletag = 'Sio#11513'
    u.save()

    print(u)
    print(u.stream_key)
