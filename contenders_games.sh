# Contenders name extraction script

echo > progress.txt
            
# Title: Blank Esports vs MEGA | Week 4 Day 1 Match 1 Game 5 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249878417
# Created: 2018-04-13 14:19:00+00:00
# Duration 0:19:10
echo "0 / 343" >> progress.txt
echo "Title: Blank Esports vs MEGA | Week 4 Day 1 Match 1 Game 5 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249878417" >> progress.txt
echo "Duration: 0:19:10" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249878417
tar cvf /media/ephemeral0/names_249878417.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249878417.tar s3://overtrack-training-data/vod-names/names_249878417.tar
rm /media/ephemeral0/names_249878417.tar
            
# Title: Machi Esports vs Detonator KR | Week 1 Day 2 Match 2 Game 2 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242331098
# Created: 2018-03-24 15:03:50+00:00
# Duration 0:19:20
echo "1 / 343" >> progress.txt
echo "Title: Machi Esports vs Detonator KR | Week 1 Day 2 Match 2 Game 2 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242331098" >> progress.txt
echo "Duration: 0:19:20" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242331098
tar cvf /media/ephemeral0/names_242331098.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242331098.tar s3://overtrack-training-data/vod-names/names_242331098.tar
rm /media/ephemeral0/names_242331098.tar
            
# Title: LogitechG ABANG vs OneShine Esports | Week 4 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250295175
# Created: 2018-04-14 16:09:39+00:00
# Duration 0:18:26
echo "2 / 343" >> progress.txt
echo "Title: LogitechG ABANG vs OneShine Esports | Week 4 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250295175" >> progress.txt
echo "Duration: 0:18:26" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250295175
tar cvf /media/ephemeral0/names_250295175.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250295175.tar s3://overtrack-training-data/vod-names/names_250295175.tar
rm /media/ephemeral0/names_250295175.tar
            
# Title: Mosaic Esports vs Eagle Gaming | Week 5 Day 2 Match 1 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248459536
# Created: 2018-04-09 16:50:15+00:00
# Duration 0:16:18
echo "3 / 343" >> progress.txt
echo "Title: Mosaic Esports vs Eagle Gaming | Week 5 Day 2 Match 1 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248459536" >> progress.txt
echo "Duration: 0:16:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248459536
tar cvf /media/ephemeral0/names_248459536.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248459536.tar s3://overtrack-training-data/vod-names/names_248459536.tar
rm /media/ephemeral0/names_248459536.tar
            
# Title: Fusion University vs. GG Esports Academy | Week 5 Day 1 Match 1 Game 3 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291862692
# Created: 2018-08-01 17:31:40+00:00
# Duration 0:19:07
echo "4 / 343" >> progress.txt
echo "Title: Fusion University vs. GG Esports Academy | Week 5 Day 1 Match 1 Game 3 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291862692" >> progress.txt
echo "Duration: 0:19:07" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291862692
tar cvf /media/ephemeral0/names_291862692.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291862692.tar s3://overtrack-training-data/vod-names/names_291862692.tar
rm /media/ephemeral0/names_291862692.tar
            
# Title: Gladiators Legion vs. Second Wind | Week 5 Day 1 Match 2 Game 4 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291871492
# Created: 2018-08-01 17:56:31+00:00
# Duration 0:17:13
echo "5 / 343" >> progress.txt
echo "Title: Gladiators Legion vs. Second Wind | Week 5 Day 1 Match 2 Game 4 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291871492" >> progress.txt
echo "Duration: 0:17:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291871492
tar cvf /media/ephemeral0/names_291871492.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291871492.tar s3://overtrack-training-data/vod-names/names_291871492.tar
rm /media/ephemeral0/names_291871492.tar
            
# Title: Incipience (INC) vs Blank Esports (BLK) | Week 2 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284434619
# Created: 2018-07-14 03:40:40+00:00
# Duration 0:10:00
echo "6 / 343" >> progress.txt
echo "Title: Incipience (INC) vs Blank Esports (BLK) | Week 2 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284434619" >> progress.txt
echo "Duration: 0:10:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284434619
tar cvf /media/ephemeral0/names_284434619.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284434619.tar s3://overtrack-training-data/vod-names/names_284434619.tar
rm /media/ephemeral0/names_284434619.tar
            
# Title: Fusion University vs. GG Esports Academy | Week 5 Day 1 Match 1 Game 2 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291860167
# Created: 2018-08-01 17:24:19+00:00
# Duration 0:11:00
echo "7 / 343" >> progress.txt
echo "Title: Fusion University vs. GG Esports Academy | Week 5 Day 1 Match 1 Game 2 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291860167" >> progress.txt
echo "Duration: 0:11:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291860167
tar cvf /media/ephemeral0/names_291860167.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291860167.tar s3://overtrack-training-data/vod-names/names_291860167.tar
rm /media/ephemeral0/names_291860167.tar
            
# Title: Team Gigantti vs Team Singularity | Week 5 Day 1 Match 2 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248098940
# Created: 2018-04-08 16:17:42+00:00
# Duration 0:10:36
echo "8 / 343" >> progress.txt
echo "Title: Team Gigantti vs Team Singularity | Week 5 Day 1 Match 2 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248098940" >> progress.txt
echo "Duration: 0:10:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248098940
tar cvf /media/ephemeral0/names_248098940.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248098940.tar s3://overtrack-training-data/vod-names/names_248098940.tar
rm /media/ephemeral0/names_248098940.tar
            
# Title: Chaos Theory vs Hong Kong Attitude | Week 3 Day 2 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/247672514
# Created: 2018-04-07 14:51:59+00:00
# Duration 0:24:30
echo "9 / 343" >> progress.txt
echo "Title: Chaos Theory vs Hong Kong Attitude | Week 3 Day 2 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/247672514" >> progress.txt
echo "Duration: 0:24:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/247672514
tar cvf /media/ephemeral0/names_247672514.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_247672514.tar s3://overtrack-training-data/vod-names/names_247672514.tar
rm /media/ephemeral0/names_247672514.tar
            
# Title: NOVA ESPORTS vs Blank Esports (BLK) | Week 4 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290154182
# Created: 2018-07-28 09:03:51+00:00
# Duration 0:27:32
echo "10 / 343" >> progress.txt
echo "Title: NOVA ESPORTS vs Blank Esports (BLK) | Week 4 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290154182" >> progress.txt
echo "Duration: 0:27:32" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290154182
tar cvf /media/ephemeral0/names_290154182.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290154182.tar s3://overtrack-training-data/vod-names/names_290154182.tar
rm /media/ephemeral0/names_290154182.tar
            
# Title: Team Singularity vs That's a Disband | Week 3 Day 1 Match 2 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243950592
# Created: 2018-03-28 19:07:22+00:00
# Duration 0:25:57
echo "11 / 343" >> progress.txt
echo "Title: Team Singularity vs That's a Disband | Week 3 Day 1 Match 2 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243950592" >> progress.txt
echo "Duration: 0:25:57" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243950592
tar cvf /media/ephemeral0/names_243950592.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243950592.tar s3://overtrack-training-data/vod-names/names_243950592.tar
rm /media/ephemeral0/names_243950592.tar
            
# Title: Nova Esports vs Hong Kong Attitude | Week 2 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284702281
# Created: 2018-07-14 21:10:02+00:00
# Duration 0:28:12
echo "12 / 343" >> progress.txt
echo "Title: Nova Esports vs Hong Kong Attitude | Week 2 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284702281" >> progress.txt
echo "Duration: 0:28:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284702281
tar cvf /media/ephemeral0/names_284702281.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284702281.tar s3://overtrack-training-data/vod-names/names_284702281.tar
rm /media/ephemeral0/names_284702281.tar
            
# Title: Chaos Theory vs Detonator KR | Week 2 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244342649
# Created: 2018-03-29 19:37:50+00:00
# Duration 0:14:53
echo "13 / 343" >> progress.txt
echo "Title: Chaos Theory vs Detonator KR | Week 2 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244342649" >> progress.txt
echo "Duration: 0:14:53" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244342649
tar cvf /media/ephemeral0/names_244342649.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244342649.tar s3://overtrack-training-data/vod-names/names_244342649.tar
rm /media/ephemeral0/names_244342649.tar
            
# Title: EnVision vs Bye Week | Week 3 Day 1 Match 1 Game 4 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243671496
# Created: 2018-03-28 00:13:50+00:00
# Duration 0:17:25
echo "14 / 343" >> progress.txt
echo "Title: EnVision vs Bye Week | Week 3 Day 1 Match 1 Game 4 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243671496" >> progress.txt
echo "Duration: 0:17:25" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243671496
tar cvf /media/ephemeral0/names_243671496.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243671496.tar s3://overtrack-training-data/vod-names/names_243671496.tar
rm /media/ephemeral0/names_243671496.tar
            
# Title: MEGA vs LogitechG ABANG | Week 1 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241687128
# Created: 2018-03-22 20:57:05+00:00
# Duration 0:22:24
echo "15 / 343" >> progress.txt
echo "Title: MEGA vs LogitechG ABANG | Week 1 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241687128" >> progress.txt
echo "Duration: 0:22:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241687128
tar cvf /media/ephemeral0/names_241687128.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241687128.tar s3://overtrack-training-data/vod-names/names_241687128.tar
rm /media/ephemeral0/names_241687128.tar
            
# Title: Mega (MGA) vs Talon Esport (TLN) | Week 4 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290156204
# Created: 2018-07-28 09:16:39+00:00
# Duration 0:12:48
echo "16 / 343" >> progress.txt
echo "Title: Mega (MGA) vs Talon Esport (TLN) | Week 4 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290156204" >> progress.txt
echo "Duration: 0:12:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290156204
tar cvf /media/ephemeral0/names_290156204.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290156204.tar s3://overtrack-training-data/vod-names/names_290156204.tar
rm /media/ephemeral0/names_290156204.tar
            
# Title: Eagle Gaming vs Young and Beautiful | Week 3 Day 2 Match 1 Game 5 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244341381
# Created: 2018-03-29 19:34:22+00:00
# Duration 0:19:54
echo "17 / 343" >> progress.txt
echo "Title: Eagle Gaming vs Young and Beautiful | Week 3 Day 2 Match 1 Game 5 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244341381" >> progress.txt
echo "Duration: 0:19:54" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244341381
tar cvf /media/ephemeral0/names_244341381.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244341381.tar s3://overtrack-training-data/vod-names/names_244341381.tar
rm /media/ephemeral0/names_244341381.tar
            
# Title: Chaos Theory vs Detonator KR | Week 2 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244330247
# Created: 2018-03-29 19:05:25+00:00
# Duration 0:31:41
echo "18 / 343" >> progress.txt
echo "Title: Chaos Theory vs Detonator KR | Week 2 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244330247" >> progress.txt
echo "Duration: 0:31:41" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244330247
tar cvf /media/ephemeral0/names_244330247.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244330247.tar s3://overtrack-training-data/vod-names/names_244330247.tar
rm /media/ephemeral0/names_244330247.tar
            
# Title: MONSTER SHIELD KR vs EXL-Esports | Week 2 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284435715
# Created: 2018-07-14 03:44:19+00:00
# Duration 0:21:18
echo "19 / 343" >> progress.txt
echo "Title: MONSTER SHIELD KR vs EXL-Esports | Week 2 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284435715" >> progress.txt
echo "Duration: 0:21:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284435715
tar cvf /media/ephemeral0/names_284435715.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284435715.tar s3://overtrack-training-data/vod-names/names_284435715.tar
rm /media/ephemeral0/names_284435715.tar
            
# Title: Machi Esports (M17) vs Talon Esport (TLN) | Week 1 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282154736
# Created: 2018-07-08 07:49:59+00:00
# Duration 0:15:25
echo "20 / 343" >> progress.txt
echo "Title: Machi Esports (M17) vs Talon Esport (TLN) | Week 1 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282154736" >> progress.txt
echo "Duration: 0:15:25" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282154736
tar cvf /media/ephemeral0/names_282154736.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282154736.tar s3://overtrack-training-data/vod-names/names_282154736.tar
rm /media/ephemeral0/names_282154736.tar
            
# Title: Team Singularity vs That's a Disband | Week 3 Day 1 Match 2 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243940567
# Created: 2018-03-28 18:43:24+00:00
# Duration 0:23:31
echo "21 / 343" >> progress.txt
echo "Title: Team Singularity vs That's a Disband | Week 3 Day 1 Match 2 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243940567" >> progress.txt
echo "Duration: 0:23:31" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243940567
tar cvf /media/ephemeral0/names_243940567.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243940567.tar s3://overtrack-training-data/vod-names/names_243940567.tar
rm /media/ephemeral0/names_243940567.tar
            
# Title: Orgless and Hungry vs Angry Titans | Week 5 Day 1 Match 1 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248082702
# Created: 2018-04-08 15:23:38+00:00
# Duration 0:24:12
echo "22 / 343" >> progress.txt
echo "Title: Orgless and Hungry vs Angry Titans | Week 5 Day 1 Match 1 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248082702" >> progress.txt
echo "Duration: 0:24:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248082702
tar cvf /media/ephemeral0/names_248082702.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248082702.tar s3://overtrack-training-data/vod-names/names_248082702.tar
rm /media/ephemeral0/names_248082702.tar
            
# Title: Nova Esports vs Hong Kong Attitude | Week 2 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284703653
# Created: 2018-07-14 21:14:08+00:00
# Duration 0:20:30
echo "23 / 343" >> progress.txt
echo "Title: Nova Esports vs Hong Kong Attitude | Week 2 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284703653" >> progress.txt
echo "Duration: 0:20:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284703653
tar cvf /media/ephemeral0/names_284703653.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284703653.tar s3://overtrack-training-data/vod-names/names_284703653.tar
rm /media/ephemeral0/names_284703653.tar
            
# Title: NEW PARADIGM vs MONSTER SHIELD KR | Week 4 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290497404
# Created: 2018-07-29 05:15:22+00:00
# Duration 0:20:49
echo "24 / 343" >> progress.txt
echo "Title: NEW PARADIGM vs MONSTER SHIELD KR | Week 4 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290497404" >> progress.txt
echo "Duration: 0:20:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290497404
tar cvf /media/ephemeral0/names_290497404.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290497404.tar s3://overtrack-training-data/vod-names/names_290497404.tar
rm /media/ephemeral0/names_290497404.tar
            
# Title: Hong Kong Attitude vs Machi Esports | Week 2 Day 2 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/245354253
# Created: 2018-04-01 08:44:15+00:00
# Duration 0:29:28
echo "25 / 343" >> progress.txt
echo "Title: Hong Kong Attitude vs Machi Esports | Week 2 Day 2 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245354253" >> progress.txt
echo "Duration: 0:29:28" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245354253
tar cvf /media/ephemeral0/names_245354253.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245354253.tar s3://overtrack-training-data/vod-names/names_245354253.tar
rm /media/ephemeral0/names_245354253.tar
            
# Title: Hong Kong Attitude (HKA) vs Incipience (INC) | Week 1 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281775403
# Created: 2018-07-07 06:29:16+00:00
# Duration 0:16:19
echo "26 / 343" >> progress.txt
echo "Title: Hong Kong Attitude (HKA) vs Incipience (INC) | Week 1 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281775403" >> progress.txt
echo "Duration: 0:16:19" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281775403
tar cvf /media/ephemeral0/names_281775403.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281775403.tar s3://overtrack-training-data/vod-names/names_281775403.tar
rm /media/ephemeral0/names_281775403.tar
            
# Title: Blank Esports vs Xavier Esports | Week 3 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246935130
# Created: 2018-04-05 16:16:51+00:00
# Duration 0:14:48
echo "27 / 343" >> progress.txt
echo "Title: Blank Esports vs Xavier Esports | Week 3 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246935130" >> progress.txt
echo "Duration: 0:14:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246935130
tar cvf /media/ephemeral0/names_246935130.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246935130.tar s3://overtrack-training-data/vod-names/names_246935130.tar
rm /media/ephemeral0/names_246935130.tar
            
# Title: Xavier Esports (XVE) vs Incipience (INC) | Week 5 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292929688
# Created: 2018-08-04 06:49:47+00:00
# Duration 0:09:17
echo "28 / 343" >> progress.txt
echo "Title: Xavier Esports (XVE) vs Incipience (INC) | Week 5 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292929688" >> progress.txt
echo "Duration: 0:09:17" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292929688
tar cvf /media/ephemeral0/names_292929688.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292929688.tar s3://overtrack-training-data/vod-names/names_292929688.tar
rm /media/ephemeral0/names_292929688.tar
            
# Title: Toronto Esports vs. Team Envy | Week 5 Day 2 Match 3 Game 5 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292488550
# Created: 2018-08-03 04:38:58+00:00
# Duration 0:28:01
echo "29 / 343" >> progress.txt
echo "Title: Toronto Esports vs. Team Envy | Week 5 Day 2 Match 3 Game 5 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292488550" >> progress.txt
echo "Duration: 0:28:01" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292488550
tar cvf /media/ephemeral0/names_292488550.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292488550.tar s3://overtrack-training-data/vod-names/names_292488550.tar
rm /media/ephemeral0/names_292488550.tar
            
# Title: Contenders Pacific | OneShine Esports vs Xavier Esports | Week 2 Day 2 Match 1 Game 4 | S1: Regular Season
# URL: https://www.twitch.tv/videos/245008281
# Created: 2018-03-31 12:40:42+00:00
# Duration 0:17:44
echo "30 / 343" >> progress.txt
echo "Title: Contenders Pacific | OneShine Esports vs Xavier Esports | Week 2 Day 2 Match 1 Game 4 | S1: Regular Season" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245008281" >> progress.txt
echo "Duration: 0:17:44" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245008281
tar cvf /media/ephemeral0/names_245008281.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245008281.tar s3://overtrack-training-data/vod-names/names_245008281.tar
rm /media/ephemeral0/names_245008281.tar
            
# Title: MEGA vs YOSHIMOTO ENCOUNT | Week 2 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/245351690
# Created: 2018-04-01 08:27:36+00:00
# Duration 0:18:11
echo "31 / 343" >> progress.txt
echo "Title: MEGA vs YOSHIMOTO ENCOUNT | Week 2 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245351690" >> progress.txt
echo "Duration: 0:18:11" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245351690
tar cvf /media/ephemeral0/names_245351690.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245351690.tar s3://overtrack-training-data/vod-names/names_245351690.tar
rm /media/ephemeral0/names_245351690.tar
            
# Title: Mega (MGA) vs MONSTER SHIELD KR | Week 1 Day 2 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282153489
# Created: 2018-07-08 07:42:11+00:00
# Duration 0:09:27
echo "32 / 343" >> progress.txt
echo "Title: Mega (MGA) vs MONSTER SHIELD KR | Week 1 Day 2 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282153489" >> progress.txt
echo "Duration: 0:09:27" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282153489
tar cvf /media/ephemeral0/names_282153489.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282153489.tar s3://overtrack-training-data/vod-names/names_282153489.tar
rm /media/ephemeral0/names_282153489.tar
            
# Title: Incipience (INC) vs Blank Esports (BLK) | Week 2 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284434620
# Created: 2018-07-14 03:40:40+00:00
# Duration 0:15:24
echo "33 / 343" >> progress.txt
echo "Title: Incipience (INC) vs Blank Esports (BLK) | Week 2 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284434620" >> progress.txt
echo "Duration: 0:15:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284434620
tar cvf /media/ephemeral0/names_284434620.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284434620.tar s3://overtrack-training-data/vod-names/names_284434620.tar
rm /media/ephemeral0/names_284434620.tar
            
# Title: Yoshimoto Encount vs Xavier Esports | Week 1 Day 2 Match 3 Game 1 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242338929
# Created: 2018-03-24 15:29:32+00:00
# Duration 0:17:06
echo "34 / 343" >> progress.txt
echo "Title: Yoshimoto Encount vs Xavier Esports | Week 1 Day 2 Match 3 Game 1 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242338929" >> progress.txt
echo "Duration: 0:17:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242338929
tar cvf /media/ephemeral0/names_242338929.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242338929.tar s3://overtrack-training-data/vod-names/names_242338929.tar
rm /media/ephemeral0/names_242338929.tar
            
# Title: Mosaic Esports vs CIS Hope | Week 3 Day 2 Match 3 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244367178
# Created: 2018-03-29 20:46:39+00:00
# Duration 0:17:48
echo "35 / 343" >> progress.txt
echo "Title: Mosaic Esports vs CIS Hope | Week 3 Day 2 Match 3 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244367178" >> progress.txt
echo "Duration: 0:17:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244367178
tar cvf /media/ephemeral0/names_244367178.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244367178.tar s3://overtrack-training-data/vod-names/names_244367178.tar
rm /media/ephemeral0/names_244367178.tar
            
# Title: Xavier Esports vs CYCLOPS athlete gaming | Week 2 Day 2 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284692529
# Created: 2018-07-14 20:42:09+00:00
# Duration 0:16:18
echo "36 / 343" >> progress.txt
echo "Title: Xavier Esports vs CYCLOPS athlete gaming | Week 2 Day 2 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284692529" >> progress.txt
echo "Duration: 0:16:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284692529
tar cvf /media/ephemeral0/names_284692529.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284692529.tar s3://overtrack-training-data/vod-names/names_284692529.tar
rm /media/ephemeral0/names_284692529.tar
            
# Title: Talon Esports vs Machi Esports | Week 4 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249880077
# Created: 2018-04-13 14:26:08+00:00
# Duration 0:16:43
echo "37 / 343" >> progress.txt
echo "Title: Talon Esports vs Machi Esports | Week 4 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249880077" >> progress.txt
echo "Duration: 0:16:43" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249880077
tar cvf /media/ephemeral0/names_249880077.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249880077.tar s3://overtrack-training-data/vod-names/names_249880077.tar
rm /media/ephemeral0/names_249880077.tar
            
# Title: Team Gigantti vs Team Singularity | Week 5 Day 1 Match 2 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248120959
# Created: 2018-04-08 17:22:20+00:00
# Duration 0:22:54
echo "38 / 343" >> progress.txt
echo "Title: Team Gigantti vs Team Singularity | Week 5 Day 1 Match 2 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248120959" >> progress.txt
echo "Duration: 0:22:54" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248120959
tar cvf /media/ephemeral0/names_248120959.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248120959.tar s3://overtrack-training-data/vod-names/names_248120959.tar
rm /media/ephemeral0/names_248120959.tar
            
# Title: Grizzlys vs XL2 Academy | Week 3 Day 2 Match 3 Game 4 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244148241
# Created: 2018-03-29 05:09:43+00:00
# Duration 0:31:01
echo "39 / 343" >> progress.txt
echo "Title: Grizzlys vs XL2 Academy | Week 3 Day 2 Match 3 Game 4 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244148241" >> progress.txt
echo "Duration: 0:31:01" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244148241
tar cvf /media/ephemeral0/names_244148241.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244148241.tar s3://overtrack-training-data/vod-names/names_244148241.tar
rm /media/ephemeral0/names_244148241.tar
            
# Title: CIS Hope vs Copenhagen Flames | Week 5 Day 2 Match 3 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248535926
# Created: 2018-04-09 20:26:30+00:00
# Duration 0:19:18
echo "40 / 343" >> progress.txt
echo "Title: CIS Hope vs Copenhagen Flames | Week 5 Day 2 Match 3 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248535926" >> progress.txt
echo "Duration: 0:19:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248535926
tar cvf /media/ephemeral0/names_248535926.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248535926.tar s3://overtrack-training-data/vod-names/names_248535926.tar
rm /media/ephemeral0/names_248535926.tar
            
# Title: Talon Esports vs BAZAAR | Week 2 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244321637
# Created: 2018-03-29 18:43:57+00:00
# Duration 0:23:25
echo "41 / 343" >> progress.txt
echo "Title: Talon Esports vs BAZAAR | Week 2 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244321637" >> progress.txt
echo "Duration: 0:23:25" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244321637
tar cvf /media/ephemeral0/names_244321637.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244321637.tar s3://overtrack-training-data/vod-names/names_244321637.tar
rm /media/ephemeral0/names_244321637.tar
            
# Title: LogitechG ABANG vs OneShine Esports | Week 4 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250296320
# Created: 2018-04-14 16:13:27+00:00
# Duration 0:31:27
echo "42 / 343" >> progress.txt
echo "Title: LogitechG ABANG vs OneShine Esports | Week 4 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250296320" >> progress.txt
echo "Duration: 0:31:27" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250296320
tar cvf /media/ephemeral0/names_250296320.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250296320.tar s3://overtrack-training-data/vod-names/names_250296320.tar
rm /media/ephemeral0/names_250296320.tar
            
# Title: Machi Esports vs MEGA | Week 2 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284709662
# Created: 2018-07-14 21:32:03+00:00
# Duration 0:20:06
echo "43 / 343" >> progress.txt
echo "Title: Machi Esports vs MEGA | Week 2 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284709662" >> progress.txt
echo "Duration: 0:20:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284709662
tar cvf /media/ephemeral0/names_284709662.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284709662.tar s3://overtrack-training-data/vod-names/names_284709662.tar
rm /media/ephemeral0/names_284709662.tar
            
