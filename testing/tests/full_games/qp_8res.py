from testing.tests.test_games import ExpectedGame, ExpectedKill

MUON = 'MUON'
ORITHETOAST = 'ORITHETOAST'
GINJERSPICE = 'GINJERSPICE'
NIPPLEBUTTER = 'NIPPLEBUTTER'
SUBD = 'SUBD'
THEILLEGAL = 'THEILLEGAL'
ZIPPERWEASEL = 'ZIPPERWEASEL'
JANGLEZ = 'JANGLEZ'
YXNOH = 'YXNOH'
BOOP = 'BOOP'
IHOOKYOUSOOK = 'IHOOKYOUSOOK'
MERRIS = 'MERRIS'

teams = (
    [
        MUON,
        ORITHETOAST,
        GINJERSPICE,
        NIPPLEBUTTER,
        SUBD,
        THEILLEGAL
     ],
    [
        ZIPPERWEASEL,
        JANGLEZ,
        YXNOH,
        BOOP,
        IHOOKYOUSOOK,
        MERRIS
    ]
)

heroes = {
    MUON: ['mercy'],
    ORITHETOAST: ['doomfist'],
    GINJERSPICE: ['widowmaker', 'hanzo'],
    NIPPLEBUTTER: ['junkrat'],
    SUBD: ['brigitte'],
    THEILLEGAL: ['soldier'],

    ZIPPERWEASEL: ['lucio', 'hammond'],
    JANGLEZ: ['genji', 'hanzo', 'sombra'],
    YXNOH: ['soldier'],
    BOOP: ['dva', 'dva.mech'],
    IHOOKYOUSOOK: ['symmetra', 'symmetra.teleporter'],
    MERRIS: ['mercy']
}

