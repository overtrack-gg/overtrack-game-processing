import re
import os
import time

from decimal import Decimal
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute

try:
    from .util import OverTrackModel, TupleAttribute
except (SystemError, ModuleNotFoundError):
    from util import OverTrackModel, TupleAttribute


player_name_pattern = re.compile('^[A-Z1-9]+$')


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
            raise ShareLink.DoesNotExist('ShareLink with user-id=%d does not exist' % (hash_key,))


# noinspection PyAbstractClass
class ShareLink(OverTrackModel):
    class Meta:
        table_name = os.environ.get('SHARED_PROFILE_TABLE', 'overtrack_share_links')
        region = 'us-west-2'

    user_id_index = UserIDIndex()

    share_key = UnicodeAttribute(attr_name='share-key', hash_key=True, null=False)
    user_id = NumberAttribute(attr_name='user-id', null=False)
    autogenerated = BooleanAttribute(attr_name='autogenerated', null=False)

    player_name_filter = TupleAttribute(attr_name='player-name-filter', null=True)
    include_customs = BooleanAttribute(attr_name='include-customs', default=False)
    created = NumberAttribute(attr_name='created', null=True)
    type = UnicodeAttribute(attr_name='type', null=True)

    @classmethod
    def create(cls, share_key, user_id, autogenerated, player_name_filter=None, include_customs=False, type_=None):
        """
        :type share_key: str
        :type user_id: int
        :type player_name_filter: tuple | list
        :type autogenerated: bool
        :type include_customs: bool
        :type type_: str
        """
        share_key = share_key.lower()

        if player_name_filter:
            if not isinstance(player_name_filter, list) and not isinstance(player_name_filter, tuple):
                raise TypeError('player_name_filter must be a list or tuple')

            for player_name in player_name_filter:
                if not player_name_pattern.match(player_name) and player_name != '[custom]':
                    raise ValueError('Player name %s invalid' % (player_name,))

        try:
            cls.get(share_key)
        except cls.DoesNotExist:
            pass
        else:
            raise ValueError('Shared profile with key=%s already exists' % (share_key, ))

        return cls(share_key=share_key, user_id=user_id, player_name_filter=player_name_filter, autogenerated=autogenerated, created=int(time.time()), type=type_)

    @classmethod
    def get(cls, share_key):
        return super(ShareLink, cls).get(share_key.lower())


if __name__ == '__main__':
    # import time
    # for l in ShareLink.scan(page_size=100):
    #   o = str(l)
    #   if l.player_name_filter:
    #       if '[custom]' in l.player_name_filter:
    #           l.include_customs = True
    #       else:
    #           l.include_customs = False
    #   else:
    #       l.include_customs = True
    #   l.save()
    #   print(o, '->', l)
    #   time.sleep(1)

    ShareLink.create('owl', 10, False, include_customs=True).save()



    # import shortuuid
    # s = ShareLink.create(share_key='IAMSAADIST-'.lower() + shortuuid.uuid(), user_id=367267829, autogenerated=False, player_name_filter=['[custom]'])
    # print(s)
    # s.save()
    # for t in ShareLink.scan():
    #   t.autogenerated = False
    #   t.save()

    # player_name_filter = [
    #   'FFC9E9',
    #   'JINGERPINK',
    #   'LEMONWATER'
    # ]
    #
    # names = list('FORAIRAN/TIGOLE/SWAHELI/SUPPORTCUCK'.upper().split('/'))
    # print(names)
    #
    # ShareLink.create(share_key='GAMEJAMMIN'.lower(), user_id=83056922, autogenerated=False).save()

    # ShareLink.create(share_key='forairan', user_id=358449631, autogenerated=False, player_name_filter=names).save()


    # link = ShareLink.get('hawkeye')
    # print(link)
    # link.player_name_filter = names
    # link.save()

    # link = ShareLink.get('forairan-8e63dd86-0054-4d21-9ccc-c27890f426ba')
    # link.player_name_filter = names
    # link.save()

    # sl = ShareLink.get('hawkeye')
    # sl.player_name_filter = ('HAWKEYE', 'JORDAN', 'ROCKET')
    # sl.save()
    # print(sl)