# Title: Detonator KR vs Hong Kong Attitude | Week 4 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249883379
# Created: 2018-04-13 14:39:35+00:00
# Duration 0:09:35
echo "44 / 343" >> progress.txt
echo "Title: Detonator KR vs Hong Kong Attitude | Week 4 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249883379" >> progress.txt
echo "Duration: 0:09:35" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249883379
tar cvf /media/ephemeral0/names_249883379.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249883379.tar s3://overtrack-training-data/vod-names/names_249883379.tar
rm /media/ephemeral0/names_249883379.tar
            
# Title: Talon Esport (TLN) vs NEW PARADIGM | Week 2 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284438249
# Created: 2018-07-14 03:53:04+00:00
# Duration 0:20:24
echo "45 / 343" >> progress.txt
echo "Title: Talon Esport (TLN) vs NEW PARADIGM | Week 2 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284438249" >> progress.txt
echo "Duration: 0:20:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284438249
tar cvf /media/ephemeral0/names_284438249.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284438249.tar s3://overtrack-training-data/vod-names/names_284438249.tar
rm /media/ephemeral0/names_284438249.tar
            
# Title: Blank Esports vs Talon Esports | Week 1 Day 2 Match 1 Game 3 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/255426641
# Created: 2018-04-28 15:28:53+00:00
# Duration 0:25:42
echo "46 / 343" >> progress.txt
echo "Title: Blank Esports vs Talon Esports | Week 1 Day 2 Match 1 Game 3 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/255426641" >> progress.txt
echo "Duration: 0:25:42" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/255426641
tar cvf /media/ephemeral0/names_255426641.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_255426641.tar s3://overtrack-training-data/vod-names/names_255426641.tar
rm /media/ephemeral0/names_255426641.tar
            
# Title: Hong Kong Attitude vs Machi Esports | Week 2 Day 2 Match 3 Game 5 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/245358286
# Created: 2018-04-01 09:09:27+00:00
# Duration 0:27:37
echo "47 / 343" >> progress.txt
echo "Title: Hong Kong Attitude vs Machi Esports | Week 2 Day 2 Match 3 Game 5 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245358286" >> progress.txt
echo "Duration: 0:27:37" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245358286
tar cvf /media/ephemeral0/names_245358286.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245358286.tar s3://overtrack-training-data/vod-names/names_245358286.tar
rm /media/ephemeral0/names_245358286.tar
            
# Title: CIS HOPE vs ONE.POINT | Week 3 Day 2 Match 1 Game 2 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285804905
# Created: 2018-07-17 16:51:08+00:00
# Duration 0:23:25
echo "48 / 343" >> progress.txt
echo "Title: CIS HOPE vs ONE.POINT | Week 3 Day 2 Match 1 Game 2 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285804905" >> progress.txt
echo "Duration: 0:23:25" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285804905
tar cvf /media/ephemeral0/names_285804905.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285804905.tar s3://overtrack-training-data/vod-names/names_285804905.tar
rm /media/ephemeral0/names_285804905.tar
            
# Title: MEGA vs YOSHIMOTO ENCOUNT | Week 2 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/245350409
# Created: 2018-04-01 08:18:46+00:00
# Duration 0:09:42
echo "49 / 343" >> progress.txt
echo "Title: MEGA vs YOSHIMOTO ENCOUNT | Week 2 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245350409" >> progress.txt
echo "Duration: 0:09:42" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245350409
tar cvf /media/ephemeral0/names_245350409.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245350409.tar s3://overtrack-training-data/vod-names/names_245350409.tar
rm /media/ephemeral0/names_245350409.tar
            
# Title: Machi Esports vs MEGA | Week 2 Day 2 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284707353
# Created: 2018-07-14 21:25:16+00:00
# Duration 0:20:00
echo "50 / 343" >> progress.txt
echo "Title: Machi Esports vs MEGA | Week 2 Day 2 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284707353" >> progress.txt
echo "Duration: 0:20:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284707353
tar cvf /media/ephemeral0/names_284707353.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284707353.tar s3://overtrack-training-data/vod-names/names_284707353.tar
rm /media/ephemeral0/names_284707353.tar
            
# Title: LogitechG ABANG vs OneShine Esports | Week 4 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250295666
# Created: 2018-04-14 16:11:20+00:00
# Duration 0:14:40
echo "51 / 343" >> progress.txt
echo "Title: LogitechG ABANG vs OneShine Esports | Week 4 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250295666" >> progress.txt
echo "Duration: 0:14:40" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250295666
tar cvf /media/ephemeral0/names_250295666.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250295666.tar s3://overtrack-training-data/vod-names/names_250295666.tar
rm /media/ephemeral0/names_250295666.tar
            
# Title: Blank Esports (BLK) vs CYCLOPS athlete gaming (CAG) | Week 1 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281774031
# Created: 2018-07-07 06:22:03+00:00
# Duration 0:18:57
echo "52 / 343" >> progress.txt
echo "Title: Blank Esports (BLK) vs CYCLOPS athlete gaming (CAG) | Week 1 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281774031" >> progress.txt
echo "Duration: 0:18:57" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281774031
tar cvf /media/ephemeral0/names_281774031.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281774031.tar s3://overtrack-training-data/vod-names/names_281774031.tar
rm /media/ephemeral0/names_281774031.tar
            
# Title: Toronto Esports vs Gladiators Legion | Week 3 Day 2 Match 2 Game 1 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244097383
# Created: 2018-03-29 02:01:47+00:00
# Duration 0:19:01
echo "53 / 343" >> progress.txt
echo "Title: Toronto Esports vs Gladiators Legion | Week 3 Day 2 Match 2 Game 1 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244097383" >> progress.txt
echo "Duration: 0:19:01" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244097383
tar cvf /media/ephemeral0/names_244097383.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244097383.tar s3://overtrack-training-data/vod-names/names_244097383.tar
rm /media/ephemeral0/names_244097383.tar
            
# Title: Talon Esports vs Machi Esports | Week 4 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249880995
# Created: 2018-04-13 14:29:47+00:00
# Duration 0:19:59
echo "54 / 343" >> progress.txt
echo "Title: Talon Esports vs Machi Esports | Week 4 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249880995" >> progress.txt
echo "Duration: 0:19:59" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249880995
tar cvf /media/ephemeral0/names_249880995.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249880995.tar s3://overtrack-training-data/vod-names/names_249880995.tar
rm /media/ephemeral0/names_249880995.tar
            
# Title: British Hurricane vs 6nakes | Week 3 Day 1 Match 3 Game 3 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285492872
# Created: 2018-07-16 21:10:54+00:00
# Duration 0:25:24
echo "55 / 343" >> progress.txt
echo "Title: British Hurricane vs 6nakes | Week 3 Day 1 Match 3 Game 3 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285492872" >> progress.txt
echo "Duration: 0:25:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285492872
tar cvf /media/ephemeral0/names_285492872.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285492872.tar s3://overtrack-training-data/vod-names/names_285492872.tar
rm /media/ephemeral0/names_285492872.tar
            
# Title: British Hurricane vs Orgless and Hungry | Week 3 Day 1 Match 1 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243933668
# Created: 2018-03-28 18:25:32+00:00
# Duration 0:15:39
echo "56 / 343" >> progress.txt
echo "Title: British Hurricane vs Orgless and Hungry | Week 3 Day 1 Match 1 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243933668" >> progress.txt
echo "Duration: 0:15:39" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243933668
tar cvf /media/ephemeral0/names_243933668.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243933668.tar s3://overtrack-training-data/vod-names/names_243933668.tar
rm /media/ephemeral0/names_243933668.tar
            
# Title: Last Night's Leftovers vs Mayhem Academy | Week 3 Day 2 Match 1 Game 2 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244054807
# Created: 2018-03-29 00:01:52+00:00
# Duration 0:25:01
echo "57 / 343" >> progress.txt
echo "Title: Last Night's Leftovers vs Mayhem Academy | Week 3 Day 2 Match 1 Game 2 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244054807" >> progress.txt
echo "Duration: 0:25:01" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244054807
tar cvf /media/ephemeral0/names_244054807.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244054807.tar s3://overtrack-training-data/vod-names/names_244054807.tar
rm /media/ephemeral0/names_244054807.tar
            
# Title: MEGA vs LogitechG ABANG | Week 1 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241689808
# Created: 2018-03-22 21:04:07+00:00
# Duration 0:16:53
echo "58 / 343" >> progress.txt
echo "Title: MEGA vs LogitechG ABANG | Week 1 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241689808" >> progress.txt
echo "Duration: 0:16:53" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241689808
tar cvf /media/ephemeral0/names_241689808.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241689808.tar s3://overtrack-training-data/vod-names/names_241689808.tar
rm /media/ephemeral0/names_241689808.tar
            
# Title: LogitechG ABANG vs YOSHIMOTO ENCOUNT | Week 3 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246937649
# Created: 2018-04-05 16:25:51+00:00
# Duration 0:25:06
echo "59 / 343" >> progress.txt
echo "Title: LogitechG ABANG vs YOSHIMOTO ENCOUNT | Week 3 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246937649" >> progress.txt
echo "Duration: 0:25:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246937649
tar cvf /media/ephemeral0/names_246937649.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246937649.tar s3://overtrack-training-data/vod-names/names_246937649.tar
rm /media/ephemeral0/names_246937649.tar
            
# Title: Talon Esport (TLN) vs NEW PARADIGM | Week 2 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284438250
# Created: 2018-07-14 03:53:04+00:00
# Duration 0:22:06
echo "60 / 343" >> progress.txt
echo "Title: Talon Esport (TLN) vs NEW PARADIGM | Week 2 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284438250" >> progress.txt
echo "Duration: 0:22:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284438250
tar cvf /media/ephemeral0/names_284438250.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284438250.tar s3://overtrack-training-data/vod-names/names_284438250.tar
rm /media/ephemeral0/names_284438250.tar
            
# Title: Fusion University vs. GG Esports Academy | Week 5 Day 1 Match 1 Game 1 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291585327
# Created: 2018-07-31 23:20:47+00:00
# Duration 0:19:13
echo "61 / 343" >> progress.txt
echo "Title: Fusion University vs. GG Esports Academy | Week 5 Day 1 Match 1 Game 1 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291585327" >> progress.txt
echo "Duration: 0:19:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291585327
tar cvf /media/ephemeral0/names_291585327.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291585327.tar s3://overtrack-training-data/vod-names/names_291585327.tar
rm /media/ephemeral0/names_291585327.tar
            
# Title: Simplicity vs Fusion University | Week 3 Day 1 Match 3 Game 3 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243741621
# Created: 2018-03-28 03:39:28+00:00
# Duration 0:20:19
echo "62 / 343" >> progress.txt
echo "Title: Simplicity vs Fusion University | Week 3 Day 1 Match 3 Game 3 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243741621" >> progress.txt
echo "Duration: 0:20:19" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243741621
tar cvf /media/ephemeral0/names_243741621.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243741621.tar s3://overtrack-training-data/vod-names/names_243741621.tar
rm /media/ephemeral0/names_243741621.tar
            
# Title: NOVA ESPORTS vs Blank Esports (BLK) | Week 4 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290154185
# Created: 2018-07-28 09:03:51+00:00
# Duration 0:17:06
echo "63 / 343" >> progress.txt
echo "Title: NOVA ESPORTS vs Blank Esports (BLK) | Week 4 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290154185" >> progress.txt
echo "Duration: 0:17:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290154185
tar cvf /media/ephemeral0/names_290154185.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290154185.tar s3://overtrack-training-data/vod-names/names_290154185.tar
rm /media/ephemeral0/names_290154185.tar
            
# Title: Talon Esports vs Detonator KR | Week 3 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246932766
# Created: 2018-04-05 16:08:36+00:00
# Duration 0:24:24
echo "64 / 343" >> progress.txt
echo "Title: Talon Esports vs Detonator KR | Week 3 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246932766" >> progress.txt
echo "Duration: 0:24:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246932766
tar cvf /media/ephemeral0/names_246932766.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246932766.tar s3://overtrack-training-data/vod-names/names_246932766.tar
rm /media/ephemeral0/names_246932766.tar
            
# Title: Blank Esports vs MEGA | Week 4 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249874609
# Created: 2018-04-13 14:03:37+00:00
# Duration 0:16:54
echo "65 / 343" >> progress.txt
echo "Title: Blank Esports vs MEGA | Week 4 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249874609" >> progress.txt
echo "Duration: 0:16:54" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249874609
tar cvf /media/ephemeral0/names_249874609.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249874609.tar s3://overtrack-training-data/vod-names/names_249874609.tar
rm /media/ephemeral0/names_249874609.tar
            
# Title: Blank Esports vs LogitechG ABANG | Week 2 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244316249
# Created: 2018-03-29 18:29:25+00:00
# Duration 0:15:43
echo "66 / 343" >> progress.txt
echo "Title: Blank Esports vs LogitechG ABANG | Week 2 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244316249" >> progress.txt
echo "Duration: 0:15:43" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244316249
tar cvf /media/ephemeral0/names_244316249.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244316249.tar s3://overtrack-training-data/vod-names/names_244316249.tar
rm /media/ephemeral0/names_244316249.tar
            
# Title: Xavier Esports vs CYCLOPS athlete gaming | Week 2 Day 2 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284691346
# Created: 2018-07-14 20:38:42+00:00
# Duration 0:24:36
echo "67 / 343" >> progress.txt
echo "Title: Xavier Esports vs CYCLOPS athlete gaming | Week 2 Day 2 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284691346" >> progress.txt
echo "Duration: 0:24:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284691346
tar cvf /media/ephemeral0/names_284691346.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284691346.tar s3://overtrack-training-data/vod-names/names_284691346.tar
rm /media/ephemeral0/names_284691346.tar
            
# Title: Xavier Esports (XVE) vs Incipience (INC) | Week 5 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292929690
# Created: 2018-08-04 06:49:47+00:00
# Duration 0:15:42
echo "68 / 343" >> progress.txt
echo "Title: Xavier Esports (XVE) vs Incipience (INC) | Week 5 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292929690" >> progress.txt
echo "Duration: 0:15:42" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292929690
tar cvf /media/ephemeral0/names_292929690.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292929690.tar s3://overtrack-training-data/vod-names/names_292929690.tar
rm /media/ephemeral0/names_292929690.tar
            
# Title: Talon Esports vs Hong Kong Attitude | Week 5 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252049886
# Created: 2018-04-19 10:25:47+00:00
# Duration 0:18:14
echo "69 / 343" >> progress.txt
echo "Title: Talon Esports vs Hong Kong Attitude | Week 5 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252049886" >> progress.txt
echo "Duration: 0:18:14" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252049886
tar cvf /media/ephemeral0/names_252049886.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252049886.tar s3://overtrack-training-data/vod-names/names_252049886.tar
rm /media/ephemeral0/names_252049886.tar
            
# Title: CIS Hope vs Orgless and Hungry | Playoffs - Round of 8 | Day 1 Match 2 Game 4 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253325347
# Created: 2018-04-22 18:03:10+00:00
# Duration 0:22:24
echo "70 / 343" >> progress.txt
echo "Title: CIS Hope vs Orgless and Hungry | Playoffs - Round of 8 | Day 1 Match 2 Game 4 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253325347" >> progress.txt
echo "Duration: 0:22:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253325347
tar cvf /media/ephemeral0/names_253325347.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253325347.tar s3://overtrack-training-data/vod-names/names_253325347.tar
rm /media/ephemeral0/names_253325347.tar
            
# Title: Eagle Gaming vs Team Gigantti | Playoffs Day 2 Match 1 Game 1 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253645367
# Created: 2018-04-23 16:40:35+00:00
# Duration 0:25:06
echo "71 / 343" >> progress.txt
echo "Title: Eagle Gaming vs Team Gigantti | Playoffs Day 2 Match 1 Game 1 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253645367" >> progress.txt
echo "Duration: 0:25:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253645367
tar cvf /media/ephemeral0/names_253645367.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253645367.tar s3://overtrack-training-data/vod-names/names_253645367.tar
rm /media/ephemeral0/names_253645367.tar
            
# Title: NRG Esports vs OpTic Academy | Week 3 Day 1 Match 2 Game 4 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243716459
# Created: 2018-03-28 02:17:54+00:00
# Duration 0:24:13
echo "72 / 343" >> progress.txt
echo "Title: NRG Esports vs OpTic Academy | Week 3 Day 1 Match 2 Game 4 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243716459" >> progress.txt
echo "Duration: 0:24:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243716459
tar cvf /media/ephemeral0/names_243716459.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243716459.tar s3://overtrack-training-data/vod-names/names_243716459.tar
rm /media/ephemeral0/names_243716459.tar
            
# Title: Talon Esports vs BAZAAR | Week 2 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244322315
# Created: 2018-03-29 18:45:47+00:00
# Duration 0:26:35
echo "73 / 343" >> progress.txt
echo "Title: Talon Esports vs BAZAAR | Week 2 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244322315" >> progress.txt
echo "Duration: 0:26:35" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244322315
tar cvf /media/ephemeral0/names_244322315.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244322315.tar s3://overtrack-training-data/vod-names/names_244322315.tar
rm /media/ephemeral0/names_244322315.tar
            
# Title: Toronto Esports vs. Team Envy | Week 5 Day 2 Match 3 Game 3 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292477361
# Created: 2018-08-03 03:57:35+00:00
# Duration 0:17:55
echo "74 / 343" >> progress.txt
echo "Title: Toronto Esports vs. Team Envy | Week 5 Day 2 Match 3 Game 3 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292477361" >> progress.txt
echo "Duration: 0:17:55" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292477361
tar cvf /media/ephemeral0/names_292477361.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292477361.tar s3://overtrack-training-data/vod-names/names_292477361.tar
rm /media/ephemeral0/names_292477361.tar
            
# Title: NOVA ESPORTS vs Xavier Esports (XVE) | Week 1 Day 2 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282156400
# Created: 2018-07-08 07:59:55+00:00
# Duration 0:16:49
echo "75 / 343" >> progress.txt
echo "Title: NOVA ESPORTS vs Xavier Esports (XVE) | Week 1 Day 2 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282156400" >> progress.txt
echo "Duration: 0:16:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282156400
tar cvf /media/ephemeral0/names_282156400.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282156400.tar s3://overtrack-training-data/vod-names/names_282156400.tar
rm /media/ephemeral0/names_282156400.tar
            
# Title: Eagle Gaming vs We Have Org | Week 3 Day 2 Match 2 Game 3 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285855472
# Created: 2018-07-17 19:00:16+00:00
# Duration 0:24:01
echo "76 / 343" >> progress.txt
echo "Title: Eagle Gaming vs We Have Org | Week 3 Day 2 Match 2 Game 3 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285855472" >> progress.txt
echo "Duration: 0:24:01" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285855472
tar cvf /media/ephemeral0/names_285855472.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285855472.tar s3://overtrack-training-data/vod-names/names_285855472.tar
rm /media/ephemeral0/names_285855472.tar
            
# Title: Eagle Gaming vs Team Gigantti | Playoffs Day 2 Match 1 Game 2 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253648882
# Created: 2018-04-23 16:53:05+00:00
# Duration 0:20:12
echo "77 / 343" >> progress.txt
echo "Title: Eagle Gaming vs Team Gigantti | Playoffs Day 2 Match 1 Game 2 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253648882" >> progress.txt
echo "Duration: 0:20:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253648882
tar cvf /media/ephemeral0/names_253648882.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253648882.tar s3://overtrack-training-data/vod-names/names_253648882.tar
rm /media/ephemeral0/names_253648882.tar
            
# Title: Machi Esports (M17) vs EXL-Esports | Week 4 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290155431
# Created: 2018-07-28 09:11:39+00:00
# Duration 0:29:13
echo "78 / 343" >> progress.txt
echo "Title: Machi Esports (M17) vs EXL-Esports | Week 4 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290155431" >> progress.txt
echo "Duration: 0:29:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290155431
tar cvf /media/ephemeral0/names_290155431.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290155431.tar s3://overtrack-training-data/vod-names/names_290155431.tar
rm /media/ephemeral0/names_290155431.tar
            
# Title: Blank Esports vs MEGA | Week 4 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249874184
# Created: 2018-04-13 14:01:55+00:00
# Duration 0:23:41
echo "79 / 343" >> progress.txt
echo "Title: Blank Esports vs MEGA | Week 4 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249874184" >> progress.txt
echo "Duration: 0:23:41" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249874184
tar cvf /media/ephemeral0/names_249874184.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249874184.tar s3://overtrack-training-data/vod-names/names_249874184.tar
rm /media/ephemeral0/names_249874184.tar
            
# Title: EnVision vs Bye Week | Week 3 Day 1 Match 1 Game 3 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243663712
# Created: 2018-03-27 23:54:10+00:00
# Duration 0:09:12
echo "80 / 343" >> progress.txt
echo "Title: EnVision vs Bye Week | Week 3 Day 1 Match 1 Game 3 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243663712" >> progress.txt
echo "Duration: 0:09:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243663712
tar cvf /media/ephemeral0/names_243663712.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243663712.tar s3://overtrack-training-data/vod-names/names_243663712.tar
rm /media/ephemeral0/names_243663712.tar
            
# Title: BAZAAR vs Machi Esports | Week 3 Day 2 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/247607630
# Created: 2018-04-07 09:53:45+00:00
# Duration 0:20:12
echo "81 / 343" >> progress.txt
echo "Title: BAZAAR vs Machi Esports | Week 3 Day 2 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/247607630" >> progress.txt
echo "Duration: 0:20:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/247607630
tar cvf /media/ephemeral0/names_247607630.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_247607630.tar s3://overtrack-training-data/vod-names/names_247607630.tar
rm /media/ephemeral0/names_247607630.tar
            
# Title: NOVA ESPORTS vs Blank Esports (BLK) | Week 4 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290154184
# Created: 2018-07-28 09:03:51+00:00
# Duration 0:18:53
echo "82 / 343" >> progress.txt
echo "Title: NOVA ESPORTS vs Blank Esports (BLK) | Week 4 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290154184" >> progress.txt
echo "Duration: 0:18:53" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290154184
tar cvf /media/ephemeral0/names_290154184.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290154184.tar s3://overtrack-training-data/vod-names/names_290154184.tar
rm /media/ephemeral0/names_290154184.tar
            
# Title: Angry Titans vs Young and Beautiful | Week 3 Day 1 Match 1 Game 2 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285395315
# Created: 2018-07-16 16:58:22+00:00
# Duration 0:21:20
echo "83 / 343" >> progress.txt
echo "Title: Angry Titans vs Young and Beautiful | Week 3 Day 1 Match 1 Game 2 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285395315" >> progress.txt
echo "Duration: 0:21:20" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285395315
tar cvf /media/ephemeral0/names_285395315.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285395315.tar s3://overtrack-training-data/vod-names/names_285395315.tar
rm /media/ephemeral0/names_285395315.tar
            
# Title: Xavier Esports vs CYCLOPS athlete gaming | Week 2 Day 2 Match 1 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284689773
# Created: 2018-07-14 20:34:02+00:00
# Duration 0:25:30
echo "84 / 343" >> progress.txt
echo "Title: Xavier Esports vs CYCLOPS athlete gaming | Week 2 Day 2 Match 1 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284689773" >> progress.txt
echo "Duration: 0:25:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284689773
tar cvf /media/ephemeral0/names_284689773.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284689773.tar s3://overtrack-training-data/vod-names/names_284689773.tar
rm /media/ephemeral0/names_284689773.tar
            
# Title: Incipience (INC) vs Blank Esports (BLK) | Week 2 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284434621
# Created: 2018-07-14 03:40:40+00:00
# Duration 0:11:30
echo "85 / 343" >> progress.txt
echo "Title: Incipience (INC) vs Blank Esports (BLK) | Week 2 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284434621" >> progress.txt
echo "Duration: 0:11:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284434621
tar cvf /media/ephemeral0/names_284434621.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284434621.tar s3://overtrack-training-data/vod-names/names_284434621.tar
rm /media/ephemeral0/names_284434621.tar
            
# Title: Eagle Gaming vs Young and Beautiful | Week 3 Day 2 Match 1 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244339762
# Created: 2018-03-29 19:30:18+00:00
# Duration 0:18:12
echo "86 / 343" >> progress.txt
echo "Title: Eagle Gaming vs Young and Beautiful | Week 3 Day 2 Match 1 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244339762" >> progress.txt
echo "Duration: 0:18:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244339762
tar cvf /media/ephemeral0/names_244339762.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244339762.tar s3://overtrack-training-data/vod-names/names_244339762.tar
rm /media/ephemeral0/names_244339762.tar
            
# Title: Simplicity vs Fusion University | Week 3 Day 1 Match 3 Game 1 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243738892
# Created: 2018-03-28 03:33:40+00:00
# Duration 0:10:24
echo "87 / 343" >> progress.txt
echo "Title: Simplicity vs Fusion University | Week 3 Day 1 Match 3 Game 1 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243738892" >> progress.txt
echo "Duration: 0:10:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243738892
tar cvf /media/ephemeral0/names_243738892.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243738892.tar s3://overtrack-training-data/vod-names/names_243738892.tar
rm /media/ephemeral0/names_243738892.tar
            
