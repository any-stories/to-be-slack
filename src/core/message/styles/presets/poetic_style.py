from core.enums.day_period import DayPeriod
from core.message.models.pack import MessagePack
from core.message.components import MessageScene, MessageTone
from core.message.conditions import WeekdayCondition, DayPeriodCondition

POETIC_STYLE = MessagePack(
    scenes=[
        MessageScene(text="日子缓慢铺展，像一页被风轻轻翻动的诗。"),
        MessageScene(text="今天的光线极其温柔，正落在微小的事物上。"),
        MessageScene(text="空气里浮动着一种被拉长了的、缓慢的安静。"),
        MessageScene(text="世界正在悄悄卸下防备，变得柔软起来。"),
        MessageScene(text="长风吹过来的时候，连时间的步履都慢了下来。"),
        MessageScene(
            text="新的一周正悄然递来序言，愿你翻开得足够轻盈。",
            conditions=[WeekdayCondition(weekdays={0})],
        ),
        MessageScene(
            text="今天的城市，似乎在空气里提前藏好了下班的松弛感。",
            conditions=[WeekdayCondition(weekdays={4})],
        ),
        MessageScene(
            text="傍晚的风是个藏不住秘密的信使，一开口就在催你回家了。",
            conditions=[
                WeekdayCondition(weekdays={3}),
                DayPeriodCondition(periods={DayPeriod.DUSK, DayPeriod.EVENING}),
            ],
        ),
        MessageScene(text="所有日常都在无声推进 没有例外"),
    ],
    greetings={
        DayPeriod.DAWN: [
            "晨光微茫，万物正静静地醒来。",
            "熹微的光线刚刚好，宜私藏一份清晨的轻盈。",
            "第一缕微风掠过长街，今天正慢慢开始。",
        ],
        DayPeriod.MORNING: [
            "有阳光落在生活里，长夜的梦境已有了着落。",
            "早安，把脚步放慢一点，别错过了蓝天的温柔。",
            "清晨的呼吸格外清澈，适合在工位上发一会儿呆。",
        ],
        DayPeriod.NOON: [
            "正午的光线有些饱满，去看一眼云朵的停顿吧。",
            "辛苦半天了，去和一杯温热的午饭握手言和。",
            "把视线从屏幕前移开，此刻的阳光正毫无动机。",
        ],
        DayPeriod.AFTERNOON: [
            "阳光开始倾斜，空气里浮动着慵懒的质感。",
            "下午茶的时间到了，愿困倦被窗外的风轻轻吹散。",
            "写字楼里的流速变慢了，适合短暂地和灵魂散个步。",
        ],
        DayPeriod.DUSK: [
            "黄昏是白昼最慷慨的告别，晚霞铺展得刚刚好。",
            "晚风正在慢慢变轻，它在催促你卸下所有的防备。",
            "忙碌快要结束了，去长廊的尽头等一辆日落的列车。",
        ],
        DayPeriod.EVENING: [
            "灯火初上，夜色擅长用细腻的笔触安抚所有情绪。",
            "晚上好，愿今晚的月色比白天的日光还要温柔一点。",
            "世界已经安静下来，今晚的风刚好能吹散一整天的疲惫。",
        ],
        DayPeriod.LATE_NIGHT: [
            "夜色在窗外静静流转，把剩下的时间留给自己吧。",
            "别太晚睡，今晚适合跌进一个没有日程表的温柔梦乡。",
            "明朝无事，愿今夜有安静而长久的梦。",
        ],
    },
    tones=[
        MessageTone(
            header="日常的琐事总是写不完的，觉得累了，就一定要大方地站起来。去走廊里看一眼窗外，去茶水间倒一杯温水，别总在工位上把自己坐成一尊雕塑。外面的世界在按部就班地运转，但这一刻的呼吸和时间，是真正属于你自己的。",
            footer="按时打卡是送给生活的交待，而偷偷放空，则是你留给自己的温柔。祝愿每个懂得照顾自己的同行人，都能愉快地虚度每一个细碎的片刻。",
        ),
        MessageTone(
            header="写字楼里的冷气总是很足，但别忘了去感受有温度的生活。有事没事就离开工位去廊道走走吧，去洗手间听听水流的声音，去露台吹吹没有方向的晚风。钱是永远赚不完的，但好好爱护自己的身体，比什么都重要。",
            footer="上班是把时间借给别人，而偶尔的失神，是把生活还给自己。愿你在这些没有任务的几分钟里，每天都能赚足满分的小确幸。",
        ),
        MessageTone(
            header="屏幕上的数字跳动得太快，快到让人忘记了外面的天色。不要总是和疲惫死磕，站起身去茶水间看看茶叶缓缓舒展，或者去走廊漫无目的地散个步。工作只是生活的一部分，多留一点闲暇给自己，人才会变得轻盈起来。",
            footer="帮世界运转是不得不做的事，而偷偷开个小差，是送给自己最体面的富有。愿每一个在写字楼里秘密出逃的你，都能心安理得地享用每一分钟的松弛。",
        ),
        MessageTone(
            header="格子间里的空气总是很安静，也容易让人觉得紧绷。觉得困顿了，就立刻站起来拍拍衣角，去长廊里收集一阵安静，去窗前看看一朵云的停顿。外界给你的薪水总有一个上限，但你留给自己的温柔，本该无限辽阔。",
            footer="既然白昼的终点都是为了碎银几两，那摸鱼时的那抹惬意，就是你最丰厚的额外犒赏。愿你每天都能在紧绷的日常里，撞进一片温柔的荒野。",
        ),
        MessageTone(
            header="周遭的空气里弥漫着催促的频率，每个人都在为了某个终点而行色匆匆。而你大可不必永远踩在别人的鼓点上，去倒一杯咖啡，去洗手间掬一捧凉水，在阴凉处安心地让自己舒展一下，保全身体的自由比什么都划算。",
            footer="在这场关于效率的赛跑里，偶尔停下来看看指尖的微光，才是最浪漫的叛逆。最后，祝愿所有正在爱护着自己的摸鱼人，都能愉快地渡过每一天。",
        ),
    ],
)
