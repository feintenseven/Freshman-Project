import asyncio
from datetime import datetime
import aiotieba
import pandas as pd
from tqdm import tqdm


async def main():
    tb_list = input().split()
    for tb in tb_list:
        print(f"--------------------{tb} Begin!--------------------")
        async with aiotieba.Client() as client:
            it_tuple = []
            for pn in tqdm(range(100)):
                threads = await client.get_threads(tb, pn=pn + 1, rn=100)
                it_tuple += [(thread.user.user_name, thread.user.nick_name_new, \
                              thread.user.level, thread.user.glevel, thread.user.gender, \
                              thread.user.is_vip, thread.title, thread.text, \
                              thread.view_num, thread.reply_num, thread.share_num, \
                              thread.agree, thread.disagree,
                              datetime.fromtimestamp(thread.create_time).strftime('%Y-%m-%d %H:%M:%S'), \
                              datetime.fromtimestamp(thread.last_time).strftime('%Y-%m-%d %H:%M:%S')) for thread in
                             threads]
        df = pd.DataFrame(it_tuple, columns=['user_name', 'nick_name', 'level', 'glevel', \
                                             'gender', 'is_vip', 'title', 'text', 'view', 'reply', \
                                             'share', 'agree', 'disagree', 'create_time', 'last_time'])
        df.to_csv(f"./result/{tb}.csv", lineterminator="\r\n", index=False, encoding='utf-8-sig')
    print("爬取完成！")


asyncio.run(main())