# Title: Orgless and Hungry vs Bazooka Puppiez | Week 3 Day 1 Match 2 Game 1 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285423020
# Created: 2018-07-16 18:11:18+00:00
# Duration 0:11:24
echo "88 / 343" >> progress.txt
echo "Title: Orgless and Hungry vs Bazooka Puppiez | Week 3 Day 1 Match 2 Game 1 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285423020" >> progress.txt
echo "Duration: 0:11:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285423020
tar cvf /media/ephemeral0/names_285423020.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285423020.tar s3://overtrack-training-data/vod-names/names_285423020.tar
rm /media/ephemeral0/names_285423020.tar
            
# Title: Mosaic Esports vs Eagle Gaming | Week 5 Day 2 Match 1 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248469206
# Created: 2018-04-09 17:19:19+00:00
# Duration 0:19:48
echo "89 / 343" >> progress.txt
echo "Title: Mosaic Esports vs Eagle Gaming | Week 5 Day 2 Match 1 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248469206" >> progress.txt
echo "Duration: 0:19:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248469206
tar cvf /media/ephemeral0/names_248469206.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248469206.tar s3://overtrack-training-data/vod-names/names_248469206.tar
rm /media/ephemeral0/names_248469206.tar
            
# Title: British Hurricane vs 6nakes | Week 3 Day 1 Match 3 Game 2 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285483621
# Created: 2018-07-16 20:45:57+00:00
# Duration 0:26:06
echo "90 / 343" >> progress.txt
echo "Title: British Hurricane vs 6nakes | Week 3 Day 1 Match 3 Game 2 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285483621" >> progress.txt
echo "Duration: 0:26:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285483621
tar cvf /media/ephemeral0/names_285483621.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285483621.tar s3://overtrack-training-data/vod-names/names_285483621.tar
rm /media/ephemeral0/names_285483621.tar
            
# Title: MONSTER SHIELD KR vs EXL-Esports | Week 2 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284435714
# Created: 2018-07-14 03:44:19+00:00
# Duration 0:13:00
echo "91 / 343" >> progress.txt
echo "Title: MONSTER SHIELD KR vs EXL-Esports | Week 2 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284435714" >> progress.txt
echo "Duration: 0:13:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284435714
tar cvf /media/ephemeral0/names_284435714.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284435714.tar s3://overtrack-training-data/vod-names/names_284435714.tar
rm /media/ephemeral0/names_284435714.tar
            
# Title: CYCLOPS athlete gaming (CAG) vs Incipience (INC) | Week 4 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290483881
# Created: 2018-07-29 04:20:43+00:00
# Duration 0:20:10
echo "92 / 343" >> progress.txt
echo "Title: CYCLOPS athlete gaming (CAG) vs Incipience (INC) | Week 4 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290483881" >> progress.txt
echo "Duration: 0:20:10" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290483881
tar cvf /media/ephemeral0/names_290483881.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290483881.tar s3://overtrack-training-data/vod-names/names_290483881.tar
rm /media/ephemeral0/names_290483881.tar
            
# Title: Team Gigantti vs Team Singularity | Week 5 Day 1 Match 2 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248123635
# Created: 2018-04-08 17:29:53+00:00
# Duration 0:21:18
echo "93 / 343" >> progress.txt
echo "Title: Team Gigantti vs Team Singularity | Week 5 Day 1 Match 2 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248123635" >> progress.txt
echo "Duration: 0:21:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248123635
tar cvf /media/ephemeral0/names_248123635.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248123635.tar s3://overtrack-training-data/vod-names/names_248123635.tar
rm /media/ephemeral0/names_248123635.tar
            
# Title: Team Gigantti vs Angry Titans | Week 3 Day 1 Match 3 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243982412
# Created: 2018-03-28 20:32:28+00:00
# Duration 0:27:16
echo "94 / 343" >> progress.txt
echo "Title: Team Gigantti vs Angry Titans | Week 3 Day 1 Match 3 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243982412" >> progress.txt
echo "Duration: 0:27:16" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243982412
tar cvf /media/ephemeral0/names_243982412.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243982412.tar s3://overtrack-training-data/vod-names/names_243982412.tar
rm /media/ephemeral0/names_243982412.tar
            
# Title: Talon Esports vs BAZAAR | Week 2 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244320280
# Created: 2018-03-29 18:40:03+00:00
# Duration 0:24:31
echo "95 / 343" >> progress.txt
echo "Title: Talon Esports vs BAZAAR | Week 2 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244320280" >> progress.txt
echo "Duration: 0:24:31" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244320280
tar cvf /media/ephemeral0/names_244320280.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244320280.tar s3://overtrack-training-data/vod-names/names_244320280.tar
rm /media/ephemeral0/names_244320280.tar
            
# Title: MEGA vs Machi Esports | Week 1 Day 1 Match 2 Game 4 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/254696948
# Created: 2018-04-26 15:19:11+00:00
# Duration 0:28:06
echo "96 / 343" >> progress.txt
echo "Title: MEGA vs Machi Esports | Week 1 Day 1 Match 2 Game 4 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/254696948" >> progress.txt
echo "Duration: 0:28:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/254696948
tar cvf /media/ephemeral0/names_254696948.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_254696948.tar s3://overtrack-training-data/vod-names/names_254696948.tar
rm /media/ephemeral0/names_254696948.tar
            
# Title: MONSTER SHIELD KR vs EXL-Esports | Week 2 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284435717
# Created: 2018-07-14 03:44:19+00:00
# Duration 0:19:18
echo "97 / 343" >> progress.txt
echo "Title: MONSTER SHIELD KR vs EXL-Esports | Week 2 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284435717" >> progress.txt
echo "Duration: 0:19:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284435717
tar cvf /media/ephemeral0/names_284435717.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284435717.tar s3://overtrack-training-data/vod-names/names_284435717.tar
rm /media/ephemeral0/names_284435717.tar
            
# Title: MEGA vs Machi Esports | Week 1 Day 1 Match 2 Game 3 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/254696670
# Created: 2018-04-26 15:17:57+00:00
# Duration 0:19:25
echo "98 / 343" >> progress.txt
echo "Title: MEGA vs Machi Esports | Week 1 Day 1 Match 2 Game 3 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/254696670" >> progress.txt
echo "Duration: 0:19:25" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/254696670
tar cvf /media/ephemeral0/names_254696670.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_254696670.tar s3://overtrack-training-data/vod-names/names_254696670.tar
rm /media/ephemeral0/names_254696670.tar
            
# Title: NOVA ESPORTS vs Xavier Esports (XVE) | Week 1 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282156397
# Created: 2018-07-08 07:59:55+00:00
# Duration 0:26:03
echo "99 / 343" >> progress.txt
echo "Title: NOVA ESPORTS vs Xavier Esports (XVE) | Week 1 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282156397" >> progress.txt
echo "Duration: 0:26:03" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282156397
tar cvf /media/ephemeral0/names_282156397.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282156397.tar s3://overtrack-training-data/vod-names/names_282156397.tar
rm /media/ephemeral0/names_282156397.tar
            
# Title: NEW PARADIGM vs MONSTER SHIELD KR | Week 4 Day 2 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290497403
# Created: 2018-07-29 05:15:22+00:00
# Duration 0:22:10
echo "100 / 343" >> progress.txt
echo "Title: NEW PARADIGM vs MONSTER SHIELD KR | Week 4 Day 2 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290497403" >> progress.txt
echo "Duration: 0:22:10" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290497403
tar cvf /media/ephemeral0/names_290497403.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290497403.tar s3://overtrack-training-data/vod-names/names_290497403.tar
rm /media/ephemeral0/names_290497403.tar
            
# Title: NRG Esports vs OpTic Academy | Week 3 Day 1 Match 2 Game 1 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243684831
# Created: 2018-03-28 00:49:59+00:00
# Duration 0:19:55
echo "101 / 343" >> progress.txt
echo "Title: NRG Esports vs OpTic Academy | Week 3 Day 1 Match 2 Game 1 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243684831" >> progress.txt
echo "Duration: 0:19:55" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243684831
tar cvf /media/ephemeral0/names_243684831.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243684831.tar s3://overtrack-training-data/vod-names/names_243684831.tar
rm /media/ephemeral0/names_243684831.tar
            
# Title: Machi Esports vs Detonator KR | Week 1 Day 2 Match 2 Game 3 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242336577
# Created: 2018-03-24 15:21:41+00:00
# Duration 0:14:14
echo "102 / 343" >> progress.txt
echo "Title: Machi Esports vs Detonator KR | Week 1 Day 2 Match 2 Game 3 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242336577" >> progress.txt
echo "Duration: 0:14:14" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242336577
tar cvf /media/ephemeral0/names_242336577.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242336577.tar s3://overtrack-training-data/vod-names/names_242336577.tar
rm /media/ephemeral0/names_242336577.tar
            
# Title: British Hurricane vs Orgless and Hungry | Week 3 Day 1 Match 1 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243930366
# Created: 2018-03-28 18:16:29+00:00
# Duration 0:26:25
echo "103 / 343" >> progress.txt
echo "Title: British Hurricane vs Orgless and Hungry | Week 3 Day 1 Match 1 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243930366" >> progress.txt
echo "Duration: 0:26:25" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243930366
tar cvf /media/ephemeral0/names_243930366.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243930366.tar s3://overtrack-training-data/vod-names/names_243930366.tar
rm /media/ephemeral0/names_243930366.tar
            
# Title: Mosaic Esports vs Eagle Gaming | Week 5 Day 2 Match 1 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248453208
# Created: 2018-04-09 16:27:14+00:00
# Duration 0:13:00
echo "104 / 343" >> progress.txt
echo "Title: Mosaic Esports vs Eagle Gaming | Week 5 Day 2 Match 1 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248453208" >> progress.txt
echo "Duration: 0:13:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248453208
tar cvf /media/ephemeral0/names_248453208.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248453208.tar s3://overtrack-training-data/vod-names/names_248453208.tar
rm /media/ephemeral0/names_248453208.tar
            
# Title: Mayhem Academy vs. Last Night's Leftovers | Week 5 Day 1 Match 3 Game 4 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291878117
# Created: 2018-08-01 18:11:48+00:00
# Duration 0:38:38
echo "105 / 343" >> progress.txt
echo "Title: Mayhem Academy vs. Last Night's Leftovers | Week 5 Day 1 Match 3 Game 4 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291878117" >> progress.txt
echo "Duration: 0:38:38" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291878117
tar cvf /media/ephemeral0/names_291878117.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291878117.tar s3://overtrack-training-data/vod-names/names_291878117.tar
rm /media/ephemeral0/names_291878117.tar
            
# Title: Blank Esports vs Xavier Esports | Week 3 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246934586
# Created: 2018-04-05 16:15:01+00:00
# Duration 0:09:43
echo "106 / 343" >> progress.txt
echo "Title: Blank Esports vs Xavier Esports | Week 3 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246934586" >> progress.txt
echo "Duration: 0:09:43" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246934586
tar cvf /media/ephemeral0/names_246934586.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246934586.tar s3://overtrack-training-data/vod-names/names_246934586.tar
rm /media/ephemeral0/names_246934586.tar
            
# Title: Eagle Gaming vs Young and Beautiful | Week 3 Day 2 Match 1 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244390027
# Created: 2018-03-29 21:53:33+00:00
# Duration 0:22:36
echo "107 / 343" >> progress.txt
echo "Title: Eagle Gaming vs Young and Beautiful | Week 3 Day 2 Match 1 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244390027" >> progress.txt
echo "Duration: 0:22:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244390027
tar cvf /media/ephemeral0/names_244390027.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244390027.tar s3://overtrack-training-data/vod-names/names_244390027.tar
rm /media/ephemeral0/names_244390027.tar
            
# Title: EXL-Esports vs NEW PARADIGM | Week 1 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281766319
# Created: 2018-07-07 05:42:24+00:00
# Duration 0:18:06
echo "108 / 343" >> progress.txt
echo "Title: EXL-Esports vs NEW PARADIGM | Week 1 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281766319" >> progress.txt
echo "Duration: 0:18:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281766319
tar cvf /media/ephemeral0/names_281766319.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281766319.tar s3://overtrack-training-data/vod-names/names_281766319.tar
rm /media/ephemeral0/names_281766319.tar
            
# Title: MEGA vs YOSHIMOTO ENCOUNT | Week 2 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/245351229
# Created: 2018-04-01 08:24:18+00:00
# Duration 0:13:19
echo "109 / 343" >> progress.txt
echo "Title: MEGA vs YOSHIMOTO ENCOUNT | Week 2 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245351229" >> progress.txt
echo "Duration: 0:13:19" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245351229
tar cvf /media/ephemeral0/names_245351229.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245351229.tar s3://overtrack-training-data/vod-names/names_245351229.tar
rm /media/ephemeral0/names_245351229.tar
            
# Title: Toronto Esports vs. Team Envy | Week 5 Day 2 Match 3 Game 2 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292470372
# Created: 2018-08-03 03:33:58+00:00
# Duration 0:11:06
echo "110 / 343" >> progress.txt
echo "Title: Toronto Esports vs. Team Envy | Week 5 Day 2 Match 3 Game 2 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292470372" >> progress.txt
echo "Duration: 0:11:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292470372
tar cvf /media/ephemeral0/names_292470372.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292470372.tar s3://overtrack-training-data/vod-names/names_292470372.tar
rm /media/ephemeral0/names_292470372.tar
            
# Title: Team Gigantti vs Copenhagen Flames | Week 3 Day 2 Match 3 Game 4 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285915360
# Created: 2018-07-17 21:37:43+00:00
# Duration 0:26:54
echo "111 / 343" >> progress.txt
echo "Title: Team Gigantti vs Copenhagen Flames | Week 3 Day 2 Match 3 Game 4 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285915360" >> progress.txt
echo "Duration: 0:26:54" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285915360
tar cvf /media/ephemeral0/names_285915360.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285915360.tar s3://overtrack-training-data/vod-names/names_285915360.tar
rm /media/ephemeral0/names_285915360.tar
            
# Title: Hong Kong Attitude (HKA) vs Xavier Esports (XVE) | Week 4 Day 2 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290479625
# Created: 2018-07-29 04:04:57+00:00
# Duration 0:22:06
echo "112 / 343" >> progress.txt
echo "Title: Hong Kong Attitude (HKA) vs Xavier Esports (XVE) | Week 4 Day 2 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290479625" >> progress.txt
echo "Duration: 0:22:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290479625
tar cvf /media/ephemeral0/names_290479625.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290479625.tar s3://overtrack-training-data/vod-names/names_290479625.tar
rm /media/ephemeral0/names_290479625.tar
            
# Title: CIS HOPE vs ONE.POINT | Week 3 Day 2 Match 1 Game 4 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285825805
# Created: 2018-07-17 17:47:28+00:00
# Duration 0:20:03
echo "113 / 343" >> progress.txt
echo "Title: CIS HOPE vs ONE.POINT | Week 3 Day 2 Match 1 Game 4 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285825805" >> progress.txt
echo "Duration: 0:20:03" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285825805
tar cvf /media/ephemeral0/names_285825805.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285825805.tar s3://overtrack-training-data/vod-names/names_285825805.tar
rm /media/ephemeral0/names_285825805.tar
            
# Title: British Hurricane vs Young & Beautiful | Playoffs - Round of 8 | Day 1 Match 1 Game 1 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253259327
# Created: 2018-04-22 14:47:53+00:00
# Duration 0:14:42
echo "114 / 343" >> progress.txt
echo "Title: British Hurricane vs Young & Beautiful | Playoffs - Round of 8 | Day 1 Match 1 Game 1 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253259327" >> progress.txt
echo "Duration: 0:14:42" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253259327
tar cvf /media/ephemeral0/names_253259327.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253259327.tar s3://overtrack-training-data/vod-names/names_253259327.tar
rm /media/ephemeral0/names_253259327.tar
            
# Title: Machi Esports vs MEGA | Week 2 Day 2 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284708920
# Created: 2018-07-14 21:29:53+00:00
# Duration 0:16:00
echo "115 / 343" >> progress.txt
echo "Title: Machi Esports vs MEGA | Week 2 Day 2 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284708920" >> progress.txt
echo "Duration: 0:16:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284708920
tar cvf /media/ephemeral0/names_284708920.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284708920.tar s3://overtrack-training-data/vod-names/names_284708920.tar
rm /media/ephemeral0/names_284708920.tar
            
# Title: EXL-Esports vs Mega (MGA) | Week 5 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292928123
# Created: 2018-08-04 06:41:26+00:00
# Duration 0:19:58
echo "116 / 343" >> progress.txt
echo "Title: EXL-Esports vs Mega (MGA) | Week 5 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292928123" >> progress.txt
echo "Duration: 0:19:58" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292928123
tar cvf /media/ephemeral0/names_292928123.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292928123.tar s3://overtrack-training-data/vod-names/names_292928123.tar
rm /media/ephemeral0/names_292928123.tar
            
# Title: Grizzlys vs XL2 Academy | Week 3 Day 2 Match 3 Game 2 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244151144
# Created: 2018-03-29 05:25:30+00:00
# Duration 0:26:37
echo "117 / 343" >> progress.txt
echo "Title: Grizzlys vs XL2 Academy | Week 3 Day 2 Match 3 Game 2 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244151144" >> progress.txt
echo "Duration: 0:26:37" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244151144
tar cvf /media/ephemeral0/names_244151144.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244151144.tar s3://overtrack-training-data/vod-names/names_244151144.tar
rm /media/ephemeral0/names_244151144.tar
            
# Title: Xavier Esports vs LogitechG ABANG | Week 5 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252453533
# Created: 2018-04-20 14:12:02+00:00
# Duration 0:15:30
echo "118 / 343" >> progress.txt
echo "Title: Xavier Esports vs LogitechG ABANG | Week 5 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252453533" >> progress.txt
echo "Duration: 0:15:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252453533
tar cvf /media/ephemeral0/names_252453533.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252453533.tar s3://overtrack-training-data/vod-names/names_252453533.tar
rm /media/ephemeral0/names_252453533.tar
            
# Title:  Toronto Esports vs Gladiators Legion | Week 3 Day 2 Match 2 Game 2 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244148963
# Created: 2018-03-29 05:13:36+00:00
# Duration 0:28:13
echo "119 / 343" >> progress.txt
echo "Title:  Toronto Esports vs Gladiators Legion | Week 3 Day 2 Match 2 Game 2 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244148963" >> progress.txt
echo "Duration: 0:28:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244148963
tar cvf /media/ephemeral0/names_244148963.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244148963.tar s3://overtrack-training-data/vod-names/names_244148963.tar
rm /media/ephemeral0/names_244148963.tar
            
# Title: Talon Esports vs Detonator KR | Week 3 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246933295
# Created: 2018-04-05 16:10:29+00:00
# Duration 0:09:13
echo "120 / 343" >> progress.txt
echo "Title: Talon Esports vs Detonator KR | Week 3 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246933295" >> progress.txt
echo "Duration: 0:09:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246933295
tar cvf /media/ephemeral0/names_246933295.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246933295.tar s3://overtrack-training-data/vod-names/names_246933295.tar
rm /media/ephemeral0/names_246933295.tar
            
# Title: MEGA vs LogitechG ABANG | Week 1 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241691329
# Created: 2018-03-22 21:08:27+00:00
# Duration 0:16:43
echo "121 / 343" >> progress.txt
echo "Title: MEGA vs LogitechG ABANG | Week 1 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241691329" >> progress.txt
echo "Duration: 0:16:43" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241691329
tar cvf /media/ephemeral0/names_241691329.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241691329.tar s3://overtrack-training-data/vod-names/names_241691329.tar
rm /media/ephemeral0/names_241691329.tar
            
# Title: MEGA vs LogitechG ABANG | Week 1 Day 1 Match 3 Game 5 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241692778
# Created: 2018-03-22 21:12:48+00:00
# Duration 0:17:21
echo "122 / 343" >> progress.txt
echo "Title: MEGA vs LogitechG ABANG | Week 1 Day 1 Match 3 Game 5 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241692778" >> progress.txt
echo "Duration: 0:17:21" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241692778
tar cvf /media/ephemeral0/names_241692778.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241692778.tar s3://overtrack-training-data/vod-names/names_241692778.tar
rm /media/ephemeral0/names_241692778.tar
            
# Title: Hong Kong Attitude vs Bazaar | Week 1 Day 2 Match 1 Game 2 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242321924
# Created: 2018-03-24 14:33:58+00:00
# Duration 0:09:08
echo "123 / 343" >> progress.txt
echo "Title: Hong Kong Attitude vs Bazaar | Week 1 Day 2 Match 1 Game 2 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242321924" >> progress.txt
echo "Duration: 0:09:08" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242321924
tar cvf /media/ephemeral0/names_242321924.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242321924.tar s3://overtrack-training-data/vod-names/names_242321924.tar
rm /media/ephemeral0/names_242321924.tar
            
# Title: EnVision vs Bye Week | Week 3 Day 1 Match 1 Game 1 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243652517
# Created: 2018-03-27 23:21:44+00:00
# Duration 0:06:54
echo "124 / 343" >> progress.txt
echo "Title: EnVision vs Bye Week | Week 3 Day 1 Match 1 Game 1 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243652517" >> progress.txt
echo "Duration: 0:06:54" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243652517
tar cvf /media/ephemeral0/names_243652517.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243652517.tar s3://overtrack-training-data/vod-names/names_243652517.tar
rm /media/ephemeral0/names_243652517.tar
            
# Title: Blank Esports (BLK) vs Hong Kong Attitude (HKA) | Week 5 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292928918
# Created: 2018-08-04 06:45:34+00:00
# Duration 0:15:34
echo "125 / 343" >> progress.txt
echo "Title: Blank Esports (BLK) vs Hong Kong Attitude (HKA) | Week 5 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292928918" >> progress.txt
echo "Duration: 0:15:34" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292928918
tar cvf /media/ephemeral0/names_292928918.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292928918.tar s3://overtrack-training-data/vod-names/names_292928918.tar
rm /media/ephemeral0/names_292928918.tar
            
# Title: Yoshimoto Encount vs Xavier Esports | Week 1 Day 2 Match 3 Game 2 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242340803
# Created: 2018-03-24 15:35:43+00:00
# Duration 0:11:32
echo "126 / 343" >> progress.txt
echo "Title: Yoshimoto Encount vs Xavier Esports | Week 1 Day 2 Match 3 Game 2 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242340803" >> progress.txt
echo "Duration: 0:11:32" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242340803
tar cvf /media/ephemeral0/names_242340803.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242340803.tar s3://overtrack-training-data/vod-names/names_242340803.tar
rm /media/ephemeral0/names_242340803.tar
            
# Title: Eagle Gaming vs We Have Org | Week 3 Day 2 Match 2 Game 1 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285842632
# Created: 2018-07-17 18:28:35+00:00
# Duration 0:24:48
echo "127 / 343" >> progress.txt
echo "Title: Eagle Gaming vs We Have Org | Week 3 Day 2 Match 2 Game 1 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285842632" >> progress.txt
echo "Duration: 0:24:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285842632
tar cvf /media/ephemeral0/names_285842632.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285842632.tar s3://overtrack-training-data/vod-names/names_285842632.tar
rm /media/ephemeral0/names_285842632.tar
            
# Title: Hong Kong Attitude vs Machi Esports | Week 2 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/245357435
# Created: 2018-04-01 09:03:57+00:00
# Duration 0:19:51
echo "128 / 343" >> progress.txt
echo "Title: Hong Kong Attitude vs Machi Esports | Week 2 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245357435" >> progress.txt
echo "Duration: 0:19:51" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245357435
tar cvf /media/ephemeral0/names_245357435.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245357435.tar s3://overtrack-training-data/vod-names/names_245357435.tar
rm /media/ephemeral0/names_245357435.tar
            
# Title: Team Gigantti vs Copenhagen Flames | Week 3 Day 2 Match 3 Game 2 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285915361
# Created: 2018-07-17 21:37:43+00:00
# Duration 0:14:35
echo "129 / 343" >> progress.txt
echo "Title: Team Gigantti vs Copenhagen Flames | Week 3 Day 2 Match 3 Game 2 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285915361" >> progress.txt
echo "Duration: 0:14:35" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285915361
tar cvf /media/ephemeral0/names_285915361.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285915361.tar s3://overtrack-training-data/vod-names/names_285915361.tar
rm /media/ephemeral0/names_285915361.tar
            
# Title: CIS HOPE vs ONE.POINT | Week 3 Day 2 Match 1 Game 1 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285798253
# Created: 2018-07-17 16:30:20+00:00
# Duration 0:21:20
echo "130 / 343" >> progress.txt
echo "Title: CIS HOPE vs ONE.POINT | Week 3 Day 2 Match 1 Game 1 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285798253" >> progress.txt
echo "Duration: 0:21:20" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285798253
tar cvf /media/ephemeral0/names_285798253.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285798253.tar s3://overtrack-training-data/vod-names/names_285798253.tar
rm /media/ephemeral0/names_285798253.tar
            
