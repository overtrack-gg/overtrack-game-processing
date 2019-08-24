import os
import time

from pynamodb.attributes import BooleanAttribute, JSONAttribute, NumberAttribute, UnicodeAttribute, ListAttribute, UnicodeSetAttribute, NumberSetAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex, KeysOnlyProjection

from models.common import OverTrackModel


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


class TwitchIDIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'twitch_id-index'

        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    twitch_id = UnicodeAttribute(attr_name='twitch_id', hash_key=True)

    def get(self, twitch_id: str) -> 'User':
        try:
            return next(self.query(twitch_id))
        except StopIteration:
            raise User.DoesNotExist(f'User with twitch_id={twitch_id} does not exist')


class BattlenetIDIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'battlenet_id-index'

        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    twitch_id = NumberAttribute(attr_name='battlenet_id', hash_key=True)

    def get(self, battlenet_id: int) -> 'User':
        try:
            return next(self.query(battlenet_id))
        except StopIteration:
            raise User.DoesNotExist(f'User with battlenet_id={battlenet_id} does not exist')


class DiscordIDIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'discord_id-index'

        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    discord_id = UnicodeAttribute(attr_name='discord_id', hash_key=True)

    def get(self, discord_id: str) -> 'User':
        try:
            return next(self.query(discord_id))
        except StopIteration:
            raise User.DoesNotExist(f'User with discord_id={discord_id} does not exist')


class UsernameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'username-index'

        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    username = UnicodeAttribute(attr_name='username', hash_key=True)

    def get(self, username: str) -> 'User':
        try:
            return next(self.query(username))
        except StopIteration:
            raise User.DoesNotExist(f'User with username={username} does not exist')


class ApexGamesIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = 'user-id-apex-games-index'

        read_capacity_units = 1
        write_capacity_units = 1
        projection = KeysOnlyProjection()

    user_id = NumberAttribute(attr_name='user_id', hash_key=True)
    apex_games = NumberAttribute(range_key=True)


# noinspection PyAbstractClass
class User(OverTrackModel):

    class Meta:
        table_name = os.environ.get('USERS_TABLE', 'overtrack_users')
        region = 'us-west-2'

    key = UnicodeAttribute(attr_name='battletag', hash_key=True, null=False)

    user_id = NumberAttribute(attr_name='user-id', default=0)
    user_id_index = UserIDIndex()

    twitch_id = UnicodeAttribute(null=True)
    twitch_id_index = TwitchIDIndex()
    twitch_user = JSONAttribute(null=True)

    battlenet_id = NumberAttribute(null=True)
    battlenet_id_index = BattlenetIDIndex()
    battlenet_user = JSONAttribute(null=True)

    _username = UnicodeAttribute(attr_name='username', null=True)
    username_index = UsernameIndex()

    discord_id = UnicodeAttribute(null=True)
    discord_user = JSONAttribute(null=True)
    discord_id_index = DiscordIDIndex()

    current_sr = NumberAttribute(attr_name='current-sr', null=True)
    twitch_account = UnicodeAttribute(attr_name='twitch-account', null=True)

    overwatch_games = NumberAttribute(attr_name='games-parsed', null=True)
    apex_games = NumberAttribute(null=True)
    apex_games_index = ApexGamesIndex()

    daily_upload_limit = NumberAttribute(attr_name='daily-upload-limit', null=True)
    game_uploads_today = NumberAttribute(attr_name='game-uploads-today', null=True, default=0)
    telemetry_uploads_today = NumberAttribute(attr_name='telemetry-uploads-today', null=True, default=0)
    last_day_uploaded = NumberAttribute(attr_name='last-day-uploaded', null=True, default=0)

    current_upload_requested = NumberAttribute(attr_name='current-upload-requested', null=True)

    type = UnicodeAttribute(attr_name='type', null=True)
    superuser = BooleanAttribute(attr_name='superuser', null=True)

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

    apex_one_time_webhook = JSONAttribute(null=True)
    apex_current_game = JSONAttribute(null=True)
    apex_games_public = BooleanAttribute(default=False)
    apex_seasons = NumberSetAttribute(default=set())
    apex_last_season = NumberAttribute(null=True)
    apex_last_game_ranked = BooleanAttribute(null=True)

    overwatch_seasons = NumberSetAttribute(default=set())
    overwatch_last_season = NumberAttribute(null=True)

    client_last_started = NumberAttribute(null=True)

    __nonce = UnicodeAttribute(attr_name='nonce', null=True)
    __record_states = BooleanAttribute(attr_name='record-states', null=True)
    __demo = BooleanAttribute(attr_name='demo', null=True)

    @property
    def battletag(self) -> str:
        return self.key

    @property
    def username(self) -> str:
        if self._username:
            return self._username
        else:
            return self.battletag.replace('#', '-').replace('!', '')

    @username.setter
    def username(self, username: str) -> None:
        self._username = username

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
    import string
    import logging

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