game = ExpectedGame(
    path="D:/overwatch_vids/8res.mp4",
    killfeed=[
        ExpectedKill('0:00:00', MERRIS, ORITHETOAST),
        ExpectedKill('0:00:00', MUON, ORITHETOAST, True),
        ExpectedKill('0:00:15', NIPPLEBUTTER, IHOOKYOUSOOK),
        ExpectedKill('0:00:20', GINJERSPICE, ZIPPERWEASEL),
        ExpectedKill('0:00:22', IHOOKYOUSOOK, MUON),
        ExpectedKill('0:00:22', ORITHETOAST, IHOOKYOUSOOK),
        ExpectedKill('0:00:32', MERRIS, ZIPPERWEASEL, True),
        ExpectedKill('0:00:32', BOOP, GINJERSPICE),
        ExpectedKill('0:00:32', BOOP, THEILLEGAL),
        ExpectedKill('0:00:33', NIPPLEBUTTER, JANGLEZ),
        ExpectedKill('0:00:39', BOOP, NIPPLEBUTTER),

        ExpectedKill('0:01:00', ORITHETOAST, YXNOH),
        ExpectedKill('0:01:13', IHOOKYOUSOOK, ORITHETOAST),
        ExpectedKill('0:01:17', MUON, ORITHETOAST, True),
        ExpectedKill('0:01:20', GINJERSPICE, JANGLEZ),
        ExpectedKill('0:01:21', IHOOKYOUSOOK, NIPPLEBUTTER),
        ExpectedKill('0:01:33', THEILLEGAL, YXNOH),
        ExpectedKill('0:01:43', MERRIS, YXNOH, True),
        ExpectedKill('0:01:49', SUBD, IHOOKYOUSOOK),
        ExpectedKill('0:01:51', THEILLEGAL, YXNOH),

        ExpectedKill('0:02:00', GINJERSPICE, JANGLEZ),
        ExpectedKill('0:02:01', BOOP, THEILLEGAL),
        ExpectedKill('0:02:01', BOOP, MUON),
        ExpectedKill('0:02:10', IHOOKYOUSOOK, ORITHETOAST),
        ExpectedKill('0:02:17', IHOOKYOUSOOK, NIPPLEBUTTER),
        ExpectedKill('0:02:19', IHOOKYOUSOOK, GINJERSPICE),
        ExpectedKill('0:02:26', MUON, NIPPLEBUTTER, True),
        ExpectedKill('0:02:29', YXNOH, MUON),
        ExpectedKill('0:02:29', BOOP, SUBD),
        ExpectedKill('0:02:29', YXNOH, THEILLEGAL),
        ExpectedKill('0:02:34', YXNOH, ORITHETOAST),
        ExpectedKill('0:02:34', NIPPLEBUTTER, YXNOH),
        ExpectedKill('0:02:34', NIPPLEBUTTER, JANGLEZ),
        ExpectedKill('0:02:37', MERRIS, YXNOH, True),
        ExpectedKill('0:02:40', BOOP, NIPPLEBUTTER),
        ExpectedKill('0:02:55', THEILLEGAL, ZIPPERWEASEL),
        ExpectedKill('0:02:59', ORITHETOAST, YXNOH),

        ExpectedKill('00:03:09', MERRIS, YXNOH, True),
        ExpectedKill('00:03:17', ORITHETOAST, JANGLEZ),
        ExpectedKill('00:03:17', GINJERSPICE, IHOOKYOUSOOK),
        ExpectedKill('00:03:19', THEILLEGAL, BOOP),
        ExpectedKill('00:03:31', ORITHETOAST, BOOP),
        ExpectedKill('00:03:33', ORITHETOAST, YXNOH),
        ExpectedKill('00:03:36', MERRIS, GINJERSPICE),
        ExpectedKill('00:03:41', THEILLEGAL, ZIPPERWEASEL),
        ExpectedKill('00:03:46', JANGLEZ, NIPPLEBUTTER),
        ExpectedKill('00:03:46', MUON, GINJERSPICE, True),
        ExpectedKill('00:03:47', THEILLEGAL, IHOOKYOUSOOK),
        ExpectedKill('00:03:48', IHOOKYOUSOOK, THEILLEGAL),

        ExpectedKill('00:04:17', THEILLEGAL, YXNOH),
        ExpectedKill('00:04:29', GINJERSPICE, ZIPPERWEASEL),
        ExpectedKill('00:04:33', BOOP, NIPPLEBUTTER),
        ExpectedKill('00:04:34', ORITHETOAST, IHOOKYOUSOOK),
        ExpectedKill('00:04:37', YXNOH, ORITHETOAST),
        ExpectedKill('00:04:39', MERRIS, IHOOKYOUSOOK, True),
        ExpectedKill('00:04:40', SUBD, MERRIS),
        ExpectedKill('00:04:42', MUON, ORITHETOAST, True),
        ExpectedKill('00:04:43', YXNOH, GINJERSPICE),
        ExpectedKill('00:04:45', YXNOH, SUBD),
        ExpectedKill('00:04:47', THEILLEGAL, IHOOKYOUSOOK),
        ExpectedKill('00:04:48', ORITHETOAST, YXNOH),

        ExpectedKill('00:05:14', YXNOH, GINJERSPICE),
        ExpectedKill('00:05:22', SUBD, ZIPPERWEASEL),
        ExpectedKill('00:05:27', MERRIS, ZIPPERWEASEL, True),
        ExpectedKill('00:05:32', ORITHETOAST, YXNOH),
        ExpectedKill('00:05:34', THEILLEGAL, JANGLEZ),
        ExpectedKill('00:05:39', SUBD, IHOOKYOUSOOK),
        ExpectedKill('00:05:53', THEILLEGAL, BOOP),
        ExpectedKill('00:05:55', THEILLEGAL, BOOP),

        ExpectedKill('00:06:22', NIPPLEBUTTER, IHOOKYOUSOOK),
        ExpectedKill('00:06:28', ORITHETOAST, JANGLEZ),
        ExpectedKill('00:06:31', NIPPLEBUTTER, MERRIS),
        ExpectedKill('00:06:31', NIPPLEBUTTER, ZIPPERWEASEL),
        ExpectedKill('00:06:33', SUBD, YXNOH),
        ExpectedKill('00:06:38', ORITHETOAST, IHOOKYOUSOOK),

        ExpectedKill('00:07:04', GINJERSPICE, BOOP),
        ExpectedKill('00:07:06', YXNOH, NIPPLEBUTTER),
        ExpectedKill('00:07:06', ORITHETOAST, ZIPPERWEASEL),
        ExpectedKill('00:07:10', YXNOH, THEILLEGAL),
        ExpectedKill('00:07:14', MUON, THEILLEGAL, True),
        ExpectedKill('00:07:17', MERRIS, ZIPPERWEASEL, True),
        ExpectedKill('00:07:19', JANGLEZ, SUBD),
        ExpectedKill('00:07:19', ORITHETOAST, YXNOH),
        ExpectedKill('00:07:19', IHOOKYOUSOOK, ORITHETOAST),
        ExpectedKill('00:07:23', IHOOKYOUSOOK, THEILLEGAL),
        ExpectedKill('00:07:27', JANGLEZ, MUON),
        ExpectedKill('00:07:40', YXNOH, NIPPLEBUTTER),
        ExpectedKill('00:07:49', THEILLEGAL, BOOP),
        ExpectedKill('00:07:52', YXNOH, ORITHETOAST),
        ExpectedKill('00:07:54', IHOOKYOUSOOK, SUBD),
        ExpectedKill('00:07:55', MUON, ORITHETOAST, True),
        ExpectedKill('00:07:56', IHOOKYOUSOOK, THEILLEGAL),

        ExpectedKill('00:08:01', YXNOH, GINJERSPICE),
        ExpectedKill('00:08:08', YXNOH, NIPPLEBUTTER),
        ExpectedKill('00:08:09', BOOP, MUON),
        ExpectedKill('00:08:10', ORITHETOAST, YXNOH),
        ExpectedKill('00:08:20', JANGLEZ, ORITHETOAST),
        ExpectedKill('00:08:20', MERRIS, YXNOH, True),
        ExpectedKill('00:08:35', IHOOKYOUSOOK, NIPPLEBUTTER),
        ExpectedKill('00:08:38', MUON, NIPPLEBUTTER, True),
        ExpectedKill('00:08:40', JANGLEZ, ORITHETOAST),
        ExpectedKill('00:08:47', YXNOH, MUON),
        ExpectedKill('00:08:50', NIPPLEBUTTER, YXNOH),
        ExpectedKill('00:08:52', BOOP, SUBD),
        ExpectedKill('00:08:53', MERRIS, YXNOH, True),
        ExpectedKill('00:08:57', YXNOH, THEILLEGAL),
        ExpectedKill('00:09:01', NIPPLEBUTTER, BOOP),
        ExpectedKill('00:09:01', ORITHETOAST, ZIPPERWEASEL),
        ExpectedKill('00:09:03', YXNOH, NIPPLEBUTTER),
        ExpectedKill('00:09:07', BOOP, GINJERSPICE),
    ]
    # stop='0:04:0'
)