# Title: Talon Esports vs Hong Kong Attitude | Week 5 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252043064
# Created: 2018-04-19 09:33:52+00:00
# Duration 0:27:10
echo "131 / 343" >> progress.txt
echo "Title: Talon Esports vs Hong Kong Attitude | Week 5 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252043064" >> progress.txt
echo "Duration: 0:27:10" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252043064
tar cvf /media/ephemeral0/names_252043064.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252043064.tar s3://overtrack-training-data/vod-names/names_252043064.tar
rm /media/ephemeral0/names_252043064.tar
            
# Title: Talon Esports vs Detonator KR | Week 3 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246933040
# Created: 2018-04-05 16:09:38+00:00
# Duration 0:12:46
echo "132 / 343" >> progress.txt
echo "Title: Talon Esports vs Detonator KR | Week 3 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246933040" >> progress.txt
echo "Duration: 0:12:46" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246933040
tar cvf /media/ephemeral0/names_246933040.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246933040.tar s3://overtrack-training-data/vod-names/names_246933040.tar
rm /media/ephemeral0/names_246933040.tar
            
# Title: Machi Esports (M17) vs Talon Esport (TLN) | Week 1 Day 2 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282154733
# Created: 2018-07-08 07:49:59+00:00
# Duration 0:18:07
echo "133 / 343" >> progress.txt
echo "Title: Machi Esports (M17) vs Talon Esport (TLN) | Week 1 Day 2 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282154733" >> progress.txt
echo "Duration: 0:18:07" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282154733
tar cvf /media/ephemeral0/names_282154733.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282154733.tar s3://overtrack-training-data/vod-names/names_282154733.tar
rm /media/ephemeral0/names_282154733.tar
            
# Title: OneShine Esports vs MEGA | Week 3 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249872060
# Created: 2018-04-13 13:53:58+00:00
# Duration 0:17:14
echo "134 / 343" >> progress.txt
echo "Title: OneShine Esports vs MEGA | Week 3 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249872060" >> progress.txt
echo "Duration: 0:17:14" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249872060
tar cvf /media/ephemeral0/names_249872060.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249872060.tar s3://overtrack-training-data/vod-names/names_249872060.tar
rm /media/ephemeral0/names_249872060.tar
            
# Title: Toronto Esports vs Gladiators Legion | Week 3 Day 2 Match 2 Game 4 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244151733
# Created: 2018-03-29 05:28:39+00:00
# Duration 0:25:01
echo "135 / 343" >> progress.txt
echo "Title: Toronto Esports vs Gladiators Legion | Week 3 Day 2 Match 2 Game 4 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244151733" >> progress.txt
echo "Duration: 0:25:01" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244151733
tar cvf /media/ephemeral0/names_244151733.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244151733.tar s3://overtrack-training-data/vod-names/names_244151733.tar
rm /media/ephemeral0/names_244151733.tar
            
# Title: Machi Esports vs Detonator KR | Week 1 Day 2 Match 2 Game 1 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242329566
# Created: 2018-03-24 14:59:17+00:00
# Duration 0:27:00
echo "136 / 343" >> progress.txt
echo "Title: Machi Esports vs Detonator KR | Week 1 Day 2 Match 2 Game 1 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242329566" >> progress.txt
echo "Duration: 0:27:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242329566
tar cvf /media/ephemeral0/names_242329566.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242329566.tar s3://overtrack-training-data/vod-names/names_242329566.tar
rm /media/ephemeral0/names_242329566.tar
            
# Title: Bazooka Puppiez vs Young and Beautiful | Week 5 Day 2 Match 2 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248500809
# Created: 2018-04-09 18:52:44+00:00
# Duration 0:19:24
echo "137 / 343" >> progress.txt
echo "Title: Bazooka Puppiez vs Young and Beautiful | Week 5 Day 2 Match 2 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248500809" >> progress.txt
echo "Duration: 0:19:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248500809
tar cvf /media/ephemeral0/names_248500809.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248500809.tar s3://overtrack-training-data/vod-names/names_248500809.tar
rm /media/ephemeral0/names_248500809.tar
            
# Title: Angry Titans vs Copenhagen Flames | Playoffs Day 2 Match 2 Game 2 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253673424
# Created: 2018-04-23 18:05:32+00:00
# Duration 0:11:12
echo "138 / 343" >> progress.txt
echo "Title: Angry Titans vs Copenhagen Flames | Playoffs Day 2 Match 2 Game 2 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253673424" >> progress.txt
echo "Duration: 0:11:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253673424
tar cvf /media/ephemeral0/names_253673424.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253673424.tar s3://overtrack-training-data/vod-names/names_253673424.tar
rm /media/ephemeral0/names_253673424.tar
            
# Title: Machi Esports (M17) vs Talon Esport (TLN) | Week 1 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282154734
# Created: 2018-07-08 07:49:59+00:00
# Duration 0:26:11
echo "139 / 343" >> progress.txt
echo "Title: Machi Esports (M17) vs Talon Esport (TLN) | Week 1 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282154734" >> progress.txt
echo "Duration: 0:26:11" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282154734
tar cvf /media/ephemeral0/names_282154734.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282154734.tar s3://overtrack-training-data/vod-names/names_282154734.tar
rm /media/ephemeral0/names_282154734.tar
            
# Title: Talon Esports vs Machi Esports | Week 4 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249878834
# Created: 2018-04-13 14:20:49+00:00
# Duration 0:17:45
echo "140 / 343" >> progress.txt
echo "Title: Talon Esports vs Machi Esports | Week 4 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249878834" >> progress.txt
echo "Duration: 0:17:45" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249878834
tar cvf /media/ephemeral0/names_249878834.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249878834.tar s3://overtrack-training-data/vod-names/names_249878834.tar
rm /media/ephemeral0/names_249878834.tar
            
# Title: Machi Esports (M17) vs Talon Esport (TLN) | Week 1 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282154735
# Created: 2018-07-08 07:49:59+00:00
# Duration 0:18:52
echo "141 / 343" >> progress.txt
echo "Title: Machi Esports (M17) vs Talon Esport (TLN) | Week 1 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282154735" >> progress.txt
echo "Duration: 0:18:52" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282154735
tar cvf /media/ephemeral0/names_282154735.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282154735.tar s3://overtrack-training-data/vod-names/names_282154735.tar
rm /media/ephemeral0/names_282154735.tar
            
# Title: Eagle Gaming vs Young and Beautiful | Week 3 Day 2 Match 1 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244392590
# Created: 2018-03-29 22:00:46+00:00
# Duration 0:31:06
echo "142 / 343" >> progress.txt
echo "Title: Eagle Gaming vs Young and Beautiful | Week 3 Day 2 Match 1 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244392590" >> progress.txt
echo "Duration: 0:31:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244392590
tar cvf /media/ephemeral0/names_244392590.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244392590.tar s3://overtrack-training-data/vod-names/names_244392590.tar
rm /media/ephemeral0/names_244392590.tar
            
# Title: Xavier Esports vs MEGA | Week 4 Day 2 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250289622
# Created: 2018-04-14 15:53:19+00:00
# Duration 0:21:40
echo "143 / 343" >> progress.txt
echo "Title: Xavier Esports vs MEGA | Week 4 Day 2 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250289622" >> progress.txt
echo "Duration: 0:21:40" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250289622
tar cvf /media/ephemeral0/names_250289622.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250289622.tar s3://overtrack-training-data/vod-names/names_250289622.tar
rm /media/ephemeral0/names_250289622.tar
            
# Title: NOVA ESPORTS vs Xavier Esports (XVE) | Week 1 Day 2 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282156398
# Created: 2018-07-08 07:59:55+00:00
# Duration 0:20:17
echo "144 / 343" >> progress.txt
echo "Title: NOVA ESPORTS vs Xavier Esports (XVE) | Week 1 Day 2 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282156398" >> progress.txt
echo "Duration: 0:20:17" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282156398
tar cvf /media/ephemeral0/names_282156398.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282156398.tar s3://overtrack-training-data/vod-names/names_282156398.tar
rm /media/ephemeral0/names_282156398.tar
            
# Title: NOVA ESPORTS vs Xavier Esports (XVE) | Week 1 Day 2 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282156400
# Created: 2018-07-08 07:59:55+00:00
# Duration 0:16:49
echo "145 / 343" >> progress.txt
echo "Title: NOVA ESPORTS vs Xavier Esports (XVE) | Week 1 Day 2 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282156400" >> progress.txt
echo "Duration: 0:16:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282156400
tar cvf /media/ephemeral0/names_282156400.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282156400.tar s3://overtrack-training-data/vod-names/names_282156400.tar
rm /media/ephemeral0/names_282156400.tar
            
# Title: Orgless and Hungry vs Angry Titans | Week 5 Day 1 Match 1 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248089476
# Created: 2018-04-08 15:48:03+00:00
# Duration 0:22:36
echo "146 / 343" >> progress.txt
echo "Title: Orgless and Hungry vs Angry Titans | Week 5 Day 1 Match 1 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248089476" >> progress.txt
echo "Duration: 0:22:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248089476
tar cvf /media/ephemeral0/names_248089476.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248089476.tar s3://overtrack-training-data/vod-names/names_248089476.tar
rm /media/ephemeral0/names_248089476.tar
            
# Title: Simplicity vs Fusion University | Week 3 Day 1 Match 3 Game 5 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243753102
# Created: 2018-03-28 04:24:28+00:00
# Duration 0:19:19
echo "147 / 343" >> progress.txt
echo "Title: Simplicity vs Fusion University | Week 3 Day 1 Match 3 Game 5 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243753102" >> progress.txt
echo "Duration: 0:19:19" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243753102
tar cvf /media/ephemeral0/names_243753102.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243753102.tar s3://overtrack-training-data/vod-names/names_243753102.tar
rm /media/ephemeral0/names_243753102.tar
            
# Title: Hong Kong Attitude (HKA) vs Xavier Esports (XVE) | Week 4 Day 2 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290479628
# Created: 2018-07-29 04:04:57+00:00
# Duration 0:21:25
echo "148 / 343" >> progress.txt
echo "Title: Hong Kong Attitude (HKA) vs Xavier Esports (XVE) | Week 4 Day 2 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290479628" >> progress.txt
echo "Duration: 0:21:25" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290479628
tar cvf /media/ephemeral0/names_290479628.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290479628.tar s3://overtrack-training-data/vod-names/names_290479628.tar
rm /media/ephemeral0/names_290479628.tar
            
# Title: Blank Esports vs LogitechG ABANG | Week 2 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244313734
# Created: 2018-03-29 18:22:23+00:00
# Duration 0:20:29
echo "149 / 343" >> progress.txt
echo "Title: Blank Esports vs LogitechG ABANG | Week 2 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244313734" >> progress.txt
echo "Duration: 0:20:29" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244313734
tar cvf /media/ephemeral0/names_244313734.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244313734.tar s3://overtrack-training-data/vod-names/names_244313734.tar
rm /media/ephemeral0/names_244313734.tar
            
# Title: NOVA ESPORTS vs Xavier Esports (XVE) | Week 1 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282156396
# Created: 2018-07-08 07:59:55+00:00
# Duration 0:19:36
echo "150 / 343" >> progress.txt
echo "Title: NOVA ESPORTS vs Xavier Esports (XVE) | Week 1 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282156396" >> progress.txt
echo "Duration: 0:19:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282156396
tar cvf /media/ephemeral0/names_282156396.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282156396.tar s3://overtrack-training-data/vod-names/names_282156396.tar
rm /media/ephemeral0/names_282156396.tar
            
# Title: Incipience (INC) vs Blank Esports (BLK) | Week 2 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284434618
# Created: 2018-07-14 03:40:40+00:00
# Duration 0:22:42
echo "151 / 343" >> progress.txt
echo "Title: Incipience (INC) vs Blank Esports (BLK) | Week 2 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284434618" >> progress.txt
echo "Duration: 0:22:42" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284434618
tar cvf /media/ephemeral0/names_284434618.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284434618.tar s3://overtrack-training-data/vod-names/names_284434618.tar
rm /media/ephemeral0/names_284434618.tar
            
# Title: MEGA vs YOSHIMOTO ENCOUNT | Week 2 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/245350055
# Created: 2018-04-01 08:16:23+00:00
# Duration 0:19:57
echo "152 / 343" >> progress.txt
echo "Title: MEGA vs YOSHIMOTO ENCOUNT | Week 2 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245350055" >> progress.txt
echo "Duration: 0:19:57" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245350055
tar cvf /media/ephemeral0/names_245350055.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245350055.tar s3://overtrack-training-data/vod-names/names_245350055.tar
rm /media/ephemeral0/names_245350055.tar
            
# Title: Eagle Gaming vs Young and Beautiful | Week 3 Day 2 Match 1 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244336001
# Created: 2018-03-29 19:20:03+00:00
# Duration 0:17:18
echo "153 / 343" >> progress.txt
echo "Title: Eagle Gaming vs Young and Beautiful | Week 3 Day 2 Match 1 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244336001" >> progress.txt
echo "Duration: 0:17:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244336001
tar cvf /media/ephemeral0/names_244336001.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244336001.tar s3://overtrack-training-data/vod-names/names_244336001.tar
rm /media/ephemeral0/names_244336001.tar
            
# Title: XL2 Academy vs. Bye Week | Week 5 Day 2 Match 2 Game 3 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292448051
# Created: 2018-08-03 02:28:15+00:00
# Duration 0:32:43
echo "154 / 343" >> progress.txt
echo "Title: XL2 Academy vs. Bye Week | Week 5 Day 2 Match 2 Game 3 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292448051" >> progress.txt
echo "Duration: 0:32:43" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292448051
tar cvf /media/ephemeral0/names_292448051.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292448051.tar s3://overtrack-training-data/vod-names/names_292448051.tar
rm /media/ephemeral0/names_292448051.tar
            
# Title: BAZAAR vs Machi Esports | Week 3 Day 2 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/247670327
# Created: 2018-04-07 14:44:10+00:00
# Duration 0:15:21
echo "155 / 343" >> progress.txt
echo "Title: BAZAAR vs Machi Esports | Week 3 Day 2 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/247670327" >> progress.txt
echo "Duration: 0:15:21" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/247670327
tar cvf /media/ephemeral0/names_247670327.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_247670327.tar s3://overtrack-training-data/vod-names/names_247670327.tar
rm /media/ephemeral0/names_247670327.tar
            
# Title: Blank Esports vs MEGA | Week 4 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249877002
# Created: 2018-04-13 14:13:04+00:00
# Duration 0:17:21
echo "156 / 343" >> progress.txt
echo "Title: Blank Esports vs MEGA | Week 4 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249877002" >> progress.txt
echo "Duration: 0:17:21" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249877002
tar cvf /media/ephemeral0/names_249877002.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249877002.tar s3://overtrack-training-data/vod-names/names_249877002.tar
rm /media/ephemeral0/names_249877002.tar
            
# Title: Orgless and Hungry vs Bazooka Puppiez | Week 3 Day 1 Match 2 Game 4 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285459257
# Created: 2018-07-16 19:43:08+00:00
# Duration 0:15:29
echo "157 / 343" >> progress.txt
echo "Title: Orgless and Hungry vs Bazooka Puppiez | Week 3 Day 1 Match 2 Game 4 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285459257" >> progress.txt
echo "Duration: 0:15:29" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285459257
tar cvf /media/ephemeral0/names_285459257.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285459257.tar s3://overtrack-training-data/vod-names/names_285459257.tar
rm /media/ephemeral0/names_285459257.tar
            
# Title: Hong Kong Attitude vs Machi Esports | Week 2 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/245354936
# Created: 2018-04-01 08:48:44+00:00
# Duration 0:22:01
echo "158 / 343" >> progress.txt
echo "Title: Hong Kong Attitude vs Machi Esports | Week 2 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245354936" >> progress.txt
echo "Duration: 0:22:01" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245354936
tar cvf /media/ephemeral0/names_245354936.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245354936.tar s3://overtrack-training-data/vod-names/names_245354936.tar
rm /media/ephemeral0/names_245354936.tar
            
# Title: Blank Esports vs Talon Esports | Week 1 Day 2 Match 1 Game 1 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/255425658
# Created: 2018-04-28 15:25:22+00:00
# Duration 0:21:17
echo "159 / 343" >> progress.txt
echo "Title: Blank Esports vs Talon Esports | Week 1 Day 2 Match 1 Game 1 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/255425658" >> progress.txt
echo "Duration: 0:21:17" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/255425658
tar cvf /media/ephemeral0/names_255425658.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_255425658.tar s3://overtrack-training-data/vod-names/names_255425658.tar
rm /media/ephemeral0/names_255425658.tar
            
# Title: NRG Esports vs. Skyfoxes | Week 5 Day 2 Match 1 Game 4 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292416323
# Created: 2018-08-03 01:01:58+00:00
# Duration 0:26:49
echo "160 / 343" >> progress.txt
echo "Title: NRG Esports vs. Skyfoxes | Week 5 Day 2 Match 1 Game 4 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292416323" >> progress.txt
echo "Duration: 0:26:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292416323
tar cvf /media/ephemeral0/names_292416323.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292416323.tar s3://overtrack-training-data/vod-names/names_292416323.tar
rm /media/ephemeral0/names_292416323.tar
            
# Title: Bazooka Puppiez vs Copenhagen Flames | Week 3 Day 2 Match 2 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244401897
# Created: 2018-03-29 22:28:15+00:00
# Duration 0:19:00
echo "161 / 343" >> progress.txt
echo "Title: Bazooka Puppiez vs Copenhagen Flames | Week 3 Day 2 Match 2 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244401897" >> progress.txt
echo "Duration: 0:19:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244401897
tar cvf /media/ephemeral0/names_244401897.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244401897.tar s3://overtrack-training-data/vod-names/names_244401897.tar
rm /media/ephemeral0/names_244401897.tar
            
# Title: NEW PARADIGM vs MONSTER SHIELD KR | Week 4 Day 2 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290497406
# Created: 2018-07-29 05:15:22+00:00
# Duration 0:20:44
echo "162 / 343" >> progress.txt
echo "Title: NEW PARADIGM vs MONSTER SHIELD KR | Week 4 Day 2 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290497406" >> progress.txt
echo "Duration: 0:20:44" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290497406
tar cvf /media/ephemeral0/names_290497406.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290497406.tar s3://overtrack-training-data/vod-names/names_290497406.tar
rm /media/ephemeral0/names_290497406.tar
            
# Title: Mega (MGA) vs Talon Esport (TLN) | Week 4 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290156202
# Created: 2018-07-28 09:16:39+00:00
# Duration 0:18:22
echo "163 / 343" >> progress.txt
echo "Title: Mega (MGA) vs Talon Esport (TLN) | Week 4 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290156202" >> progress.txt
echo "Duration: 0:18:22" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290156202
tar cvf /media/ephemeral0/names_290156202.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290156202.tar s3://overtrack-training-data/vod-names/names_290156202.tar
rm /media/ephemeral0/names_290156202.tar
            
# Title: Team British Hurricane vs Team That's A Disband | Week 5 Day 1 Match 3 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248146994
# Created: 2018-04-08 18:27:55+00:00
# Duration 0:17:36
echo "164 / 343" >> progress.txt
echo "Title: Team British Hurricane vs Team That's A Disband | Week 5 Day 1 Match 3 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248146994" >> progress.txt
echo "Duration: 0:17:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248146994
tar cvf /media/ephemeral0/names_248146994.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248146994.tar s3://overtrack-training-data/vod-names/names_248146994.tar
rm /media/ephemeral0/names_248146994.tar
            
# Title: Angry Titans vs Young and Beautiful | Week 3 Day 1 Match 1 Game 1 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285390118
# Created: 2018-07-16 16:42:53+00:00
# Duration 0:16:10
echo "165 / 343" >> progress.txt
echo "Title: Angry Titans vs Young and Beautiful | Week 3 Day 1 Match 1 Game 1 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285390118" >> progress.txt
echo "Duration: 0:16:10" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285390118
tar cvf /media/ephemeral0/names_285390118.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285390118.tar s3://overtrack-training-data/vod-names/names_285390118.tar
rm /media/ephemeral0/names_285390118.tar
            
# Title: Blank Esports vs Xavier Esports | Week 3 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246934299
# Created: 2018-04-05 16:13:56+00:00
# Duration 0:31:48
echo "166 / 343" >> progress.txt
echo "Title: Blank Esports vs Xavier Esports | Week 3 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246934299" >> progress.txt
echo "Duration: 0:31:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246934299
tar cvf /media/ephemeral0/names_246934299.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246934299.tar s3://overtrack-training-data/vod-names/names_246934299.tar
rm /media/ephemeral0/names_246934299.tar
            
# Title: BAZAAR vs Chaos Theory | Week 4 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250298397
# Created: 2018-04-14 16:20:17+00:00
# Duration 0:27:19
echo "167 / 343" >> progress.txt
echo "Title: BAZAAR vs Chaos Theory | Week 4 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250298397" >> progress.txt
echo "Duration: 0:27:19" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250298397
tar cvf /media/ephemeral0/names_250298397.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250298397.tar s3://overtrack-training-data/vod-names/names_250298397.tar
rm /media/ephemeral0/names_250298397.tar
            
# Title: Angry Titans vs Copenhagen Flames | Playoffs Day 2 Match 2 Game 1 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253670541
# Created: 2018-04-23 17:58:54+00:00
# Duration 0:16:30
echo "168 / 343" >> progress.txt
echo "Title: Angry Titans vs Copenhagen Flames | Playoffs Day 2 Match 2 Game 1 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253670541" >> progress.txt
echo "Duration: 0:16:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253670541
tar cvf /media/ephemeral0/names_253670541.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253670541.tar s3://overtrack-training-data/vod-names/names_253670541.tar
rm /media/ephemeral0/names_253670541.tar
            
# Title: Chaos Theory vs Detonator KR | Week 2 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244344382
# Created: 2018-03-29 19:42:50+00:00
# Duration 0:09:14
echo "169 / 343" >> progress.txt
echo "Title: Chaos Theory vs Detonator KR | Week 2 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244344382" >> progress.txt
echo "Duration: 0:09:14" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244344382
tar cvf /media/ephemeral0/names_244344382.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244344382.tar s3://overtrack-training-data/vod-names/names_244344382.tar
rm /media/ephemeral0/names_244344382.tar
            
# Title: Bazooka Puppiez vs Young and Beautiful | Week 5 Day 2 Match 2 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248512158
# Created: 2018-04-09 19:22:55+00:00
# Duration 0:18:36
echo "170 / 343" >> progress.txt
echo "Title: Bazooka Puppiez vs Young and Beautiful | Week 5 Day 2 Match 2 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248512158" >> progress.txt
echo "Duration: 0:18:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248512158
tar cvf /media/ephemeral0/names_248512158.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248512158.tar s3://overtrack-training-data/vod-names/names_248512158.tar
rm /media/ephemeral0/names_248512158.tar
            
# Title: British Hurricane vs 6nakes | Week 3 Day 1 Match 3 Game 1 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285474554
# Created: 2018-07-16 20:21:43+00:00
# Duration 0:22:08
echo "171 / 343" >> progress.txt
echo "Title: British Hurricane vs 6nakes | Week 3 Day 1 Match 3 Game 1 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285474554" >> progress.txt
echo "Duration: 0:22:08" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285474554
tar cvf /media/ephemeral0/names_285474554.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285474554.tar s3://overtrack-training-data/vod-names/names_285474554.tar
rm /media/ephemeral0/names_285474554.tar
            
# Title: Team Gigantti vs Copenhagen Flames | Week 3 Day 2 Match 3 Game 1 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285915362
# Created: 2018-07-17 21:37:43+00:00
# Duration 0:12:36
echo "172 / 343" >> progress.txt
echo "Title: Team Gigantti vs Copenhagen Flames | Week 3 Day 2 Match 3 Game 1 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285915362" >> progress.txt
echo "Duration: 0:12:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285915362
tar cvf /media/ephemeral0/names_285915362.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285915362.tar s3://overtrack-training-data/vod-names/names_285915362.tar
rm /media/ephemeral0/names_285915362.tar
            
# Title: NRG Esports vs OpTic Academy | Week 3 Day 1 Match 2 Game 2 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243696755
# Created: 2018-03-28 01:20:49+00:00
# Duration 0:29:07
echo "173 / 343" >> progress.txt
echo "Title: NRG Esports vs OpTic Academy | Week 3 Day 1 Match 2 Game 2 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243696755" >> progress.txt
echo "Duration: 0:29:07" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243696755
tar cvf /media/ephemeral0/names_243696755.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243696755.tar s3://overtrack-training-data/vod-names/names_243696755.tar
rm /media/ephemeral0/names_243696755.tar
            
# Title: Blank Esports vs OneShine Esports | Week 1 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241683116
# Created: 2018-03-22 20:45:07+00:00
# Duration 0:23:56
echo "174 / 343" >> progress.txt
echo "Title: Blank Esports vs OneShine Esports | Week 1 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241683116" >> progress.txt
echo "Duration: 0:23:56" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241683116
tar cvf /media/ephemeral0/names_241683116.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241683116.tar s3://overtrack-training-data/vod-names/names_241683116.tar
rm /media/ephemeral0/names_241683116.tar
            
# Title: Team Gigantti vs Angry Titans | Week 3 Day 1 Match 3 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243984260
# Created: 2018-03-28 20:37:48+00:00
# Duration 0:12:51
echo "175 / 343" >> progress.txt
echo "Title: Team Gigantti vs Angry Titans | Week 3 Day 1 Match 3 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243984260" >> progress.txt
echo "Duration: 0:12:51" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243984260
tar cvf /media/ephemeral0/names_243984260.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243984260.tar s3://overtrack-training-data/vod-names/names_243984260.tar
rm /media/ephemeral0/names_243984260.tar
            
# Title: Hong Kong Attitude (HKA) vs Xavier Esports (XVE) | Week 4 Day 2 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290479626
# Created: 2018-07-29 04:04:57+00:00
# Duration 0:21:04
echo "176 / 343" >> progress.txt
echo "Title: Hong Kong Attitude (HKA) vs Xavier Esports (XVE) | Week 4 Day 2 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290479626" >> progress.txt
echo "Duration: 0:21:04" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290479626
tar cvf /media/ephemeral0/names_290479626.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290479626.tar s3://overtrack-training-data/vod-names/names_290479626.tar
rm /media/ephemeral0/names_290479626.tar
            
# Title: Team Gigantti vs Angry Titans | Week 3 Day 1 Match 3 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243988739
# Created: 2018-03-28 20:50:53+00:00
# Duration 0:20:44
echo "177 / 343" >> progress.txt
echo "Title: Team Gigantti vs Angry Titans | Week 3 Day 1 Match 3 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243988739" >> progress.txt
echo "Duration: 0:20:44" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243988739
tar cvf /media/ephemeral0/names_243988739.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243988739.tar s3://overtrack-training-data/vod-names/names_243988739.tar
rm /media/ephemeral0/names_243988739.tar
            
# Title: Talon Esports vs Chaos Theory | Week 1 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241680709
# Created: 2018-03-22 20:38:18+00:00
# Duration 0:35:19
echo "178 / 343" >> progress.txt
echo "Title: Talon Esports vs Chaos Theory | Week 1 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241680709" >> progress.txt
echo "Duration: 0:35:19" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241680709
tar cvf /media/ephemeral0/names_241680709.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241680709.tar s3://overtrack-training-data/vod-names/names_241680709.tar
rm /media/ephemeral0/names_241680709.tar
            
# Title: Hong Kong Attitude (HKA) vs Incipience (INC) | Week 1 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281775401
# Created: 2018-07-07 06:29:16+00:00
# Duration 0:15:26
echo "179 / 343" >> progress.txt
echo "Title: Hong Kong Attitude (HKA) vs Incipience (INC) | Week 1 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281775401" >> progress.txt
echo "Duration: 0:15:26" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281775401
tar cvf /media/ephemeral0/names_281775401.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281775401.tar s3://overtrack-training-data/vod-names/names_281775401.tar
rm /media/ephemeral0/names_281775401.tar
            
# Title: MEGA vs Machi Esports | Week 1 Day 1 Match 2 Game 2 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/254696291
# Created: 2018-04-26 15:16:12+00:00
# Duration 0:12:30
echo "180 / 343" >> progress.txt
echo "Title: MEGA vs Machi Esports | Week 1 Day 1 Match 2 Game 2 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/254696291" >> progress.txt
echo "Duration: 0:12:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/254696291
tar cvf /media/ephemeral0/names_254696291.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_254696291.tar s3://overtrack-training-data/vod-names/names_254696291.tar
rm /media/ephemeral0/names_254696291.tar
            
# Title: LogitechG ABANG vs YOSHIMOTO ENCOUNT | Week 3 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246936523
# Created: 2018-04-05 16:21:48+00:00
# Duration 0:12:33
echo "181 / 343" >> progress.txt
echo "Title: LogitechG ABANG vs YOSHIMOTO ENCOUNT | Week 3 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246936523" >> progress.txt
echo "Duration: 0:12:33" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246936523
tar cvf /media/ephemeral0/names_246936523.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246936523.tar s3://overtrack-training-data/vod-names/names_246936523.tar
rm /media/ephemeral0/names_246936523.tar
            
# Title: Hong Kong Attitude (HKA) vs Incipience (INC) | Week 1 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281775400
# Created: 2018-07-07 06:29:16+00:00
# Duration 0:22:02
echo "182 / 343" >> progress.txt
echo "Title: Hong Kong Attitude (HKA) vs Incipience (INC) | Week 1 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281775400" >> progress.txt
echo "Duration: 0:22:02" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281775400
tar cvf /media/ephemeral0/names_281775400.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281775400.tar s3://overtrack-training-data/vod-names/names_281775400.tar
rm /media/ephemeral0/names_281775400.tar
            
# Title: Orgless and Hungry vs Angry Titans | Week 5 Day 1 Match 1 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248072623
# Created: 2018-04-08 14:48:23+00:00
# Duration 0:21:06
echo "183 / 343" >> progress.txt
echo "Title: Orgless and Hungry vs Angry Titans | Week 5 Day 1 Match 1 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248072623" >> progress.txt
echo "Duration: 0:21:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248072623
tar cvf /media/ephemeral0/names_248072623.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248072623.tar s3://overtrack-training-data/vod-names/names_248072623.tar
rm /media/ephemeral0/names_248072623.tar
            
# Title: MONSTER SHIELD KR vs EXL-Esports | Week 2 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284435713
# Created: 2018-07-14 03:44:19+00:00
# Duration 0:20:12
echo "184 / 343" >> progress.txt
echo "Title: MONSTER SHIELD KR vs EXL-Esports | Week 2 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284435713" >> progress.txt
echo "Duration: 0:20:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284435713
tar cvf /media/ephemeral0/names_284435713.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284435713.tar s3://overtrack-training-data/vod-names/names_284435713.tar
rm /media/ephemeral0/names_284435713.tar
            
# Title: Blank Esports vs OneShine Esports | Week 1 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241686015
# Created: 2018-03-22 20:53:50+00:00
# Duration 0:29:38
echo "185 / 343" >> progress.txt
echo "Title: Blank Esports vs OneShine Esports | Week 1 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241686015" >> progress.txt
echo "Duration: 0:29:38" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241686015
tar cvf /media/ephemeral0/names_241686015.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241686015.tar s3://overtrack-training-data/vod-names/names_241686015.tar
rm /media/ephemeral0/names_241686015.tar
            
# Title: Blank Esports (BLK) vs CYCLOPS athlete gaming (CAG) | Week 1 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281774028
# Created: 2018-07-07 06:22:03+00:00
# Duration 0:28:37
echo "186 / 343" >> progress.txt
echo "Title: Blank Esports (BLK) vs CYCLOPS athlete gaming (CAG) | Week 1 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281774028" >> progress.txt
echo "Duration: 0:28:37" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281774028
tar cvf /media/ephemeral0/names_281774028.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281774028.tar s3://overtrack-training-data/vod-names/names_281774028.tar
rm /media/ephemeral0/names_281774028.tar
            
# Title: Machi Esports (M17) vs EXL-Esports | Week 4 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290155433
# Created: 2018-07-28 09:11:39+00:00
# Duration 0:25:45
echo "187 / 343" >> progress.txt
echo "Title: Machi Esports (M17) vs EXL-Esports | Week 4 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290155433" >> progress.txt
echo "Duration: 0:25:45" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290155433
tar cvf /media/ephemeral0/names_290155433.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290155433.tar s3://overtrack-training-data/vod-names/names_290155433.tar
rm /media/ephemeral0/names_290155433.tar
            
# Title: CIS Hope vs Orgless and Hungry | Playoffs - Round of 8 | Day 1 Match 2 Game 5 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253327299
# Created: 2018-04-22 18:07:50+00:00
# Duration 0:22:48
echo "188 / 343" >> progress.txt
echo "Title: CIS Hope vs Orgless and Hungry | Playoffs - Round of 8 | Day 1 Match 2 Game 5 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253327299" >> progress.txt
echo "Duration: 0:22:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253327299
tar cvf /media/ephemeral0/names_253327299.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253327299.tar s3://overtrack-training-data/vod-names/names_253327299.tar
rm /media/ephemeral0/names_253327299.tar
            
# Title: Blank Esports (BLK) vs Hong Kong Attitude (HKA) | Week 5 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292928919
# Created: 2018-08-04 06:45:34+00:00
# Duration 0:21:24
echo "189 / 343" >> progress.txt
echo "Title: Blank Esports (BLK) vs Hong Kong Attitude (HKA) | Week 5 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292928919" >> progress.txt
echo "Duration: 0:21:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292928919
tar cvf /media/ephemeral0/names_292928919.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292928919.tar s3://overtrack-training-data/vod-names/names_292928919.tar
rm /media/ephemeral0/names_292928919.tar
            
# Title: Mayhem Academy vs. Last Night's Leftovers | Week 5 Day 1 Match 3 Game 1 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291873909
# Created: 2018-08-01 18:01:35+00:00
# Duration 0:21:07
echo "190 / 343" >> progress.txt
echo "Title: Mayhem Academy vs. Last Night's Leftovers | Week 5 Day 1 Match 3 Game 1 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291873909" >> progress.txt
echo "Duration: 0:21:07" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291873909
tar cvf /media/ephemeral0/names_291873909.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291873909.tar s3://overtrack-training-data/vod-names/names_291873909.tar
rm /media/ephemeral0/names_291873909.tar
            
# Title: Talon Esports vs Hong Kong Attitude | Week 5 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252046939
# Created: 2018-04-19 10:03:35+00:00
# Duration 0:08:27
echo "191 / 343" >> progress.txt
echo "Title: Talon Esports vs Hong Kong Attitude | Week 5 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252046939" >> progress.txt
echo "Duration: 0:08:27" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252046939
tar cvf /media/ephemeral0/names_252046939.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252046939.tar s3://overtrack-training-data/vod-names/names_252046939.tar
rm /media/ephemeral0/names_252046939.tar
            
# Title: Xavier Esports vs LogitechG ABANG | Week 5 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252454725
# Created: 2018-04-20 14:17:09+00:00
# Duration 0:20:00
echo "192 / 343" >> progress.txt
echo "Title: Xavier Esports vs LogitechG ABANG | Week 5 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252454725" >> progress.txt
echo "Duration: 0:20:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252454725
tar cvf /media/ephemeral0/names_252454725.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252454725.tar s3://overtrack-training-data/vod-names/names_252454725.tar
rm /media/ephemeral0/names_252454725.tar
            
# Title: Chaos Theory vs Hong Kong Attitude | Week 3 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/247672982
# Created: 2018-04-07 14:53:42+00:00
# Duration 0:15:08
echo "193 / 343" >> progress.txt
echo "Title: Chaos Theory vs Hong Kong Attitude | Week 3 Day 2 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/247672982" >> progress.txt
echo "Duration: 0:15:08" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/247672982
tar cvf /media/ephemeral0/names_247672982.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_247672982.tar s3://overtrack-training-data/vod-names/names_247672982.tar
rm /media/ephemeral0/names_247672982.tar
            
# Title: Bazooka Puppiez vs Copenhagen Flames | Week 3 Day 2 Match 2 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244343779
# Created: 2018-03-29 19:41:02+00:00
# Duration 0:17:36
echo "194 / 343" >> progress.txt
echo "Title: Bazooka Puppiez vs Copenhagen Flames | Week 3 Day 2 Match 2 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244343779" >> progress.txt
echo "Duration: 0:17:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244343779
tar cvf /media/ephemeral0/names_244343779.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244343779.tar s3://overtrack-training-data/vod-names/names_244343779.tar
rm /media/ephemeral0/names_244343779.tar
            
# Title: British Hurricane vs 6nakes | Week 3 Day 1 Match 3 Game 4 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285502831
# Created: 2018-07-16 21:39:46+00:00
# Duration 0:27:23
echo "195 / 343" >> progress.txt
echo "Title: British Hurricane vs 6nakes | Week 3 Day 1 Match 3 Game 4 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285502831" >> progress.txt
echo "Duration: 0:27:23" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285502831
tar cvf /media/ephemeral0/names_285502831.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285502831.tar s3://overtrack-training-data/vod-names/names_285502831.tar
rm /media/ephemeral0/names_285502831.tar
            
# Title: Xavier Esports vs LogitechG ABANG | Week 5 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252452632
# Created: 2018-04-20 14:08:07+00:00
# Duration 0:23:14
echo "196 / 343" >> progress.txt
echo "Title: Xavier Esports vs LogitechG ABANG | Week 5 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252452632" >> progress.txt
echo "Duration: 0:23:14" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252452632
tar cvf /media/ephemeral0/names_252452632.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252452632.tar s3://overtrack-training-data/vod-names/names_252452632.tar
rm /media/ephemeral0/names_252452632.tar
            
# Title: Yoshimoto Encount vs Xavier Esports | Week 1 Day 2 Match 3 Game 4 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242343567
# Created: 2018-03-24 15:44:53+00:00
# Duration 0:17:48
echo "197 / 343" >> progress.txt
echo "Title: Yoshimoto Encount vs Xavier Esports | Week 1 Day 2 Match 3 Game 4 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242343567" >> progress.txt
echo "Duration: 0:17:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242343567
tar cvf /media/ephemeral0/names_242343567.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242343567.tar s3://overtrack-training-data/vod-names/names_242343567.tar
rm /media/ephemeral0/names_242343567.tar
            
# Title: Angry Titans vs Copenhagen Flames | Playoffs Day 2 Match 2 Game 3 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253684392
# Created: 2018-04-23 18:36:12+00:00
# Duration 0:27:42
echo "198 / 343" >> progress.txt
echo "Title: Angry Titans vs Copenhagen Flames | Playoffs Day 2 Match 2 Game 3 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253684392" >> progress.txt
echo "Duration: 0:27:42" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253684392
tar cvf /media/ephemeral0/names_253684392.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253684392.tar s3://overtrack-training-data/vod-names/names_253684392.tar
rm /media/ephemeral0/names_253684392.tar
            
# Title: Talon Esports vs Chaos Theory | Week 1 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241676173
# Created: 2018-03-22 20:25:49+00:00
# Duration 0:20:11
echo "199 / 343" >> progress.txt
echo "Title: Talon Esports vs Chaos Theory | Week 1 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241676173" >> progress.txt
echo "Duration: 0:20:11" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241676173
tar cvf /media/ephemeral0/names_241676173.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241676173.tar s3://overtrack-training-data/vod-names/names_241676173.tar
rm /media/ephemeral0/names_241676173.tar
            
# Title: Detonator KR vs Hong Kong Attitude | Week 4 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249883970
# Created: 2018-04-13 14:42:13+00:00
# Duration 0:23:24
echo "200 / 343" >> progress.txt
echo "Title: Detonator KR vs Hong Kong Attitude | Week 4 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249883970" >> progress.txt
echo "Duration: 0:23:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249883970
tar cvf /media/ephemeral0/names_249883970.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249883970.tar s3://overtrack-training-data/vod-names/names_249883970.tar
rm /media/ephemeral0/names_249883970.tar
            
# Title: Blank Esports (BLK) vs Hong Kong Attitude (HKA) | Week 5 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292928920
# Created: 2018-08-04 06:45:34+00:00
# Duration 0:19:23
echo "201 / 343" >> progress.txt
echo "Title: Blank Esports (BLK) vs Hong Kong Attitude (HKA) | Week 5 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292928920" >> progress.txt
echo "Duration: 0:19:23" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292928920
tar cvf /media/ephemeral0/names_292928920.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292928920.tar s3://overtrack-training-data/vod-names/names_292928920.tar
rm /media/ephemeral0/names_292928920.tar
            
# Title: British Hurricane vs Orgless and Hungry | Week 3 Day 1 Match 1 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243935247
# Created: 2018-03-28 18:29:39+00:00
# Duration 0:32:27
echo "202 / 343" >> progress.txt
echo "Title: British Hurricane vs Orgless and Hungry | Week 3 Day 1 Match 1 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243935247" >> progress.txt
echo "Duration: 0:32:27" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243935247
tar cvf /media/ephemeral0/names_243935247.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243935247.tar s3://overtrack-training-data/vod-names/names_243935247.tar
rm /media/ephemeral0/names_243935247.tar
            
# Title: Mosaic Esports vs CIS Hope | Week 3 Day 2 Match 3 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244406588
# Created: 2018-03-29 22:42:42+00:00
# Duration 0:26:24
echo "203 / 343" >> progress.txt
echo "Title: Mosaic Esports vs CIS Hope | Week 3 Day 2 Match 3 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244406588" >> progress.txt
echo "Duration: 0:26:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244406588
tar cvf /media/ephemeral0/names_244406588.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244406588.tar s3://overtrack-training-data/vod-names/names_244406588.tar
rm /media/ephemeral0/names_244406588.tar
            
# Title: Chaos Theory vs Detonator KR | Week 2 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244345432
# Created: 2018-03-29 19:45:47+00:00
# Duration 0:19:45
echo "204 / 343" >> progress.txt
echo "Title: Chaos Theory vs Detonator KR | Week 2 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244345432" >> progress.txt
echo "Duration: 0:19:45" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244345432
tar cvf /media/ephemeral0/names_244345432.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244345432.tar s3://overtrack-training-data/vod-names/names_244345432.tar
rm /media/ephemeral0/names_244345432.tar
            
# Title: Detonator KR vs LogitechG ABANG | Week 1 Day 1 Match 1 Game 2 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/254694106
# Created: 2018-04-26 15:06:58+00:00
# Duration 0:18:49
echo "205 / 343" >> progress.txt
echo "Title: Detonator KR vs LogitechG ABANG | Week 1 Day 1 Match 1 Game 2 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/254694106" >> progress.txt
echo "Duration: 0:18:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/254694106
tar cvf /media/ephemeral0/names_254694106.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_254694106.tar s3://overtrack-training-data/vod-names/names_254694106.tar
rm /media/ephemeral0/names_254694106.tar
            
# Title: Hong Kong Attitude (HKA) vs Xavier Esports (XVE) | Week 4 Day 2 Match 1 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290479627
# Created: 2018-07-29 04:04:57+00:00
# Duration 0:21:42
echo "206 / 343" >> progress.txt
echo "Title: Hong Kong Attitude (HKA) vs Xavier Esports (XVE) | Week 4 Day 2 Match 1 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290479627" >> progress.txt
echo "Duration: 0:21:42" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290479627
tar cvf /media/ephemeral0/names_290479627.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290479627.tar s3://overtrack-training-data/vod-names/names_290479627.tar
rm /media/ephemeral0/names_290479627.tar
            
# Title: Mega (MGA) vs Talon Esport (TLN) | Week 4 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290156203
# Created: 2018-07-28 09:16:39+00:00
# Duration 0:23:02
echo "207 / 343" >> progress.txt
echo "Title: Mega (MGA) vs Talon Esport (TLN) | Week 4 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290156203" >> progress.txt
echo "Duration: 0:23:02" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290156203
tar cvf /media/ephemeral0/names_290156203.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290156203.tar s3://overtrack-training-data/vod-names/names_290156203.tar
rm /media/ephemeral0/names_290156203.tar
            
# Title: Talon Esports vs Chaos Theory | Week 1 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241677869
# Created: 2018-03-22 20:30:23+00:00
# Duration 0:11:40
echo "208 / 343" >> progress.txt
echo "Title: Talon Esports vs Chaos Theory | Week 1 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241677869" >> progress.txt
echo "Duration: 0:11:40" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241677869
tar cvf /media/ephemeral0/names_241677869.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241677869.tar s3://overtrack-training-data/vod-names/names_241677869.tar
rm /media/ephemeral0/names_241677869.tar
            
# Title: Blank Esports vs YOSHIMOTO ENCOUNT | Week 5 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252064585
# Created: 2018-04-19 12:01:56+00:00
# Duration 0:14:29
echo "209 / 343" >> progress.txt
echo "Title: Blank Esports vs YOSHIMOTO ENCOUNT | Week 5 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252064585" >> progress.txt
echo "Duration: 0:14:29" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252064585
tar cvf /media/ephemeral0/names_252064585.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252064585.tar s3://overtrack-training-data/vod-names/names_252064585.tar
rm /media/ephemeral0/names_252064585.tar
            
# Title: Detonator KR vs LogitechG ABANG | Week 1 Day 1 Match 1 Game 1 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/254693879
# Created: 2018-04-26 15:05:55+00:00
# Duration 0:22:52
echo "210 / 343" >> progress.txt
echo "Title: Detonator KR vs LogitechG ABANG | Week 1 Day 1 Match 1 Game 1 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/254693879" >> progress.txt
echo "Duration: 0:22:52" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/254693879
tar cvf /media/ephemeral0/names_254693879.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_254693879.tar s3://overtrack-training-data/vod-names/names_254693879.tar
rm /media/ephemeral0/names_254693879.tar
            
# Title: Mega (MGA) vs MONSTER SHIELD KR | Week 1 Day 2 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282153491
# Created: 2018-07-08 07:42:11+00:00
# Duration 0:15:59
echo "211 / 343" >> progress.txt
echo "Title: Mega (MGA) vs MONSTER SHIELD KR | Week 1 Day 2 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282153491" >> progress.txt
echo "Duration: 0:15:59" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282153491
tar cvf /media/ephemeral0/names_282153491.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282153491.tar s3://overtrack-training-data/vod-names/names_282153491.tar
rm /media/ephemeral0/names_282153491.tar
            
# Title: Fusion University vs. GG Esports Academy | Week 5 Day 1 Match 1 Game 4 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291863602
# Created: 2018-08-01 17:34:18+00:00
# Duration 0:22:55
echo "212 / 343" >> progress.txt
echo "Title: Fusion University vs. GG Esports Academy | Week 5 Day 1 Match 1 Game 4 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291863602" >> progress.txt
echo "Duration: 0:22:55" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291863602
tar cvf /media/ephemeral0/names_291863602.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291863602.tar s3://overtrack-training-data/vod-names/names_291863602.tar
rm /media/ephemeral0/names_291863602.tar
            
# Title: Talon Esports vs Chaos Theory | Week 1 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241670400
# Created: 2018-03-22 20:09:44+00:00
# Duration 0:27:16
echo "213 / 343" >> progress.txt
echo "Title: Talon Esports vs Chaos Theory | Week 1 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241670400" >> progress.txt
echo "Duration: 0:27:16" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241670400
tar cvf /media/ephemeral0/names_241670400.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241670400.tar s3://overtrack-training-data/vod-names/names_241670400.tar
rm /media/ephemeral0/names_241670400.tar
            
# Title: CIS Hope vs Copenhagen Flames | Week 5 Day 2 Match 3 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248538765
# Created: 2018-04-09 20:34:56+00:00
# Duration 0:27:48
echo "214 / 343" >> progress.txt
echo "Title: CIS Hope vs Copenhagen Flames | Week 5 Day 2 Match 3 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248538765" >> progress.txt
echo "Duration: 0:27:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248538765
tar cvf /media/ephemeral0/names_248538765.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248538765.tar s3://overtrack-training-data/vod-names/names_248538765.tar
rm /media/ephemeral0/names_248538765.tar
            
# Title: Mega (MGA) vs Talon Esport (TLN) | Week 4 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290156205
# Created: 2018-07-28 09:16:39+00:00
# Duration 0:22:59
echo "215 / 343" >> progress.txt
echo "Title: Mega (MGA) vs Talon Esport (TLN) | Week 4 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290156205" >> progress.txt
echo "Duration: 0:22:59" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290156205
tar cvf /media/ephemeral0/names_290156205.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290156205.tar s3://overtrack-training-data/vod-names/names_290156205.tar
rm /media/ephemeral0/names_290156205.tar
            
# Title: Contenders Pacific | OneShine Esports vs Xavier Esports | Week 2 Day 2 Match 1 Game 5 | S1: Regular Season
# URL: https://www.twitch.tv/videos/245009750
# Created: 2018-03-31 12:47:28+00:00
# Duration 0:09:30
echo "216 / 343" >> progress.txt
echo "Title: Contenders Pacific | OneShine Esports vs Xavier Esports | Week 2 Day 2 Match 1 Game 5 | S1: Regular Season" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245009750" >> progress.txt
echo "Duration: 0:09:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245009750
tar cvf /media/ephemeral0/names_245009750.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245009750.tar s3://overtrack-training-data/vod-names/names_245009750.tar
rm /media/ephemeral0/names_245009750.tar
            
# Title: Nova Esports vs Hong Kong Attitude | Week 2 Day 2 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284701772
# Created: 2018-07-14 21:08:30+00:00
# Duration 0:23:48
echo "217 / 343" >> progress.txt
echo "Title: Nova Esports vs Hong Kong Attitude | Week 2 Day 2 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284701772" >> progress.txt
echo "Duration: 0:23:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284701772
tar cvf /media/ephemeral0/names_284701772.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284701772.tar s3://overtrack-training-data/vod-names/names_284701772.tar
rm /media/ephemeral0/names_284701772.tar
            
# Title: Team Singularity vs That's a Disband | Week 3 Day 1 Match 2 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243963165
# Created: 2018-03-28 19:39:45+00:00
# Duration 0:26:15
echo "218 / 343" >> progress.txt
echo "Title: Team Singularity vs That's a Disband | Week 3 Day 1 Match 2 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243963165" >> progress.txt
echo "Duration: 0:26:15" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243963165
tar cvf /media/ephemeral0/names_243963165.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243963165.tar s3://overtrack-training-data/vod-names/names_243963165.tar
rm /media/ephemeral0/names_243963165.tar
            
# Title: CIS Hope vs Orgless and Hungry | Playoffs - Round of 8 | Day 1 Match 2 Game 2 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253290825
# Created: 2018-04-22 16:28:33+00:00
# Duration 0:25:18
echo "219 / 343" >> progress.txt
echo "Title: CIS Hope vs Orgless and Hungry | Playoffs - Round of 8 | Day 1 Match 2 Game 2 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253290825" >> progress.txt
echo "Duration: 0:25:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253290825
tar cvf /media/ephemeral0/names_253290825.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253290825.tar s3://overtrack-training-data/vod-names/names_253290825.tar
rm /media/ephemeral0/names_253290825.tar
            
# Title: Eagle Gaming vs Team Gigantti | Playoffs Day 2 Match 1 Game 3 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253661283
# Created: 2018-04-23 17:30:53+00:00
# Duration 0:22:24
echo "220 / 343" >> progress.txt
echo "Title: Eagle Gaming vs Team Gigantti | Playoffs Day 2 Match 1 Game 3 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253661283" >> progress.txt
echo "Duration: 0:22:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253661283
tar cvf /media/ephemeral0/names_253661283.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253661283.tar s3://overtrack-training-data/vod-names/names_253661283.tar
rm /media/ephemeral0/names_253661283.tar
            
# Title: Blank Esports vs YOSHIMOTO ENCOUNT | Week 5 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252070926
# Created: 2018-04-19 12:36:43+00:00
# Duration 0:15:30
echo "221 / 343" >> progress.txt
echo "Title: Blank Esports vs YOSHIMOTO ENCOUNT | Week 5 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252070926" >> progress.txt
echo "Duration: 0:15:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252070926
tar cvf /media/ephemeral0/names_252070926.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252070926.tar s3://overtrack-training-data/vod-names/names_252070926.tar
rm /media/ephemeral0/names_252070926.tar
            
# Title: Team Gigantti vs Team Singularity | Week 5 Day 1 Match 2 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248103854
# Created: 2018-04-08 16:33:13+00:00
# Duration 0:14:36
echo "222 / 343" >> progress.txt
echo "Title: Team Gigantti vs Team Singularity | Week 5 Day 1 Match 2 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248103854" >> progress.txt
echo "Duration: 0:14:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248103854
tar cvf /media/ephemeral0/names_248103854.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248103854.tar s3://overtrack-training-data/vod-names/names_248103854.tar
rm /media/ephemeral0/names_248103854.tar
            
# Title: Machi Esports (M17) vs EXL-Esports | Week 4 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290155432
# Created: 2018-07-28 09:11:39+00:00
# Duration 0:24:14
echo "223 / 343" >> progress.txt
echo "Title: Machi Esports (M17) vs EXL-Esports | Week 4 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290155432" >> progress.txt
echo "Duration: 0:24:14" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290155432
tar cvf /media/ephemeral0/names_290155432.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290155432.tar s3://overtrack-training-data/vod-names/names_290155432.tar
rm /media/ephemeral0/names_290155432.tar
            
# Title: NOVA ESPORTS vs Blank Esports (BLK) | Week 4 Day 1 Match 1 Game 5 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290154183
# Created: 2018-07-28 09:03:51+00:00
# Duration 0:12:29
echo "224 / 343" >> progress.txt
echo "Title: NOVA ESPORTS vs Blank Esports (BLK) | Week 4 Day 1 Match 1 Game 5 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290154183" >> progress.txt
echo "Duration: 0:12:29" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290154183
tar cvf /media/ephemeral0/names_290154183.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290154183.tar s3://overtrack-training-data/vod-names/names_290154183.tar
rm /media/ephemeral0/names_290154183.tar
            
# Title: Mosaic Esports vs Eagle Gaming | Week 5 Day 2 Match 1 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248473419
# Created: 2018-04-09 17:33:27+00:00
# Duration 0:10:06
echo "225 / 343" >> progress.txt
echo "Title: Mosaic Esports vs Eagle Gaming | Week 5 Day 2 Match 1 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248473419" >> progress.txt
echo "Duration: 0:10:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248473419
tar cvf /media/ephemeral0/names_248473419.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248473419.tar s3://overtrack-training-data/vod-names/names_248473419.tar
rm /media/ephemeral0/names_248473419.tar
            
# Title: Mayhem Academy vs. Last Night's Leftovers | Week 5 Day 1 Match 3 Game 3 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291876398
# Created: 2018-08-01 18:07:34+00:00
# Duration 0:21:37
echo "226 / 343" >> progress.txt
echo "Title: Mayhem Academy vs. Last Night's Leftovers | Week 5 Day 1 Match 3 Game 3 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291876398" >> progress.txt
echo "Duration: 0:21:37" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291876398
tar cvf /media/ephemeral0/names_291876398.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291876398.tar s3://overtrack-training-data/vod-names/names_291876398.tar
rm /media/ephemeral0/names_291876398.tar
            
# Title: Hong Kong Attitude vs Bazaar | Week 1 Day 2 Match 1 Game 1 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242319158
# Created: 2018-03-24 14:24:22+00:00
# Duration 0:22:34
echo "227 / 343" >> progress.txt
echo "Title: Hong Kong Attitude vs Bazaar | Week 1 Day 2 Match 1 Game 1 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242319158" >> progress.txt
echo "Duration: 0:22:34" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242319158
tar cvf /media/ephemeral0/names_242319158.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242319158.tar s3://overtrack-training-data/vod-names/names_242319158.tar
rm /media/ephemeral0/names_242319158.tar
            
# Title: NRG Esports vs. Skyfoxes | Week 5 Day 2 Match 1 Game 2 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292389039
# Created: 2018-08-02 23:51:24+00:00
# Duration 0:30:13
echo "228 / 343" >> progress.txt
echo "Title: NRG Esports vs. Skyfoxes | Week 5 Day 2 Match 1 Game 2 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292389039" >> progress.txt
echo "Duration: 0:30:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292389039
tar cvf /media/ephemeral0/names_292389039.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292389039.tar s3://overtrack-training-data/vod-names/names_292389039.tar
rm /media/ephemeral0/names_292389039.tar
            
# Title: Blank Esports vs YOSHIMOTO ENCOUNT | Week 5 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252056767
# Created: 2018-04-19 11:12:52+00:00
# Duration 0:25:50
echo "229 / 343" >> progress.txt
echo "Title: Blank Esports vs YOSHIMOTO ENCOUNT | Week 5 Day 1 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252056767" >> progress.txt
echo "Duration: 0:25:50" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252056767
tar cvf /media/ephemeral0/names_252056767.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252056767.tar s3://overtrack-training-data/vod-names/names_252056767.tar
rm /media/ephemeral0/names_252056767.tar
            
# Title: Last Night's Leftovers vs Mayhem Academy | Week 3 Day 2 Match 1 Game 4 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244147194
# Created: 2018-03-29 05:04:27+00:00
# Duration 0:22:19
echo "230 / 343" >> progress.txt
echo "Title: Last Night's Leftovers vs Mayhem Academy | Week 3 Day 2 Match 1 Game 4 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244147194" >> progress.txt
echo "Duration: 0:22:19" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244147194
tar cvf /media/ephemeral0/names_244147194.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244147194.tar s3://overtrack-training-data/vod-names/names_244147194.tar
rm /media/ephemeral0/names_244147194.tar
            
# Title: Machi Esports (M17) vs EXL-Esports | Week 4 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290155587
# Created: 2018-07-28 09:12:40+00:00
# Duration 0:28:20
echo "231 / 343" >> progress.txt
echo "Title: Machi Esports (M17) vs EXL-Esports | Week 4 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290155587" >> progress.txt
echo "Duration: 0:28:20" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290155587
tar cvf /media/ephemeral0/names_290155587.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290155587.tar s3://overtrack-training-data/vod-names/names_290155587.tar
rm /media/ephemeral0/names_290155587.tar
            
# Title: Gladiators Legion vs. Second Wind | Week 5 Day 1 Match 2 Game 1 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291867704
# Created: 2018-08-01 17:46:23+00:00
# Duration 0:19:13
echo "232 / 343" >> progress.txt
echo "Title: Gladiators Legion vs. Second Wind | Week 5 Day 1 Match 2 Game 1 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291867704" >> progress.txt
echo "Duration: 0:19:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291867704
tar cvf /media/ephemeral0/names_291867704.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291867704.tar s3://overtrack-training-data/vod-names/names_291867704.tar
rm /media/ephemeral0/names_291867704.tar
            
# Title: NRG Esports vs OpTic Academy | Week 3 Day 1 Match 2 Game 3 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243706796
# Created: 2018-03-28 01:49:46+00:00
# Duration 0:19:49
echo "233 / 343" >> progress.txt
echo "Title: NRG Esports vs OpTic Academy | Week 3 Day 1 Match 2 Game 3 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243706796" >> progress.txt
echo "Duration: 0:19:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243706796
tar cvf /media/ephemeral0/names_243706796.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243706796.tar s3://overtrack-training-data/vod-names/names_243706796.tar
rm /media/ephemeral0/names_243706796.tar
            
# Title: EXL-Esports vs Mega (MGA) | Week 5 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292928125
# Created: 2018-08-04 06:41:26+00:00
# Duration 0:14:06
echo "234 / 343" >> progress.txt
echo "Title: EXL-Esports vs Mega (MGA) | Week 5 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292928125" >> progress.txt
echo "Duration: 0:14:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292928125
tar cvf /media/ephemeral0/names_292928125.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292928125.tar s3://overtrack-training-data/vod-names/names_292928125.tar
rm /media/ephemeral0/names_292928125.tar
            
# Title: EXL-Esports vs Mega (MGA) | Week 5 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292928124
# Created: 2018-08-04 06:41:26+00:00
# Duration 0:27:28
echo "235 / 343" >> progress.txt
echo "Title: EXL-Esports vs Mega (MGA) | Week 5 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292928124" >> progress.txt
echo "Duration: 0:27:28" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292928124
tar cvf /media/ephemeral0/names_292928124.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292928124.tar s3://overtrack-training-data/vod-names/names_292928124.tar
rm /media/ephemeral0/names_292928124.tar
            
# Title: Simplicity vs Fusion University | Week 3 Day 1 Match 3 Game 4 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243746162
# Created: 2018-03-28 03:57:19+00:00
# Duration 0:17:49
echo "236 / 343" >> progress.txt
echo "Title: Simplicity vs Fusion University | Week 3 Day 1 Match 3 Game 4 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243746162" >> progress.txt
echo "Duration: 0:17:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243746162
tar cvf /media/ephemeral0/names_243746162.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243746162.tar s3://overtrack-training-data/vod-names/names_243746162.tar
rm /media/ephemeral0/names_243746162.tar
            
# Title: Hong Kong Attitude vs Machi Esports | Week 2 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/245358037
# Created: 2018-04-01 09:07:54+00:00
# Duration 0:18:55
echo "237 / 343" >> progress.txt
echo "Title: Hong Kong Attitude vs Machi Esports | Week 2 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245358037" >> progress.txt
echo "Duration: 0:18:55" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245358037
tar cvf /media/ephemeral0/names_245358037.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245358037.tar s3://overtrack-training-data/vod-names/names_245358037.tar
rm /media/ephemeral0/names_245358037.tar
            
# Title: LogitechG ABANG vs YOSHIMOTO ENCOUNT | Week 3 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246936146
# Created: 2018-04-05 16:20:27+00:00
# Duration 0:28:24
echo "238 / 343" >> progress.txt
echo "Title: LogitechG ABANG vs YOSHIMOTO ENCOUNT | Week 3 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246936146" >> progress.txt
echo "Duration: 0:28:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246936146
tar cvf /media/ephemeral0/names_246936146.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246936146.tar s3://overtrack-training-data/vod-names/names_246936146.tar
rm /media/ephemeral0/names_246936146.tar
            
# Title: Eagle Gaming vs We Have Org | Week 3 Day 2 Match 2 Game 4 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285867841
# Created: 2018-07-17 19:30:38+00:00
# Duration 0:29:28
echo "239 / 343" >> progress.txt
echo "Title: Eagle Gaming vs We Have Org | Week 3 Day 2 Match 2 Game 4 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285867841" >> progress.txt
echo "Duration: 0:29:28" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285867841
tar cvf /media/ephemeral0/names_285867841.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285867841.tar s3://overtrack-training-data/vod-names/names_285867841.tar
rm /media/ephemeral0/names_285867841.tar
            
# Title: MONSTER SHIELD KR vs EXL-Esports | Week 2 Day 1 Match 2 Game 5 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284435716
# Created: 2018-07-14 03:44:19+00:00
# Duration 0:13:18
echo "240 / 343" >> progress.txt
echo "Title: MONSTER SHIELD KR vs EXL-Esports | Week 2 Day 1 Match 2 Game 5 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284435716" >> progress.txt
echo "Duration: 0:13:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284435716
tar cvf /media/ephemeral0/names_284435716.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284435716.tar s3://overtrack-training-data/vod-names/names_284435716.tar
rm /media/ephemeral0/names_284435716.tar
            
# Title: Grizzlys vs XL2 Academy | Week 3 Day 2 Match 3 Game 3 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244136038
# Created: 2018-03-29 04:12:47+00:00
# Duration 0:19:01
echo "241 / 343" >> progress.txt
echo "Title: Grizzlys vs XL2 Academy | Week 3 Day 2 Match 3 Game 3 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244136038" >> progress.txt
echo "Duration: 0:19:01" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244136038
tar cvf /media/ephemeral0/names_244136038.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244136038.tar s3://overtrack-training-data/vod-names/names_244136038.tar
rm /media/ephemeral0/names_244136038.tar
            
# Title: Last Night's Leftovers vs Mayhem Academy | Week 3 Day 2 Match 1 Game 3 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244146478
# Created: 2018-03-29 05:01:00+00:00
# Duration 0:29:43
echo "242 / 343" >> progress.txt
echo "Title: Last Night's Leftovers vs Mayhem Academy | Week 3 Day 2 Match 1 Game 3 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244146478" >> progress.txt
echo "Duration: 0:29:43" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244146478
tar cvf /media/ephemeral0/names_244146478.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244146478.tar s3://overtrack-training-data/vod-names/names_244146478.tar
rm /media/ephemeral0/names_244146478.tar
            
# Title: Bazooka Puppiez vs Young and Beautiful | Week 5 Day 2 Match 2 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248515803
# Created: 2018-04-09 19:33:28+00:00
# Duration 0:16:18
echo "243 / 343" >> progress.txt
echo "Title: Bazooka Puppiez vs Young and Beautiful | Week 5 Day 2 Match 2 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248515803" >> progress.txt
echo "Duration: 0:16:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248515803
tar cvf /media/ephemeral0/names_248515803.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248515803.tar s3://overtrack-training-data/vod-names/names_248515803.tar
rm /media/ephemeral0/names_248515803.tar
            
# Title: BAZAAR vs Chaos Theory | Week 4 Day 2 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250297274
# Created: 2018-04-14 16:16:30+00:00
# Duration 0:08:40
echo "244 / 343" >> progress.txt
echo "Title: BAZAAR vs Chaos Theory | Week 4 Day 2 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250297274" >> progress.txt
echo "Duration: 0:08:40" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250297274
tar cvf /media/ephemeral0/names_250297274.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250297274.tar s3://overtrack-training-data/vod-names/names_250297274.tar
rm /media/ephemeral0/names_250297274.tar
            
# Title: British Hurricane vs Young & Beautiful | Playoffs - Round of 8 | Day 1 Match 1 Game 2 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253266631
# Created: 2018-04-22 15:11:20+00:00
# Duration 0:21:54
echo "245 / 343" >> progress.txt
echo "Title: British Hurricane vs Young & Beautiful | Playoffs - Round of 8 | Day 1 Match 1 Game 2 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253266631" >> progress.txt
echo "Duration: 0:21:54" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253266631
tar cvf /media/ephemeral0/names_253266631.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253266631.tar s3://overtrack-training-data/vod-names/names_253266631.tar
rm /media/ephemeral0/names_253266631.tar
            
# Title: CIS Hope vs Copenhagen Flames | Week 5 Day 2 Match 3 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248550518
# Created: 2018-04-09 21:10:27+00:00
# Duration 0:17:18
echo "246 / 343" >> progress.txt
echo "Title: CIS Hope vs Copenhagen Flames | Week 5 Day 2 Match 3 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248550518" >> progress.txt
echo "Duration: 0:17:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248550518
tar cvf /media/ephemeral0/names_248550518.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248550518.tar s3://overtrack-training-data/vod-names/names_248550518.tar
rm /media/ephemeral0/names_248550518.tar
            
# Title: LogitechG ABANG vs OneShine Esports | Week 4 Day 2 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250294480
# Created: 2018-04-14 16:07:24+00:00
# Duration 0:17:59
echo "247 / 343" >> progress.txt
echo "Title: LogitechG ABANG vs OneShine Esports | Week 4 Day 2 Match 2 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250294480" >> progress.txt
echo "Duration: 0:17:59" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250294480
tar cvf /media/ephemeral0/names_250294480.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250294480.tar s3://overtrack-training-data/vod-names/names_250294480.tar
rm /media/ephemeral0/names_250294480.tar
            
# Title: NOVA ESPORTS vs Blank Esports (BLK) | Week 4 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290154186
# Created: 2018-07-28 09:03:51+00:00
# Duration 0:23:56
echo "248 / 343" >> progress.txt
echo "Title: NOVA ESPORTS vs Blank Esports (BLK) | Week 4 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290154186" >> progress.txt
echo "Duration: 0:23:56" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290154186
tar cvf /media/ephemeral0/names_290154186.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290154186.tar s3://overtrack-training-data/vod-names/names_290154186.tar
rm /media/ephemeral0/names_290154186.tar
            
# Title: Detonator KR vs Hong Kong Attitude | Week 4 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249882493
# Created: 2018-04-13 14:35:35+00:00
# Duration 0:22:32
echo "249 / 343" >> progress.txt
echo "Title: Detonator KR vs Hong Kong Attitude | Week 4 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249882493" >> progress.txt
echo "Duration: 0:22:32" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249882493
tar cvf /media/ephemeral0/names_249882493.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249882493.tar s3://overtrack-training-data/vod-names/names_249882493.tar
rm /media/ephemeral0/names_249882493.tar
            
# Title: Team British Hurricane vs Team That's A Disband | Week 5 Day 1 Match 3 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248149116
# Created: 2018-04-08 18:33:07+00:00
# Duration 0:16:18
echo "250 / 343" >> progress.txt
echo "Title: Team British Hurricane vs Team That's A Disband | Week 5 Day 1 Match 3 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248149116" >> progress.txt
echo "Duration: 0:16:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248149116
tar cvf /media/ephemeral0/names_248149116.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248149116.tar s3://overtrack-training-data/vod-names/names_248149116.tar
rm /media/ephemeral0/names_248149116.tar
            
# Title: XL2 Academy vs. Bye Week | Week 5 Day 2 Match 2 Game 2 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292433265
# Created: 2018-08-03 01:47:22+00:00
# Duration 0:19:19
echo "251 / 343" >> progress.txt
echo "Title: XL2 Academy vs. Bye Week | Week 5 Day 2 Match 2 Game 2 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292433265" >> progress.txt
echo "Duration: 0:19:19" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292433265
tar cvf /media/ephemeral0/names_292433265.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292433265.tar s3://overtrack-training-data/vod-names/names_292433265.tar
rm /media/ephemeral0/names_292433265.tar
            
# Title: CIS Hope vs Orgless and Hungry | Playoffs - Round of 8 | Day 1 Match 2 Game 3 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253304245
# Created: 2018-04-22 17:07:24+00:00
# Duration 0:26:48
echo "252 / 343" >> progress.txt
echo "Title: CIS Hope vs Orgless and Hungry | Playoffs - Round of 8 | Day 1 Match 2 Game 3 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253304245" >> progress.txt
echo "Duration: 0:26:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253304245
tar cvf /media/ephemeral0/names_253304245.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253304245.tar s3://overtrack-training-data/vod-names/names_253304245.tar
rm /media/ephemeral0/names_253304245.tar
            
# Title: Xavier Esports vs LogitechG ABANG | Week 5 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252454239
# Created: 2018-04-20 14:14:59+00:00
# Duration 0:20:20
echo "253 / 343" >> progress.txt
echo "Title: Xavier Esports vs LogitechG ABANG | Week 5 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252454239" >> progress.txt
echo "Duration: 0:20:20" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252454239
tar cvf /media/ephemeral0/names_252454239.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252454239.tar s3://overtrack-training-data/vod-names/names_252454239.tar
rm /media/ephemeral0/names_252454239.tar
            
# Title: Xavier Esports vs CYCLOPS athlete gaming | Week 2 Day 2 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284690508
# Created: 2018-07-14 20:36:07+00:00
# Duration 0:19:24
echo "254 / 343" >> progress.txt
echo "Title: Xavier Esports vs CYCLOPS athlete gaming | Week 2 Day 2 Match 1 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284690508" >> progress.txt
echo "Duration: 0:19:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284690508
tar cvf /media/ephemeral0/names_284690508.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284690508.tar s3://overtrack-training-data/vod-names/names_284690508.tar
rm /media/ephemeral0/names_284690508.tar
            
# Title: Toronto Esports vs Gladiators Legion | Week 3 Day 2 Match 2 Game 2 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244097965
# Created: 2018-03-29 02:03:14+00:00
# Duration 0:22:49
echo "255 / 343" >> progress.txt
echo "Title: Toronto Esports vs Gladiators Legion | Week 3 Day 2 Match 2 Game 2 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244097965" >> progress.txt
echo "Duration: 0:22:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244097965
tar cvf /media/ephemeral0/names_244097965.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244097965.tar s3://overtrack-training-data/vod-names/names_244097965.tar
rm /media/ephemeral0/names_244097965.tar
            
# Title: Mosaic Esports vs CIS Hope | Week 3 Day 2 Match 3 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244408326
# Created: 2018-03-29 22:48:00+00:00
# Duration 0:29:54
echo "256 / 343" >> progress.txt
echo "Title: Mosaic Esports vs CIS Hope | Week 3 Day 2 Match 3 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244408326" >> progress.txt
echo "Duration: 0:29:54" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244408326
tar cvf /media/ephemeral0/names_244408326.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244408326.tar s3://overtrack-training-data/vod-names/names_244408326.tar
rm /media/ephemeral0/names_244408326.tar
            
# Title: Blank Esports vs OneShine Esports | Week 1 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241684251
# Created: 2018-03-22 20:48:37+00:00
# Duration 0:13:49
echo "257 / 343" >> progress.txt
echo "Title: Blank Esports vs OneShine Esports | Week 1 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241684251" >> progress.txt
echo "Duration: 0:13:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241684251
tar cvf /media/ephemeral0/names_241684251.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241684251.tar s3://overtrack-training-data/vod-names/names_241684251.tar
rm /media/ephemeral0/names_241684251.tar
            
# Title: Talon Esports vs Machi Esports | Week 4 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249881749
# Created: 2018-04-13 14:32:36+00:00
# Duration 0:30:23
echo "258 / 343" >> progress.txt
echo "Title: Talon Esports vs Machi Esports | Week 4 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249881749" >> progress.txt
echo "Duration: 0:30:23" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249881749
tar cvf /media/ephemeral0/names_249881749.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249881749.tar s3://overtrack-training-data/vod-names/names_249881749.tar
rm /media/ephemeral0/names_249881749.tar
            
# Title: Blank Esports vs Xavier Esports | Week 3 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246935606
# Created: 2018-04-05 16:18:26+00:00
# Duration 0:24:30
echo "259 / 343" >> progress.txt
echo "Title: Blank Esports vs Xavier Esports | Week 3 Day 1 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246935606" >> progress.txt
echo "Duration: 0:24:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246935606
tar cvf /media/ephemeral0/names_246935606.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246935606.tar s3://overtrack-training-data/vod-names/names_246935606.tar
rm /media/ephemeral0/names_246935606.tar
            
# Title: Xavier Esports vs MEGA | Week 4 Day 2 Match 1 Game 5 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250292756
# Created: 2018-04-14 16:02:06+00:00
# Duration 0:25:59
echo "260 / 343" >> progress.txt
echo "Title: Xavier Esports vs MEGA | Week 4 Day 2 Match 1 Game 5 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250292756" >> progress.txt
echo "Duration: 0:25:59" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250292756
tar cvf /media/ephemeral0/names_250292756.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250292756.tar s3://overtrack-training-data/vod-names/names_250292756.tar
rm /media/ephemeral0/names_250292756.tar
            
# Title: Chaos Theory vs Hong Kong Attitude | Week 3 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/247674112
# Created: 2018-04-07 14:57:28+00:00
# Duration 0:19:15
echo "261 / 343" >> progress.txt
echo "Title: Chaos Theory vs Hong Kong Attitude | Week 3 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/247674112" >> progress.txt
echo "Duration: 0:19:15" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/247674112
tar cvf /media/ephemeral0/names_247674112.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_247674112.tar s3://overtrack-training-data/vod-names/names_247674112.tar
rm /media/ephemeral0/names_247674112.tar
            
# Title: Orgless and Hungry vs Angry Titans | Week 5 Day 1 Match 1 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248068925
# Created: 2018-04-08 14:34:20+00:00
# Duration 0:08:12
echo "262 / 343" >> progress.txt
echo "Title: Orgless and Hungry vs Angry Titans | Week 5 Day 1 Match 1 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248068925" >> progress.txt
echo "Duration: 0:08:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248068925
tar cvf /media/ephemeral0/names_248068925.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248068925.tar s3://overtrack-training-data/vod-names/names_248068925.tar
rm /media/ephemeral0/names_248068925.tar
            
# Title: Team Gigantti vs Copenhagen Flames | Week 3 Day 2 Match 3 Game 3 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285915363
# Created: 2018-07-17 21:37:43+00:00
# Duration 0:18:21
echo "263 / 343" >> progress.txt
echo "Title: Team Gigantti vs Copenhagen Flames | Week 3 Day 2 Match 3 Game 3 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285915363" >> progress.txt
echo "Duration: 0:18:21" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285915363
tar cvf /media/ephemeral0/names_285915363.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285915363.tar s3://overtrack-training-data/vod-names/names_285915363.tar
rm /media/ephemeral0/names_285915363.tar
            
# Title: Team Gigantti vs Angry Titans | Week 3 Day 1 Match 3 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243997043
# Created: 2018-03-28 21:13:57+00:00
# Duration 0:20:16
echo "264 / 343" >> progress.txt
echo "Title: Team Gigantti vs Angry Titans | Week 3 Day 1 Match 3 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243997043" >> progress.txt
echo "Duration: 0:20:16" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243997043
tar cvf /media/ephemeral0/names_243997043.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243997043.tar s3://overtrack-training-data/vod-names/names_243997043.tar
rm /media/ephemeral0/names_243997043.tar
            
# Title: BAZAAR vs Machi Esports | Week 3 Day 2 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/247608048
# Created: 2018-04-07 09:56:16+00:00
# Duration 0:16:52
echo "265 / 343" >> progress.txt
echo "Title: BAZAAR vs Machi Esports | Week 3 Day 2 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/247608048" >> progress.txt
echo "Duration: 0:16:52" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/247608048
tar cvf /media/ephemeral0/names_247608048.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_247608048.tar s3://overtrack-training-data/vod-names/names_247608048.tar
rm /media/ephemeral0/names_247608048.tar
            
# Title: Blank Esports (BLK) vs CYCLOPS athlete gaming (CAG) | Week 1 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281774030
# Created: 2018-07-07 06:22:03+00:00
# Duration 0:16:12
echo "266 / 343" >> progress.txt
echo "Title: Blank Esports (BLK) vs CYCLOPS athlete gaming (CAG) | Week 1 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281774030" >> progress.txt
echo "Duration: 0:16:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281774030
tar cvf /media/ephemeral0/names_281774030.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281774030.tar s3://overtrack-training-data/vod-names/names_281774030.tar
rm /media/ephemeral0/names_281774030.tar
            
# Title: Blank Esports (BLK) vs Hong Kong Attitude (HKA) | Week 5 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292928917
# Created: 2018-08-04 06:45:34+00:00
# Duration 0:16:15
echo "267 / 343" >> progress.txt
echo "Title: Blank Esports (BLK) vs Hong Kong Attitude (HKA) | Week 5 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292928917" >> progress.txt
echo "Duration: 0:16:15" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292928917
tar cvf /media/ephemeral0/names_292928917.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292928917.tar s3://overtrack-training-data/vod-names/names_292928917.tar
rm /media/ephemeral0/names_292928917.tar
            
# Title: EXL-Esports vs Mega (MGA) | Week 5 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292928126
# Created: 2018-08-04 06:41:26+00:00
# Duration 0:25:32
echo "268 / 343" >> progress.txt
echo "Title: EXL-Esports vs Mega (MGA) | Week 5 Day 1 Match 1 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292928126" >> progress.txt
echo "Duration: 0:25:32" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292928126
tar cvf /media/ephemeral0/names_292928126.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292928126.tar s3://overtrack-training-data/vod-names/names_292928126.tar
rm /media/ephemeral0/names_292928126.tar
            
# Title: Blank Esports vs LogitechG ABANG | Week 2 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244315072
# Created: 2018-03-29 18:26:12+00:00
# Duration 0:17:33
echo "269 / 343" >> progress.txt
echo "Title: Blank Esports vs LogitechG ABANG | Week 2 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244315072" >> progress.txt
echo "Duration: 0:17:33" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244315072
tar cvf /media/ephemeral0/names_244315072.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244315072.tar s3://overtrack-training-data/vod-names/names_244315072.tar
rm /media/ephemeral0/names_244315072.tar
            
# Title: Orgless and Hungry vs Bazooka Puppiez | Week 3 Day 1 Match 2 Game 3 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285443127
# Created: 2018-07-16 19:02:15+00:00
# Duration 0:26:18
echo "270 / 343" >> progress.txt
echo "Title: Orgless and Hungry vs Bazooka Puppiez | Week 3 Day 1 Match 2 Game 3 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285443127" >> progress.txt
echo "Duration: 0:26:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285443127
tar cvf /media/ephemeral0/names_285443127.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285443127.tar s3://overtrack-training-data/vod-names/names_285443127.tar
rm /media/ephemeral0/names_285443127.tar
            
# Title: XL2 Academy vs. Bye Week | Week 5 Day 2 Match 2 Game 1 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292426855
# Created: 2018-08-03 01:29:47+00:00
# Duration 0:21:25
echo "271 / 343" >> progress.txt
echo "Title: XL2 Academy vs. Bye Week | Week 5 Day 2 Match 2 Game 1 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292426855" >> progress.txt
echo "Duration: 0:21:25" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292426855
tar cvf /media/ephemeral0/names_292426855.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292426855.tar s3://overtrack-training-data/vod-names/names_292426855.tar
rm /media/ephemeral0/names_292426855.tar
            
# Title: \Talon Esport (TLN) vs NEW PARADIGM | Week 2 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284438251
# Created: 2018-07-14 03:53:04+00:00
# Duration 0:19:12
echo "272 / 343" >> progress.txt
echo "Title: \Talon Esport (TLN) vs NEW PARADIGM | Week 2 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284438251" >> progress.txt
echo "Duration: 0:19:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284438251
tar cvf /media/ephemeral0/names_284438251.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284438251.tar s3://overtrack-training-data/vod-names/names_284438251.tar
rm /media/ephemeral0/names_284438251.tar
            
# Title: OneShine Esports vs MEGA | Week 3 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249872622
# Created: 2018-04-13 13:56:15+00:00
# Duration 0:23:58
echo "273 / 343" >> progress.txt
echo "Title: OneShine Esports vs MEGA | Week 3 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249872622" >> progress.txt
echo "Duration: 0:23:58" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249872622
tar cvf /media/ephemeral0/names_249872622.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249872622.tar s3://overtrack-training-data/vod-names/names_249872622.tar
rm /media/ephemeral0/names_249872622.tar
            
# Title: CIS Hope vs Orgless and Hungry | Playoffs - Round of 8 | Day 1 Match 2 Game 1 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253282433
# Created: 2018-04-22 16:02:37+00:00
# Duration 0:25:00
echo "274 / 343" >> progress.txt
echo "Title: CIS Hope vs Orgless and Hungry | Playoffs - Round of 8 | Day 1 Match 2 Game 1 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253282433" >> progress.txt
echo "Duration: 0:25:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253282433
tar cvf /media/ephemeral0/names_253282433.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253282433.tar s3://overtrack-training-data/vod-names/names_253282433.tar
rm /media/ephemeral0/names_253282433.tar
            
# Title: MEGA vs LogitechG ABANG | Week 1 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241692021
# Created: 2018-03-22 21:10:36+00:00
# Duration 0:19:39
echo "275 / 343" >> progress.txt
echo "Title: MEGA vs LogitechG ABANG | Week 1 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241692021" >> progress.txt
echo "Duration: 0:19:39" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241692021
tar cvf /media/ephemeral0/names_241692021.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241692021.tar s3://overtrack-training-data/vod-names/names_241692021.tar
rm /media/ephemeral0/names_241692021.tar
            
# Title: Chaos Theory vs Hong Kong Attitude | Week 3 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/247673356
# Created: 2018-04-07 14:54:58+00:00
# Duration 0:15:18
echo "276 / 343" >> progress.txt
echo "Title: Chaos Theory vs Hong Kong Attitude | Week 3 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/247673356" >> progress.txt
echo "Duration: 0:15:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/247673356
tar cvf /media/ephemeral0/names_247673356.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_247673356.tar s3://overtrack-training-data/vod-names/names_247673356.tar
rm /media/ephemeral0/names_247673356.tar
            
# Title: Angry Titans vs Young and Beautiful | Week 3 Day 1 Match 1 Game 3 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285403480
# Created: 2018-07-16 17:20:26+00:00
# Duration 0:14:17
echo "277 / 343" >> progress.txt
echo "Title: Angry Titans vs Young and Beautiful | Week 3 Day 1 Match 1 Game 3 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285403480" >> progress.txt
echo "Duration: 0:14:17" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285403480
tar cvf /media/ephemeral0/names_285403480.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285403480.tar s3://overtrack-training-data/vod-names/names_285403480.tar
rm /media/ephemeral0/names_285403480.tar
            
# Title: NEW PARADIGM vs MONSTER SHIELD KR | Week 4 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290497405
# Created: 2018-07-29 05:15:22+00:00
# Duration 0:27:56
echo "278 / 343" >> progress.txt
echo "Title: NEW PARADIGM vs MONSTER SHIELD KR | Week 4 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290497405" >> progress.txt
echo "Duration: 0:27:56" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290497405
tar cvf /media/ephemeral0/names_290497405.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290497405.tar s3://overtrack-training-data/vod-names/names_290497405.tar
rm /media/ephemeral0/names_290497405.tar
            
# Title: Xavier Esports (XVE) vs Incipience (INC) | Week 5 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292929689
# Created: 2018-08-04 06:49:47+00:00
# Duration 0:16:16
echo "279 / 343" >> progress.txt
echo "Title: Xavier Esports (XVE) vs Incipience (INC) | Week 5 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292929689" >> progress.txt
echo "Duration: 0:16:16" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292929689
tar cvf /media/ephemeral0/names_292929689.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292929689.tar s3://overtrack-training-data/vod-names/names_292929689.tar
rm /media/ephemeral0/names_292929689.tar
            
# Title: Grizzlys vs XL2 Academy | Week 3 Day 2 Match 3 Game 1 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244134479
# Created: 2018-03-29 04:06:41+00:00
# Duration 0:18:31
echo "280 / 343" >> progress.txt
echo "Title: Grizzlys vs XL2 Academy | Week 3 Day 2 Match 3 Game 1 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244134479" >> progress.txt
echo "Duration: 0:18:31" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244134479
tar cvf /media/ephemeral0/names_244134479.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244134479.tar s3://overtrack-training-data/vod-names/names_244134479.tar
rm /media/ephemeral0/names_244134479.tar
            
# Title: Angry Titans vs Young and Beautiful | Week 3 Day 1 Match 1 Game 4 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285410271
# Created: 2018-07-16 17:39:51+00:00
# Duration 0:13:18
echo "281 / 343" >> progress.txt
echo "Title: Angry Titans vs Young and Beautiful | Week 3 Day 1 Match 1 Game 4 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285410271" >> progress.txt
echo "Duration: 0:13:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285410271
tar cvf /media/ephemeral0/names_285410271.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285410271.tar s3://overtrack-training-data/vod-names/names_285410271.tar
rm /media/ephemeral0/names_285410271.tar
            
# Title: EXL-Esports vs NEW PARADIGM | Week 1 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281774029
# Created: 2018-07-07 06:22:03+00:00
# Duration 0:14:37
echo "282 / 343" >> progress.txt
echo "Title: EXL-Esports vs NEW PARADIGM | Week 1 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281774029" >> progress.txt
echo "Duration: 0:14:37" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281774029
tar cvf /media/ephemeral0/names_281774029.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281774029.tar s3://overtrack-training-data/vod-names/names_281774029.tar
rm /media/ephemeral0/names_281774029.tar
            
# Title: Orgless and Hungry vs Bazooka Puppiez | Week 3 Day 1 Match 2 Game 2 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285428018
# Created: 2018-07-16 18:24:25+00:00
# Duration 0:08:26
echo "283 / 343" >> progress.txt
echo "Title: Orgless and Hungry vs Bazooka Puppiez | Week 3 Day 1 Match 2 Game 2 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285428018" >> progress.txt
echo "Duration: 0:08:26" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285428018
tar cvf /media/ephemeral0/names_285428018.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285428018.tar s3://overtrack-training-data/vod-names/names_285428018.tar
rm /media/ephemeral0/names_285428018.tar
            
# Title: BAZAAR vs Machi Esports | Week 3 Day 2 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/247670940
# Created: 2018-04-07 14:46:24+00:00
# Duration 0:16:32
echo "284 / 343" >> progress.txt
echo "Title: BAZAAR vs Machi Esports | Week 3 Day 2 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/247670940" >> progress.txt
echo "Duration: 0:16:32" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/247670940
tar cvf /media/ephemeral0/names_247670940.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_247670940.tar s3://overtrack-training-data/vod-names/names_247670940.tar
rm /media/ephemeral0/names_247670940.tar
            
# Title: Detonator KR vs Hong Kong Attitude | Week 4 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249883000
# Created: 2018-04-13 14:38:01+00:00
# Duration 0:19:02
echo "285 / 343" >> progress.txt
echo "Title: Detonator KR vs Hong Kong Attitude | Week 4 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249883000" >> progress.txt
echo "Duration: 0:19:02" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249883000
tar cvf /media/ephemeral0/names_249883000.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249883000.tar s3://overtrack-training-data/vod-names/names_249883000.tar
rm /media/ephemeral0/names_249883000.tar
            
# Title: Bazooka Puppiez vs Young and Beautiful | Week 5 Day 2 Match 2 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248520242
# Created: 2018-04-09 19:43:48+00:00
# Duration 0:29:06
echo "286 / 343" >> progress.txt
echo "Title: Bazooka Puppiez vs Young and Beautiful | Week 5 Day 2 Match 2 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248520242" >> progress.txt
echo "Duration: 0:29:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248520242
tar cvf /media/ephemeral0/names_248520242.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248520242.tar s3://overtrack-training-data/vod-names/names_248520242.tar
rm /media/ephemeral0/names_248520242.tar
            
# Title: Hong Kong Attitude vs Bazaar | Week 1 Day 2 Match 1 Game 4 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242323756
# Created: 2018-03-24 14:40:10+00:00
# Duration 0:15:29
echo "287 / 343" >> progress.txt
echo "Title: Hong Kong Attitude vs Bazaar | Week 1 Day 2 Match 1 Game 4 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242323756" >> progress.txt
echo "Duration: 0:15:29" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242323756
tar cvf /media/ephemeral0/names_242323756.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242323756.tar s3://overtrack-training-data/vod-names/names_242323756.tar
rm /media/ephemeral0/names_242323756.tar
            
# Title: MEGA vs Machi Esports | Week 1 Day 1 Match 2 Game 1 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/254695228
# Created: 2018-04-26 15:11:36+00:00
# Duration 0:23:46
echo "288 / 343" >> progress.txt
echo "Title: MEGA vs Machi Esports | Week 1 Day 1 Match 2 Game 1 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/254695228" >> progress.txt
echo "Duration: 0:23:46" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/254695228
tar cvf /media/ephemeral0/names_254695228.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_254695228.tar s3://overtrack-training-data/vod-names/names_254695228.tar
rm /media/ephemeral0/names_254695228.tar
            
# Title: Toronto Esports vs. Team Envy | Week 5 Day 2 Match 3 Game 1 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292467023
# Created: 2018-08-03 03:23:06+00:00
# Duration 0:19:13
echo "289 / 343" >> progress.txt
echo "Title: Toronto Esports vs. Team Envy | Week 5 Day 2 Match 3 Game 1 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292467023" >> progress.txt
echo "Duration: 0:19:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292467023
tar cvf /media/ephemeral0/names_292467023.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292467023.tar s3://overtrack-training-data/vod-names/names_292467023.tar
rm /media/ephemeral0/names_292467023.tar
            
# Title: Mayhem Academy vs. Last Night's Leftovers | Week 5 Day 1 Match 3 Game 2 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291874758
# Created: 2018-08-01 18:03:32+00:00
# Duration 0:28:19
echo "290 / 343" >> progress.txt
echo "Title: Mayhem Academy vs. Last Night's Leftovers | Week 5 Day 1 Match 3 Game 2 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291874758" >> progress.txt
echo "Duration: 0:28:19" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291874758
tar cvf /media/ephemeral0/names_291874758.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291874758.tar s3://overtrack-training-data/vod-names/names_291874758.tar
rm /media/ephemeral0/names_291874758.tar
            
# Title: Eagle Gaming vs We Have Org | Week 3 Day 2 Match 2 Game 2 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285844166
# Created: 2018-07-17 18:32:16+00:00
# Duration 0:20:03
echo "291 / 343" >> progress.txt
echo "Title: Eagle Gaming vs We Have Org | Week 3 Day 2 Match 2 Game 2 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285844166" >> progress.txt
echo "Duration: 0:20:03" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285844166
tar cvf /media/ephemeral0/names_285844166.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285844166.tar s3://overtrack-training-data/vod-names/names_285844166.tar
rm /media/ephemeral0/names_285844166.tar
            
# Title: Xavier Esports (XVE) vs Incipience (INC) | Week 5 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/292929687
# Created: 2018-08-04 06:49:47+00:00
# Duration 0:16:52
echo "292 / 343" >> progress.txt
echo "Title: Xavier Esports (XVE) vs Incipience (INC) | Week 5 Day 1 Match 3 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292929687" >> progress.txt
echo "Duration: 0:16:52" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292929687
tar cvf /media/ephemeral0/names_292929687.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292929687.tar s3://overtrack-training-data/vod-names/names_292929687.tar
rm /media/ephemeral0/names_292929687.tar
            
# Title: Hong Kong Attitude vs Bazaar | Week 1 Day 2 Match 1 Game 3 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242322663
# Created: 2018-03-24 14:36:28+00:00
# Duration 0:18:45
echo "293 / 343" >> progress.txt
echo "Title: Hong Kong Attitude vs Bazaar | Week 1 Day 2 Match 1 Game 3 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242322663" >> progress.txt
echo "Duration: 0:18:45" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242322663
tar cvf /media/ephemeral0/names_242322663.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242322663.tar s3://overtrack-training-data/vod-names/names_242322663.tar
rm /media/ephemeral0/names_242322663.tar
            
# Title: NRG Esports vs. Skyfoxes | Week 5 Day 2 Match 1 Game 1 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292379270
# Created: 2018-08-02 23:21:55+00:00
# Duration 0:20:13
echo "294 / 343" >> progress.txt
echo "Title: NRG Esports vs. Skyfoxes | Week 5 Day 2 Match 1 Game 1 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292379270" >> progress.txt
echo "Duration: 0:20:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292379270
tar cvf /media/ephemeral0/names_292379270.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292379270.tar s3://overtrack-training-data/vod-names/names_292379270.tar
rm /media/ephemeral0/names_292379270.tar
            
# Title: British Hurricane vs Young & Beautiful | Playoffs - Round of 8 | Day 1 Match 1 Game 3 | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/253270538
# Created: 2018-04-22 15:24:14+00:00
# Duration 0:17:00
echo "295 / 343" >> progress.txt
echo "Title: British Hurricane vs Young & Beautiful | Playoffs - Round of 8 | Day 1 Match 1 Game 3 | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/253270538" >> progress.txt
echo "Duration: 0:17:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/253270538
tar cvf /media/ephemeral0/names_253270538.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_253270538.tar s3://overtrack-training-data/vod-names/names_253270538.tar
rm /media/ephemeral0/names_253270538.tar
            
# Title: Talon Esport (TLN) vs NEW PARADIGM | Week 2 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284438248
# Created: 2018-07-14 03:53:04+00:00
# Duration 0:17:30
echo "296 / 343" >> progress.txt
echo "Title: Talon Esport (TLN) vs NEW PARADIGM | Week 2 Day 1 Match 3 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284438248" >> progress.txt
echo "Duration: 0:17:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284438248
tar cvf /media/ephemeral0/names_284438248.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284438248.tar s3://overtrack-training-data/vod-names/names_284438248.tar
rm /media/ephemeral0/names_284438248.tar
            
# Title: Blank Esports vs LogitechG ABANG | Week 2 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244318169
# Created: 2018-03-29 18:34:17+00:00
# Duration 0:21:49
echo "297 / 343" >> progress.txt
echo "Title: Blank Esports vs LogitechG ABANG | Week 2 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244318169" >> progress.txt
echo "Duration: 0:21:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244318169
tar cvf /media/ephemeral0/names_244318169.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244318169.tar s3://overtrack-training-data/vod-names/names_244318169.tar
rm /media/ephemeral0/names_244318169.tar
            
# Title: Blank Esports vs Talon Esports | Week 1 Day 2 Match 1 Game 4 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/255426969
# Created: 2018-04-28 15:30:07+00:00
# Duration 0:22:49
echo "298 / 343" >> progress.txt
echo "Title: Blank Esports vs Talon Esports | Week 1 Day 2 Match 1 Game 4 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/255426969" >> progress.txt
echo "Duration: 0:22:49" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/255426969
tar cvf /media/ephemeral0/names_255426969.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_255426969.tar s3://overtrack-training-data/vod-names/names_255426969.tar
rm /media/ephemeral0/names_255426969.tar
            
# Title: CIS Hope vs Copenhagen Flames | Week 5 Day 2 Match 3 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248556520
# Created: 2018-04-09 21:30:15+00:00
# Duration 0:17:48
echo "299 / 343" >> progress.txt
echo "Title: CIS Hope vs Copenhagen Flames | Week 5 Day 2 Match 3 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248556520" >> progress.txt
echo "Duration: 0:17:48" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248556520
tar cvf /media/ephemeral0/names_248556520.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248556520.tar s3://overtrack-training-data/vod-names/names_248556520.tar
rm /media/ephemeral0/names_248556520.tar
            
# Title: XL2 Academy vs. Bye Week | Week 5 Day 2 Match 2 Game 4 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292455114
# Created: 2018-08-03 02:48:38+00:00
# Duration 0:21:55
echo "300 / 343" >> progress.txt
echo "Title: XL2 Academy vs. Bye Week | Week 5 Day 2 Match 2 Game 4 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292455114" >> progress.txt
echo "Duration: 0:21:55" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292455114
tar cvf /media/ephemeral0/names_292455114.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292455114.tar s3://overtrack-training-data/vod-names/names_292455114.tar
rm /media/ephemeral0/names_292455114.tar
            
# Title: Talon Esports vs BAZAAR | Week 2 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/244320995
# Created: 2018-03-29 18:42:06+00:00
# Duration 0:29:44
echo "301 / 343" >> progress.txt
echo "Title: Talon Esports vs BAZAAR | Week 2 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244320995" >> progress.txt
echo "Duration: 0:29:44" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244320995
tar cvf /media/ephemeral0/names_244320995.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244320995.tar s3://overtrack-training-data/vod-names/names_244320995.tar
rm /media/ephemeral0/names_244320995.tar
            
# Title: Mega (MGA) vs MONSTER SHIELD KR | Week 1 Day 2 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/282153490
# Created: 2018-07-08 07:42:11+00:00
# Duration 0:10:03
echo "302 / 343" >> progress.txt
echo "Title: Mega (MGA) vs MONSTER SHIELD KR | Week 1 Day 2 Match 1 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/282153490" >> progress.txt
echo "Duration: 0:10:03" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/282153490
tar cvf /media/ephemeral0/names_282153490.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_282153490.tar s3://overtrack-training-data/vod-names/names_282153490.tar
rm /media/ephemeral0/names_282153490.tar
            
# Title: Simplicity vs Fusion University | Week 3 Day 1 Match 3 Game 2 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243739503
# Created: 2018-03-28 03:36:00+00:00
# Duration 0:17:19
echo "303 / 343" >> progress.txt
echo "Title: Simplicity vs Fusion University | Week 3 Day 1 Match 3 Game 2 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243739503" >> progress.txt
echo "Duration: 0:17:19" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243739503
tar cvf /media/ephemeral0/names_243739503.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243739503.tar s3://overtrack-training-data/vod-names/names_243739503.tar
rm /media/ephemeral0/names_243739503.tar
            
# Title: Xavier Esports vs MEGA | Week 4 Day 2 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250290864
# Created: 2018-04-14 15:57:10+00:00
# Duration 0:10:56
echo "304 / 343" >> progress.txt
echo "Title: Xavier Esports vs MEGA | Week 4 Day 2 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250290864" >> progress.txt
echo "Duration: 0:10:56" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250290864
tar cvf /media/ephemeral0/names_250290864.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250290864.tar s3://overtrack-training-data/vod-names/names_250290864.tar
rm /media/ephemeral0/names_250290864.tar
            
# Title: CYCLOPS athlete gaming (CAG) vs Incipience (INC) | Week 4 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290483879
# Created: 2018-07-29 04:20:43+00:00
# Duration 0:13:16
echo "305 / 343" >> progress.txt
echo "Title: CYCLOPS athlete gaming (CAG) vs Incipience (INC) | Week 4 Day 2 Match 2 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290483879" >> progress.txt
echo "Duration: 0:13:16" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290483879
tar cvf /media/ephemeral0/names_290483879.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290483879.tar s3://overtrack-training-data/vod-names/names_290483879.tar
rm /media/ephemeral0/names_290483879.tar
            
# Title: CYCLOPS athlete gaming (CAG) vs Incipience (INC) | Week 4 Day 2 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290483882
# Created: 2018-07-29 04:20:43+00:00
# Duration 0:27:59
echo "306 / 343" >> progress.txt
echo "Title: CYCLOPS athlete gaming (CAG) vs Incipience (INC) | Week 4 Day 2 Match 2 Game 1 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290483882" >> progress.txt
echo "Duration: 0:27:59" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290483882
tar cvf /media/ephemeral0/names_290483882.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290483882.tar s3://overtrack-training-data/vod-names/names_290483882.tar
rm /media/ephemeral0/names_290483882.tar
            
# Title: Team Singularity vs That's a Disband | Week 3 Day 1 Match 2 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243939230
# Created: 2018-03-28 18:39:51+00:00
# Duration 0:16:12
echo "307 / 343" >> progress.txt
echo "Title: Team Singularity vs That's a Disband | Week 3 Day 1 Match 2 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243939230" >> progress.txt
echo "Duration: 0:16:12" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243939230
tar cvf /media/ephemeral0/names_243939230.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243939230.tar s3://overtrack-training-data/vod-names/names_243939230.tar
rm /media/ephemeral0/names_243939230.tar
            
# Title: Team British Hurricane vs Team That's A Disband | Week 5 Day 1 Match 3 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248152265
# Created: 2018-04-08 18:41:06+00:00
# Duration 0:24:36
echo "308 / 343" >> progress.txt
echo "Title: Team British Hurricane vs Team That's A Disband | Week 5 Day 1 Match 3 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248152265" >> progress.txt
echo "Duration: 0:24:36" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248152265
tar cvf /media/ephemeral0/names_248152265.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248152265.tar s3://overtrack-training-data/vod-names/names_248152265.tar
rm /media/ephemeral0/names_248152265.tar
            
# Title: BAZAAR vs Chaos Theory | Week 4 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250298180
# Created: 2018-04-14 16:19:29+00:00
# Duration 0:11:09
echo "309 / 343" >> progress.txt
echo "Title: BAZAAR vs Chaos Theory | Week 4 Day 2 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250298180" >> progress.txt
echo "Duration: 0:11:09" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250298180
tar cvf /media/ephemeral0/names_250298180.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250298180.tar s3://overtrack-training-data/vod-names/names_250298180.tar
rm /media/ephemeral0/names_250298180.tar
            
# Title: Last Night's Leftovers vs Mayhem Academy | Week 3 Day 2 Match 1 Game 1 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/244040658
# Created: 2018-03-28 23:21:22+00:00
# Duration 0:15:06
echo "310 / 343" >> progress.txt
echo "Title: Last Night's Leftovers vs Mayhem Academy | Week 3 Day 2 Match 1 Game 1 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244040658" >> progress.txt
echo "Duration: 0:15:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244040658
tar cvf /media/ephemeral0/names_244040658.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244040658.tar s3://overtrack-training-data/vod-names/names_244040658.tar
rm /media/ephemeral0/names_244040658.tar
            
# Title: Machi Esports vs Detonator KR | Week 1 Day 2 Match 2 Game 4 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242337529
# Created: 2018-03-24 15:24:49+00:00
# Duration 0:17:54
echo "311 / 343" >> progress.txt
echo "Title: Machi Esports vs Detonator KR | Week 1 Day 2 Match 2 Game 4 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242337529" >> progress.txt
echo "Duration: 0:17:54" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242337529
tar cvf /media/ephemeral0/names_242337529.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242337529.tar s3://overtrack-training-data/vod-names/names_242337529.tar
rm /media/ephemeral0/names_242337529.tar
            
# Title: Yoshimoto Encount vs Xavier Esports | Week 1 Day 2 Match 3 Game 5 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242344677
# Created: 2018-03-24 15:48:47+00:00
# Duration 0:17:37
echo "312 / 343" >> progress.txt
echo "Title: Yoshimoto Encount vs Xavier Esports | Week 1 Day 2 Match 3 Game 5 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242344677" >> progress.txt
echo "Duration: 0:17:37" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242344677
tar cvf /media/ephemeral0/names_242344677.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242344677.tar s3://overtrack-training-data/vod-names/names_242344677.tar
rm /media/ephemeral0/names_242344677.tar
            
# Title: Machi Esports vs MEGA | Week 2 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284710736
# Created: 2018-07-14 21:35:20+00:00
# Duration 0:32:54
echo "313 / 343" >> progress.txt
echo "Title: Machi Esports vs MEGA | Week 2 Day 2 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284710736" >> progress.txt
echo "Duration: 0:32:54" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284710736
tar cvf /media/ephemeral0/names_284710736.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284710736.tar s3://overtrack-training-data/vod-names/names_284710736.tar
rm /media/ephemeral0/names_284710736.tar
            
# Title: Blank Esports vs MEGA | Week 4 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/249875653
# Created: 2018-04-13 14:07:46+00:00
# Duration 0:16:33
echo "314 / 343" >> progress.txt
echo "Title: Blank Esports vs MEGA | Week 4 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/249875653" >> progress.txt
echo "Duration: 0:16:33" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/249875653
tar cvf /media/ephemeral0/names_249875653.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_249875653.tar s3://overtrack-training-data/vod-names/names_249875653.tar
rm /media/ephemeral0/names_249875653.tar
            
# Title: Blank Esports vs Talon Esports | Week 1 Day 2 Match 1 Game 2 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/255426159
# Created: 2018-04-28 15:27:12+00:00
# Duration 0:13:05
echo "315 / 343" >> progress.txt
echo "Title: Blank Esports vs Talon Esports | Week 1 Day 2 Match 1 Game 2 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/255426159" >> progress.txt
echo "Duration: 0:13:05" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/255426159
tar cvf /media/ephemeral0/names_255426159.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_255426159.tar s3://overtrack-training-data/vod-names/names_255426159.tar
rm /media/ephemeral0/names_255426159.tar
            
# Title: Yoshimoto Encount vs Xavier Esports | Week 1 Day 2 Match 3 Game 3 | Contenders Pacific
# URL: https://www.twitch.tv/videos/242342440
# Created: 2018-03-24 15:41:10+00:00
# Duration 0:23:30
echo "316 / 343" >> progress.txt
echo "Title: Yoshimoto Encount vs Xavier Esports | Week 1 Day 2 Match 3 Game 3 | Contenders Pacific" >> progress.txt
echo "URL: https://www.twitch.tv/videos/242342440" >> progress.txt
echo "Duration: 0:23:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/242342440
tar cvf /media/ephemeral0/names_242342440.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_242342440.tar s3://overtrack-training-data/vod-names/names_242342440.tar
rm /media/ephemeral0/names_242342440.tar
            
# Title: Bazooka Puppiez vs Copenhagen Flames | Week 3 Day 2 Match 2 Game 2 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244345824
# Created: 2018-03-29 19:46:55+00:00
# Duration 0:25:00
echo "317 / 343" >> progress.txt
echo "Title: Bazooka Puppiez vs Copenhagen Flames | Week 3 Day 2 Match 2 Game 2 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244345824" >> progress.txt
echo "Duration: 0:25:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244345824
tar cvf /media/ephemeral0/names_244345824.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244345824.tar s3://overtrack-training-data/vod-names/names_244345824.tar
rm /media/ephemeral0/names_244345824.tar
            
# Title: Blank Esports vs OneShine Esports | Week 1 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/241685168
# Created: 2018-03-22 20:51:07+00:00
# Duration 0:08:29
echo "318 / 343" >> progress.txt
echo "Title: Blank Esports vs OneShine Esports | Week 1 Day 1 Match 2 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/241685168" >> progress.txt
echo "Duration: 0:08:29" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/241685168
tar cvf /media/ephemeral0/names_241685168.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_241685168.tar s3://overtrack-training-data/vod-names/names_241685168.tar
rm /media/ephemeral0/names_241685168.tar
            
# Title: LogitechG ABANG vs YOSHIMOTO ENCOUNT | Week 3 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246937105
# Created: 2018-04-05 16:23:58+00:00
# Duration 0:19:28
echo "319 / 343" >> progress.txt
echo "Title: LogitechG ABANG vs YOSHIMOTO ENCOUNT | Week 3 Day 1 Match 3 Game 3 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246937105" >> progress.txt
echo "Duration: 0:19:28" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246937105
tar cvf /media/ephemeral0/names_246937105.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246937105.tar s3://overtrack-training-data/vod-names/names_246937105.tar
rm /media/ephemeral0/names_246937105.tar
            
# Title: BAZAAR vs Chaos Theory | Week 4 Day 2 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250296622
# Created: 2018-04-14 16:14:28+00:00
# Duration 0:18:15
echo "320 / 343" >> progress.txt
echo "Title: BAZAAR vs Chaos Theory | Week 4 Day 2 Match 3 Game 1 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250296622" >> progress.txt
echo "Duration: 0:18:15" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250296622
tar cvf /media/ephemeral0/names_250296622.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250296622.tar s3://overtrack-training-data/vod-names/names_250296622.tar
rm /media/ephemeral0/names_250296622.tar
            
# Title: Xavier Esports vs MEGA | Week 4 Day 2 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250291785
# Created: 2018-04-14 15:59:45+00:00
# Duration 0:15:01
echo "321 / 343" >> progress.txt
echo "Title: Xavier Esports vs MEGA | Week 4 Day 2 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250291785" >> progress.txt
echo "Duration: 0:15:01" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250291785
tar cvf /media/ephemeral0/names_250291785.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250291785.tar s3://overtrack-training-data/vod-names/names_250291785.tar
rm /media/ephemeral0/names_250291785.tar
            
# Title: Hong Kong Attitude (HKA) vs Incipience (INC) | Week 1 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281775402
# Created: 2018-07-07 06:29:16+00:00
# Duration 0:19:30
echo "322 / 343" >> progress.txt
echo "Title: Hong Kong Attitude (HKA) vs Incipience (INC) | Week 1 Day 1 Match 3 Game 4 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281775402" >> progress.txt
echo "Duration: 0:19:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281775402
tar cvf /media/ephemeral0/names_281775402.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281775402.tar s3://overtrack-training-data/vod-names/names_281775402.tar
rm /media/ephemeral0/names_281775402.tar
            
# Title: Gladiators Legion vs. Second Wind | Week 5 Day 1 Match 2 Game 2 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291869566
# Created: 2018-08-01 17:51:38+00:00
# Duration 0:22:13
echo "323 / 343" >> progress.txt
echo "Title: Gladiators Legion vs. Second Wind | Week 5 Day 1 Match 2 Game 2 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291869566" >> progress.txt
echo "Duration: 0:22:13" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291869566
tar cvf /media/ephemeral0/names_291869566.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291869566.tar s3://overtrack-training-data/vod-names/names_291869566.tar
rm /media/ephemeral0/names_291869566.tar
            
# Title: British Hurricane vs Orgless and Hungry | Week 3 Day 1 Match 1 Game 1 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/243926153
# Created: 2018-03-28 18:05:44+00:00
# Duration 0:31:06
echo "324 / 343" >> progress.txt
echo "Title: British Hurricane vs Orgless and Hungry | Week 3 Day 1 Match 1 Game 1 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243926153" >> progress.txt
echo "Duration: 0:31:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243926153
tar cvf /media/ephemeral0/names_243926153.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243926153.tar s3://overtrack-training-data/vod-names/names_243926153.tar
rm /media/ephemeral0/names_243926153.tar
            
# Title: Team British Hurricane vs Team That's A Disband | Week 5 Day 1 Match 3 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/248159209
# Created: 2018-04-08 18:58:39+00:00
# Duration 0:12:24
echo "325 / 343" >> progress.txt
echo "Title: Team British Hurricane vs Team That's A Disband | Week 5 Day 1 Match 3 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/248159209" >> progress.txt
echo "Duration: 0:12:24" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/248159209
tar cvf /media/ephemeral0/names_248159209.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_248159209.tar s3://overtrack-training-data/vod-names/names_248159209.tar
rm /media/ephemeral0/names_248159209.tar
            
# Title: Blank Esports vs YOSHIMOTO ENCOUNT | Week 5 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252060433
# Created: 2018-04-19 11:37:17+00:00
# Duration 0:18:06
echo "326 / 343" >> progress.txt
echo "Title: Blank Esports vs YOSHIMOTO ENCOUNT | Week 5 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252060433" >> progress.txt
echo "Duration: 0:18:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252060433
tar cvf /media/ephemeral0/names_252060433.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252060433.tar s3://overtrack-training-data/vod-names/names_252060433.tar
rm /media/ephemeral0/names_252060433.tar
            
# Title: CIS HOPE vs ONE.POINT | Week 3 Day 2 Match 1 Game 3 | Regular Season | Contenders Europe Season 2
# URL: https://www.twitch.tv/videos/285818288
# Created: 2018-07-17 17:26:39+00:00
# Duration 0:24:07
echo "327 / 343" >> progress.txt
echo "Title: CIS HOPE vs ONE.POINT | Week 3 Day 2 Match 1 Game 3 | Regular Season | Contenders Europe Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/285818288" >> progress.txt
echo "Duration: 0:24:07" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/285818288
tar cvf /media/ephemeral0/names_285818288.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_285818288.tar s3://overtrack-training-data/vod-names/names_285818288.tar
rm /media/ephemeral0/names_285818288.tar
            
# Title: CYCLOPS athlete gaming (CAG) vs Incipience (INC) | Week 4 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/290483880
# Created: 2018-07-29 04:20:43+00:00
# Duration 0:25:29
echo "328 / 343" >> progress.txt
echo "Title: CYCLOPS athlete gaming (CAG) vs Incipience (INC) | Week 4 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/290483880" >> progress.txt
echo "Duration: 0:25:29" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/290483880
tar cvf /media/ephemeral0/names_290483880.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_290483880.tar s3://overtrack-training-data/vod-names/names_290483880.tar
rm /media/ephemeral0/names_290483880.tar
            
# Title: Toronto Esports vs. Team Envy | Week 5 Day 2 Match 3 Game 4 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292481081
# Created: 2018-08-03 04:10:15+00:00
# Duration 0:12:06
echo "329 / 343" >> progress.txt
echo "Title: Toronto Esports vs. Team Envy | Week 5 Day 2 Match 3 Game 4 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292481081" >> progress.txt
echo "Duration: 0:12:06" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292481081
tar cvf /media/ephemeral0/names_292481081.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292481081.tar s3://overtrack-training-data/vod-names/names_292481081.tar
rm /media/ephemeral0/names_292481081.tar
            
# Title: Blank Esports (BLK) vs CYCLOPS athlete gaming (CAG) | Week 1 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281774027
# Created: 2018-07-07 06:22:03+00:00
# Duration 0:13:40
echo "330 / 343" >> progress.txt
echo "Title: Blank Esports (BLK) vs CYCLOPS athlete gaming (CAG) | Week 1 Day 1 Match 2 Game 2 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281774027" >> progress.txt
echo "Duration: 0:13:40" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281774027
tar cvf /media/ephemeral0/names_281774027.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281774027.tar s3://overtrack-training-data/vod-names/names_281774027.tar
rm /media/ephemeral0/names_281774027.tar
            
# Title: Contenders Pacific | OneShine Esports vs Xavier Esports | Week 2 Day 2 Match 1 Game 3 | S1: Regular Season
# URL: https://www.twitch.tv/videos/245006838
# Created: 2018-03-31 12:34:02+00:00
# Duration 0:26:58
echo "331 / 343" >> progress.txt
echo "Title: Contenders Pacific | OneShine Esports vs Xavier Esports | Week 2 Day 2 Match 1 Game 3 | S1: Regular Season" >> progress.txt
echo "URL: https://www.twitch.tv/videos/245006838" >> progress.txt
echo "Duration: 0:26:58" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/245006838
tar cvf /media/ephemeral0/names_245006838.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_245006838.tar s3://overtrack-training-data/vod-names/names_245006838.tar
rm /media/ephemeral0/names_245006838.tar
            
# Title: Gladiators Legion vs. Second Wind | Week 5 Day 1 Match 2 Game 3 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/291870781
# Created: 2018-08-01 17:54:44+00:00
# Duration 0:13:30
echo "332 / 343" >> progress.txt
echo "Title: Gladiators Legion vs. Second Wind | Week 5 Day 1 Match 2 Game 3 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/291870781" >> progress.txt
echo "Duration: 0:13:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/291870781
tar cvf /media/ephemeral0/names_291870781.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_291870781.tar s3://overtrack-training-data/vod-names/names_291870781.tar
rm /media/ephemeral0/names_291870781.tar
            
# Title: Talon Esports vs Hong Kong Attitude | Week 5 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/252044849
# Created: 2018-04-19 09:48:45+00:00
# Duration 0:12:25
echo "333 / 343" >> progress.txt
echo "Title: Talon Esports vs Hong Kong Attitude | Week 5 Day 1 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/252044849" >> progress.txt
echo "Duration: 0:12:25" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/252044849
tar cvf /media/ephemeral0/names_252044849.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_252044849.tar s3://overtrack-training-data/vod-names/names_252044849.tar
rm /media/ephemeral0/names_252044849.tar
            
# Title: Xavier Esports vs MEGA | Week 4 Day 2 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/250290239
# Created: 2018-04-14 15:55:19+00:00
# Duration 0:20:37
echo "334 / 343" >> progress.txt
echo "Title: Xavier Esports vs MEGA | Week 4 Day 2 Match 1 Game 2 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/250290239" >> progress.txt
echo "Duration: 0:20:37" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/250290239
tar cvf /media/ephemeral0/names_250290239.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_250290239.tar s3://overtrack-training-data/vod-names/names_250290239.tar
rm /media/ephemeral0/names_250290239.tar
            
# Title: Detonator KR vs LogitechG ABANG | Week 1 Day 1 Match 1 Game 3 | Contenders Pacific Season 1 Playoffs
# URL: https://www.twitch.tv/videos/254694503
# Created: 2018-04-26 15:08:34+00:00
# Duration 0:19:27
echo "335 / 343" >> progress.txt
echo "Title: Detonator KR vs LogitechG ABANG | Week 1 Day 1 Match 1 Game 3 | Contenders Pacific Season 1 Playoffs" >> progress.txt
echo "URL: https://www.twitch.tv/videos/254694503" >> progress.txt
echo "Duration: 0:19:27" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/254694503
tar cvf /media/ephemeral0/names_254694503.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_254694503.tar s3://overtrack-training-data/vod-names/names_254694503.tar
rm /media/ephemeral0/names_254694503.tar
            
# Title: Mosaic Esports vs CIS Hope | Week 3 Day 2 Match 3 Game 4 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244409336
# Created: 2018-03-29 22:51:13+00:00
# Duration 0:26:42
echo "336 / 343" >> progress.txt
echo "Title: Mosaic Esports vs CIS Hope | Week 3 Day 2 Match 3 Game 4 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244409336" >> progress.txt
echo "Duration: 0:26:42" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244409336
tar cvf /media/ephemeral0/names_244409336.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244409336.tar s3://overtrack-training-data/vod-names/names_244409336.tar
rm /media/ephemeral0/names_244409336.tar
            
# Title: Bazooka Puppiez vs Copenhagen Flames | Week 3 Day 2 Match 2 Game 3 | Regular Season | Contenders Europe Season 1
# URL: https://www.twitch.tv/videos/244350222
# Created: 2018-03-29 19:59:12+00:00
# Duration 0:30:00
echo "337 / 343" >> progress.txt
echo "Title: Bazooka Puppiez vs Copenhagen Flames | Week 3 Day 2 Match 2 Game 3 | Regular Season | Contenders Europe Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/244350222" >> progress.txt
echo "Duration: 0:30:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/244350222
tar cvf /media/ephemeral0/names_244350222.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_244350222.tar s3://overtrack-training-data/vod-names/names_244350222.tar
rm /media/ephemeral0/names_244350222.tar
            
# Title: EXL-Esports vs NEW PARADIGM | Week 1 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/281768432
# Created: 2018-07-07 05:53:11+00:00
# Duration 0:33:03
echo "338 / 343" >> progress.txt
echo "Title: EXL-Esports vs NEW PARADIGM | Week 1 Day 1 Match 1 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/281768432" >> progress.txt
echo "Duration: 0:33:03" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/281768432
tar cvf /media/ephemeral0/names_281768432.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_281768432.tar s3://overtrack-training-data/vod-names/names_281768432.tar
rm /media/ephemeral0/names_281768432.tar
            
# Title: Talon Esports vs Detonator KR | Week 3 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1
# URL: https://www.twitch.tv/videos/246933797
# Created: 2018-04-05 16:12:14+00:00
# Duration 0:19:18
echo "339 / 343" >> progress.txt
echo "Title: Talon Esports vs Detonator KR | Week 3 Day 1 Match 1 Game 4 | Regular Season | Contenders Pacific Season 1" >> progress.txt
echo "URL: https://www.twitch.tv/videos/246933797" >> progress.txt
echo "Duration: 0:19:18" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/246933797
tar cvf /media/ephemeral0/names_246933797.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_246933797.tar s3://overtrack-training-data/vod-names/names_246933797.tar
rm /media/ephemeral0/names_246933797.tar
            
# Title: NRG Esports vs. Skyfoxes | Week 5 Day 2 Match 1 Game 3 | Regular Season | Contenders North America Season 2
# URL: https://www.twitch.tv/videos/292403453
# Created: 2018-08-03 00:28:32+00:00
# Duration 0:29:01
echo "340 / 343" >> progress.txt
echo "Title: NRG Esports vs. Skyfoxes | Week 5 Day 2 Match 1 Game 3 | Regular Season | Contenders North America Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/292403453" >> progress.txt
echo "Duration: 0:29:01" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/292403453
tar cvf /media/ephemeral0/names_292403453.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_292403453.tar s3://overtrack-training-data/vod-names/names_292403453.tar
rm /media/ephemeral0/names_292403453.tar
            
# Title: Nova Esports vs Hong Kong Attitude | Week 2 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2
# URL: https://www.twitch.tv/videos/284703111
# Created: 2018-07-14 21:12:33+00:00
# Duration 0:24:00
echo "341 / 343" >> progress.txt
echo "Title: Nova Esports vs Hong Kong Attitude | Week 2 Day 2 Match 2 Game 3 | Regular Season | Contenders Pacific Season 2" >> progress.txt
echo "URL: https://www.twitch.tv/videos/284703111" >> progress.txt
echo "Duration: 0:24:00" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/284703111
tar cvf /media/ephemeral0/names_284703111.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_284703111.tar s3://overtrack-training-data/vod-names/names_284703111.tar
rm /media/ephemeral0/names_284703111.tar
            
# Title: EnVision vs Bye Week | Week 3 Day 1 Match 1 Game 2 | S1: Regular Season | Contenders North America
# URL: https://www.twitch.tv/videos/243657131
# Created: 2018-03-27 23:35:16+00:00
# Duration 0:12:30
echo "342 / 343" >> progress.txt
echo "Title: EnVision vs Bye Week | Week 3 Day 1 Match 1 Game 2 | S1: Regular Season | Contenders North America" >> progress.txt
echo "URL: https://www.twitch.tv/videos/243657131" >> progress.txt
echo "Duration: 0:12:30" >> progress.txt
echo >> progress.txt
export NAME_IMAGE_SAVE_DIR=/media/ephemeral0/names
mkdir $NAME_IMAGE_SAVE_DIR
python main.py https://www.twitch.tv/videos/243657131
tar cvf /media/ephemeral0/names_243657131.tar -C /media/ephemeral0/names .
rm /media/ephemeral0/names -Rf
aws s3 cp /media/ephemeral0/names_243657131.tar s3://overtrack-training-data/vod-names/names_243657131.tar
rm /media/ephemeral0/names_243657131.tar
